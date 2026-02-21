const fs = require('fs');
const path = require('path');

const CONSULT_PATH = path.join(__dirname, '../../../../commands/consult.md');

describe('/consult Command Integrity', () => {
  let consultContent;

  beforeAll(() => {
    consultContent = fs.readFileSync(CONSULT_PATH, 'utf-8');
  });

  test('consult.md does not reference archived agents', () => {
    const ARCHIVED_AGENTS = [
      'backend-expert',
      'database-expert',
      'devops-expert',
      'testing-expert',
      'ux-expert',
      'data-expert',
      'devrel-expert'
    ];
    for (const agent of ARCHIVED_AGENTS) {
      const tablePattern = new RegExp(`\\| ${agent}\\b`, 'i');
      expect(tablePattern.test(consultContent)).toBe(false);
    }
  });

  test('consult.md references all 5 active agents', () => {
    const ACTIVE_AGENTS = [
      'backend-db-expert',
      'frontend-ux-expert',
      'platform-expert',
      'product-expert',
      'security-expert'
    ];
    for (const agent of ACTIVE_AGENTS) {
      expect(consultContent).toContain(agent);
    }
  });

  test('consult.md does not reference archived skills', () => {
    const ARCHIVED_SKILLS = [
      'feature-prioritization',
      'ux-research',
      'design-system',
      'analytics-setup',
      'data-pipeline-design',
      'developer-portal'
    ];
    for (const skill of ARCHIVED_SKILLS) {
      expect(consultContent).not.toContain(skill);
    }
  });
});
