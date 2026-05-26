---
name: frontend-design/components
---

# Patrones de Componentes Comunes

## Hero Section

```typescript
// Hero moderno con gradiente y CTA
export function HeroSection() {
  return (
    <section className="
      relative overflow-hidden
      bg-gradient-to-br from-primary-600 via-primary-700 to-primary-900
      py-24 sm:py-32 lg:py-40
    ">

      {/* Background pattern */}
      <div className="
        absolute inset-0
        bg-[url('/grid.svg')]
        opacity-10
      " />

      <div className="relative max-w-7xl mx-auto px-6 lg:px-8">

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="max-w-3xl"
        >

          {/* Badge */}
          <div className="
            inline-flex items-center gap-2
            px-4 py-2 rounded-full
            bg-white/10 backdrop-blur-sm
            text-white text-sm font-medium
            mb-6
          ">
            <Sparkles className="w-4 h-4" />
            <span>Nuevo: Feature Launch</span>
          </div>

          {/* Headline */}
          <h1 className="
            text-5xl sm:text-6xl lg:text-7xl
            font-bold text-white
            leading-tight mb-6
          ">
            Transforma tu negocio con{' '}
            <span className="
              bg-gradient-to-r from-accent-400 to-accent-600
              bg-clip-text text-transparent
            ">
              nuestra solución
            </span>
          </h1>

          {/* Subheadline */}
          <p className="
            text-xl sm:text-2xl
            text-primary-100
            leading-relaxed mb-10
          ">
            La plataforma todo-en-uno para gestionar tu empresa de manera eficiente y escalable
          </p>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row gap-4">
            <Button
              size="lg"
              className="
                bg-white text-primary-700
                hover:bg-primary-50
                shadow-xl hover:shadow-2xl
              "
            >
              Comenzar gratis
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>

            <Button
              size="lg"
              variant="outline"
              className="
                border-2 border-white/20
                text-white
                hover:bg-white/10
                backdrop-blur-sm
              "
            >
              Ver demo
              <Play className="ml-2 w-5 h-5" />
            </Button>
          </div>

          {/* Social proof */}
          <div className="mt-12 flex items-center gap-6">
            <div className="flex -space-x-2">
              {[1,2,3,4].map(i => (
                <Image
                  key={i}
                  src={`/avatars/${i}.jpg`}
                  alt="User"
                  width={40}
                  height={40}
                  className="rounded-full border-2 border-white"
                />
              ))}
            </div>
            <div className="text-white/90">
              <div className="font-semibold">+10,000 empresas</div>
              <div className="text-sm text-white/70">confían en nosotros</div>
            </div>
          </div>

        </motion.div>

      </div>

      {/* Decorative elements */}
      <div className="
        absolute -top-24 -right-24
        w-96 h-96
        bg-accent-500/20
        rounded-full
        blur-3xl
      " />
      <div className="
        absolute -bottom-24 -left-24
        w-96 h-96
        bg-primary-400/20
        rounded-full
        blur-3xl
      " />

    </section>
  )
}
```

## Feature Cards

```typescript
// Feature cards con iconos y hover effects
export function FeatureCards() {
  const features = [
    {
      icon: Zap,
      title: 'Ultra rápido',
      description: 'Rendimiento optimizado para experiencias instantáneas',
      color: 'from-yellow-400 to-orange-500',
    },
    {
      icon: Shield,
      title: 'Seguro',
      description: 'Encriptación de nivel empresarial para tus datos',
      color: 'from-blue-400 to-cyan-500',
    },
    {
      icon: Users,
      title: 'Colaborativo',
      description: 'Trabaja en equipo sin fricción ni límites',
      color: 'from-purple-400 to-pink-500',
    },
  ]

  return (
    <section className="py-24 bg-neutral-50">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">

        <div className="text-center max-w-2xl mx-auto mb-16">
          <h2 className="text-4xl font-bold text-neutral-900 mb-4">
            Todo lo que necesitas
          </h2>
          <p className="text-xl text-neutral-600">
            Potencia tu productividad con features diseñadas para tu éxito
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card className="
                group
                h-full p-8
                border-2 border-neutral-200
                hover:border-primary-300
                hover:shadow-xl hover:shadow-primary-100
                transition-all duration-300
                cursor-pointer
              ">

                {/* Icon */}
                <div className={`
                  w-14 h-14 rounded-2xl
                  bg-gradient-to-br ${feature.color}
                  flex items-center justify-center
                  mb-6
                  group-hover:scale-110
                  transition-transform duration-300
                `}>
                  <feature.icon className="w-7 h-7 text-white" />
                </div>

                {/* Content */}
                <h3 className="
                  text-2xl font-bold text-neutral-900 mb-3
                  group-hover:text-primary-600
                  transition-colors
                ">
                  {feature.title}
                </h3>

                <p className="text-neutral-600 leading-relaxed mb-6">
                  {feature.description}
                </p>

                {/* Link */}
                <div className="
                  inline-flex items-center gap-2
                  text-primary-600 font-medium
                  group-hover:gap-3
                  transition-all
                ">
                  <span>Conocer más</span>
                  <ArrowRight className="w-4 h-4" />
                </div>

              </Card>
            </motion.div>
          ))}
        </div>

      </div>
    </section>
  )
}
```

## Dashboard Layout

```typescript
// Dashboard moderno con sidebar y stats
export function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-neutral-50">

      {/* Sidebar */}
      <aside className="
        w-64 bg-white border-r border-neutral-200
        flex flex-col
      ">

        {/* Logo */}
        <div className="p-6 border-b border-neutral-200">
          <Logo className="h-8" />
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          <NavItem icon={LayoutDashboard} label="Dashboard" active />
          <NavItem icon={Users} label="Clientes" />
          <NavItem icon={FileText} label="Documentos" />
          <NavItem icon={Settings} label="Configuración" />
        </nav>

        {/* User menu */}
        <div className="p-4 border-t border-neutral-200">
          <UserMenu />
        </div>

      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">

        {/* Header */}
        <header className="
          bg-white border-b border-neutral-200
          px-8 py-4
          flex items-center justify-between
        ">
          <div>
            <h1 className="text-2xl font-bold text-neutral-900">
              Dashboard
            </h1>
            <p className="text-neutral-600">
              Bienvenido de vuelta, Juan
            </p>
          </div>

          <div className="flex items-center gap-4">
            <SearchBar />
            <NotificationsButton />
          </div>
        </header>

        {/* Content area */}
        <main className="flex-1 overflow-y-auto p-8">

          {/* Stats grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <StatCard
              label="Ingresos totales"
              value="$48,574"
              change="+12.5%"
              trend="up"
              icon={DollarSign}
            />
            <StatCard
              label="Nuevos clientes"
              value="324"
              change="+8.2%"
              trend="up"
              icon={Users}
            />
            <StatCard
              label="Tasa de conversión"
              value="3.24%"
              change="-2.1%"
              trend="down"
              icon={TrendingUp}
            />
            <StatCard
              label="Proyectos activos"
              value="12"
              change="+3"
              trend="up"
              icon={Briefcase}
            />
          </div>

          {/* Main content */}
          {children}

        </main>

      </div>

    </div>
  )
}

function StatCard({ label, value, change, trend, icon: Icon }) {
  return (
    <Card className="p-6">
      <div className="flex items-start justify-between mb-4">
        <div className={`
          w-12 h-12 rounded-lg
          flex items-center justify-center
          ${trend === 'up'
            ? 'bg-green-100 text-green-600'
            : 'bg-red-100 text-red-600'
          }
        `}>
          <Icon className="w-6 h-6" />
        </div>
        <div className={`
          text-sm font-medium
          ${trend === 'up' ? 'text-green-600' : 'text-red-600'}
        `}>
          {change}
        </div>
      </div>
      <div className="text-3xl font-bold text-neutral-900 mb-1">
        {value}
      </div>
      <div className="text-neutral-600">
        {label}
      </div>
    </Card>
  )
}
```

## Form Design

```typescript
// Formulario con validación y UX pulida
export function ModernForm() {
  const [isLoading, setIsLoading] = useState(false)
  const [errors, setErrors] = useState({})

  return (
    <div className="min-h-screen bg-neutral-50 flex items-center justify-center p-6">

      <Card className="w-full max-w-md p-8">

        {/* Header */}
        <div className="text-center mb-8">
          <div className="
            w-16 h-16 mx-auto mb-4
            bg-gradient-to-br from-primary-500 to-primary-700
            rounded-2xl
            flex items-center justify-center
          ">
            <Rocket className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-3xl font-bold text-neutral-900 mb-2">
            Crear cuenta
          </h2>
          <p className="text-neutral-600">
            Comienza tu prueba gratuita de 14 días
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-5">

          {/* Name field */}
          <div>
            <label className="
              block text-sm font-medium text-neutral-700 mb-2
            ">
              Nombre completo
            </label>
            <div className="relative">
              <User className="
                absolute left-3 top-1/2 -translate-y-1/2
                w-5 h-5 text-neutral-400
              " />
              <input
                type="text"
                placeholder="Juan Pérez"
                className={`
                  w-full pl-10 pr-4 py-3
                  border-2 rounded-lg
                  focus:outline-none focus:ring-4
                  transition-all
                  ${errors.name
                    ? 'border-red-300 focus:border-red-500 focus:ring-red-100'
                    : 'border-neutral-200 focus:border-primary-500 focus:ring-primary-100'
                  }
                `}
              />
            </div>
            {errors.name && (
              <p className="mt-2 text-sm text-red-600 flex items-center gap-1">
                <AlertCircle className="w-4 h-4" />
                {errors.name}
              </p>
            )}
          </div>

          {/* Email field */}
          <div>
            <label className="
              block text-sm font-medium text-neutral-700 mb-2
            ">
              Email
            </label>
            <div className="relative">
              <Mail className="
                absolute left-3 top-1/2 -translate-y-1/2
                w-5 h-5 text-neutral-400
              " />
              <input
                type="email"
                placeholder="juan@ejemplo.com"
                className="
                  w-full pl-10 pr-4 py-3
                  border-2 border-neutral-200 rounded-lg
                  focus:outline-none focus:ring-4
                  focus:border-primary-500 focus:ring-primary-100
                  transition-all
                "
              />
            </div>
          </div>

          {/* Password field */}
          <div>
            <label className="
              block text-sm font-medium text-neutral-700 mb-2
            ">
              Contraseña
            </label>
            <div className="relative">
              <Lock className="
                absolute left-3 top-1/2 -translate-y-1/2
                w-5 h-5 text-neutral-400
              " />
              <input
                type="password"
                placeholder="••••••••"
                className="
                  w-full pl-10 pr-4 py-3
                  border-2 border-neutral-200 rounded-lg
                  focus:outline-none focus:ring-4
                  focus:border-primary-500 focus:ring-primary-100
                  transition-all
                "
              />
            </div>
            <p className="mt-2 text-xs text-neutral-500">
              Mínimo 8 caracteres con mayúsculas y números
            </p>
          </div>

          {/* Terms */}
          <div className="flex items-start gap-3">
            <input
              type="checkbox"
              id="terms"
              className="
                mt-1 w-4 h-4
                text-primary-600 rounded
                focus:ring-2 focus:ring-primary-200
              "
            />
            <label htmlFor="terms" className="text-sm text-neutral-600">
              Acepto los{' '}
              <a href="#" className="text-primary-600 hover:underline">
                términos y condiciones
              </a>
              {' '}y la{' '}
              <a href="#" className="text-primary-600 hover:underline">
                política de privacidad
              </a>
            </label>
          </div>

          {/* Submit button */}
          <Button
            type="submit"
            disabled={isLoading}
            className="
              w-full py-3
              bg-gradient-to-r from-primary-600 to-primary-700
              hover:from-primary-700 hover:to-primary-800
              text-white font-medium
              shadow-lg hover:shadow-xl
              transition-all
            "
          >
            {isLoading ? (
              <span className="flex items-center justify-center gap-2">
                <Loader className="w-5 h-5 animate-spin" />
                Creando cuenta...
              </span>
            ) : (
              <span className="flex items-center justify-center gap-2">
                Crear cuenta
                <ArrowRight className="w-5 h-5" />
              </span>
            )}
          </Button>

          {/* Footer */}
          <p className="text-center text-sm text-neutral-600">
            ¿Ya tienes cuenta?{' '}
            <a href="#" className="
              text-primary-600 font-medium
              hover:text-primary-700
            ">
              Inicia sesión
            </a>
          </p>

        </form>

      </Card>

    </div>
  )
}
```
