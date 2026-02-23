import { createClient, type SupabaseClient } from '@supabase/supabase-js'

export interface Category {
  id: string
  name: string
  emoji: string
}

export interface WordPair {
  word: string
  ref: string
  hint?: string | null
}

// Inicialización lazy — no crashea el servidor si las env vars faltan al importar
let _client: SupabaseClient | null = null

function getClient(): SupabaseClient {
  if (_client) return _client

  const url = process.env.SUPABASE_URL
  const key = process.env.SUPABASE_ANON_KEY

  if (!url || !key) {
    throw new Error(
      '[supabase] SUPABASE_URL y SUPABASE_ANON_KEY son requeridas. Revisa tu archivo .env'
    )
  }

  _client = createClient(url, key)
  return _client
}

export async function getActiveCategories(): Promise<Category[]> {
  const { data, error } = await getClient().rpc('get_active_categories')

  if (error) {
    console.error('[supabase] getActiveCategories error:', error.message)
    return []
  }

  return (data as Category[]) ?? []
}

export async function getRandomWordPair(categoryId: string): Promise<WordPair> {
  const { data, error } = await getClient().rpc('get_random_word', {
    p_category_id: categoryId,
  })

  if (error) {
    console.error('[supabase] getRandomWordPair error:', error.message)
    throw new Error(`Failed to get word pair: ${error.message}`)
  }

  const rows = data as WordPair[]
  const result = Array.isArray(rows) ? rows[0] : (data as WordPair)

  if (!result?.word || !result?.ref) {
    throw new Error('No se encontraron palabras para esta categoría')
  }

  return result
}
