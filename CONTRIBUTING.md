# Contributing to Agent007

Thank you for your interest in contributing to Agent007! This document provides guidelines for contributing to the project.

---

## 🎯 Contribution Model

Agent007 follows a **reviewed contribution model**:

- ✅ **Issues**: Anyone can create issues for bugs, features, or questions
- ✅ **Discussions**: Open for community questions and ideas
- ⚠️ **Pull Requests**: Require core team review and approval before merge
- ❌ **Direct Commits**: Only core team members can commit directly to `main`

**Why?** This ensures:
- Architecture consistency across the codebase
- Token optimization strategies remain effective
- Quality standards are maintained
- Breaking changes are carefully evaluated

---

## 🐛 Reporting Bugs

### Before Submitting a Bug Report

1. **Update to latest**: Run `/plugin update agent007`
2. **Search existing issues**: Check if it's already reported
3. **Reproduce**: Ensure the bug is reproducible

### How to Submit

Use the [Bug Report template](https://github.com/SebastianDevps/agent007/issues/new?template=bug_report.yml)

**Include**:
- Clear description
- Steps to reproduce
- Expected vs actual behavior
- Agent007 version
- Relevant logs/screenshots

---

## 💡 Suggesting Features

### Before Suggesting a Feature

1. **Search existing issues**: Check if someone else suggested it
2. **Read ARCHITECTURE.md**: Understand how Agent007 works
3. **Consider scope**: Does it fit Agent007's purpose?

### How to Suggest

Use the [Feature Request template](https://github.com/SebastianDevps/agent007/issues/new?template=feature_request.yml)

**Include**:
- Problem statement (what pain point does this solve?)
- Proposed solution
- Use case examples
- Alternatives you've considered

**Note**: All feature requests are reviewed by the core team. Not all features will be accepted, even if well-intentioned.

---

## 🔧 Contributing Code

### Getting Started

1. **Fork the repository**
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/agent007.git
   cd agent007
   ```
3. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Development Setup

**Test locally**:
```bash
# In any project directory
claude --plugin-dir /path/to/agent007

# Test your changes
/agent007:consult "test query"
```

### Making Changes

**Guidelines**:

1. **One Feature Per PR**: Focus on a single bug/feature per pull request
2. **Follow Existing Patterns**: Match the architecture and code style
3. **Update Documentation**: Update README.md, ARCHITECTURE.md as needed
4. **Test Thoroughly**: Verify your changes don't break existing functionality
5. **Consider Token Impact**: If your change affects token consumption, document it

**Code Style**:
- Use clear, descriptive variable names
- Add comments for complex logic
- Follow existing markdown formatting for skills
- Keep skills under 700 lines (create SUMMARY.md for >100 lines)

### Submitting a Pull Request

1. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create PR** from your fork to `SebastianDevps/agent007:main`

3. **Fill out PR template** completely

4. **Link related issue**: All PRs must reference an issue

5. **Wait for review**: Core team will review and provide feedback

**PR Review Process**:
- Initial review: 2-7 days
- Feedback provided via PR comments
- You may be asked to make changes
- Approval required before merge

---

## 📚 Documentation Contributions

Documentation improvements are always welcome!

**Where to contribute**:
- Fix typos or unclear sections in README.md
- Improve ARCHITECTURE.md explanations
- Add examples to INSTALLATION.md
- Enhance skill documentation

**Process**:
1. Create an issue describing the documentation improvement
2. Submit a PR with changes
3. Use the PR template (mark as "Documentation update")

---

## 🎓 Adding Skills or Agents

### Adding a New Skill

**Requirements**:
1. Must fit within an existing expert's domain
2. Must provide clear value (not duplicate existing skills)
3. Must follow skill structure:
   ```
   /skills/{category}/{skill-name}/
   ├── SKILL.md (full, 500-700 lines max)
   └── SUMMARY.md (100 lines max)
   ```

**Process**:
1. Create an issue proposing the skill
2. Wait for core team approval
3. Implement following the template (see existing skills)
4. Submit PR with both SKILL.md and SUMMARY.md

### Adding a New Expert Agent

**Requirements**:
- Must cover a distinct domain not covered by existing experts
- Must have at least 2-3 associated skills
- Requires strong justification (experts are intentionally limited to 5)

**Process**:
1. Create a detailed proposal issue
2. Discuss with core team (expect extensive review)
3. Only proceed if approved

---

## 🚫 What NOT to Contribute

**We won't accept**:

- ❌ Breaking changes without strong justification
- ❌ Features that significantly increase token consumption
- ❌ Changes that don't follow existing architecture patterns
- ❌ Duplicate functionality (check existing skills first)
- ❌ Unrelated changes bundled together in one PR
- ❌ Changes without proper documentation
- ❌ PRs without linked issues

---

## 🧪 Testing Guidelines

### Manual Testing Checklist

Before submitting a PR, test:

- [ ] Installation: `/plugin install` from local directory works
- [ ] Basic functionality: `/agent007:consult "test query"` works
- [ ] No regressions: Existing skills still work
- [ ] Documentation: README examples are accurate
- [ ] No errors in logs

### Automated Testing (Future)

We plan to add:
- Unit tests for skill-selector.js
- Integration tests for orchestration flow
- Token consumption benchmarks

Contributions to testing infrastructure are welcome!

---

## 📞 Getting Help

**Need help contributing?**

- 💬 **GitHub Discussions**: https://github.com/SebastianDevps/agent007/discussions
- 🎫 **Create a Question Issue**: Use the [Question template](https://github.com/SebastianDevps/agent007/issues/new?template=question.yml)
- 📖 **Read Documentation**: See ARCHITECTURE.md for technical details

---

## 🏆 Recognition

Contributors will be recognized in:
- Release notes (for merged PRs)
- CONTRIBUTORS.md file (planned)
- GitHub contributors page

---

## 📄 License

By contributing to Agent007, you agree that your contributions will be licensed under the [MIT License](LICENSE).

---

## ✅ Quick Contribution Checklist

Before submitting a PR, ensure:

- [ ] I created an issue first and it was discussed
- [ ] I read CONTRIBUTING.md (this file)
- [ ] I read ARCHITECTURE.md to understand the system
- [ ] My code follows existing patterns
- [ ] I tested locally with `/plugin install` from directory
- [ ] I updated documentation (README, ARCHITECTURE, etc.)
- [ ] I created SUMMARY.md if adding/updating skills
- [ ] My PR focuses on ONE feature/fix
- [ ] I filled out the PR template completely
- [ ] I linked the related issue in my PR

---

## 🙏 Thank You

Thank you for contributing to Agent007! Your contributions help make this tool better for everyone.

**Questions?** Open an issue or start a discussion. We're here to help!

---

**Sebastian Guerra**
