---
title: Server Components (Next.js)
parent: react-best-practices
rules: 8
---

# Server Components (Next.js) (8 reglas)

## 6.1 Usar Server Components por Defecto
**✅ HACER:**
```typescript
// app/dashboard/page.tsx - Server Component por defecto
async function DashboardPage() {
  const user = await getCurrentUser();
  const stats = await fetchDashboardStats(user.id);

  return (
    <div>
      <h1>Dashboard de {user.name}</h1>
      <StatsDisplay stats={stats} />
    </div>
  );
}

export default DashboardPage;
```

## 6.2 Marcar Client Components con 'use client'
**✅ HACER:**
```typescript
// components/InteractiveButton.tsx
'use client';

import { useState } from 'react';

export function InteractiveButton() {
  const [count, setCount] = useState(0);

  return (
    <button onClick={() => setCount(count + 1)}>
      Clicks: {count}
    </button>
  );
}
```

## 6.3 Fetch Data en Server Components
**✅ HACER:**
```typescript
// app/posts/page.tsx
async function PostsPage() {
  // Fetch directo en Server Component
  const posts = await db.post.findMany({
    orderBy: { createdAt: 'desc' },
    take: 10,
  });

  return (
    <div>
      <h1>Posts Recientes</h1>
      {posts.map(post => (
        <PostCard key={post.id} post={post} />
      ))}
    </div>
  );
}
```

**❌ EVITAR (en Server Components):**
```typescript
// ❌ No usar useEffect para fetch en Server Components
function PostsPage() {
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    fetch('/api/posts').then(res => res.json()).then(setPosts);
  }, []);

  return <div>{/* ... */}</div>;
}
```

## 6.4 Usar Streaming y Suspense
**✅ HACER:**
```typescript
// app/dashboard/page.tsx
import { Suspense } from 'react';

async function RecentOrders() {
  const orders = await fetchRecentOrders();
  return <OrdersList orders={orders} />;
}

async function Analytics() {
  const data = await fetchAnalytics();
  return <AnalyticsChart data={data} />;
}

export default function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>

      <Suspense fallback={<Skeleton />}>
        <RecentOrders />
      </Suspense>

      <Suspense fallback={<ChartSkeleton />}>
        <Analytics />
      </Suspense>
    </div>
  );
}
```

## 6.5 Pasar Solo Datos Serializables a Client Components
**✅ HACER:**
```typescript
// app/user/page.tsx - Server Component
async function UserPage({ params }: { params: { id: string } }) {
  const user = await fetchUser(params.id);

  // Convertir Date a string antes de pasar a Client Component
  const userData = {
    ...user,
    createdAt: user.createdAt.toISOString(),
  };

  return <UserProfile user={userData} />;
}

// components/UserProfile.tsx - Client Component
'use client';

interface UserProfileProps {
  user: {
    name: string;
    email: string;
    createdAt: string; // ✅ String, no Date
  };
}

export function UserProfile({ user }: UserProfileProps) {
  const date = new Date(user.createdAt);
  return <div>Miembro desde: {date.toLocaleDateString()}</div>;
}
```

## 6.6 Usar Server Actions para Mutaciones
**✅ HACER:**
```typescript
// app/actions.ts
'use server';

export async function createPost(formData: FormData) {
  const title = formData.get('title') as string;
  const content = formData.get('content') as string;

  await db.post.create({
    data: { title, content },
  });

  revalidatePath('/posts');
  redirect('/posts');
}

// app/posts/new/page.tsx
import { createPost } from '@/app/actions';

export default function NewPostPage() {
  return (
    <form action={createPost}>
      <input name="title" required />
      <textarea name="content" required />
      <button type="submit">Crear Post</button>
    </form>
  );
}
```

## 6.7 Implementar Loading y Error States
**✅ HACER:**
```typescript
// app/posts/loading.tsx
export default function Loading() {
  return <PostsListSkeleton />;
}

// app/posts/error.tsx
'use client';

export default function Error({ error, reset }: ErrorProps) {
  return (
    <div>
      <h2>Algo salió mal</h2>
      <p>{error.message}</p>
      <button onClick={reset}>Intentar de nuevo</button>
    </div>
  );
}

// app/posts/page.tsx
export default async function PostsPage() {
  const posts = await fetchPosts(); // Si falla, muestra error.tsx
  return <PostsList posts={posts} />;
}
```

## 6.8 Optimizar con Metadata API
**✅ HACER:**
```typescript
// app/posts/[id]/page.tsx
import { Metadata } from 'next';

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const post = await fetchPost(params.id);

  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      images: [post.coverImage],
    },
  };
}

export default async function PostPage({ params }: Props) {
  const post = await fetchPost(params.id);
  return <PostContent post={post} />;
}
```
