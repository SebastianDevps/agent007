/**
 * Project Context Scanner
 *
 * Scans the project to detect:
 * - Framework (NestJS, Express, Next.js, etc.)
 * - Database (PostgreSQL, MongoDB, MySQL, etc.)
 * - ORM (TypeORM, Prisma, Mongoose, etc.)
 * - Testing setup (Jest, Vitest, Mocha, etc.)
 * - Project structure
 * - Existing modules/features
 */

const fs = require('fs');
const path = require('path');

/**
 * Scan project and return context
 * @param {string} projectPath - Path to project root
 * @returns {Object} Project context
 */
function scanProjectContext(projectPath = process.cwd()) {
  const context = {
    framework: detectFramework(projectPath),
    database: detectDatabase(projectPath),
    orm: detectORM(projectPath),
    testing: detectTesting(projectPath),
    language: detectLanguage(projectPath),
    structure: detectStructure(projectPath),
    modules: detectModules(projectPath),
    dependencies: detectDependencies(projectPath),
    hasAuth: hasAuthImplementation(projectPath),
    hasApi: hasApiEndpoints(projectPath)
  };

  return context;
}

/**
 * Detect framework from package.json
 */
function detectFramework(projectPath) {
  const packageJson = readPackageJson(projectPath);
  if (!packageJson) return 'unknown';

  const deps = { ...packageJson.dependencies, ...packageJson.devDependencies };

  // Check for frameworks in priority order
  if (deps['@nestjs/core']) return 'NestJS';
  if (deps['next']) return 'Next.js';
  if (deps['react']) return 'React';
  if (deps['express']) return 'Express';
  if (deps['fastify']) return 'Fastify';
  if (deps['@angular/core']) return 'Angular';
  if (deps['vue']) return 'Vue';

  return 'Node.js';
}

/**
 * Detect database from dependencies and config files
 */
function detectDatabase(projectPath) {
  const databases = [];
  const packageJson = readPackageJson(projectPath);

  if (!packageJson) return [];

  const deps = { ...packageJson.dependencies, ...packageJson.devDependencies };

  if (deps['pg'] || deps['postgres']) databases.push('PostgreSQL');
  if (deps['mysql'] || deps['mysql2']) databases.push('MySQL');
  if (deps['mongodb'] || deps['mongoose']) databases.push('MongoDB');
  if (deps['redis']) databases.push('Redis');
  if (deps['sqlite3'] || deps['better-sqlite3']) databases.push('SQLite');

  return databases.length > 0 ? databases : ['unknown'];
}

/**
 * Detect ORM from dependencies
 */
function detectORM(projectPath) {
  const packageJson = readPackageJson(projectPath);
  if (!packageJson) return 'none';

  const deps = { ...packageJson.dependencies, ...packageJson.devDependencies };

  if (deps['typeorm']) return 'TypeORM';
  if (deps['@prisma/client']) return 'Prisma';
  if (deps['mongoose']) return 'Mongoose';
  if (deps['sequelize']) return 'Sequelize';
  if (deps['drizzle-orm']) return 'Drizzle';
  if (deps['knex']) return 'Knex';

  return 'none';
}

/**
 * Detect testing framework
 */
function detectTesting(projectPath) {
  const packageJson = readPackageJson(projectPath);
  if (!packageJson) return 'none';

  const deps = { ...packageJson.dependencies, ...packageJson.devDependencies };

  if (deps['jest'] || deps['@nestjs/testing']) return 'Jest';
  if (deps['vitest']) return 'Vitest';
  if (deps['mocha']) return 'Mocha';
  if (deps['@playwright/test']) return 'Playwright';
  if (deps['cypress']) return 'Cypress';

  return 'none';
}

/**
 * Detect programming language
 */
function detectLanguage(projectPath) {
  const packageJson = readPackageJson(projectPath);
  if (!packageJson) return 'JavaScript';

  const deps = { ...packageJson.dependencies, ...packageJson.devDependencies };

  if (deps['typescript'] || fs.existsSync(path.join(projectPath, 'tsconfig.json'))) {
    return 'TypeScript';
  }

  return 'JavaScript';
}

/**
 * Detect project structure
 */
function detectStructure(projectPath) {
  const srcPath = path.join(projectPath, 'src');

  if (!fs.existsSync(srcPath)) {
    return { type: 'flat', hasModules: false };
  }

  // Check for modular structure (NestJS-style)
  const modulesPath = path.join(srcPath, 'modules');
  if (fs.existsSync(modulesPath)) {
    return { type: 'modular', pattern: 'src/modules/', hasModules: true };
  }

  // Check for feature-based structure
  const entries = fs.readdirSync(srcPath, { withFileTypes: true });
  const hasMultipleDirs = entries.filter(e => e.isDirectory()).length > 3;

  if (hasMultipleDirs) {
    return { type: 'feature-based', pattern: 'src/[features]/', hasModules: true };
  }

  return { type: 'standard', pattern: 'src/', hasModules: false };
}

/**
 * Detect existing modules (for NestJS)
 */
function detectModules(projectPath) {
  const modules = [];
  const modulesPath = path.join(projectPath, 'src', 'modules');

  if (!fs.existsSync(modulesPath)) {
    // Try src/ directly
    const srcPath = path.join(projectPath, 'src');
    if (fs.existsSync(srcPath)) {
      const entries = fs.readdirSync(srcPath, { withFileTypes: true });
      entries
        .filter(e => e.isDirectory())
        .forEach(dir => {
          if (fs.existsSync(path.join(srcPath, dir.name, `${dir.name}.module.ts`))) {
            modules.push(dir.name);
          }
        });
    }
    return modules;
  }

  const entries = fs.readdirSync(modulesPath, { withFileTypes: true });

  entries
    .filter(e => e.isDirectory())
    .forEach(dir => {
      // Check if it's a NestJS module
      const moduleFile = path.join(modulesPath, dir.name, `${dir.name}.module.ts`);
      if (fs.existsSync(moduleFile)) {
        modules.push(dir.name);
      }
    });

  return modules;
}

/**
 * Detect dependencies and their versions
 */
function detectDependencies(projectPath) {
  const packageJson = readPackageJson(projectPath);
  if (!packageJson) return {};

  const mainDeps = packageJson.dependencies || {};
  const relevantDeps = {};

  // Extract key dependencies
  const keyPackages = [
    '@nestjs/core', '@nestjs/common', 'typeorm', 'express',
    'next', 'react', 'pg', 'redis', 'mongoose', 'prisma'
  ];

  keyPackages.forEach(pkg => {
    if (mainDeps[pkg]) {
      relevantDeps[pkg] = mainDeps[pkg];
    }
  });

  return relevantDeps;
}

/**
 * Check if project has authentication
 */
function hasAuthImplementation(projectPath) {
  const indicators = [
    'src/modules/auth',
    'src/auth',
    'src/modules/users',
    'src/users'
  ];

  return indicators.some(p => fs.existsSync(path.join(projectPath, p)));
}

/**
 * Check if project has API endpoints
 */
function hasApiEndpoints(projectPath) {
  const indicators = [
    'src/modules',
    'src/controllers',
    'src/routes',
    'src/api'
  ];

  return indicators.some(p => fs.existsSync(path.join(projectPath, p)));
}

/**
 * Helper: Read package.json
 */
function readPackageJson(projectPath) {
  try {
    const packagePath = path.join(projectPath, 'package.json');
    if (!fs.existsSync(packagePath)) return null;

    const content = fs.readFileSync(packagePath, 'utf-8');
    return JSON.parse(content);
  } catch (error) {
    return null;
  }
}

/**
 * Generate human-readable context summary
 */
function formatContextSummary(context) {
  const lines = [];

  lines.push('## Project Context');
  lines.push('');
  lines.push(`**Framework**: ${context.framework}`);
  lines.push(`**Language**: ${context.language}`);

  if (context.database.length > 0 && context.database[0] !== 'unknown') {
    lines.push(`**Database**: ${context.database.join(', ')}`);
  }

  if (context.orm !== 'none') {
    lines.push(`**ORM**: ${context.orm}`);
  }

  if (context.testing !== 'none') {
    lines.push(`**Testing**: ${context.testing}`);
  }

  lines.push(`**Structure**: ${context.structure.type}`);

  if (context.modules.length > 0) {
    lines.push(`**Existing Modules**: ${context.modules.slice(0, 5).join(', ')}${context.modules.length > 5 ? '...' : ''}`);
  }

  if (context.hasAuth) {
    lines.push('**Has Auth**: Yes');
  }

  lines.push('');

  return lines.join('\n');
}

module.exports = {
  scanProjectContext,
  formatContextSummary,
  detectFramework,
  detectDatabase,
  detectORM,
  detectTesting,
  detectLanguage
};
