#!/usr/bin/env node
/**
 * Static Analysis Script for NestJS + TypeORM Code
 *
 * Usage:
 *   node analyze.js <file-or-directory>
 *   node analyze.js src/users/users.controller.ts
 *   node analyze.js src/
 */

const fs = require('fs');
const path = require('path');

class CodeAnalyzer {
  constructor() {
    this.issues = {
      critical: [],
      warning: [],
      info: []
    };
  }

  analyzeFile(filePath) {
    const content = fs.readFileSync(filePath, 'utf-8');
    const lines = content.split('\n');

    lines.forEach((line, index) => {
      const lineNumber = index + 1;

      // SQL Injection Detection
      if (line.match(/query\s*\(\s*[`'"].*\$\{.*\}.*[`'"]/)) {
        this.issues.critical.push({
          file: filePath,
          line: lineNumber,
          message: 'Potential SQL injection - string interpolation in query',
          code: line.trim()
        });
      }

      // Missing ValidationPipe
      if (line.includes('@Body()') && !line.includes(':') && !line.includes('Dto')) {
        this.issues.warning.push({
          file: filePath,
          line: lineNumber,
          message: 'Body parameter without DTO type - consider using typed DTO',
          code: line.trim()
        });
      }

      // Password without hashing
      if (line.match(/password\s*=.*(?!bcrypt|hash)/i) && line.includes('save')) {
        this.issues.critical.push({
          file: filePath,
          line: lineNumber,
          message: 'Password assignment without apparent hashing',
          code: line.trim()
        });
      }

      // Any type usage
      if (line.match(/:\s*any\b/) && !line.includes('//')) {
        this.issues.warning.push({
          file: filePath,
          line: lineNumber,
          message: 'Usage of "any" type - consider using specific types',
          code: line.trim()
        });
      }

      // Missing await on async calls
      if (line.match(/=\s*this\.\w+Repository\.(find|save|delete|update)/)) {
        if (!line.includes('await')) {
          this.issues.critical.push({
            file: filePath,
            line: lineNumber,
            message: 'Async repository call without await',
            code: line.trim()
          });
        }
      }

      // N+1 Query Pattern
      if (line.includes('for') && content.includes('.find(') && content.includes('await')) {
        const forLoopContext = content.substring(
          Math.max(0, content.indexOf(line) - 200),
          content.indexOf(line) + 200
        );

        if (forLoopContext.match(/await.*\.find\(/g)?.length > 1) {
          this.issues.warning.push({
            file: filePath,
            line: lineNumber,
            message: 'Potential N+1 query - consider using relations or joins',
            code: line.trim()
          });
        }
      }

      // CORS wildcard
      if (line.match(/enableCors.*origin.*['"]?\*['"]?/)) {
        this.issues.critical.push({
          file: filePath,
          line: lineNumber,
          message: 'CORS configured with wildcard (*) - security risk',
          code: line.trim()
        });
      }

      // Missing guards on sensitive endpoints
      if (line.match(/@(Delete|Put|Patch)\(/)) {
        const nextLines = lines.slice(index - 3, index).join('\n');
        if (!nextLines.includes('@UseGuards')) {
          this.issues.warning.push({
            file: filePath,
            line: lineNumber,
            message: 'Destructive endpoint without guards - consider adding @UseGuards',
            code: line.trim()
          });
        }
      }

      // SELECT * pattern
      if (line.match(/SELECT\s+\*/i)) {
        this.issues.info.push({
          file: filePath,
          line: lineNumber,
          message: 'SELECT * detected - consider selecting specific columns',
          code: line.trim()
        });
      }

      // Missing pagination
      if (line.match(/@Get\(\s*['"]?\)/) && filePath.includes('controller')) {
        const methodContext = content.substring(
          content.indexOf(line),
          content.indexOf(line) + 500
        );

        if (!methodContext.includes('take') && !methodContext.includes('limit')) {
          this.issues.info.push({
            file: filePath,
            line: lineNumber,
            message: 'GET endpoint without apparent pagination',
            code: line.trim()
          });
        }
      }
    });
  }

  analyzeDirectory(dirPath) {
    const files = fs.readdirSync(dirPath);

    files.forEach(file => {
      const fullPath = path.join(dirPath, file);
      const stat = fs.statSync(fullPath);

      if (stat.isDirectory() && !file.includes('node_modules')) {
        this.analyzeDirectory(fullPath);
      } else if (file.endsWith('.ts') && !file.endsWith('.spec.ts')) {
        this.analyzeFile(fullPath);
      }
    });
  }

  printReport() {
    console.log('\n═══════════════════════════════════════════════════════');
    console.log('📊 NestJS Code Analysis Report');
    console.log('═══════════════════════════════════════════════════════\n');

    const total = this.issues.critical.length +
                  this.issues.warning.length +
                  this.issues.info.length;

    if (total === 0) {
      console.log('✅ No issues found! Great job!\n');
      return;
    }

    if (this.issues.critical.length > 0) {
      console.log('🔴 CRITICAL ISSUES (' + this.issues.critical.length + ')');
      console.log('─────────────────────────────────────────────────────\n');
      this.issues.critical.forEach(issue => {
        console.log(`  ${issue.file}:${issue.line}`);
        console.log(`  ⚠️  ${issue.message}`);
        console.log(`  📝 ${issue.code}\n`);
      });
    }

    if (this.issues.warning.length > 0) {
      console.log('\n🟡 WARNINGS (' + this.issues.warning.length + ')');
      console.log('─────────────────────────────────────────────────────\n');
      this.issues.warning.forEach(issue => {
        console.log(`  ${issue.file}:${issue.line}`);
        console.log(`  ⚠️  ${issue.message}`);
        console.log(`  📝 ${issue.code}\n`);
      });
    }

    if (this.issues.info.length > 0) {
      console.log('\n💡 SUGGESTIONS (' + this.issues.info.length + ')');
      console.log('─────────────────────────────────────────────────────\n');
      this.issues.info.forEach(issue => {
        console.log(`  ${issue.file}:${issue.line}`);
        console.log(`  ℹ️  ${issue.message}`);
        console.log(`  📝 ${issue.code}\n`);
      });
    }

    console.log('═══════════════════════════════════════════════════════');
    console.log(`Total issues: ${total} (${this.issues.critical.length} critical, ${this.issues.warning.length} warnings, ${this.issues.info.length} suggestions)`);
    console.log('═══════════════════════════════════════════════════════\n');
  }
}

// Main execution
const targetPath = process.argv[2] || './src';

if (!fs.existsSync(targetPath)) {
  console.error(`❌ Error: Path "${targetPath}" does not exist`);
  process.exit(1);
}

const analyzer = new CodeAnalyzer();
const stat = fs.statSync(targetPath);

console.log(`🔍 Analyzing: ${targetPath}\n`);

if (stat.isDirectory()) {
  analyzer.analyzeDirectory(targetPath);
} else {
  analyzer.analyzeFile(targetPath);
}

analyzer.printReport();

// Exit with error code if critical issues found
process.exit(analyzer.issues.critical.length > 0 ? 1 : 0);
