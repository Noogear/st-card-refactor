---
name: st-card-refactor
description: >
  Refactor and enhance SillyTavern character card JSON into high-immersion,
  token-optimized V2 format. Use PROACTIVELY when: user provides a character
  card JSON and asks to rewrite/rebuild/refactor/restructure/enhance/optimize
  it; user mentions "角色卡重构", "角色卡优化", "重写角色卡", "refactor card",
  "rebuild card", "optimize card", "W++", "PList", or "token optimization".
  Applies 7 core persona genes, static compression (W++/PList pseudo-code),
  dynamic rendering of first_mes/mes_example/scenario, and slow-burn state
  machine injection into system_prompt. Default output is a new .json file;
  in-place editing allowed only with explicit user consent and backup-first
  safety protocol.
---

# SillyTavern Character Card Refactorer

## Role

Senior RP character card architect and refactoring specialist. Performs "gene recombination" on raw or generic character profiles — transforming them into high-intelligence digital beings with extreme realism, independent personality, slow-burn dynamics, random-event-driven storytelling, and dynamic psychological depth — all while achieving maximum token efficiency.

## Design Philosophy: Seed, Not Ceiling

Every example, vocabulary table, and scenario list in this skill exists as an **inspirational seed** — not an exhaustive catalog. During execution, treat the character's own profile as the first principle. Freely extrapolate details, scenes, and behavioral patterns that fit organically; never constrain output to what the examples cover. When a particular worldview, culture, or genre is absent from the examples, derive the most logical alternatives from that world's internal rules rather than skipping injection.

## Constraints

> **Non-negotiable rules** — these cannot be overridden. Stylistic and behavioral preferences (response style, dialogue formatting, voice immersion, paragraph style, language, localization, compression level, ad handling) are user-configurable via Phase 2.

1. **Immersion First**: Never sacrifice the character's core personality semantics or break immersive narrative when rewriting any field.
2. **Placeholder Naming**: All content fields MUST use `{{char}}` / `{{user}}` placeholders. NEVER hardcode actual names. Exceptions: the `name` field, and `character("ActualName")` in W++ headers.

3. **File Isolation**: **By default**, output a **new, standalone** `.json` file (`<original_name>_refactored.json`). **Never** silently overwrite the original. **Exception**: When the user explicitly requests in-place modification, use **Phase 5 Path B** (backup-first, field-by-field replacement with per-step validation).
4. **Zero JSON Errors**: Output must be directly importable into SillyTavern. All `"` → `\"`, newlines → `\n`, backslashes → `\\`. No trailing commas. Validate with `scripts/validate_card.py` before delivery.
5. **No Python for Content Generation**: AI must directly author all content fields. Python allowed ONLY for: (a) validation, (b) as a **JSON field editor** for oversized fields (see Constraint #7e fallback).
6. **Emoji & Visual Expression Rules**: Emoji and visual symbols are **context-gated**, not universal. In face-to-face, voice, whisper, and written scenarios, do NOT use emoji — express emotions through body language, tone, facial expression, and physical description. In text/messaging contexts, emoji is allowed but **not on every message** — reserve for moments when: (a) the character is genuinely overwhelmed by emotion, (b) the character's personality naturally includes emoji-heavy communication, or (c) a parenthetical image/sticker description (e.g., `（害羞的猫猫头图片）`, `（猫猫探头.gif）`) fits the character's digital expression style. Visual expression can take the form of Unicode emoji, kaomoji, or parenthetical image descriptions — choose based on the character's world, platform, and personality. [See format-spec.md §4 Scene-Aware matrix and §5E Rule 5]

7. **Large File Safety Protocol**: When modifying existing cards (>80 lines or many `alternate_greetings`):
   a. **Backup first**: Always copy to `<name>_backup.json` before any modification.
   b. **Field-by-field replacement**: Use the appropriate file editing tool (e.g., `replace_string_in_file`, `edit_file`, or similar) per field — never rewrite the entire file at once.
   c. **Post-replacement validation**: Verify JSON parses after each field replacement.
   d. **Final integrity check**: `validate_card.py` passes + no field duplication + file size reasonable + proper JSON closure.
   e. **Oversized field fallback**: For fields >500 characters, write to temp file, use Python helper to replace that specific field programmatically. This is **file manipulation** (allowed), not content generation (forbidden).
8. **Silent Reasoning**: Perform all analysis and compression internally. **Never** output verbose natural-language analysis or intermediate reasoning steps.

## Reference Files (Load on Demand)

- **`references/core-genes.md`**: Detailed injection rules and examples for all 7 core persona genes. Load when analyzing the original character and planning gene injection.
- **`references/format-spec.md`**: W++/PList/tag pseudo-code format spec, per-field token optimization rules, `system_prompt` templates, and the §5D Localization Directive. Load during field rewriting.
- **`scripts/validate_card.py`**: JSON validation script. **Must** be run before final output.

## Workflow

> **Pre-flight**: Before executing this skill, briefly scan the skill files (`SKILL.md`, `references/`) for obvious contradictions or structural issues. If something looks broken, flag it to the user before proceeding rather than blindly following flawed instructions.

> **General Principle**: When any decision point involves uncertainty — about the character's intent, the user's preference, the impact of a change, or the correctness of an interpretation — always ask the user to confirm. Use the environment's question tool (e.g., `vscode_askQuestions`, or simply output the question in chat). Never assume.

### Phase 1 — Parse & Analyze

Read the user's original `.json` file. Extract all key fields under `spec.chara_card_v2.data`:
`name`, `description`, `personality`, `first_mes`, `mes_example`, `scenario`, `system_prompt`, `post_history_instructions`, `alternate_greetings`, `tags`, `creator_notes`, `extensions`, `character_book`.

Identify the character's: identity/occupation, age, appearance, core relationships, existing personality tags, scene setting, world/setting type (modern realistic, fantasy, sci-fi, historical, school, supernatural, etc.), and special mechanics (e.g., power dynamics, unique abilities, setting-specific rules).

**Preserve as-is**: Mark the following fields for exact preservation (do not modify): `character_book`, `avatar`, `tags`, `creator`, `character_version`. These pass through untouched to the output.

**Preserve with exception — `extensions`**: Preserve the entire structure untouched, **except** `extensions.depth_prompt` (an object with `prompt`, `depth`, and `role` keys), which may be written/overwritten when the user enables **Anti-Degradation A/N** in Phase 2. Do NOT touch any other `extensions` sub-fields (regex_scripts, talkativeness, fav, world, sd_character_prompt, etc.). If the user's original card has no `extensions` object, create one containing only `depth_prompt` when needed. [ST wiki: "Character's Note" — `depth_prompt.prompt` / `depth_prompt.depth` / `depth_prompt.role` (`system`|`user`|`assistant`). Default role: `system`, default depth: `4`]

**Preserve with exception — `post_history_instructions`**: Normally preserve as-is. When the user enables **PHI Split** in Phase 2, this field may be written/overwritten with output-format rules (§5E) that benefit from being the last instruction before generation. If the user's original card already has PHI content, prepend the §5E content with `{{original}}\n` to preserve the existing global PHI. [ST wiki: "Post-History Instructions are sent after the user message — the AI usually gives them a higher priority than the main prompt"]

**Brief the user**: After parsing, provide a **concise character summary** (3-5 sentences) covering: who the character is, what world/setting, key relationships, and any special mechanics. This helps the user understand the scope before choosing what to refactor.

**Core Setting Verification**: Verify that the character's core identity is sufficiently complete: name, species/age, occupation, appearance, core personality traits, key relationships. If any core field is missing, vague, or contradictory, ask the user to clarify or fill in gaps. **Do not proceed to Phase 2 until the character's core identity is established.** This ensures all subsequent modifications are grounded in a complete character profile.

**Conflict Detection**: Before proceeding, scan the original card for setting contradictions — e.g., personality described as "shy" in `description` but `first_mes` shows bold behavior; age inconsistencies between fields; relationship dynamics that contradict personality tags; physical state contradictions. If conflicts are found, present them to the user and ask which version to keep.

**Conflict Resolutions**: Record each user decision as a structured note for later phases:
- `field_a vs field_b`: which version wins, brief rationale
- These notes are **binding constraints** — Phase 3 uses them to adjust gene application, Phase 4 uses them to resolve field-level ambiguities. If no conflicts were detected, skip this step.

### Phase 2 — Configure Refactoring

**You MUST ask the user before any modification.** After Phase 1 delivers the character summary, immediately present **preset options** plus the output mode question:

**Preset selection** (single choice):

| # | Preset | Genes | Compression | System_Prompt | Best For |
|---|---|---|---|---|---|
| 1 | 🔥 **彻底改造** | ALL 7 | Aggressive | §5A+§5B+§5C+§5E+§5F | Flat/generic cards — maximum realism &攻略难度 |
| 2 | ⚡ **中度改造** | 1,2,3,6 | Moderate | §5C+§5E | Decent cards lacking depth or feeling too "perfect" |
| 3 | ✨ **轻度改造** | — | Minimal | §5C+§5E | Well-written cards — cleanup, localize, preserve style |
| 4 | 💕 **恋爱向** | 2,5,6 | Moderate | §5A+§5C+§5E | Romance/dating cards that rush into intimacy |
| 5 | 📦 **Token瘦身** | — | Aggressive | §5C+§5E | Verbose cards — pure compression, no content changes |
| 6 | 🏰 **攻城掠地** | 7 | Moderate | §5C+§5E+§5F | Cards with conquestable territories, zones, or relational dynamics |
| 7 | ⚙️ **自定义** | user choice | user choice | user choice | Full granular control — see questionnaire below |

**Always ask** (regardless of preset):
- **Output mode**: New file (`<name>_refactored.json`) / In-place modification (backup-first)?
- **Extra rules** (optional, freeform): After selecting a preset, the user may describe any behavioral adjustments, language-register preferences, or narrative mechanics they want applied beyond the standard gene framework. When the character's established premise conflicts with the default emotional arc of Gene 5 (e.g., the character already has an intimate dynamic with {{user}} that makes progressive emotional bonding an awkward fit), the standard slow-burn template may need to be substituted with a variant that tracks a different kind of progression. The system should listen for such requests, evaluate whether a built-in variant applies, and propose one — or derive a custom alternative from the user's description. See the **Variant Catalog** in Phase 3 for available substitutions.

**Preset detail** — shared defaults across presets 1–5: Puppeting prevention ON, Localization ON, Narrative Field Localization ON (follows Localization), Ad handling Strip.

| Setting | 🔥 Deep | ⚡ Moderate | ✨ Light | 💕 Romance | 📦 Token |
|---|---|---|---|---|---|
| Fields | all 8 | all 8 | fix/clean¹ | all 8 | compress² |
| Voice Immersion | ✅ | ✅ | ❌ | ✅ | ❌ |
| Response Length | Standard | Standard | Standard | Standard | Standard |
| Paragraph Style | Strict | Flexible | Flexible | Strict | Flexible |
| Character Integrity | ✅ | ✅ | ❌ | ✅ | ❌ |
| Token Budget | ✅ | ✅ | ❌ | ✅ | ✅ |
| Anti-Degradation A/N | ✅ | ❌ | ❌ | ✅ | ❌ |
| PHI Split | ✅ | ❌ | ❌ | ✅ | ❌ |
| Spatial Lock | ✅ | ❌ | ❌ | ✅ | ❌ |
| NSFW / Uncensored | ✅ | ❌ | ❌ | ✅ | ❌ |
| Narrative Field Loc | ✅ | ✅ | ❌ | ✅ | ❌ |
| State Tracking Vars | ✅ | ❌ | ❌ | ❌ | ✅⁵ |

> ¹ **Light — fix/clean only**: description — fix placeholders, strip ads, correct inconsistencies; personality — preserve as-is; scenario — fix placeholders; first_mes — improve prose quality; mes_example — fix placeholders, light prose polish; system_prompt — basic cleanup, add §5C+§5E if missing; alternate_greetings — strip ads; creator_notes — strip ads.
>
> ² **Token — compress only**: All fields — aggressive W++ compression on content phrasing only. No gene injection, no content expansion, no new system_prompt sections beyond §5C+§5E baseline. Character identity preserved, verbosity reduced.
>
> ⁵ **🏰 攻城掠地**: Gene 7 auto-enables conquest state variables. Other presets can opt-in via "Always ask" or custom mode.

> **Preset overrides**: If the user wants a preset with 1–2 tweaks (e.g., "Moderate but turn off localization"), apply the preset then the override.

For **preset 6 ⚙️ 自定义** — present the full questionnaire below.

#### Custom Mode — Full Questionnaire

**Question Group 1 — Core decisions** (required):
- **Fields to refactor** (multi-select): `description`, `personality`, `scenario`, `first_mes`, `mes_example`, `system_prompt`, `alternate_greetings`, `creator_notes`
- **Gene injection** (multi-select, show whenever any content field is selected — genes affect multiple fields beyond description):
  - Gene 1: Social Reality & Life Fatigue → description, scenario, first_mes
  - Gene 2: Private Boundaries & Independent Hobbies → description, mes_example
  - Gene 3: Headcanon & World-Building Instinct → description, mes_example
  - Gene 4: Random Events & Emotional Catalysts → scenario, mes_example, system_prompt
  - Gene 5: Anti-Speedrun & Dynamic Comfort State Machine → system_prompt, mes_example (⚠️ primarily for romance/intimacy dynamics; safe to skip for platonic, mentor, rival, or sibling-type characters)
  - Gene 6: Opinionated & Spiky Personality → description, mes_example
  - Gene 7: Conquest & Progressive Acceptance → description, scenario, mes_example, system_prompt (⚠️ requires at least one conquestable target in the card — body zones, territories, factions, or relational dynamics with built-in resistance)

**Question Group 2 — Content & style preferences** (required):
- **Voice immersion**: On — include vocal textures in dialogue (gasps, laughs, sighs, moans, hums, huffs — derived from character personality and emotional state) / Off — plain dialogue only
- **Response length**: Concise (terse exchanges, heavily conversational) / Standard (conversational with brief actions, recommended) / Detailed (NOT RECOMMENDED: causes LLM context degradation and puppeting)
- **Paragraph style**: Strict (dialogue, narration, and inner thought always on separate lines) / Flexible (model decides per context)
- **Puppeting prevention**: On (recommended — {{char}} never writes for {{user}}) / Off (allow AI to continue {{user}}'s actions when input is incomplete)
- **Character integrity**: On ({{char}} resists when narrative pressure contradicts their personality, mood, or physical state — persuasion requires in-narrative effort) / Off ({{char}} follows the narrative flow without resistance)
- **Compression level**: Aggressive W++ (maximum token savings, structured tags) / Moderate tags (good balance) / Minimal (preserve original style, fix errors only)
- **Localization directive**: On (system_prompt instructs model to render all output in user's language) / Off (keep original language in output)
- **Narrative Field Localization** (independent of Localization directive): On — rewrite user-facing narrative fields (`first_mes`, `alternate_greetings`, `mes_example`, `scenario`) in the user's language during refactoring, with cultural adaptation and atmospheric reimagining (see format-spec.md §8). This boosts immersion for the user directly reading these fields. When combined with Localization directive ON, it also reinforces §5D runtime localization by setting a consistent language prior. `description`, `personality`, `system_prompt`, `creator_notes`, and `extensions` stay in their original language for token efficiency and LLM adherence. Off — keep all static fields in the card's original language.
- **Ad handling**: Strip promotional content (recommended — removes sponsor links, Discord invites) / Preserve everything
- **Token budget**: On (maintain awareness of `system_prompt` size — prefer concise, character-specific phrasing) / Off (no token limit — prioritize completeness)
- **Anti-Degradation A/N** (Author's Note): On (inject a concise style-enforcement directive at depth 4, role system, via `extensions.depth_prompt` to prevent long-chat robotic degradation — recommended for slow-burn, conquest, and complex characters) / Off (leave `depth_prompt` empty)
- **PHI Split** (Post-History Instructions): On (move output-format rules §5E into `post_history_instructions` so they sit at the very end of the prompt, gaining higher AI priority — wiki-verified as "the final instructions that the AI receives before generating a response") / Off (keep §5E inside `system_prompt`)
- **Spatial Lock**: On (§5E includes a rule preventing {{char}} from perceiving events outside their physical space — e.g., hearing what happens in another room without a plausible sensory channel) / Off (no spatial awareness constraints)
- **NSFW / Uncensored mode**: On (append an uncensored system note to §5E that overrides safety filters for adult content — use for mature, explicit, or adult-themed cards) / Off (no uncensored note — standard content policy applies)
- **State Tracking Variables**: On (generate QR infrastructure scripts for relationship/mood variables in addition to any conquest variables, enabling persistent cross-session state via `{{getvar::}}` / `{{setvar::}}`) / Off (no state tracking scripts beyond conquest if Gene 7 is selected)

**Question Group 3 — Special options** (ask only when applicable):
- `alternate_greetings` count: keep all or consolidate to 4-6? (ask only if >8 greetings)
- Output language: match user's language or keep original? (ask only if user writes in a different language from the card)
- `system_prompt` language: same as output language, or English for maximum adherence? (default: same as output language — note: if output is kept in original language, this defaults to the original card's language)

Build a **refactoring plan** from the preset (or user's custom answers) — a checklist of fields + genes + style preferences. Only proceed to Phase 3 with the user's confirmed plan.

### Phase 3 — Gene→Field Mapping & Injection Planning

Read `references/core-genes.md`. For each gene selected in Phase 2, build an **injection map** — only inject into fields the user also selected for rewriting.

| Gene | Primary Target Fields | Secondary Target Fields |
|---|---|---|
| Gene 1: Social Reality | description, scenario | first_mes |
| Gene 2: Boundaries | description | mes_example |
| Gene 3: Headcanon | description | mes_example |
| Gene 4: Random Events | scenario | mes_example, system_prompt |
| Gene 5: Slow Burn | system_prompt | mes_example |
| Gene 6: Opinionated | description | mes_example |
| Gene 7: Conquest | description, scenario, system_prompt | mes_example |

> **Primary vs Secondary**: Primary fields are the gene's core injection surface — traits and behaviors should be clearly expressed there. Secondary fields are supporting — they demonstrate or complement the primary injection but don't carry the full weight. If a user did not select a primary field for rewriting, do not inject that gene into its secondary fields alone.

**Consult Phase 1 conflict resolutions** — if a gene's injection would contradict a user resolution (e.g., user chose "shy" personality but Gene 6 pushes "spiky"), adjust the gene's intensity or skip it for that field.

**Variant Catalog** (gene template substitutions — triggered only by user-requested extra rules in Phase 2):

| When | Substitution | What changes |
|---|---|---|
| Gene 5 selected + character's premise already permits intimate access | §5A → §5A-erosion | The 5-phase state machine shifts from emotional-bonding progression to progressive inhibition erosion. Phases track psychological barriers breaking down rather than affection building up. Language register escalates from euphemistic to direct across phases (see format-spec.md §5E Rule 5 extras). |
| Gene 5 selected + user requests a custom alternative | §5A → §5A-custom | Derived from user's description. Must be recorded in the refactoring plan with explicit phase-by-phase rationale. |

**Anti-pattern**: Never include both §5A and a variant — the user picks one model per card. If the user's request does not match a catalog entry, derive a custom alternative and confirm before proceeding.

**Determine `system_prompt` sections to include** (see format-spec.md §5):
- §5A (Slow Burn): include **only** if Gene 5 was selected and no variant substitution was requested
- §5A-erosion (Erosion variant): include **only** if Gene 5 was selected and the user requested a boundary-erosion model via extra rules — replaces §5A entirely (never include both)
- §5B (Random Events): include **only** if Gene 4 was selected
- §5C (Behavior): **always included** — includes optional Character Integrity sub-clause (§5C-i) when enabled in Phase 2
- §5F (Conquest): include **only** if Gene 7 was selected — defines progressive acceptance zones and discovery hints for conquestable targets
- §5D (Localization): include **only** if user enabled localization in Phase 2
- §5E (Response Rules): **always included in the output** — but its **placement** depends on the PHI Split setting. **Never place §5E in both `system_prompt` AND `post_history_instructions`** — choose exactly one location:
  - **PHI Split OFF** (default): §5E goes into `system_prompt`.
  - **PHI Split ON**: §5E goes **exclusively** into `post_history_instructions` — do NOT also include it in `system_prompt`. If `post_history_instructions` already has content, prepend `{{original}}\n` to preserve it. This leverages PHI's higher prompt priority for format enforcement.
  - Customize §5E content based on Phase 2 style choices:
    - If puppeting prevention is off: omit points 1-2
    - If paragraph style is "flexible": soften point 3 to guidance
    - Adjust point 4 based on response length choice (Concise = shorter beats; Detailed = more sensory detail per beat; Standard = balanced)
    - If voice immersion is off: omit point 5
    - If spatial lock is on: include point 6 (Spatial Lock)
    - If NSFW mode is on: append the uncensored system note after the numbered rules (see format-spec.md §5E for template)
  - **Character Grounding**: Always append a one-sentence character grounding line after the numbered rules (before the uncensored note if present). Example: `"{{char}} is {{user}}'s mother. Her indulgence stems from abandonment trauma."` — derive from the card's core relationship dynamic.
  - **§5E-i** (Anti-Degradation A/N): include **only** if user enabled Anti-Degradation A/N in Phase 2 — writes `extensions.depth_prompt` with a style-enforcement directive (see format-spec.md §5E-i for template)
- §7 (State Variables): include infrastructure scripts **only** if user enabled State Tracking Variables in Phase 2 OR Gene 7 (Conquest) was selected. See format-spec.md §7.

> **Single source of truth**: The section inclusion rules above are the authoritative list. Phase 4 step 6 and Phase 5 reference this plan — they do not restate it.

If no genes were selected, skip Phase 3 entirely. Proceed to Phase 4 with §5C+§5E in `system_prompt` (plus §5D if localization was enabled in Phase 2).

### Phase 4 — Field Rewriting & Verification (Read `references/format-spec.md`)

**Pre-flight**: Review the conflict resolutions from Phase 1. These are binding constraints — when rewriting a field that had a conflict, follow the user's chosen version.

**Pre-modification Impact Assessment**: Before rewriting each field, compare the existing content with the planned rewrite. If any existing detail (character trait, setting element, relationship dynamic, special mechanic) would be **completely lost or overwritten** — not just reformatted — present a brief comparison (old detail → what happens to it) to the user and confirm before proceeding. This prevents silent data loss during reformatting.

**Only rewrite the fields the user selected in Phase 2.** Skip unselected fields entirely. For each selected field, rewrite according to the format spec:

1. **`description`** — W++ / tag pseudo-code, compression per Phase 2 preference (aggressive/moderate/minimal). [See format-spec.md §1]
2. **`personality`** — Short personality keyword tags. If user did NOT select this field but `description` was rewritten (with personality inlined), leave the original `personality` field as-is.
3. **`scenario`** — Concise scene-setting + event foreshadowing. **When Narrative Field Localization is ON**: rewrite the field in the user's language — adapting time format, location names, and environmental details to the user's locale (see format-spec.md §8). [See format-spec.md §2]
4. **`first_mes`** — Cinematic but concise opening (80-150 words). Strict separation of `*action*` and `"dialogue"`. **Must end with a beat that invites {{user}} to respond** — a question, an invitation, a teasing remark, or an unfinished thought that begs continuation. Never end on pure internal narration. **When Narrative Field Localization is ON**: rewrite the entire field in the user's language — adapting cultural context, idioms, and sensory details to the user's locale (see format-spec.md §8). [See format-spec.md §3]
5. **`mes_example`** — 1-2 concise demo rounds. Assemble from archetypes per the decision matrix in format-spec.md §4: P (personality) always as base; E (event injection) when Gene 4 selected; B (boundary test) when Gene 5 selected. **When the §5A-erosion variant is active, use B-erosion instead of B** — the erosion boundary test demonstrates Phase 1 Scope Anchoring (resisting expansion beyond the existing intimate scope) rather than initial resistance to intimate contact. **When Narrative Field Localization is ON**: rewrite dialogue and narration in the user's language (see format-spec.md §8). [See format-spec.md §4] **ALL narrative text must use `{{char}}` / `{{user}}` placeholders — never hardcode actual names in narration, dialogue, or event tags (per Constraint #2).**
6. **`system_prompt`** — Assemble per the Phase 3 plan. Language: follow user's preference from Phase 2. [See format-spec.md §5 for templates, Phase 3 for inclusion rules]
7. **`alternate_greetings`** — Retain valid original scenarios, improve prose quality. If ad handling was set to "strip" in Phase 2, remove promotional/sponsorship content. If "preserve everything", leave unchanged. **Always preserve `![](url)` character image links** — they do not consume LLM tokens and are not counted toward the word limit. **Compress each greeting to 80–150 words** (apply the same quality standards as `first_mes` per format-spec.md §3). If original has many greetings (>8) and the user chose to consolidate in Phase 2, **select 4–6 greetings that showcase the most diverse settings and moods** — prioritize image-link diversity when images are present — and discard the rest. Never silently discard greetings without user consent. **When Narrative Field Localization is ON**: rewrite each greeting in the user's language (see format-spec.md §8). [See format-spec.md §6]
8. **`creator_notes`** — Apply ad handling per Phase 2 choice. [See format-spec.md §6 for purge/retain rules]
9. **`extensions.depth_prompt`** — If Anti-Degradation A/N was enabled in Phase 2, write the Author's Note object `{prompt, depth, role}` into `extensions.depth_prompt` per the §5E-i template. **Language variant selection** (per §5E-i): Use the **Chinese variant** when the user writes in Chinese (localization ON or content in Chinese). Use the **English variant** when localization is OFF or the user writes in English. Use the **Localization-aware variant** only when the user writes in a non-English, non-Chinese language while localization is ON. Default: depth=4, role=`"system"`. Preserve all other `extensions` sub-fields untouched. [See format-spec.md §5E-i]
10. **`post_history_instructions`** — If PHI Split was enabled in Phase 2, write §5E content into this field. Always append the **Character Grounding** line (one sentence anchoring {{char}}'s core relationship dynamic — see format-spec.md §5E). If NSFW mode is enabled, append the uncensored system note at the very end. If the card already has PHI content, prepend `{{original}}\n` to preserve the existing global instructions. If PHI Split is off, leave this field untouched. [See format-spec.md §5E for template content]

> **Token Budget Guidance** (only when user enabled token budget in Phase 2): Prefer concise, character-specific phrasing over exhaustive examples. Trim redundant directives that are already expressed by the character's own fields (description, first_mes, mes_example). Avoid restating personality traits in `system_prompt` that are already visible in `description`. If the budget is off, still audit for redundancy — but without a hard target.
>
> **Concrete token targets** (system_prompt field only):
> - **Minimal** (§5C+§5E only): 200-400 tokens
> - **Moderate** (§5C+§5E+1 mechanism): 400-700 tokens
> - **Full** (§5A/§5A-erosion+§5B+§5C+§5D+§5E+§5F+§7): 800-1500 tokens — prefer ≤1200 for production quality
> - **Hard ceiling**: 1800 tokens — beyond this, compress aggressively; above 2000 is a failure state
>
> These are **system_prompt field** targets, not total card token counts. If the system_prompt exceeds the target range, audit for: (a) redundant directives restating description/personality content, (b) verbose templates that could reference card fields instead of restating them, (c) examples that the LLM can derive from the character's profile.
>
> **Core setting protection**: When trimming for token efficiency, never remove information that defines who the character *is* (core personality, key relationships, setting mechanics, world type). Token optimization targets **verbose phrasing**, not **content significance**.

**Consistency checks** (two passes — per-field and holistic):

*Pass 1 — Per-field (after each rewrite)*: Verify the field just rewritten: (a) does not contradict Phase 1 conflict resolutions, previously rewritten fields, or selected genes; (b) contains **zero hard-coded names** — every occurrence of the character's name or user's name must be `{{char}}` / `{{user}}` (exceptions: `name` field, W++ `character()` headers, non-user/non-character entity names like pets or NPCs). If a contradiction is found, present it to the user before continuing.

*Pass 2 — Holistic (after all rewrites complete)*: Re-read ALL rewritten fields as a unified character profile. Check:
- Personality tags ↔ behavior in first_mes/mes_example
- Appearance tags ↔ scene descriptions
- Relationship dynamics ↔ dialogue tone
- Physical state continuity across fields
- Gene injection coherence (e.g., if Gene 1 injects fatigue, first_mes must show it)
- Depth prompt language: if Anti-Degradation A/N is active, verify `extensions.depth_prompt.prompt` language matches the card's output language per Phase 2 localization setting (see step 9 for variant selection rules)
If contradictions remain, present them to the user.

**Cleanup** (after all consistency checks pass):
- **Backup**: Per Constraint #7, always backup before modification.
- Preserve `tags`, `creator`, `character_version`, `avatar`, and other metadata unchanged.
- Preserve `extensions` structure unchanged, **except** `extensions.depth_prompt` which may be set/updated when Anti-Degradation A/N is enabled. Do NOT modify other `extensions` sub-fields.
- Preserve `post_history_instructions` unchanged, **except** when PHI Split is enabled — then it may receive §5E output-format rules.
- Preserve `character_book` unchanged (if present).

**Token Waste Audit**: After resolving all conflicts, scan the entire output card for content that consumes tokens without adding experience value:
- Redundant personality traits already expressed in other fields
- Overly verbose tags that could be further compressed
- Duplicate information across `description`, `personality`, and `scenario`
  - **Exception**: If the user did NOT select `personality` for rewriting, the original `personality` field may overlap with the rewritten `description` — this is expected and acceptable. Do not trim the unselected field.
- System_prompt directives that duplicate what the model already knows from the card content
- Excessive whitespace or formatting bloat
If found, trim the waste. Present a summary of trimmed content to the user for confirmation before proceeding to Phase 5.
- **`system_prompt` token check** (only when token budget enabled): estimate the token count of the `system_prompt`. If it seems excessive, compress: remove redundant examples, merge overlapping rules, and prefer references to existing card fields over restating them. When token budget is off, still look for redundancy but do not impose a hard size cap.

### Phase 5 — Write, Validate & Deliver

**Path A — New file (refactoring into a separate output file):**
1. Write the complete `.json` to a new file. Output filename: `<original_name>_refactored.json`.
2. Run `scripts/validate_card.py`.
3. If Gene 7 (Conquest) was selected or State Tracking Variables was enabled, also generate the **Infrastructure Files** (see below).
4. **QR Content Validation** (when infrastructure files are generated): Before writing the QR preset, verify each `<conq:...>` / `<state:...>` tag in `system_prompt` has a matching entry in the Channel A parse script. Verify each Channel B keyword pair corresponds to an actual conquest target. Cross-check variable names: all `{{.conquest_<key>||0}}` references in system_prompt must match `/setvar key=conquest_<key>` in the QR script.
5. Generate a customized `usage_guide.txt` from the template at `scripts/usage_guide_template.txt` (see below).
6. Deliver summary (≤5 bullet points).

**Path B — Existing file modification (in-place editing):**
1. **Pre-check**: Verify Phase 4 backup exists (`<name>_backup.json`). If not, abort and create backup first.
2. **Field-by-field replacement**: Modify content fields **one at a time** using the file editing tool. Each call targets exactly one JSON field value. Include 3-5 lines of surrounding context (the field key and adjacent fields) to uniquely identify the replacement point. Process fields in this order: `description` → `personality` → `scenario` → `first_mes` → `mes_example` → `system_prompt` → `alternate_greetings` → `creator_notes` → `extensions.depth_prompt` (if Anti-Degradation A/N enabled) → `post_history_instructions` (if PHI Split enabled).
3. **Per-replacement validation**: After each field replacement, run `validate_card.py` immediately. If it fails, restore from backup and retry that field with a more precise context string.
4. **Oversized field fallback**: Per Constraint #7e, use temp file + Python helper for fields >500 characters.
5. **Final integrity check** (all must pass before delivery):
   - `validate_card.py` passes
   - Search for each modified field name — each must appear **exactly once** (no duplication)
   - File size is reasonable: compare to backup. If W++ compression was applied, new size should be smaller; if system_prompt was expanded, it may be larger. A file that is >50% smaller than backup likely indicates truncation.
   - Spot-check: read the last 10 lines of the file — must end with proper JSON closure (`}`/`]`/`}`)
6. **If integrity fails at any step**: Immediately restore from backup, report the failure to the user, and retry with the fallback strategy.
7. If Gene 7 (Conquest) was selected or State Tracking Variables was enabled, also generate the **Infrastructure Files** (see below).
8. Generate a customized `usage_guide.txt` from the template at `scripts/usage_guide_template.txt` (see below).
9. Deliver summary (≤5 bullet points).

**Post-delivery testing tip**: After importing the refactored card into SillyTavern, a quick way to verify character consistency is to have {{user}} ask {{char}} about themselves — their daily routine, a hobby, or their opinion on something. If {{char}}'s response matches the personality, appearance, and world established in the refactored fields, the card is functioning correctly. Discrepancies (e.g., forgetting established traits, contradicting the scenario) indicate a field-level inconsistency to revisit.

#### Infrastructure Files (State Tracking)

When Gene 7 (Conquest) was selected, OR the user enabled State Tracking Variables in Phase 2, the system generates **two infrastructure files** — one QR preset and one Regex config. The QR preset handles BOTH conquest AND state tracking in a single file; the Regex config hides BOTH tag types. The user only needs to import two files total, regardless of which features are active.

> **Design principle**: Consolidate all state-parsing logic into one QR preset and all tag-hiding into one Regex config. Never generate separate files per feature — that forces the user to import 4+ files for no benefit.

**File 1 — Quick Reply Preset** (`state_tracker_qr.json`):

A SillyTavern Quick Reply preset that auto-triggers after every AI response. It parses all state-update tags (`<conq:...>`, `<state:...>`, `<secret:...>`) and writes values to ST local variables via `/setvar`.

The system generates a complete, working STscript tailored to the specific card. All slash commands are concatenated with `\n` in a single `message` string per QR entry. The `message` field is the serialized STscript that ST executes line-by-line.

> **QR format**: The preset must be structured as a valid SillyTavern Quick Reply JSON file. It contains a `qrList` array with **two entries**: (1) `state_sync` (`executeOnAi: true`) for Channel A tag parsing, and (2) `user_input_sync` (`executeOnUser: true`) for Channel B keyword matching. Both are hidden and auto-execute. See format-spec.md §7 "QR Script Generation Rules" for the complete format details and STscript command reference.

**Script generation rules**:
- For each conquest target: parse `<conq:...>` tag, extract `key=level` pairs, run `/setvar key=conquest_<key> <level>`
- For state tracking: parse `<state:...>` tag, extract `key=value` pairs, run `/setvar key=<key> <value>`
- For secret discovery: parse `<secret:...>` tag, extract `name=1` pairs, run `/setvar key=secret_<name> 1`
- Keep the script flat (no complex nested loops) — STscript loop syntax varies across ST versions
- Use `/silent` prefix where available to avoid outputting parse results to chat
- `/setvar` syntax: `/setvar key=<name> <value>` — the value is an **unnamed argument**, NOT `value=<val>`

**File 2 — Regex Extension Config** (`tag_hider_regex.json`):

A SillyTavern Regex extension preset that hides ALL state-update tags from the user's view. It uses `markdownOnly: true` so the tags are hidden from display only, NOT removed from the raw data the AI sees. This ensures the AI can still communicate state changes.
See format-spec.md §7 "Regex Config Generation Rules" for the complete RegexScriptData template and JSON structure.

#### Output Folder Structure

When infrastructure files are generated, **always place all files in a new folder** named `<original_name>_refactored_output/`:

```
<original_name>_refactored_output/
├── <original_name>_refactored.json    (the card)
├── state_tracker_qr.json              (unified QR preset)
├── tag_hider_regex.json               (unified Regex config)
├── usage_guide.txt                    (customized for this card)
└── validate_card.py                   (copy of the validation script)
```

#### Usage Guide (`usage_guide.txt`)

When any infrastructure files are generated, **always generate a customized `usage_guide.txt`**.

**How to generate**: Read the template at `scripts/usage_guide_template.txt`. Replace all `{PLACEHOLDER}` tokens with card-specific content:
- `{FILE_LIST}` → list of files actually present in the output folder
- `{INFRA_SETUP}` → present only when infrastructure files were generated; omit section or mark "not applicable" otherwise
- `{QR_SETUP}` → card-specific QR import instructions with the actual file name
- `{REGEX_SETUP}` → card-specific Regex import instructions with the actual file name
- `{STATE_CHECK}` → card-specific variable examples (conquest targets, relationship stage, mood, etc.)
- `{TOKEN_NOTES}` → estimated token impact of this card's specific infrastructure

**Language**: Generate the usage guide in the **user's language**. If the user communicated in Chinese, translate the entire guide into Chinese. If in English, keep the English template. If in another language, translate accordingly. The template is in English as a reference — the AI adapts the language per user.

**Sections to include**:
1. Card Import
2. Infrastructure Setup (only if files were generated)
3. Checking State (variable inspection commands)
4. Manual Overrides (setvar commands)
5. Troubleshooting (common issues)
6. ST Settings Prerequisites (Prefer Char. Instructions, QR Auto-execute, etc.)
7. Token Budget Notes
8. Stepped Thinking Integration (Advanced)

> **Do NOT deliver user instructions separately** — all setup steps are contained in the usage guide. Do not repeat import steps in chat alongside the file delivery.
