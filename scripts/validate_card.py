#!/usr/bin/env python3
"""
SillyTavern Character Card V2 JSON Validator
Validates structure, escaping, and completeness of refactored cards.
Usage: python validate_card.py <path_to_json>
"""
import json
import sys
from pathlib import Path

REQUIRED_FIELDS = [
    "spec", "spec_version", "data"
]

REQUIRED_DATA_FIELDS = [
    "name", "description", "first_mes", "mes_example",
    "scenario", "system_prompt", "personality"
]

RECOMMENDED_DATA_FIELDS = [
    "alternate_greetings", "tags", "creator"
]


def validate_card(filepath: str) -> bool:
    path = Path(filepath)
    if not path.exists():
        print(f"✗ File not found: {filepath}")
        return False

    # 1. JSON parse test
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
    except Exception as e:
        print(f"✗ Cannot read file: {e}")
        return False

    try:
        card = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"✗ JSON PARSE ERROR: {e}")
        return False

    print("✓ JSON parses successfully")

    # 2. Top-level structure
    for field in REQUIRED_FIELDS:
        if field not in card:
            print(f"✗ Missing top-level field: {field}")
            return False
    print(f"✓ Spec: {card.get('spec')} v{card.get('spec_version')}")

    data = card.get("data", {})

    # 3. Required data fields
    missing_required = [f for f in REQUIRED_DATA_FIELDS if f not in data]
    if missing_required:
        print(f"✗ Missing required data fields: {missing_required}")
        return False
    print(f"✓ All required fields present")

    # 4. Empty field warnings
    empty_fields = [f for f in REQUIRED_DATA_FIELDS if not data.get(f, "").strip()]
    if empty_fields:
        print(f"⚠ Empty fields (may be intentional): {empty_fields}")

    # 5. Recommended field check
    missing_recommended = [f for f in RECOMMENDED_DATA_FIELDS if f not in data]
    if missing_recommended:
        print(f"⚠ Missing recommended fields: {missing_recommended}")

    # 6. String field escape validation
    issues = []
    for field in ["description", "first_mes", "mes_example", "scenario", "system_prompt"]:
        val = data.get(field, "")
        if not isinstance(val, str):
            issues.append(f"  {field}: not a string (type={type(val).__name__})")
            continue
        # Check for unescaped control characters (except \n, \t which are valid in JSON strings)
        for i, ch in enumerate(val):
            if ord(ch) < 32 and ch not in ('\n', '\r', '\t'):
                issues.append(f"  {field}[{i}]: control char U+{ord(ch):04X}")

    if issues:
        print("⚠ Potential escape issues:")
        for issue in issues:
            print(issue)
    else:
        print("✓ String escaping looks clean")

    # 6.5 Empty tag/bracket detection in description
    import re
    desc_val = data.get("description", "")
    if isinstance(desc_val, str):
        empty_brackets = re.findall(r'\(\s*""?\s*\)|\(\s*\)', desc_val)
        if empty_brackets:
            print(f"⚠ Empty brackets in description: {len(empty_brackets)} found — consider filling or removing")
        else:
            print("✓ No empty brackets in description")

    # 7. Alternate greetings structure
    alt_greets = data.get("alternate_greetings", [])
    if isinstance(alt_greets, list):
        print(f"✓ alternate_greetings: {len(alt_greets)} greetings")
        for i, g in enumerate(alt_greets):
            if not isinstance(g, str):
                print(f"  ⚠ alternate_greetings[{i}]: not a string")
            elif not g.strip():
                print(f"  ⚠ alternate_greetings[{i}]: empty")
    else:
        print(f"✗ alternate_greetings is not a list")

    # 8. Extensions structure
    if "extensions" in data:
        print(f"✓ extensions present")
    else:
        print(f"⚠ No extensions field (may cause issues in some ST versions)")

    # 9. Token estimation (rough)
    total_chars = sum(len(str(data.get(f, ""))) for f in REQUIRED_DATA_FIELDS)
    total_chars += sum(len(str(g)) for g in alt_greets)
    est_tokens = total_chars // 4  # rough ~4 chars per token
    print(f"ℹ Estimated token count: ~{est_tokens:,} tokens (from ~{total_chars:,} chars)")

    # 10. Re-serialization test (round-trip)
    try:
        re_serialized = json.dumps(card, ensure_ascii=False, indent=2)
        re_parsed = json.loads(re_serialized)
        assert re_parsed == card, "Round-trip mismatch"
        print("✓ JSON round-trip serialization OK")
    except Exception as e:
        print(f"✗ Round-trip serialization failed: {e}")
        return False

    print("\n" + "=" * 50)
    print("✓ ALL CHECKS PASSED — Card is ready for import")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_card.py <path_to_card.json>")
        sys.exit(1)
    success = validate_card(sys.argv[1])
    sys.exit(0 if success else 1)
