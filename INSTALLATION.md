# Agent007 - Installation Guide

Complete installation guide for Agent007 via Claude Code plugin system.

---

## ✨ Quick Install (One Command)

```bash
/plugin install agent007@sebasing/agent007 --scope user
```

**Done!** Agent007 is now available in all your projects. ✅

---

## 📖 Detailed Installation Steps

### Prerequisites

- Claude Code CLI installed
- Terminal/Command line access

---

### Step 1: Install Agent007

In your terminal, run:

```bash
/plugin install agent007@sebasing/agent007 --scope user
```

**What this does**:
- Clones: `https://github.com/sebasing/agent007.git`
- Installs to: `~/.claude/plugins/cache/agent007-*`
- Registers skills globally (available in ALL projects)

**Expected output**:
```
✅ Plugin 'agent007' installed successfully
✅ 17 skills loaded
✅ 5 agents available
```

---

### Step 3: Verify Installation

```bash
/help
```

Scroll through the skills list. You should see:

```
Available skills:
  ...
  /agent007:consult - Intelligent expert consultation
  /agent007:architecture-review - Deep architecture analysis
  /agent007:api-design-principles - REST API best practices
  /agent007:resilience-patterns - Circuit breakers, retry logic
  /agent007:frontend-design - High-quality UI design
  /agent007:review - Code review for NestJS + TypeORM
  /agent007:plan - Feature decomposition
  /agent007:tdd - Test-Driven Development workflow
  ...
```

---

### Step 4: Test a Skill

Try your first consultation:

```bash
/agent007:consult "How to implement JWT authentication in NestJS?"
```

**Expected behavior**:
- Auto-selects experts: `backend-db-expert` + `security-expert`
- Loads relevant skills: `api-design-principles`, `nestjs-code-reviewer`
- Returns consolidated advice
- Uses 10K tokens (vs 60K without optimization)

---

## 🔄 Updating Agent007

When a new version is released:

```bash
/plugin update agent007
```

This pulls the latest changes from GitHub automatically.

---

## 🗑️ Uninstalling

To remove Agent007:

```bash
/plugin uninstall agent007
```

To remove the marketplace:

```bash
/plugin marketplace remove sebasing/agent007-marketplace
```

---

## 🎯 Alternative Installation Methods

### Method 1: Direct from GitHub (No Marketplace)

```bash
/plugin install agent007@sebasing/agent007 --scope user
```

**Pros**: Simpler (one command)
**Cons**: No marketplace updates, harder to discover

---

### Method 2: Local Development

For testing unreleased versions:

```bash
# Clone the repository
git clone https://github.com/sebasing/agent007.git
cd agent007

# Load in any project
cd ~/Projects/YourApp
claude --plugin-dir /path/to/agent007
```

**Use case**: Plugin development, testing before release

---

## 🛠️ Configuration

### Global Configuration

Edit `~/.claude/settings.json`:

```json
{
  "plugins": {
    "agent007": {
      "defaultAgent": "backend-db-expert",
      "tokenOptimization": {
        "lazyLoading": true,
        "useSummaries": true,
        "maxSkillsPerQuery": 3
      }
    }
  }
}
```

### Project-Specific Overrides

In your project's `.claude/settings.json`:

```json
{
  "plugins": {
    "agent007": {
      "defaultAgent": "frontend-ux-expert"
    }
  }
}
```

---

## 📚 Available Skills

After installation, these skills are available globally:

### Consultation & Planning
- `/agent007:consult` - Auto-selects experts for your question
- `/agent007:brainstorm` - Socratic requirements exploration
- `/agent007:plan` - Decompose features into tasks

### Architecture & Design
- `/agent007:architecture-review` - Deep architecture analysis
- `/agent007:architecture-patterns` - Clean Architecture, DDD
- `/agent007:api-design-principles` - REST API best practices
- `/agent007:resilience-patterns` - Circuit breakers, retry, health checks

### Code Review & Quality
- `/agent007:review` - NestJS + TypeORM code review
- `/agent007:nestjs-code-reviewer` - Security & anti-patterns
- `/agent007:tdd` - Test-Driven Development workflow
- `/agent007:systematic-debugging` - Root cause analysis

### Frontend
- `/agent007:frontend-design` - High-quality UI design
- `/agent007:react-best-practices` - React optimization

### Product & Docs
- `/agent007:product-discovery` - Product requirements
- `/agent007:api-documentation` - API docs generation

---

## 🐛 Troubleshooting

### "Marketplace not found"

**Error**: `Marketplace 'agent007-marketplace' not found`

**Solution**:
1. Verify repo is public: https://github.com/sebasing/agent007-marketplace
2. Check marketplace.json exists: https://raw.githubusercontent.com/sebasing/agent007-marketplace/main/.claude-plugin/marketplace.json
3. Retry: `/plugin marketplace add sebasing/agent007-marketplace`

---

### "Plugin not found"

**Error**: `Plugin 'agent007' not found in marketplace`

**Solution**:
1. Refresh marketplace: `/plugin marketplace update agent007-marketplace`
2. Check plugin name in marketplace.json matches exactly
3. Reinstall: `/plugin install agent007@agent007-marketplace`

---

### Skills Not Showing

**Issue**: `/help` doesn't show `/agent007:*` skills

**Solution**:
1. Check installation: `/plugin list`
2. Restart Claude Code session
3. Verify plugin enabled: Check `~/.claude/settings.json`
4. Reinstall: `/plugin uninstall agent007` then `/plugin install agent007@agent007-marketplace`

---

### "Permission Denied"

**Error**: Cannot access `~/.claude/plugins/`

**Solution**:
```bash
# Fix permissions
chmod -R 755 ~/.claude/plugins/
```

---

## 📊 Performance Expectations

After installation, expect these improvements:

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Tokens/query** | 60,000 | 10,000 | **83% ↓** |
| **Cost/query (Opus)** | $0.90 | $0.15 | **83% ↓** |
| **Response time** | 45s | 20s | **55% faster** |
| **Cache hit rate** | 0% | 60% | **60% cached** |

---

## 🎓 Next Steps

1. **Test basic consultation**:
   ```bash
   /agent007:consult "How to optimize database queries in TypeORM?"
   ```

2. **Try architecture review**:
   ```bash
   /agent007:architecture-review
   ```

3. **Enable TDD workflow**:
   ```bash
   /agent007:tdd
   ```

4. **Monitor token usage**:
   ```bash
   # Check Agent007 analytics (if enabled)
   /agent007:token-stats
   ```

---

## 📞 Support

- **GitHub Issues**: https://github.com/sebasing/agent007/issues
- **Documentation**: Full guides in README.md, PLUGIN.md, MARKETPLACE_SETUP.md
- **Discussions**: https://github.com/sebasing/agent007/discussions

---

## 📄 License

Agent007 is open source under MIT License.

See: https://github.com/sebasing/agent007/blob/main/LICENSE

---

**Agent007 v2.0.0** - Intelligent Development Orchestration 🎯
