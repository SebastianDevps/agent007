#!/usr/bin/env node
/**
 * a11y-contrast-check — WCAG 2.2 AA contrast ratio checker.
 *
 * Usage:
 *   node check-contrast.js <file> [<file> ...]
 *
 * Exit codes:
 *   0 — all pairs pass (≥ 4.5:1 normal, ≥ 3:1 large/UI)
 *   1 — at least one pair fails
 *   2 — usage / file-read error
 *
 * Zero dependencies — Node.js stdlib only.
 *
 * Detects:
 *   - Tailwind class pairs:   text-<color>-<shade>  +  bg-<color>-<shade>
 *   - Inline CSS pairs:       color: <c>;  background[-color]: <c>;
 *   - CSS custom properties:  --foreground / --background (root or :root)
 *
 * WCAG formula: https://www.w3.org/TR/WCAG22/#contrast-minimum
 */

'use strict';

const fs = require('fs');
const path = require('path');

const NORMAL_THRESHOLD = 4.5;
const LARGE_THRESHOLD = 3.0;

// ---------- color parsing ----------

function hexToRgb(hex) {
  const h = hex.replace('#', '');
  const full = h.length === 3 ? h.split('').map((c) => c + c).join('') : h;
  if (!/^[0-9a-fA-F]{6}$/.test(full)) return null;
  return {
    r: parseInt(full.slice(0, 2), 16),
    g: parseInt(full.slice(2, 4), 16),
    b: parseInt(full.slice(4, 6), 16),
  };
}

function rgbStringToRgb(str) {
  const m = str.match(/rgba?\(\s*(\d+)[,\s]+(\d+)[,\s]+(\d+)/i);
  if (!m) return null;
  return { r: +m[1], g: +m[2], b: +m[3] };
}

function parseColor(raw) {
  if (!raw) return null;
  const v = raw.trim().toLowerCase();
  if (v.startsWith('#')) return hexToRgb(v);
  if (v.startsWith('rgb')) return rgbStringToRgb(v);
  if (TAILWIND_PALETTE[v]) return hexToRgb(TAILWIND_PALETTE[v]);
  return null;
}

// ---------- WCAG luminance + contrast ----------

function channelLuminance(c) {
  const s = c / 255;
  return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
}

function relativeLuminance({ r, g, b }) {
  return (
    0.2126 * channelLuminance(r) +
    0.7152 * channelLuminance(g) +
    0.0722 * channelLuminance(b)
  );
}

function contrastRatio(fg, bg) {
  const l1 = relativeLuminance(fg);
  const l2 = relativeLuminance(bg);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

// ---------- Tailwind palette (subset, default v3) ----------

const TAILWIND_PALETTE = {
  white: '#ffffff', black: '#000000',
  'slate-50': '#f8fafc', 'slate-100': '#f1f5f9', 'slate-200': '#e2e8f0', 'slate-300': '#cbd5e1',
  'slate-400': '#94a3b8', 'slate-500': '#64748b', 'slate-600': '#475569', 'slate-700': '#334155',
  'slate-800': '#1e293b', 'slate-900': '#0f172a', 'slate-950': '#020617',
  'gray-50': '#f9fafb', 'gray-100': '#f3f4f6', 'gray-200': '#e5e7eb', 'gray-300': '#d1d5db',
  'gray-400': '#9ca3af', 'gray-500': '#6b7280', 'gray-600': '#4b5563', 'gray-700': '#374151',
  'gray-800': '#1f2937', 'gray-900': '#111827', 'gray-950': '#030712',
  'zinc-50': '#fafafa', 'zinc-100': '#f4f4f5', 'zinc-400': '#a1a1aa', 'zinc-500': '#71717a',
  'zinc-700': '#3f3f46', 'zinc-800': '#27272a', 'zinc-900': '#18181b',
  'red-50': '#fef2f2', 'red-100': '#fee2e2', 'red-300': '#fca5a5', 'red-400': '#f87171',
  'red-500': '#ef4444', 'red-600': '#dc2626', 'red-700': '#b91c1c', 'red-900': '#7f1d1d',
  'orange-400': '#fb923c', 'orange-500': '#f97316', 'orange-600': '#ea580c',
  'amber-300': '#fcd34d', 'amber-400': '#fbbf24', 'amber-500': '#f59e0b',
  'yellow-300': '#fde047', 'yellow-400': '#facc15', 'yellow-500': '#eab308',
  'green-300': '#86efac', 'green-400': '#4ade80', 'green-500': '#22c55e', 'green-600': '#16a34a',
  'green-700': '#15803d', 'green-900': '#14532d',
  'emerald-400': '#34d399', 'emerald-500': '#10b981', 'emerald-600': '#059669',
  'teal-400': '#2dd4bf', 'teal-500': '#14b8a6', 'teal-600': '#0d9488',
  'cyan-400': '#22d3ee', 'cyan-500': '#06b6d4', 'cyan-600': '#0891b2',
  'sky-400': '#38bdf8', 'sky-500': '#0ea5e9', 'sky-600': '#0284c7',
  'blue-300': '#93c5fd', 'blue-400': '#60a5fa', 'blue-500': '#3b82f6',
  'blue-600': '#2563eb', 'blue-700': '#1d4ed8', 'blue-900': '#1e3a8a',
  'indigo-400': '#818cf8', 'indigo-500': '#6366f1', 'indigo-600': '#4f46e5',
  'violet-400': '#a78bfa', 'violet-500': '#8b5cf6', 'violet-600': '#7c3aed',
  'purple-400': '#c084fc', 'purple-500': '#a855f7', 'purple-600': '#9333ea',
  'fuchsia-500': '#d946ef', 'pink-400': '#f472b6', 'pink-500': '#ec4899', 'pink-600': '#db2777',
  'rose-400': '#fb7185', 'rose-500': '#f43f5e', 'rose-600': '#e11d48',
};

// ---------- extractors ----------

function extractTailwindPairs(source) {
  // class="..." or className="..." or className={`...`} or clsx("...")
  const classBlocks = source.match(/(?:class(?:Name)?\s*=\s*[`"']|clsx\(|cn\()([^`"')]+)/g) || [];
  const pairs = [];
  for (const block of classBlocks) {
    const fg = block.match(/\btext-((?:slate|gray|zinc|red|orange|amber|yellow|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-\d{2,3}|white|black)\b/);
    const bg = block.match(/\bbg-((?:slate|gray|zinc|red|orange|amber|yellow|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-\d{2,3}|white|black)\b/);
    if (fg && bg) {
      pairs.push({ source: 'tailwind', fg: fg[1], bg: bg[1], context: block.slice(0, 80) });
    }
  }
  return pairs;
}

function extractCssPairs(source) {
  const pairs = [];
  // Inline / CSS rules with both color and background[-color]
  const ruleRegex = /\{([^}]+)\}/g;
  let m;
  while ((m = ruleRegex.exec(source)) !== null) {
    const body = m[1];
    const fg = body.match(/(?:^|[;\s])color\s*:\s*([^;]+)/);
    const bg = body.match(/(?:^|[;\s])background(?:-color)?\s*:\s*([^;]+)/);
    if (fg && bg) {
      pairs.push({ source: 'css', fg: fg[1].trim(), bg: bg[1].trim(), context: body.trim().slice(0, 80) });
    }
  }
  // CSS custom properties on :root
  const rootMatch = source.match(/:root\s*\{([^}]+)\}/);
  if (rootMatch) {
    const fgVar = rootMatch[1].match(/--foreground\s*:\s*([^;]+)/);
    const bgVar = rootMatch[1].match(/--background\s*:\s*([^;]+)/);
    if (fgVar && bgVar) {
      pairs.push({ source: 'css-vars', fg: fgVar[1].trim(), bg: bgVar[1].trim(), context: ':root vars' });
    }
  }
  return pairs;
}

// ---------- runner ----------

function checkPair(pair) {
  const fg = parseColor(pair.fg);
  const bg = parseColor(pair.bg);
  if (!fg || !bg) {
    return { ...pair, skipped: true, reason: 'unresolved color' };
  }
  const ratio = contrastRatio(fg, bg);
  const passNormal = ratio >= NORMAL_THRESHOLD;
  const passLarge = ratio >= LARGE_THRESHOLD;
  return { ...pair, ratio: Math.round(ratio * 100) / 100, passNormal, passLarge };
}

function processFile(filePath) {
  const source = fs.readFileSync(filePath, 'utf8');
  const ext = path.extname(filePath);
  const pairs = [];
  if (/\.(tsx?|jsx?|html|svelte|vue)$/.test(ext)) {
    pairs.push(...extractTailwindPairs(source));
  }
  if (/\.(css|scss|sass|less|tsx?|jsx?|html|svelte|vue)$/.test(ext)) {
    pairs.push(...extractCssPairs(source));
  }
  return pairs.map(checkPair);
}

function report(results, filePath) {
  if (results.length === 0) {
    console.log(`✓ ${filePath}: no fg/bg pairs detected`);
    return 0;
  }
  let failures = 0;
  for (const r of results) {
    if (r.skipped) {
      console.log(`  - ${filePath} [${r.source}] ${r.fg} / ${r.bg} → SKIP (${r.reason})`);
      continue;
    }
    const status = r.passNormal ? 'PASS' : r.passLarge ? 'WARN (large only)' : 'FAIL';
    if (!r.passNormal) failures++;
    console.log(`  - ${filePath} [${r.source}] ${r.fg} on ${r.bg} → ${r.ratio}:1 ${status}`);
    if (r.context) console.log(`      ↳ ${r.context.replace(/\s+/g, ' ')}`);
  }
  return failures;
}

function main() {
  const files = process.argv.slice(2);
  if (files.length === 0) {
    console.error('Usage: check-contrast.js <file> [<file> ...]');
    process.exit(2);
  }
  let total = 0;
  for (const f of files) {
    try {
      const results = processFile(f);
      total += report(results, f);
    } catch (err) {
      console.error(`! ${f}: ${err.message}`);
      process.exit(2);
    }
  }
  if (total > 0) {
    console.log(`\n✗ ${total} contrast failure(s) — fix to meet WCAG AA (4.5:1 normal, 3:1 large).`);
    process.exit(1);
  }
  console.log('\n✓ All detected pairs meet WCAG AA.');
  process.exit(0);
}

main();
