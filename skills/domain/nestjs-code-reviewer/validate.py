#!/usr/bin/env python3
"""
Validador de skill compatible con UTF-8 para Windows
"""
import sys
from pathlib import Path
import re
import yaml

def validate_skill(skill_path: Path) -> list[str]:
    """Valida un skill según la especificación de agentskills"""
    errors = []

    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return [f"ERROR: SKILL.md not found in {skill_path}"]

    # Leer con UTF-8 explícito
    try:
        content = skill_md.read_text(encoding='utf-8')
    except Exception as e:
        return [f"ERROR: Cannot read SKILL.md: {e}"]

    # Validar frontmatter YAML
    if not content.startswith('---'):
        errors.append("ERROR: SKILL.md must start with '---' (YAML frontmatter)")
        return errors

    # Extraer frontmatter
    parts = content.split('---', 2)
    if len(parts) < 3:
        errors.append("ERROR: SKILL.md must have closing '---' for frontmatter")
        return errors

    frontmatter_text = parts[1].strip()
    markdown_content = parts[2].strip()

    # Parsear YAML
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError as e:
        errors.append(f"ERROR: Invalid YAML frontmatter: {e}")
        return errors

    # Validar campos requeridos
    if 'name' not in frontmatter:
        errors.append("ERROR: 'name' field is required in frontmatter")
    else:
        name = frontmatter['name']
        if not re.match(r'^[a-z0-9-]+$', name):
            errors.append(f"WARNING: 'name' should be lowercase with hyphens only: {name}")

    if 'description' not in frontmatter:
        errors.append("ERROR: 'description' field is required in frontmatter")
    else:
        desc = frontmatter['description']
        if len(desc) > 200:
            errors.append(f"WARNING: 'description' is too long ({len(desc)} chars, max 200 recommended)")

    # Validar campos opcionales
    if 'license' in frontmatter:
        license_val = frontmatter['license']
        valid_licenses = ['MIT', 'Apache-2.0', 'BSD-3-Clause', 'GPL-3.0', 'ISC']
        if license_val not in valid_licenses:
            errors.append(f"INFO: License '{license_val}' is not a common SPDX identifier")

    if 'metadata' in frontmatter:
        if not isinstance(frontmatter['metadata'], dict):
            errors.append("WARNING: 'metadata' should be a dictionary")

    if 'allowed-tools' in frontmatter:
        tools = frontmatter['allowed-tools']
        if isinstance(tools, str):
            # Convertir a lista si es string
            tools = [t.strip() for t in tools.split()]
        if not isinstance(tools, list):
            errors.append("WARNING: 'allowed-tools' should be a list or space-separated string")

    # Validar contenido Markdown
    if not markdown_content:
        errors.append("WARNING: SKILL.md has no content after frontmatter")

    if len(markdown_content) < 100:
        errors.append("WARNING: SKILL.md content is very short (< 100 chars)")

    # Validar estructura de directorios
    if (skill_path / 'scripts').exists():
        script_count = len(list((skill_path / 'scripts').glob('*')))
        if script_count == 0:
            errors.append("INFO: 'scripts/' directory exists but is empty")

    if (skill_path / 'references').exists():
        ref_count = len(list((skill_path / 'references').glob('*.md')))
        if ref_count == 0:
            errors.append("INFO: 'references/' directory exists but has no .md files")

    if (skill_path / 'assets').exists():
        asset_count = len(list((skill_path / 'assets').glob('*')))
        if asset_count == 0:
            errors.append("INFO: 'assets/' directory exists but is empty")

    return errors

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate.py <skill-directory>")
        sys.exit(1)

    skill_path = Path(sys.argv[1])

    if not skill_path.exists():
        print(f"ERROR: Path does not exist: {skill_path}")
        sys.exit(1)

    if not skill_path.is_dir():
        print(f"ERROR: Path is not a directory: {skill_path}")
        sys.exit(1)

    print(f"Validating skill: {skill_path.name}")
    print("=" * 60)

    errors = validate_skill(skill_path)

    if not errors:
        print("[PASS] Skill passed all validation checks!")
        print("\nSkill Summary:")

        # Leer y mostrar metadata
        skill_md = skill_path / "SKILL.md"
        content = skill_md.read_text(encoding='utf-8')
        parts = content.split('---', 2)
        frontmatter = yaml.safe_load(parts[1])

        print(f"   Name: {frontmatter.get('name', 'N/A')}")
        print(f"   Description: {frontmatter.get('description', 'N/A')}")
        if 'license' in frontmatter:
            print(f"   License: {frontmatter['license']}")
        if 'metadata' in frontmatter:
            for key, value in frontmatter['metadata'].items():
                print(f"   {key.capitalize()}: {value}")

        # Contar recursos
        script_count = len(list((skill_path / 'scripts').glob('*'))) if (skill_path / 'scripts').exists() else 0
        ref_count = len(list((skill_path / 'references').glob('*.md'))) if (skill_path / 'references').exists() else 0

        print(f"\nResources:")
        print(f"   Scripts: {script_count}")
        print(f"   References: {ref_count}")

        sys.exit(0)
    else:
        print("Issues found:\n")

        critical = [e for e in errors if "ERROR" in e]
        warnings = [e for e in errors if "WARNING" in e]
        info = [e for e in errors if "INFO" in e]

        if critical:
            print("[CRITICAL ERRORS]:")
            for error in critical:
                print(f"  {error}")

        if warnings:
            print("\n[WARNINGS]:")
            for warning in warnings:
                print(f"  {warning}")

        if info:
            print("\n[INFO]:")
            for i in info:
                print(f"  {i}")

        print(f"\n{'=' * 60}")
        print(f"Total: {len(critical)} errors, {len(warnings)} warnings, {len(info)} info")

        sys.exit(1 if critical else 0)

if __name__ == '__main__':
    main()
