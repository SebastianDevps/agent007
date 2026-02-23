"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getActiveCategories = getActiveCategories;
exports.getRandomWordPair = getRandomWordPair;
const supabase_js_1 = require("@supabase/supabase-js");
// Inicialización lazy — no crashea el servidor si las env vars faltan al importar
let _client = null;
function getClient() {
    if (_client)
        return _client;
    const url = process.env.SUPABASE_URL;
    const key = process.env.SUPABASE_ANON_KEY;
    if (!url || !key) {
        throw new Error('[supabase] SUPABASE_URL y SUPABASE_ANON_KEY son requeridas. Revisa tu archivo .env');
    }
    _client = (0, supabase_js_1.createClient)(url, key);
    return _client;
}
async function getActiveCategories() {
    const { data, error } = await getClient().rpc('get_active_categories');
    if (error) {
        console.error('[supabase] getActiveCategories error:', error.message);
        return [];
    }
    return data ?? [];
}
async function getRandomWordPair(categoryId) {
    const { data, error } = await getClient().rpc('get_random_word', {
        p_category_id: categoryId,
    });
    if (error) {
        console.error('[supabase] getRandomWordPair error:', error.message);
        throw new Error(`Failed to get word pair: ${error.message}`);
    }
    const rows = data;
    const result = Array.isArray(rows) ? rows[0] : data;
    if (!result?.word || !result?.ref) {
        throw new Error('No se encontraron palabras para esta categoría');
    }
    return result;
}
