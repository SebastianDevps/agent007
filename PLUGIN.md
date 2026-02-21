# Agent007 Plugin Guide

This guide explains how to use Agent007 as a Claude Code plugin for global availability across all your projects.

---

## 📦 What is a Claude Code Plugin?

Claude Code plugins are **reusable packages** that provide:
- ✅ Skills available across ALL projects
- ✅ Expert agents that work globally
- ✅ Versioned releases with updates
- ✅ Team distribution via GitHub
- ✅ Zero file duplication

---

## 🚀 Installation Methods

### Method 1: Install from GitHub (Production Use)

**Step 1: Push Agent007 to GitHub**

```bash
cd /Users/sebasing/Projects/Agent007
git init
git add .
git commit -m "Initial Agent007 plugin v2.0.0"
git remote add origin https://github.com/yourusername/agent007.git
git push -u origin main
```

**Step 2: Install the Plugin**

```bash
# Navigate to ANY project
cd ~/Projects/YourApp

# Install globally (available in all projects)
claude /plugin install agent007@yourusername/agent007 --scope user

# Or install for current project only
claude /plugin install agent007@yourusername/agent007 --scope project
```

**Step 3: Verify Installation**

```bash
claude /help
# You should see /agent007:* skills listed
```

---

### Method 2: Install Locally (Development & Testing)

During development, test the plugin without publishing:

```bash
# Navigate to your test project
cd ~/Projects/TestProject

# Load plugin from local directory
claude --plugin-dir /Users/sebasing/Projects/Agent007

# Or add to your project's .claude/settings.json:
{
  "plugins": [
    {
      "path": "/Users/sebasing/Projects/Agent007",
      "enabled": true
    }
  ]
}
```

---

### Method 3: Create a Marketplace (Team Distribution)

For sharing with your team:

**Step 1: Create marketplace.json**

```bash
# In a separate GitHub repo
mkdir agent007-marketplace
cd agent007-marketplace
```

Create `marketplace.json`:

```json
{
  "name": "Agent007 Marketplace",
  "description": "Internal marketplace for Agent007 team tools",
  "plugins": [
    {
      "name": "agent007",
      "repository": "yourusername/agent007",
      "description": "Intelligent Development Orchestration System",
      "author": "Sebastian G",
      "version": "2.0.0",
      "homepage": "https://github.com/yourusername/agent007"
    }
  ]
}
```

**Step 2: Share with Team**

```bash
# Team members add your marketplace
claude /plugin marketplace add yourusername/agent007-marketplace

# Then install
claude /plugin marketplace install agent007
```

---

## 📖 Using Agent007 Skills

Once installed, all skills are namespaced with `agent007:`:

### Core Consultation

```bash
# Simple consultation (lazy loading + summaries)
/agent007:consult "How to implement JWT authentication in NestJS?"

# Deep consultation (full skills loaded)
/agent007:consult "Complete API architecture review" --deep

# Quick mode (minimal, fast)
/agent007:consult "Quick circuit breaker pattern" --quick
```

### Architecture & Design

```bash
# Review architecture patterns
/agent007:architecture-patterns

# API design principles audit
/agent007:api-design-principles

# Resilience patterns implementation
/agent007:resilience-patterns
```

### Code Review & Quality

```bash
# NestJS code review
/agent007:nestjs-code-reviewer

# Frontend design review
/agent007:frontend-design

# React best practices
/agent007:react-best-practices
```

### Workflows

```bash
# Brainstorm requirements
/agent007:brainstorm

# Create implementation plan
/agent007:plan

# TDD workflow
/agent007:tdd

# Systematic debugging
/agent007:systematic-debugging
```

---

## ⚙️ Configuration

### Global Configuration

Edit `~/.claude/settings.json`:

```json
{
  "plugins": {
    "agent007": {
      "defaultAgent": "backend-db-expert",
      "effortLevel": "medium",
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
      "defaultAgent": "frontend-ux-expert",
      "consultation": {
        "defaultMode": "deep"
      }
    }
  }
}
```

---

## 🔄 Updating Agent007

### Manual Update

```bash
# Pull latest changes
cd /Users/sebasing/Projects/Agent007
git pull origin main

# If installed from GitHub, reinstall
claude /plugin install agent007@yourusername/agent007 --force
```

### Automatic Updates (Coming Soon)

Future versions will support automatic updates:

```bash
claude /plugin update agent007
```

---

## 🗑️ Uninstalling

```bash
# Remove global installation
claude /plugin uninstall agent007 --scope user

# Remove project installation
claude /plugin uninstall agent007 --scope project
```

---

## 🐛 Troubleshooting

### Skills Not Showing

```bash
# Check if plugin is loaded
claude /plugin list

# Verify plugin manifest
cat /Users/sebasing/Projects/Agent007/.claude-plugin/plugin.json

# Check Claude Code version (requires >=1.0.0)
claude --version
```

### Namespace Issues

If skills aren't working:

1. ✅ Use full namespace: `/agent007:consult`
2. ❌ Don't use: `/consult` (only works for non-plugin skills)

### Cache Issues

```bash
# Clear plugin cache
rm -rf ~/.claude/plugins/cache/agent007-*

# Reinstall
claude /plugin install agent007@yourusername/agent007 --force
```

---

## 📊 Plugin vs Standalone Comparison

| Feature | Plugin | Standalone (.claude/) |
|---------|--------|----------------------|
| **Reusable across projects** | ✅ Yes | ❌ No (duplicates files) |
| **Versioning** | ✅ Yes | ❌ Manual |
| **Team distribution** | ✅ GitHub/Marketplace | ⚠️ Copy files |
| **Updates** | ✅ `git pull` + reinstall | ❌ Manual copy |
| **Skill namespace** | `/agent007:skill` | `/skill` |
| **Installation time** | 30 seconds | 5 minutes (per project) |
| **Disk space** (10 projects) | 5 MB (once) | 50 MB (duplicated) |

**Recommendation**: Use plugin for multi-project use. Use standalone only for custom per-project agents.

---

## 🎯 Best Practices

### 1. Use Global Installation

```bash
# Install once, use everywhere
claude /plugin install agent007@yourusername/agent007 --scope user
```

### 2. Project-Specific Customization

Don't duplicate Agent007 files. Instead, create project-specific overrides:

```
YourProject/
├── .claude/
│   ├── CLAUDE.md              # Project instructions
│   ├── memory/                # Project memory
│   └── settings.json          # Override plugin defaults
└── src/
```

### 3. Version Pinning (Production)

For stable production environments:

```json
{
  "plugins": {
    "agent007": {
      "version": "2.0.0",
      "autoUpdate": false
    }
  }
}
```

### 4. Development vs Production

- **Development**: Use local plugin (`--plugin-dir`)
- **Production**: Use GitHub installation (versioned)

---

## 📚 Additional Resources

- **Main README**: Full feature documentation
- **IMPLEMENTATION_PLAN.md**: Token optimization roadmap
- **FINAL_SUMMARY.md**: Implementation results (83-92% token reduction)
- **Claude Code Docs**: https://code.claude.com/docs/en/plugins

---

## 🤝 Contributing

Agent007 is a team tool. To contribute:

1. Fork the repository
2. Create a feature branch
3. Test locally with `--plugin-dir`
4. Submit PR
5. Team reviews and merges
6. Version bump + release

---

## 📞 Support

- **GitHub Issues**: https://github.com/yourusername/agent007/issues
- **Documentation**: See README.md, IMPLEMENTATION_PLAN.md
- **Team Chat**: #agent007 (your team channel)

---

**Agent007 v2.0.0** - Intelligent Development Orchestration as a Plugin 🎉
