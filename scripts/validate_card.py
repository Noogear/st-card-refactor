#!/usr/bin/env python3
"""
SillyTavern Character Card V2 JSON Validator
Validates structure, escaping, completeness, and macro/tag syntax of refactored cards.
Usage: python validate_card.py <path_to_json>
"""
import json
import re
import sys
from pathlib import Path
from typing import Any

# ──────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────

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

STRING_FIELDS = [
    "name", "description", "personality", "first_mes",
    "mes_example", "scenario", "system_prompt",
    "post_history_instructions", "creator_notes", "talkativeness"
]

DEPTH_PROMPT_VALID_ROLES = {"system", "user", "assistant"}
DEPTH_PROMPT_DEFAULT_DEPTH = 4
DEPTH_PROMPT_MAX_DEPTH = 100  # reasonable upper bound

# Valid ST macro patterns (must match complete macro syntax)
ST_MACRO_PATTERNS = [
    r'\{\{char\}\}',
    r'\{\{user\}\}',
    r'\{\{original\}\}',
    r'\{\{charPrompt\}\}',
    r'\{\{charInstruction\}\}',
    r'\{\{charDepthPrompt\}\}',
    r'\{\{lastMessage\}\}',
    r'\{\{getvar::[^}]+\}\}',
    r'\{\{setvar::[^}]+::[^}]*\}\}',
    r'\{\{incvar::[^}]+\}\}',
    r'\{\{decvar::[^}]+\}\}',
    r'\{\{hasvar::[^}]+\}\}',
    r'\{\{random::[^}]+\}\}',
    r'\{\{roll:[^}]+\}\}',
    r'\{\{pick:[^}]+\}\}',
    r'\{\{[ij]var::[^}]+\}\}',
    r'\{\{\.[a-zA-Z_][a-zA-Z0-9_]*\}\}',         # {{.name}} shorthand
    r'\{\{\.[a-zA-Z_][a-zA-Z0-9_]*\|\|[^}]+\}\}', # {{.name||fallback}} shorthand
    r'\{\{/if\}\}',
    r'\{\{if [^}]+\}\}',
    r'\{\{else\}\}',
    r'\{\{trim\}\}',
    r'\{\{(wi|bx|mesExamples)::[^}]*\}\}',
]

# Custom domain tags that the AI generates (not ST macros)
CUSTOM_TAG_PATTERNS = [
    r'<conq:[^>]+>',       # conquest state update
    r'<state:[^>]+>',      # state tracking update
    r'<secret:[^>]+>',     # secret discovery
    r'<roleplay:[^>]+>',   # roleplay directive (§5A)
    r'<memory:[^>]+>',     # memory trigger (§5C)
]

# ──────────────────────────────────────────────
# Validation result collector
# ──────────────────────────────────────────────

class ValidationResult:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.info: list[str] = []
        self.passed: bool = True

    def error(self, msg: str):
        self.errors.append(f"✗ {msg}")
        self.passed = False

    def warn(self, msg: str):
        self.warnings.append(f"⚠ {msg}")

    def ok(self, msg: str):
        self.info.append(f"✓ {msg}")

    def note(self, msg: str):
        self.info.append(f"ℹ {msg}")

    def report(self) -> bool:
        for line in self.info:
            print(line)
        if self.warnings:
            print()
            for line in self.warnings:
                print(line)
        if self.errors:
            print()
            for line in self.errors:
                print(line)
        print()
        print("=" * 60)
        if self.passed:
            total_warn = len(self.warnings)
            if total_warn:
                print(f"✓ ALL CHECKS PASSED ({total_warn} warning{'s' if total_warn > 1 else ''}) — Card is ready for import")
            else:
                print("✓ ALL CHECKS PASSED — Card is ready for import")
        else:
            print(f"✗ VALIDATION FAILED ({len(self.errors)} error{'s' if len(self.errors) > 1 else ''}, {len(self.warnings)} warning{'s' if len(self.warnings) > 1 else ''})")
        return self.passed


# ──────────────────────────────────────────────
# Validation functions
# ──────────────────────────────────────────────

def validate_json_parse(filepath: str, result: ValidationResult) -> dict | None:
    """Step 1: Validate JSON can be parsed."""
    path = Path(filepath)
    if not path.exists():
        result.error(f"File not found: {filepath}")
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
    except Exception as e:
        result.error(f"Cannot read file: {e}")
        return None

    try:
        card = json.loads(raw)
    except json.JSONDecodeError as e:
        result.error(f"JSON PARSE ERROR at line {e.lineno}, col {e.colno}: {e.msg}")
        return None

    result.ok("JSON parses successfully")
    return card


def validate_top_level(card: dict, result: ValidationResult) -> bool:
    """Step 2: Validate top-level structure (spec, spec_version, data)."""
    for field in REQUIRED_FIELDS:
        if field not in card:
            result.error(f"Missing top-level field: '{field}'")
            return False

    spec = card.get("spec", "")
    spec_version = card.get("spec_version", "")
    valid_specs = {"chara_card_v2", "chara_card_v3"}
    if spec not in valid_specs:
        result.warn(f"Unexpected spec value: '{spec}' (expected one of {valid_specs})")
    result.ok(f"Spec: {spec} v{spec_version}")
    return True


def validate_data_fields(data: dict, result: ValidationResult) -> bool:
    """Step 3: Validate required and recommended data fields."""
    missing_required = [f for f in REQUIRED_DATA_FIELDS if f not in data]
    if missing_required:
        result.error(f"Missing required data fields: {missing_required}")
        return False
    result.ok("All required fields present")

    # Empty field warnings
    empty_fields = [f for f in REQUIRED_DATA_FIELDS if not str(data.get(f, "")).strip()]
    if empty_fields:
        result.warn(f"Empty fields (may be intentional): {empty_fields}")

    # Recommended fields
    missing_recommended = [f for f in RECOMMENDED_DATA_FIELDS if f not in data]
    if missing_recommended:
        result.warn(f"Missing recommended fields: {missing_recommended}")

    return True


def validate_string_fields(data: dict, result: ValidationResult):
    """Step 4: Validate string field types and control characters."""
    for field in STRING_FIELDS:
        val = data.get(field)
        if val is None:
            continue  # optional field, skip
        if not isinstance(val, str):
            result.error(f"'{field}' is not a string (type={type(val).__name__})")
            continue
        # Check for unescaped control characters (except \n, \r, \t)
        for i, ch in enumerate(val):
            if ord(ch) < 32 and ch not in ('\n', '\r', '\t'):
                result.warn(f"'{field}'[{i}]: contains control char U+{ord(ch):04X}")
                break  # one warning per field is enough
    result.ok("String field types and control chars validated")


def validate_alternate_greetings(data: dict, result: ValidationResult):
    """Step 5: Validate alternate_greetings structure."""
    alt_greets = data.get("alternate_greetings", [])
    if not isinstance(alt_greets, list):
        result.error("'alternate_greetings' is not a list")
        return

    result.ok(f"alternate_greetings: {len(alt_greets)} greetings")
    for i, g in enumerate(alt_greets):
        if not isinstance(g, str):
            result.error(f"alternate_greetings[{i}]: not a string (type={type(g).__name__})")
        elif not g.strip():
            result.warn(f"alternate_greetings[{i}]: empty string")


def validate_extensions(data: dict, result: ValidationResult):
    """Step 6: Validate extensions field structure and depth_prompt if present."""
    extensions = data.get("extensions")
    if extensions is None:
        result.warn("No 'extensions' field present")
        return

    if not isinstance(extensions, dict):
        result.error("'extensions' is not a JSON object")
        return

    result.ok("'extensions' is present and is a JSON object")

    # 6a. Validate depth_prompt if present
    depth_prompt = extensions.get("depth_prompt")
    if depth_prompt is not None:
        validate_depth_prompt(depth_prompt, result)

    # 6b. Validate character_book if present
    char_book = extensions.get("character_book")
    if char_book is not None:
        validate_character_book(char_book, result)

    # 6c. Check for known extension keys
    known_keys = {
        "depth_prompt", "character_book", "fav", "world",
        "talkativeness", "regex_scripts", "lorebook"
    }
    unknown_keys = set(extensions.keys()) - known_keys
    if unknown_keys:
        result.note(f"Unknown extension keys (may be valid): {unknown_keys}")


def validate_depth_prompt(dp: Any, result: ValidationResult):
    """Step 6a: Validate depth_prompt structure (extensions.depth_prompt)."""
    if not isinstance(dp, dict):
        result.error("'extensions.depth_prompt' is not a JSON object")
        return

    # Required field: prompt
    prompt = dp.get("prompt")
    if prompt is None:
        result.error("depth_prompt missing 'prompt' field")
    elif not isinstance(prompt, str):
        result.error(f"depth_prompt.prompt is not a string (type={type(prompt).__name__})")
    elif not prompt.strip():
        result.warn("depth_prompt.prompt is empty")
    else:
        result.ok(f"depth_prompt.prompt: {len(prompt)} chars")

    # Optional field: depth (number)
    depth = dp.get("depth")
    if depth is not None:
        if not isinstance(depth, (int, float)):
            result.error(f"depth_prompt.depth is not a number (type={type(depth).__name__})")
        elif depth < 0:
            result.error(f"depth_prompt.depth is negative ({depth})")
        elif depth > DEPTH_PROMPT_MAX_DEPTH:
            result.warn(f"depth_prompt.depth is unusually high ({depth})")
        else:
            result.ok(f"depth_prompt.depth: {depth}")
    else:
        result.note("depth_prompt.depth not set (ST default: 4)")

    # Optional field: role (string)
    role = dp.get("role")
    if role is not None:
        if not isinstance(role, str):
            result.error(f"depth_prompt.role is not a string (type={type(role).__name__})")
        elif role not in DEPTH_PROMPT_VALID_ROLES:
            result.error(f"depth_prompt.role is '{role}' (valid: {DEPTH_PROMPT_VALID_ROLES})")
        else:
            result.ok(f"depth_prompt.role: '{role}'")
    else:
        result.note("depth_prompt.role not set (ST default: 'system')")

    # Warn on unknown keys
    known_dp_keys = {"prompt", "depth", "role"}
    unknown_dp = set(dp.keys()) - known_dp_keys
    if unknown_dp:
        result.warn(f"depth_prompt has unknown keys: {unknown_dp}")


def validate_character_book(book: Any, result: ValidationResult):
    """Step 6b: Validate character_book / lorebook structure."""
    if not isinstance(book, dict):
        result.error("'extensions.character_book' is not a JSON object")
        return

    entries = book.get("entries")
    if entries is None:
        result.warn("character_book has no 'entries' field")
    elif not isinstance(entries, list):
        result.error("character_book.entries is not a list")
    else:
        result.ok(f"character_book: {len(entries)} entries")
        # Validate each entry has required fields
        for i, entry in enumerate(entries):
            if not isinstance(entry, dict):
                result.error(f"character_book.entries[{i}] is not an object")
                continue
            if "key" not in entry and "keys" not in entry and "keysecondary" not in entry:
                result.warn(f"character_book.entries[{i}]: no activation keys")
            if "content" not in entry and "comment" not in entry:
                result.warn(f"character_book.entries[{i}]: no content or comment")


def validate_macros(data: dict, result: ValidationResult):
    """Step 7: Validate ST macro syntax in all string fields."""
    all_text_fields = ["description", "personality", "first_mes", "mes_example",
                       "scenario", "system_prompt", "post_history_instructions"]

    macro_issues = []
    for field in all_text_fields:
        val = data.get(field, "")
        if not isinstance(val, str) or not val:
            continue

        # Find all {{...}} patterns
        raw_macros = re.findall(r'\{\{[^}]*\}\}?', val)
        for macro in raw_macros:
            # Check if it matches any known macro pattern
            matched = any(re.fullmatch(pattern, macro) for pattern in ST_MACRO_PATTERNS)
            if not matched:
                macro_issues.append(f"  [{field}] Unrecognized macro: {macro}")

    if macro_issues:
        result.warn("Potentially unrecognized ST macros (may be valid custom macros):")
        for issue in macro_issues[:20]:  # cap output
            print(issue)
        if len(macro_issues) > 20:
            print(f"  ... and {len(macro_issues) - 20} more")
    else:
        result.ok("All macros match known ST patterns")


def validate_custom_tags(data: dict, result: ValidationResult):
    """Step 8: Validate custom domain tags (conq, state, secret, roleplay, memory)."""
    system_prompt = data.get("system_prompt", "")
    first_mes = data.get("first_mes", "")
    mes_example = data.get("mes_example", "")

    tag_fields = {
        "system_prompt": system_prompt,
        "first_mes": first_mes,
        "mes_example": mes_example,
    }

    found_tags: dict[str, list[str]] = {}
    for field, text in tag_fields.items():
        if not isinstance(text, str):
            continue
        for pattern in CUSTOM_TAG_PATTERNS:
            matches = re.findall(pattern, text)
            if matches:
                tag_type = pattern.split(':')[0].lstrip('<')
                found_tags.setdefault(tag_type, []).extend(
                    f"[{field}] {m}" for m in matches
                )

    if found_tags:
        for tag_type, locations in found_tags.items():
            result.ok(f"Custom tag <{tag_type}:...> found: {len(locations)} instance(s)")
    else:
        result.note("No custom domain tags found (conq/state/secret/roleplay/memory)")


def validate_conquest_state_consistency(data: dict, result: ValidationResult):
    """Step 9: Check consistency between system_prompt conquest directives and variable references."""
    system_prompt = data.get("system_prompt", "")
    if not isinstance(system_prompt, str):
        return

    # Find all conquest_<key> variable references
    var_refs = set(re.findall(r'\{\{\.conquest_(\w+?)(?:\|\|.*?)?\}\}', system_prompt))
    # Find all conquest_<key> in <conq:...> tags
    tag_keys = set()
    for tag in re.findall(r'<conq:([^>]+)>', system_prompt):
        for pair in tag.split(','):
            parts = pair.strip().split('=')
            if len(parts) >= 1:
                key = parts[0].strip()
                if key:
                    tag_keys.add(key)

    if var_refs and tag_keys:
        # Cross-check: every variable ref should appear in the TARGET_MAP
        if var_refs != tag_keys:
            in_ref_not_tag = var_refs - tag_keys
            in_tag_not_ref = tag_keys - var_refs
            if in_ref_not_tag:
                result.warn(f"Conquest keys in variable refs but not in tags: {in_ref_not_tag}")
            if in_tag_not_ref:
                result.warn(f"Conquest keys in tags but not in variable refs: {in_tag_not_ref}")
        else:
            result.ok(f"Conquest keys consistent across variable refs and tags ({len(var_refs)} targets)")

    if var_refs:
        # Validate variable naming: all lowercase + underscores
        for key in var_refs:
            if not re.fullmatch(r'[a-z][a-z0-9_]*', key):
                result.warn(f"Conquest key '{key}' doesn't follow lowercase_snake_case convention")


def validate_post_history_instructions(data: dict, result: ValidationResult):
    """Step 10: Validate post_history_instructions field if present."""
    phi = data.get("post_history_instructions")
    if phi is None:
        result.note("No post_history_instructions field (may not be needed)")
        return

    if not isinstance(phi, str):
        result.error(f"post_history_instructions is not a string (type={type(phi).__name__})")
        return

    if not phi.strip():
        result.warn("post_history_instructions is empty")
        return

    result.ok(f"post_history_instructions: {len(phi)} chars")

    # Check for {{original}} macro usage (best practice for PHIs)
    if "{{original}}" in phi:
        result.ok("PHI uses {{original}} macro — correctly prepends global PHI content")
    else:
        result.note("PHI does not use {{original}} — global PHI content won't be prepended")


def validate_roundtrip(card: dict, result: ValidationResult) -> bool:
    """Step 11: Validate JSON round-trip serialization."""
    try:
        re_serialized = json.dumps(card, ensure_ascii=False, indent=2)
        re_parsed = json.loads(re_serialized)
        if re_parsed != card:
            result.error("Round-trip serialization mismatch")
            return False
        result.ok("JSON round-trip serialization OK")
        return True
    except Exception as e:
        result.error(f"Round-trip serialization failed: {e}")
        return False


def estimate_tokens(data: dict, result: ValidationResult):
    """Step 12: Estimate total token count."""
    all_text = ""
    for f in STRING_FIELDS:
        val = data.get(f)
        if isinstance(val, str):
            all_text += val + "\n"
    # Include alternate greetings
    for g in data.get("alternate_greetings", []):
        if isinstance(g, str):
            all_text += g + "\n"
    # Include character_book content
    book = data.get("extensions", {}).get("character_book", {})
    if isinstance(book, dict):
        for entry in book.get("entries", []):
            if isinstance(entry, dict):
                for key in ("content", "comment", "key"):
                    val = entry.get(key)
                    if isinstance(val, str):
                        all_text += val + "\n"

    # Rough token estimate: ~1 token per 4 chars for English, ~1.5 tokens per char for CJK
    char_count = len(all_text)
    # Count CJK characters for better estimation
    cjk_count = sum(1 for ch in all_text if '\u4e00' <= ch <= '\u9fff' or
                    '\u3000' <= ch <= '\u303f' or '\uff00' <= ch <= '\uffef')
    non_cjk = char_count - cjk_count
    estimated_tokens = (non_cjk // 4) + int(cjk_count * 1.0)

    result.ok(f"Estimated token count: ~{estimated_tokens:,} (from {char_count:,} chars)")

    if estimated_tokens > 3000:
        result.warn(f"High token count ({estimated_tokens:,}) — consider compression or token budget mode")
    elif estimated_tokens > 1500:
        result.note(f"Moderate token count ({estimated_tokens:,}) — within reasonable range")
    else:
        result.ok(f"Token count is low ({estimated_tokens:,}) — no compression needed")


def validate_brackets(data: dict, result: ValidationResult):
    """Step 13: Check for empty or malformed brackets in description field."""
    description = data.get("description", "")
    if not isinstance(description, str) or not description:
        return

    # Detect empty brackets: () [] {} that are not part of macros {{ }}
    empty_round = re.findall(r'\(\s*\)', description)
    empty_square = re.findall(r'\[\s*\]', description)

    if empty_round:
        result.warn(f"description: {len(empty_round)} empty round bracket(s) '()' found")
    if empty_square:
        result.warn(f"description: {len(empty_square)} empty square bracket(s) '[]' found")

    if not empty_round and not empty_square:
        result.ok("No empty brackets in description")


# ──────────────────────────────────────────────
# Main validation pipeline
# ──────────────────────────────────────────────

def validate_character_card(card: dict, result: ValidationResult) -> bool:
    """Validate a standard character card."""
    result.note("Detected Character Card V2 format.")

    # Step 2: Top-level structure
    if not validate_top_level(card, result):
        return False

    data = card.get("data", {})
    if not isinstance(data, dict):
        result.error("'data' field is not a JSON object")
        return False

    # Step 3: Required/recommended fields
    validate_data_fields(data, result)

    # Step 4: String field types and control chars
    validate_string_fields(data, result)

    # Step 5: Alternate greetings
    validate_alternate_greetings(data, result)

    # Step 6: Extensions (including depth_prompt and character_book)
    validate_extensions(data, result)

    # Step 7: ST macro syntax
    validate_macros(data, result)

    # Step 8: Custom domain tags
    validate_custom_tags(data, result)

    # Step 9: Conquest/state consistency
    validate_conquest_state_consistency(data, result)

    # Step 10: post_history_instructions
    validate_post_history_instructions(data, result)

    # Step 11: JSON round-trip
    validate_roundtrip(card, result)

    # Step 12: Token estimation
    estimate_tokens(data, result)

    # Step 13: Bracket checks
    validate_brackets(data, result)

    return True


def validate_qr_preset(data: dict, result: ValidationResult) -> bool:
    """Validate a Quick Reply preset."""
    result.note("Detected QR Preset format.")

    if "entries" in data:
        result.error("QR Preset uses 'entries' instead of 'qrList'. This will cause a 'Cannot read properties of undefined (reading \\'map\\')' error on import in SillyTavern.")
    elif "qrList" not in data:
        result.error("QR Preset missing 'qrList' array.")
    else:
        qrList = data.get("qrList")
        if not isinstance(qrList, list):
            result.error("'qrList' is not a list")
        else:
            result.ok(f"Found valid 'qrList' with {len(qrList)} entries.")

    if "name" not in data:
        result.warn("QR Preset missing 'name' field.")

    # JSON round-trip
    validate_roundtrip(data, result)
    return True


def validate(filepath: str) -> bool:
    """Run the appropriate validation pipeline based on the file format."""
    result = ValidationResult()

    # Step 1: JSON parse
    card = validate_json_parse(filepath, result)
    if card is None:
        return result.report()

    # Detect format: QR Presets have 'qrList' (or mistakenly 'entries' without 'spec')
    # Character cards have 'spec': 'chara_card_v2'
    if "qrList" in card or ("entries" in card and "spec" not in card):
        validate_qr_preset(card, result)
    else:
        validate_character_card(card, result)

    return result.report()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_card.py <path_to_json>")
        print("  Validates a SillyTavern V2 character card JSON or QR Preset JSON.")
        sys.exit(1)

    filepath = sys.argv[1]
    success = validate(filepath)
    sys.exit(0 if success else 1)
