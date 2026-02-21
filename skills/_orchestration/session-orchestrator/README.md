# Session Orchestrator

**Version**: 2.0 (Connected)
**Status**: ✅ Fully Connected

Intelligent orchestration system that automatically detects task context and routes to appropriate workflows.

---

## 🎯 What It Does

The session orchestrator analyzes user input and automatically:
1. **Detects** task type, risk level, and tech stack
2. **Routes** to the appropriate skill or command
3. **Invokes** workflows based on `when` conditions from SKILL.md files

---

## 🏗️ Architecture

```
User Input
    ↓
index.js (Entry Point)
    ↓
detector.js (Context Detection)
    ↓
router.js (Workflow Routing)
    ↓
Skill/Command Invocation
```

### Components

#### **index.js** - Entry Point
Main orchestration function that coordinates detector → router → execution.

```javascript
const { orchestrate } = require('./_orchestration/session-orchestrator');

const result = await orchestrate(userInput);
// { action, skill, command, requiresConfirmation, reason }
```

#### **detector.js** - Context Detection
Analyzes user input to determine:
- **taskType**: consult, feature, bug, refactor
- **riskLevel**: low, medium, high, critical
- **stack**: nestjs, typeorm, react, etc.
- **scope**: small, medium, large
- **confidence**: 0.0 - 1.0

Uses config from: `config/orchestrator.config.json`

#### **router.js** - Workflow Routing
Routes based on detected context using:
- **Static rules**: Hardcoded routing table (fallback)
- **Dynamic rules**: `when` conditions from SKILL.md files (precedence)

Returns routing decision with skill/command to invoke.

---

## 🔧 Configuration

### orchestrator.config.json

```json
{
  "contextDetection": {
    "enabled": true,
    "rules": {
      "feature": {
        "keywords": ["implement", "add", "create"],
        "patterns": ["implement .+", "add .+ to .+"]
      },
      "bug": {
        "keywords": ["bug", "error", "fix", "broken"]
      }
    }
  },
  "riskDetection": {
    "enabled": true,
    "rules": {
      "critical": {
        "pathContains": ["auth", "payment", "migration"]
      }
    }
  }
}
```

### settings.json

```json
{
  "orchestration": {
    "enabled": true,
    "auto_detect": true,
    "confirmations": {
      "critical_risk": true,
      "high_risk": false
    }
  }
}
```

---

## 🎨 When Conditions (Dynamic Routing)

Skills can define auto-activation rules in their SKILL.md frontmatter:

```yaml
---
name: brainstorming
when:
  - task_type: feature
    risk_level: [medium, high, critical]
  - task_type: refactor
    risk_level: [high, critical]
  - user_mentions: ["unclear requirements", "explore options"]
---
```

The router automatically reads these and creates dynamic routing rules.

### Supported Condition Fields

- `task_type`: string or array - Match detected task type
- `risk_level`: string or array - Match detected risk level
- `stack`: string or array - Match detected tech stack
- `user_mentions`: array - Match phrases in user input
- `previous_skill`: string - Match if previous skill completed (requires session state)

### Priority

Dynamic rules (from `when`) take **precedence** over static rules (hardcoded).

---

## 📊 Usage Examples

### Basic Orchestration

```javascript
const { orchestrate } = require('./session-orchestrator');

const result = await orchestrate("Add JWT authentication");

console.log(result);
// {
//   detection: {
//     taskType: 'feature',
//     riskLevel: 'critical',
//     stack: ['jwt'],
//     confidence: 0.9
//   },
//   skill: 'brainstorming',
//   requiresConfirmation: true,
//   reason: 'Auto-activation condition matched for brainstorming'
// }
```

### Get Recommendation Only

```javascript
const { recommend } = require('./session-orchestrator');

const rec = recommend("Fix N+1 query in users service");

console.log(rec);
// {
//   taskType: 'bug',
//   riskLevel: 'high',
//   recommendedSkill: 'systematic-debugging',
//   reason: 'Bug requires systematic debugging approach'
// }
```

### Check Specific Skill

```javascript
const { shouldInvokeSkill } = require('./session-orchestrator');

const shouldInvoke = shouldInvokeSkill("Fix bug in payment", "systematic-debugging");
// true
```

---

## 🔄 Routing Flow

### 1. Consult Requests
```
User: "Should I use Redis or in-memory cache?"
→ Detected: consult
→ Routed to: /consult command
→ Confirmation: No
```

### 2. Medium+ Risk Features
```
User: "Add email verification to registration"
→ Detected: feature, risk=high
→ Routed to: brainstorming skill
→ Confirmation: Yes
→ After brainstorming: writing-plans skill
```

### 3. Bug Fixes
```
User: "Users endpoint returns 500 error"
→ Detected: bug, risk=high
→ Routed to: systematic-debugging skill
→ Confirmation: No (auto-invoked)
```

### 4. Low Risk Changes
```
User: "Add createdAt field to User entity"
→ Detected: feature, risk=low
→ Routed to: proceed (direct implementation)
→ Confirmation: No
```

---

## 🧪 Testing

### Run Tests

```bash
npm test .claude/skills/_orchestration/session-orchestrator/__tests__
```

### Test Files

```
__tests__/
├── detector.test.js     # Context detection tests
├── router.test.js       # Routing logic tests
└── integration.test.js  # End-to-end orchestration tests
```

---

## 🐛 Troubleshooting

### Orchestration Not Working

**Check settings.json:**
```json
{
  "orchestration": {
    "enabled": true,  // Must be true
    "auto_detect": true
  }
}
```

### Skills Not Auto-Activating

**Check SKILL.md frontmatter:**
- `invokable: true` must be set
- `when` conditions must be valid YAML
- File must be named `SKILL.md` (case-sensitive)

**Debug routing:**
```javascript
const { recommend } = require('./session-orchestrator');
console.log(recommend("your input here"));
```

### Config Not Loading

**Check paths:**
- `config/orchestrator.config.json` exists
- `config/risk-profiles.json` exists
- No syntax errors in JSON files

**Test manually:**
```javascript
const fs = require('fs');
const path = require('path');

const configPath = path.join(__dirname, 'config/orchestrator.config.json');
const config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
console.log(config);
```

---

## 📈 Metrics

After implementing, you should see:
- ✅ Reduced manual skill invocation
- ✅ Consistent workflow enforcement
- ✅ Better risk assessment
- ✅ Auto-routing based on context

---

## 🚀 Next Steps

### v2.1 Improvements

1. **Session State Tracking**
   - Track previous skills executed
   - Enable `previous_skill` conditions
   - Chain workflows automatically

2. **Context Scanning**
   - Scan project files for better stack detection
   - Analyze codebase complexity
   - Improve risk assessment

3. **Learning System**
   - Track successful routes
   - Learn from user overrides
   - Improve confidence over time

---

## 🔗 Related Files

- `config/orchestrator.config.json` - Detection rules
- `config/risk-profiles.json` - Risk assessment rules
- `config/adaptive-gates.yml` - Quality gate configs
- `../../../settings.json` - Global orchestration settings

---

**Status**: ✅ Fully Connected and Operational
**Version**: 2.0
**Last Updated**: 2026-02-08
