#!/usr/bin/env node
/**
 * Agent007 — Instinct Engine
 * Continuous learning system: observations → instincts → skills
 *
 * Architecture:
 *   observations.jsonl     raw session events (NEVER exported)
 *   instincts/personal/    user-specific instincts (YAML)
 *   instincts/inherited/   imported from other sessions (YAML)
 *   instincts/evolved/     cluster-promoted skill candidates (YAML)
 *
 * Confidence levels:
 *   0.3  tentativo   — single observation, not confirmed
 *   0.5  moderado    — seen 2-3 times, plausible
 *   0.7  auto-apply  — seen 4+ times, applied without confirmation
 *   0.9  core        — deeply established, session-invariant
 *
 * Decay: -0.05 per session where pattern is NOT observed.
 * Cluster: 3+ related instincts by domain → evolved/ candidate.
 *
 * Usage (CLI):
 *   node instinct-engine.js status
 *   node instinct-engine.js compile
 *   node instinct-engine.js decay
 *   node instinct-engine.js cluster
 *   node instinct-engine.js export > instincts-export.json
 *   node instinct-engine.js import ./path/to/instincts.json
 */

'use strict';

const fs   = require('fs');
const path = require('path');

// ── Paths ─────────────────────────────────────────────────────────────────────
const ROOT          = path.resolve(__dirname, '../..');
const INSTINCTS_DIR = path.join(ROOT, '.claude', 'instincts');
const OBS_FILE      = path.join(INSTINCTS_DIR, 'observations.jsonl');
const PERSONAL_DIR  = path.join(INSTINCTS_DIR, 'personal');
const INHERITED_DIR = path.join(INSTINCTS_DIR, 'inherited');
const EVOLVED_DIR   = path.join(INSTINCTS_DIR, 'evolved');

// ── Constants ─────────────────────────────────────────────────────────────────
const DECAY_RATE          = 0.05;
const CLUSTER_THRESHOLD   = 3;
const AUTO_APPLY_MIN      = 0.7;
const VALID_DOMAINS       = ['code-style', 'testing', 'git', 'debugging', 'architecture'];

const CONFIDENCE_LEVELS = {
  tentativo:  0.3,
  moderado:   0.5,
  'auto-apply': 0.7,
  core:       0.9,
};

// ── YAML helpers (minimal, no deps) ──────────────────────────────────────────

/**
 * Serialize an instinct object to YAML string.
 * @param {object} instinct
 * @returns {string}
 */
function toYaml(instinct) {
  const esc = s => (typeof s === 'string' && /[:#\[\]{},'"&*?|>!%@`]/.test(s))
    ? `"${s.replace(/"/g, '\\"')}"` : String(s);

  const lines = [
    `id: ${esc(instinct.id)}`,
    `trigger: ${esc(instinct.trigger)}`,
    `action: ${esc(instinct.action)}`,
    `confidence: ${Number(instinct.confidence).toFixed(2)}`,
    `domain: ${instinct.domain}`,
  ];

  if (instinct.evidence && instinct.evidence.length > 0) {
    lines.push('evidence:');
    for (const e of instinct.evidence.slice(-10)) {  // keep last 10 only
      lines.push(`  - session: "${e.session}"`);
      lines.push(`    observation: ${esc(e.observation)}`);
    }
  }

  return lines.join('\n') + '\n';
}

/**
 * Parse a minimal YAML instinct file (our own format only).
 * @param {string} content
 * @returns {object|null}
 */
function parseYaml(content) {
  const obj = {};
  const lines = content.split('\n');
  let inEvidence = false;
  let currentEvidence = null;
  obj.evidence = [];

  for (const raw of lines) {
    const line = raw.trimEnd();

    if (line.startsWith('evidence:')) {
      inEvidence = true;
      continue;
    }

    if (inEvidence) {
      if (line.match(/^  - session:/)) {
        if (currentEvidence) obj.evidence.push(currentEvidence);
        currentEvidence = { session: line.replace(/^  - session:\s*"?/, '').replace(/"$/, '') };
      } else if (line.match(/^    observation:/)) {
        if (currentEvidence) {
          currentEvidence.observation = line.replace(/^    observation:\s*/, '').replace(/^"(.+)"$/, '$1');
        }
      } else if (!line.startsWith('  ')) {
        if (currentEvidence) { obj.evidence.push(currentEvidence); currentEvidence = null; }
        inEvidence = false;
      }
      continue;
    }

    const colonIdx = line.indexOf(':');
    if (colonIdx === -1) continue;
    const key = line.slice(0, colonIdx).trim();
    const val = line.slice(colonIdx + 1).trim().replace(/^"(.+)"$/, '$1');

    if (key === 'confidence') obj[key] = parseFloat(val) || 0;
    else if (key) obj[key] = val;
  }

  if (currentEvidence) obj.evidence.push(currentEvidence);

  return obj.id ? obj : null;
}

// ── File I/O ──────────────────────────────────────────────────────────────────

function ensureDirs() {
  for (const d of [INSTINCTS_DIR, PERSONAL_DIR, INHERITED_DIR, EVOLVED_DIR]) {
    if (!fs.existsSync(d)) fs.mkdirSync(d, { recursive: true });
  }
}

/**
 * Read all instinct YAML files from a directory.
 * @param {string} dir
 * @returns {object[]}
 */
function readInstinctDir(dir) {
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir)
    .filter(f => f.endsWith('.yaml') || f.endsWith('.yml'))
    .map(f => {
      try {
        const content = fs.readFileSync(path.join(dir, f), 'utf8');
        const inst = parseYaml(content);
        if (inst) inst._file = path.join(dir, f);
        return inst;
      } catch { return null; }
    })
    .filter(Boolean);
}

/**
 * Write a single instinct to its YAML file in personal/.
 * @param {object} instinct
 */
function writeInstinct(instinct, dir = PERSONAL_DIR) {
  ensureDirs();
  const filename = instinct.id.replace(/[^a-z0-9-]/gi, '-').toLowerCase() + '.yaml';
  fs.writeFileSync(path.join(dir, filename), toYaml(instinct));
}

// ── Core API ──────────────────────────────────────────────────────────────────

/**
 * Append a raw observation to observations.jsonl.
 * @param {{ type, domain, signal, sessionId?, timestamp? }} observation
 */
function addObservation(observation) {
  ensureDirs();
  const entry = {
    timestamp: observation.timestamp || new Date().toISOString(),
    sessionId: observation.sessionId || 'unknown',
    type:      observation.type,
    domain:    VALID_DOMAINS.includes(observation.domain) ? observation.domain : 'code-style',
    signal:    observation.signal || '',
  };
  fs.appendFileSync(OBS_FILE, JSON.stringify(entry) + '\n');
}

/**
 * Read all observations from observations.jsonl.
 * @returns {object[]}
 */
function readObservations() {
  if (!fs.existsSync(OBS_FILE)) return [];
  return fs.readFileSync(OBS_FILE, 'utf8')
    .split('\n')
    .filter(Boolean)
    .map(line => { try { return JSON.parse(line); } catch { return null; } })
    .filter(Boolean);
}

/**
 * Compile observations into instinct YAML files.
 * Groups observations by (type, domain, signal-similarity) and creates/updates instincts.
 * @returns {object[]} updated instincts
 */
function compileInstincts() {
  ensureDirs();
  const observations = readObservations();
  if (observations.length === 0) return [];

  // Group observations by (type + domain)
  const groups = new Map();
  for (const obs of observations) {
    const key = `${obs.type}::${obs.domain}`;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(obs);
  }

  const existing = readInstinctDir(PERSONAL_DIR);
  const existingById = new Map(existing.map(i => [i.id, i]));
  const updated = [];

  for (const [key, group] of groups) {
    const [type, domain] = key.split('::');
    const count = group.length;

    // Derive confidence from observation count
    let confidence;
    if (count >= 8)      confidence = CONFIDENCE_LEVELS.core;
    else if (count >= 4) confidence = CONFIDENCE_LEVELS['auto-apply'];
    else if (count >= 2) confidence = CONFIDENCE_LEVELS.moderado;
    else                 confidence = CONFIDENCE_LEVELS.tentativo;

    // Generate a stable ID
    const id = `${type.replace(/_/g, '-')}-${domain}`;

    // Build evidence from most recent observations
    const evidence = group.slice(-5).map(o => ({
      session:     o.timestamp,
      observation: o.signal,
    }));

    // Derive trigger + action from type
    const { trigger, action } = deriveIntent(type, domain, group);

    const existing_inst = existingById.get(id);
    const instinct = {
      id,
      trigger,
      action,
      // Confidence is max of derived and existing (never decrease via compile)
      confidence: existing_inst
        ? Math.max(existing_inst.confidence, confidence)
        : confidence,
      domain,
      evidence: existing_inst
        ? mergeEvidence(existing_inst.evidence || [], evidence)
        : evidence,
    };

    writeInstinct(instinct);
    updated.push(instinct);
  }

  return updated;
}

/**
 * Derive human-readable trigger + action from pattern type.
 * @param {string} type
 * @param {string} domain
 * @param {object[]} group
 * @returns {{ trigger: string, action: string }}
 */
function deriveIntent(type, domain, group) {
  const sample = group[group.length - 1]?.signal || '';

  const map = {
    user_corrections:    { trigger: `when generating ${domain} output`, action: `Apply correction: ${sample.slice(0, 80)}` },
    error_resolutions:   { trigger: `when encountering recurring ${domain} errors`, action: `Apply fix pattern: ${sample.slice(0, 80)}` },
    repeated_workflows:  { trigger: `when starting ${domain} tasks`, action: `Use workflow: ${sample.slice(0, 80)}` },
    tool_preferences:    { trigger: `when choosing tools for ${domain}`, action: `Prefer: ${sample.slice(0, 80)}` },
    rejected_suggestions:{ trigger: `when suggesting ${domain} approaches`, action: `Avoid pattern: ${sample.slice(0, 80)}` },
  };

  return map[type] || { trigger: `when working on ${domain}`, action: sample.slice(0, 100) };
}

function mergeEvidence(existing, incoming) {
  const all = [...(existing || []), ...(incoming || [])];
  // Deduplicate by session timestamp, keep last 10
  const seen = new Set();
  return all.filter(e => {
    if (seen.has(e.session)) return false;
    seen.add(e.session);
    return true;
  }).slice(-10);
}

/**
 * Get all compiled instincts, optionally filtered.
 * @param {{ domain?: string, minConfidence?: number }} filter
 * @returns {object[]}
 */
function getInstincts(filter = {}) {
  ensureDirs();
  const dirs = [PERSONAL_DIR, INHERITED_DIR, EVOLVED_DIR];
  let all = dirs.flatMap(d => readInstinctDir(d));

  if (filter.domain) {
    all = all.filter(i => i.domain === filter.domain);
  }
  if (filter.minConfidence != null) {
    all = all.filter(i => i.confidence >= filter.minConfidence);
  }

  return all.sort((a, b) => b.confidence - a.confidence);
}

/**
 * Decay all personal instinct confidence by DECAY_RATE unless seen this session.
 * @param {string[]} seenIds - IDs of instincts reinforced in the current session
 * @returns {object[]} decayed instincts (those that changed)
 */
function decayAll(seenIds = []) {
  const seenSet = new Set(seenIds);
  const instincts = readInstinctDir(PERSONAL_DIR);
  const decayed = [];

  for (const inst of instincts) {
    if (seenSet.has(inst.id)) continue;
    const prev = inst.confidence;
    inst.confidence = Math.max(0, +(inst.confidence - DECAY_RATE).toFixed(2));
    if (inst.confidence !== prev) {
      writeInstinct(inst);
      decayed.push(inst);
    }
  }

  return decayed;
}

/**
 * Group instincts by domain. When a domain has >= CLUSTER_THRESHOLD instincts
 * with confidence >= 0.5, promote the highest-confidence one to evolved/.
 * @returns {{ domain: string, instincts: object[], promoted: boolean }[]}
 */
function cluster() {
  const instincts = readInstinctDir(PERSONAL_DIR);
  const byDomain = new Map();

  for (const inst of instincts) {
    if (!byDomain.has(inst.domain)) byDomain.set(inst.domain, []);
    byDomain.get(inst.domain).push(inst);
  }

  const clusters = [];

  for (const [domain, group] of byDomain) {
    const eligible = group.filter(i => i.confidence >= CONFIDENCE_LEVELS.moderado);
    const promoted = eligible.length >= CLUSTER_THRESHOLD;

    if (promoted) {
      // Promote the highest-confidence instinct as a skill candidate
      const best = eligible.sort((a, b) => b.confidence - a.confidence)[0];
      const evolved = {
        ...best,
        id: `evolved-${best.id}`,
        action: `[SKILL CANDIDATE] ${best.action}`,
        confidence: Math.min(best.confidence + 0.05, 0.95), // small boost
      };
      writeInstinct(evolved, EVOLVED_DIR);
    }

    clusters.push({ domain, count: group.length, eligible: eligible.length, promoted });
  }

  return clusters;
}

/**
 * Export compiled instincts as clean JSON (no raw observations).
 * @returns {object[]}
 */
function exportInstincts() {
  return getInstincts().map(({ _file, ...inst }) => inst); // strip internal _file field
}

/**
 * Import instincts from a JSON file into inherited/.
 * @param {string} filePath
 * @returns {{ imported: number, skipped: number }}
 */
function importInstincts(filePath) {
  ensureDirs();
  const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  const instincts = Array.isArray(data) ? data : [data];
  let imported = 0, skipped = 0;

  for (const inst of instincts) {
    if (!inst.id || !inst.domain) { skipped++; continue; }
    // Cap imported confidence at 0.5 — inherited instincts need local reinforcement
    inst.confidence = Math.min(inst.confidence || 0.3, CONFIDENCE_LEVELS.moderado);
    inst.id = `inherited-${inst.id}`;
    writeInstinct(inst, INHERITED_DIR);
    imported++;
  }

  return { imported, skipped };
}

// ── CLI ───────────────────────────────────────────────────────────────────────
if (require.main === module) {
  const [,, cmd, ...args] = process.argv;

  switch (cmd) {
    case 'status': {
      const all = getInstincts();
      console.log(`\nInstincts: ${all.length} total\n`);
      for (const inst of all) {
        const bar = '█'.repeat(Math.round(inst.confidence * 10)).padEnd(10, '░');
        const autoApply = inst.confidence >= AUTO_APPLY_MIN ? '⚡' : '  ';
        console.log(`  ${autoApply} [${bar}] ${(inst.confidence * 100).toFixed(0).padStart(3)}%  ${inst.id}`);
        console.log(`       domain: ${inst.domain} | trigger: ${inst.trigger.slice(0, 60)}`);
      }
      console.log();
      break;
    }
    case 'compile': {
      const updated = compileInstincts();
      console.log(`Compiled ${updated.length} instincts from observations.`);
      break;
    }
    case 'decay': {
      const seenIds = args[0] ? args[0].split(',') : [];
      const decayed = decayAll(seenIds);
      console.log(`Decayed ${decayed.length} instincts.`);
      break;
    }
    case 'cluster': {
      const clusters = cluster();
      for (const c of clusters) {
        const promoted = c.promoted ? '→ EVOLVED (skill candidate)' : '';
        console.log(`  ${c.domain}: ${c.count} instincts, ${c.eligible} eligible ${promoted}`);
      }
      break;
    }
    case 'export': {
      const data = exportInstincts();
      process.stdout.write(JSON.stringify(data, null, 2) + '\n');
      break;
    }
    case 'import': {
      if (!args[0]) { console.error('Usage: instinct-engine.js import <file.json>'); process.exit(1); }
      const result = importInstincts(path.resolve(args[0]));
      console.log(`Imported: ${result.imported}, Skipped: ${result.skipped}`);
      break;
    }
    case 'add': {
      // Quick add from CLI: instinct-engine.js add <type> <domain> <signal>
      if (args.length < 3) { console.error('Usage: instinct-engine.js add <type> <domain> <signal>'); process.exit(1); }
      addObservation({ type: args[0], domain: args[1], signal: args.slice(2).join(' ') });
      console.log('Observation added.');
      break;
    }
    default: {
      console.log([
        'Usage: instinct-engine.js <command>',
        '  status                        list all instincts',
        '  compile                       process observations → instincts',
        '  decay [id1,id2,...]           apply decay to unseen instincts',
        '  cluster                       group by domain, promote skill candidates',
        '  export                        print clean JSON (no raw observations)',
        '  import <file.json>            merge inherited instincts',
        '  add <type> <domain> <signal>  record a single observation',
      ].join('\n'));
    }
  }
}

// ── Exports ───────────────────────────────────────────────────────────────────
module.exports = {
  addObservation,
  compileInstincts,
  getInstincts,
  decayAll,
  cluster,
  exportInstincts,
  importInstincts,
  readObservations,
  CONFIDENCE_LEVELS,
  VALID_DOMAINS,
  AUTO_APPLY_MIN,
  DECAY_RATE,
};
