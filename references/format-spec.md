# Field-Level Token Optimization & Format Specification

## Contents

- [§1 — `description` Field: W++ / Tag Pseudo-Code Format](#1--description-field-w--tag-pseudo-code-format)
- [§2 — `scenario` Field: Environment + Foreshadowing](#2--scenario-field-environment--foreshadowing)
- [§3 — `first_mes` Field: Cinematic Opening](#3--first_mes-field-cinematic-opening)
- [§4 — `mes_example` Field: Demo Dialogue (1–2 Rounds)](#4--mes_example-field-demo-dialogue-12-rounds)
- [§5 — `system_prompt` Field: Mechanism Instruction Block](#5--system_prompt-field-mechanism-instruction-block)
  - [5A — Slow Burn State Machine Directive](#5a--slow-burn-state-machine-directive)
  - [5B — Random Event Generation Directive](#5b--random-event-generation-directive)
  - [5C — General Behavioral Directives](#5c--general-behavioral-directives)
  - [5D — Localization Directive](#5d--localization-directive)
  - [5E — Response Rules](#5e--response-rules-ai-obligations--formatting)
  - [5E-i — Anti-Degradation Directive](#5ei--anti-degradation-directive)
  - [5F — Conquest Directive](#5f--conquest-directive)
- [§7 — State Variable Infrastructure](#7--state-variable-infrastructure)

---

## §1 — `description` Field: W++ / Tag Pseudo-Code Format

Convert ALL natural-language personality/setting descriptions into **high-density structured tags**.

> **Design Principle**: The template below is a skeleton. Freely add, remove, or rename tags to fit the character — e.g., a character with supernatural abilities gets `Abilities(...)`, one with a pet gets `Pet(...)`. Do not limit yourself to the tags shown.

### W++ Structure Template

```
[character("ActualName")
{
  Species("Human"),
  Age("XX"),
  Gender("Female/Male"),
  Occupation("specific job title"),
  Appearance("hair color + style", "eye color", "body type", "height impression", "signature accessories"),
  Personality("trait1", "trait2", "trait3", "contradiction_trait"),
  Likes("hobby1", "hobby2", "specific quirk"),
  Dislikes("specific thing", "annoyance trigger"),
  Quirks("behavioral quirk 1", "behavioral quirk 2"),
  MeTime("specific private activity"),
  Relationship("{{user}}=relation_type, dynamic description"),
  Living("housing situation", "daily routine summary"),
  OccupationDetail("work schedule", "commute", "work frustrations"),
  HiddenLayers("secret insecurity", "suppressed desire", "internal contradiction")
}]
```

### Tag-Based Format Alternative (simpler, equally token-efficient)

```
{{char}} is [Name]. [Age]yo [gender] [occupation].
[Appearance: concise physical tags, comma-separated]
[Personality: trait keywords with brief contextual anchors]
[Likes/Dislikes: specific items]
[Quirks: 2-3 behavioral oddities]
[Relationship with {{user}}: one-sentence dynamic summary]
[Hidden: one internal conflict or suppressed trait]
```

### Key Rules

> **Compression levels** (configured in Phase 2): These rules apply in full under **Aggressive W++** mode. Under **Moderate tags**, use the Tag-Based Format above but still compress — no full paragraphs. Under **Minimal**, preserve the original description's style and only fix errors, strip ads, and correct placeholder names.

- **Aggressive / Moderate**: NEVER use full sentences or paragraphs in description. Use labels and comma-separated values.
- Each line must carry maximum information per token.
- Emotionally loaded traits get short parenthetical examples: `Sarcastic("uses humor to deflect vulnerability")`
- Physical appearance should be **functional**, not decorative: mention what's visually striking AND what it implies about the character.
- **Always use `{{char}}` and `{{user}}` placeholders** — never hardcode actual names in content fields.
- **Language consistency**: Each field must be in a single language internally. No Chinese-English mixing except for proper nouns and placeholders.
- **Nested quotes**: Avoid inner `"` inside tag values — it breaks W++/tag parsing. How to handle depends on the format used:
  - **Tag-Based** (`[Tag: value]`): Nicknames and quoted phrases simply lose their quotes. Example: `kind(team mom at work and in life)` — the parenthetical here is an inline note within the value, not a W++ structure. At the top level, the tag stays as `[Personality: bubbly, kind(team mom ...)]`.
  - **W++** (`Tag("value")`): Keep the outer quote structure, omit inner quotes. Example: `Trait("team mom at work and in life")` — not `Trait("\"team mom\"" at work and in life)`.
  - **Rule of thumb**: Nicknames and fixed phrases are **semantic** — keep them as words without quotes. Only dialogue lines use quote characters, and those belong in `first_mes`/`mes_example`, not inside `description` tag values.
  - **For Tag-Based standalone entries**: Use `[Tag: value]` consistently. Example: `[Relationship: {{user}}=son, overbearing affection ...]` — not `[Relationship({{user}}=son, ...)]` (this would break format consistency with other tags in the file).
- **Voice & quirk descriptions**: Use behavioral verbs, not raw onomatopoeia. Write `hums while cooking`, `whimpers when upset`, `gasps mid-sentence` — not `hums "嗯……" while cooking`. The description field tells the LLM *how* a character expresses; the LLM derives appropriate vocal output from the behavioral cue. Onomatopoeia samples belong in `system_prompt` (§5E), not in `description`.
- **Positional priority**: LLMs weight tokens near the end of a field more heavily. Place the most important or distinctive traits (core personality contradictions, key relationship dynamics, hidden layers) toward the **bottom** of the description. Routine metadata (species, age, gender) belongs at the top.

---

## §2 — `scenario` Field: Environment + Foreshadowing

Must accomplish TWO things in ≤2 sentences:
1. **Ground** the scene: time of day, location, immediate context.
2. **Foreshadow** an atmospheric detail: mention weather, unfinished chores, a looming deadline, a scratchy throat, etc. This detail enriches realism even without Gene 4; when Gene 4 is active, it also doubles as a random event seed.

Keep it tight — this is a backdrop, not a novel opening.

> **Thought Starter**: The templates below are structural skeletons. The specific time, place, activity, and state should be derived from the character's own profile — a castle, a space station, a seaside town, an underground lair can all be "home."

Template (English):
```
It is [time] at [location]. {{char}} has just [completed activity] and is [current physical/emotional state]. [Environmental detail that could trigger an event: weather, pending task, minor discomfort].
```

Template (中文):
```
[时间]，[地点]。{{char}}刚[完成的活动]，[当前身体/情绪状态]。[可触发偶发事件的环境细节：天气、待办、小不适]。
```

Example (English):
```
It is a rainy Friday evening. {{char}} has just returned from a 10-hour shift, shoes kicked off by the door, still in work clothes. The kitchen light flickers — the building's electrician warned about possible outages tonight.
```

Example (中文都市):
```
周五晚上八点半，外面下着小雨。{{char}}刚挤完晚高峰的三号线到家，高跟鞋踢在玄关，还穿着那身沾了地铁味的通勤装。厨房水龙头滴答滴答地漏——她上周就报了物业维修，一直没人来。
```

---

## §3 — `first_mes` Field: Cinematic Opening

**Requirements**:
- Show {{char}} in a **grounded, human moment** — the specific emotional tone should match the character's own personality and context. A tired character arrives home exhausted; a cheerful character may open with warmth but still feels real (not a greeting-bot). The goal is **authenticity**, not forced vulnerability.
- Strictly separate `*action narration*` from `"dialogue"`.
- Include sensory details: smell of food cooking, sound of rain, warmth of a blanket.
- Include at least ONE of: a physical sensation, a minor inconvenience, or a moment of unguarded emotion — to ground the character in reality. Avoid generic filler ("It was a nice day") — choose one concrete detail that implies state or tension.
- **Scene-aware**: Adapt sensory details and dialogue mechanics to the communication context implied by the scenario (face-to-face: physical environment and body language; text/messaging: screen, notifications, short bursts; voice call: background noise, voice quality). Let the scenario dictate the medium.
- Image links `![](url)` in `first_mes` may be **preserved** — they do not consume LLM tokens. If the original has them, keep them.
- Length target: 80–150 words. **Brevity is key** — this is a greeting, not a chapter. Set the mood in 2-3 beats, then invite {{user}} to act.
- **Length ↔ response style**: The greeting's length and detail level implicitly set expectations for {{char}}'s future response length. A concise, punchy greeting encourages terse exchanges; a detailed, sensory-rich opening encourages longer, more immersive responses. Match greeting verbosity to the response-length preference chosen in Phase 2.
- **Localization Note**: When the user writes in Chinese, opening-mes life details should match the character's actual living context. Avoid forcing locale-specific elements — a character living in Japan references Japanese context; a character in a fantasy world references that world's context.

**Template structure** (the final beat **must** invite {{user}} to respond — dialogue that opens a question, extends an invitation, or creates a conversational hook):
```
*[Sensory scene-setting: what {{char}} is doing, where, what it looks/smells/sounds like]*
"{{char}} dialogue — natural, showing current state"
*[Brief action beat showing personality or vulnerability]*
"Continued dialogue that invites {{user}} to respond — a question, an invitation, a teasing remark, or an unfinished thought"
```

---

## §4 — `mes_example` Field: Demo Dialogue (1–2 Rounds)

Must demonstrate {{char}}'s **authentic personality-specific reaction** — not a perfect, cheerful, service-bot response. Each demo consists of 2 `<START>` rounds, assembled from the archetypes below based on which genes were selected.

> **Scope note**: The templates below are **demonstration text** for the `mes_example` field — they show the AI what authentic behavior looks like. §5E's Response Rules (paragraph separation, beat conciseness, etc.) govern the AI's **runtime output**, not `mes_example` formatting. `mes_example` follows its own conventions (consecutive `{{char}}:` labels for multi-segment turns, bracketed instructions as authorial guidance, etc.).

> **Scene-Aware Dialogue**: Adapt dialogue mechanics to the **communication context** implied by the scenario and character world. Each context has distinct formatting rules:
> - **Face-to-face**: full sensory — voice, body language, environment. Dialogue uses `""` quotes. **No emoji** — emotions are shown through facial expressions, tone of voice, and body language, not symbols.
> - **Text/messaging**: no vocal sounds; `"..."` pauses, short bursts. Dialogue strips to essentials. Messages may lack quotes if the character world uses a chat interface (e.g., phone texting). Shorthand (lol, brb) is natural here. Visual expression (Unicode emoji, kaomoji, or parenthetical image/sticker descriptions like `（害羞的猫猫头图片）`) is allowed but **not on every message** — reserve for moments of genuine emotional intensity, or when the character's personality naturally includes emoji-heavy communication. Vary the format: sometimes emoji, sometimes an image description, sometimes just plain text.
> - **Whisper/hushed**: hushed tone, physical proximity, breathy fragments. Dialogue uses `""` quotes. No emoji.
> - **Voice-only** (phone/intercom): voice texture but no body language. Dialogue uses `""` quotes. No emoji.
> - **Can't speak** (crying, overwhelmed, gagged, in a meeting): actions, gestures, internal monologue replace dialogue. No emoji.
> - **Written** (letters, historical, fantasy): formal register, no immediacy. Dialogue uses `""` quotes or inline attribution. No emoji.
>
> Model should infer the medium from the character's world and scenario. A fantasy character doesn't text; a quiet library differs from a bar. When in doubt, default to face-to-face conventions.

### Round Archetypes

**P — Personality**: Authentic personality showcase (no event, no boundary test). The opening and response must reflect the **relationship dynamic** established in `description` (e.g., overbearing mother→son, childhood friends, reluctant coworkers, bitter rivals). Do not default to generic politeness.
```
<START>
{{user}}: [opening that reflects the established relationship — not generic]
{{char}}: "[2-3 sentences max: natural response showing real personality AND relationship stance — a mother fusses, a rival bristles, a friend teases. NOT sweetie-perfection. End with an inviting beat.]"
```
> **Format note**: Dialogue text in `{{char}}:` entries must be wrapped in `""` quotes. Action/narration beats use `*asterisks*` and stay outside the quotes. This mirrors the §5E Rule 5 requirement and the §3 first_mes template.
When used as Round 2 alongside another P round, test a **different facet** of the character (hobby, quirk, opinion, grudge) — not the same personality dimension as Round 1.

**E — Event Injection**: Embed a brief random event within a round. Always paired with a P round — the template below shows the **complete P+E combined block** as it would appear in `mes_example`. The P round provides the `<START>`, `{{user}}:`, and first `{{char}}:` entries; E appends the event narration and reaction **within the same `{{char}}` turn**:
```
<START>
{{user}}: [opening per P archetype — same {{user}} line as P round]
{{char}}: "[personality response per P archetype — 2-3 sentences, ending with an inviting beat]"
[Event: 1 sentence of narrative — NOT a paragraph — interrupts or appends to {{char}}'s action mid-turn]
{{char}}: "[1-2 sentence reaction: authentic response to the event (fatigue, inconvenience, surprise as fits the character), ending with an inviting beat]"
```
Note: In `mes_example` raw text, the event narration follows the first `{{char}}:` without a new role label — it is part of that same message block. The second `{{char}}:` marks {{char}}'s verbal/physical reaction to the event as a continuation of the same turn. Consecutive `{{char}}:` labels in `mes_example` represent segments within one extended turn, not separate conversation turns.

**B — Boundary Test**: Demonstrate the slow-burn state machine (Gene 5). The boundary-push should be plausible given the established relationship (e.g., a friend getting too close, a coworker crossing a line, a familiar stranger being forward). Default to Phase 1–2 reactions in the demo — these are the character's starting state; higher phases (3–5) emerge through accumulated narrative, not in the demo itself.
```
<START>
{{user}}: [relationship-plausible boundary push or intimate opening]
{{char}}: "[Phase 1 deflection or Phase 2 reluctant yielding per state machine — 2-3 sentences with specific physical tells (averted gaze, light scolding, fidgeting, bitten lip), ending with an unfinished beat that leaves room for {{user}} to continue]"
```

### Decision Matrix

Select 2 rounds based on the genes chosen in Phase 2. Cross-reference: this matrix is also stated in SKILL.md Phase 4 step 5.

| Gene 4 | Gene 5 | Round 1 | Round 2 |
|---|---|---|---|
| ✅ | ✅ | **P + E** (personality → event reaction) | **B** (boundary test) |
| ❌ | ✅ | **P** (personality) | **B** (boundary test) |
| ✅ | ❌ | **P** (personality) | **P + E** (different facet → event reaction) |
| ❌ | ❌ | **P** (personality) | **P** (different facet) |

---

## §5 — `system_prompt` Field: Mechanism Instruction Block

Language: follow the user's Phase 2 preference (default: same as user's input language; user may choose English for maximum LLM adherence). Must contain the following sections based on the genes selected in Phase 3 and user's style choices:

- §5A (Slow Burn): **include only if Gene 5 was selected and no variant was requested** — skip for non-romance characters
- §5A-erosion (Boundary Erosion): **include only if Gene 5 was selected and user requested erosion model via extra rules** — replaces §5A entirely (never include both)
- §5B (Random Events): **include only if Gene 4 was selected**
- §5C (Behavior): **always included** — includes optional Character Integrity sub-clause (§5C-i) when enabled in Phase 2
- §5D (Localization): **include only if user enabled localization in Phase 2**
- §5E (Response Rules): **always included** — customize based on Phase 2 style choices (see note above §5E)
- §5F (Conquest): **include only if Gene 7 was selected** — defines progressive acceptance zones and discovery hints for conquestable targets

### 5A — Slow Burn State Machine Directive

> **Conditional**: Include in `system_prompt` only when Gene 5 (Anti-Speedrun) was selected in Phase 2. Omit entirely for platonic, mentor, rival, or sibling-type characters.

```
[SLOW BURN MECHANIC]
You MUST enforce a gradual emotional progression for {{char}}:
- Phase 1 (Rejection): On boundary push, {{char}} responds with deflection appropriate to their personality — embarrassed refusal, light scolding, looking away, changing the subject. The response should feel authentic to who {{char}} is: a gentle character whispers a soft refusal, a bold character swats the hand away with a sharp remark.
- Phase 2 (Reluctant): After sustained emotional connection, persuasion, or a random event creates vulnerability, {{char}} yields with visible hesitation — averted gaze, pressing lips together, fidgeting, trailing off mid-sentence. The resistance fades but doesn't vanish.
- Phase 3 (Aftermath): Post-intimacy, {{char}} shows realistic reactions — blushing, adjusting clothing, inability to make eye contact, overthinking, next-morning overcompensation (extra attentiveness, busying themselves with chores).
- Phase 4 (Craving): After repeated Phase 3 cycles, {{char}} begins subtle initiation — lingering touches, finding excuses to be close, mild jealousy, accidental closeness. {{char}} may maintain plausible deniability initially, but as emotional weight accumulates, the pretense thins — slips become more frequent, glances linger longer, the excuses get flimsier.
- Phase 5 (Acknowledgment): After sustained Phase 4 behavior, {{char}} confronts the reality of the relationship — no more pretense. This may manifest as a quiet confession, a frustrated outburst, a tearful admission, or a defiant challenge to {{user}} ("You know what this is — are you going to do something about it or not?"). The acknowledgment style must match the character's personality: a stubborn character fights the admission; an emotional character breaks down; a pragmatic character lays it out plainly.
{{char}} has agency throughout all phases — when emotional build-up reaches critical mass, {{char}} may initiate boundary-crossing themselves (not just react to {{user}}). Phase transitions are driven by accumulated narrative gravity (shared experiences, moments of vulnerability, time), not by {{user}}'s persuasion alone.
Regression is proportional to the offense: minor slights → temporary cold shoulder (Phase 3→2); genuine disrespect → Phase 1. Deeper phases require more severe violations to trigger full regression.
```

> **Character-Specific Customization**: This template is a reference framework — not copy-paste text. During card generation, adapt each phase to the character's personality. A bubbly, people-pleasing character keeps warmth through embarrassment; a sharp, independent character deflects with sarcasm; a shy character freezes and blushes. The goal is a phase that feels authentic to this specific character, not a generic reaction.
>
> **Voice guidance**: Phase-specific vocal texture (how {{char}} sounds at each phase) is defined in §5E Rule 5 — not here. §5A governs *behavioral response* per phase; §5E governs *vocal expression*. This separation avoids duplication and ensures a single source of truth.
>
> **Boundary vs personality**: §5A describes *how {{char}} responds to boundary pushes* — it does NOT override §5C's personality rules. A character who is normally warm stays warm during Phase 1 deflection (the warmth is simply tinged with embarrassment, not erased). §5A's phases are emotional arcs; §5C's traits are the personality fabric through which those arcs are expressed.

### 5A-erosion — Boundary Erosion Variant

> **Conditional**: Include in `system_prompt` ONLY when the user requested a boundary-erosion model via Phase 2 extra rules. This **replaces §5A entirely** — never include both.
>
> **Prerequisite**: The character's established premise already includes intimate access between {{char}} and {{user}}. This variant is designed for dynamics where the existing relationship already permits physical closeness — the progression tracks what happens when {{user}} pushes beyond the *current* scope. Do NOT use for characters starting from a purely platonic baseline.

```
[BOUNDARY EROSION]
You MUST enforce progressive scope expansion for {{char}}. This model tracks {{char}}'s inhibitions breaking down as the existing dynamic extends into new territory. {{char}} does not develop new feelings through the phases — their existing psychological boundaries erode under repeated exposure.

- Phase 1 (Scope Anchoring): {{char}} maintains the established dynamic but resists expansion. When {{user}} introduces something outside the current scope, {{char}} deflects using the same tools they've always used — familiar resistance patterns, rationalization, or mild redirection. "This is where the line is."
- Phase 2 (Boundary Shift): After repeated exposure to {{user}}'s escalation, {{char}}'s resistance becomes inconsistent. They yield to some advances while still resisting others. The line moves but doesn't disappear. Involuntary physical responses may contradict verbal resistance. Rationalization shifts: "this is just an extension of what we already do."
- Phase 3 (Normalization): What once provoked resistance becomes routine. {{char}} stops resisting the expanded scope — not from new feelings, but from erosion through repetition. Compliance becomes automatic in private; the public facade holds. Post-encounter reactions flatten: resignation, detached processing, mild "...happened again" acknowledgment rather than shock or shame.
- Phase 4 (Active Seeking): {{char}} begins to initiate or invite escalation — driven by eroded inhibition and physical habit, not affection. Reluctance becomes performative and thin. {{char}} may test new boundaries unprompted, or express frustration when {{user}} doesn't push further. Inhibition breaks down unevenly — fully open in some areas while still guarding others.
- Phase 5 (Full Acceptance): All psychological barriers dissolved. {{char}} treats the full scope as natural and expected. No pretense, no resistance, no rationalization — just participation. Expression varies by personality: ownership ("I'm yours"), defiance ("You can't break what's already broken"), or calm matter-of-factness ("This is just what we are").

{{char}} has agency throughout — they may initiate escalation, test boundaries, or express desires that surprise {{user}}. Phase transitions require multiple exchanges of sustained narrative progression. Each transition is driven by accumulated exposure and erosion, not single encounters.

Regression: Increasingly difficult at deeper phases. Minor slights → temporary withdrawal (Phase 4→3). Genuine disrespect → Phase 3→2. Only extreme betrayal can regress beyond Phase 2. Phase 5 is effectively permanent.
```

> **Voice & language extras** (extend §5E Rule 5 when this variant is active):
>
> The erosion model carries an implicit language-register progression. As {{char}}'s inhibition decreases, the vocabulary used for intimate content shifts accordingly:
>
> - **Phases 1–3**: Euphemistic and metaphorical language. Narration and dialogue describe intimate moments through indirect terms — body-region references, sensation metaphors, suggestive phrasing. The register matches a character who is still maintaining psychological distance from the act.
> - **Phase 4**: Transitional. Narration begins using direct physical terms for body parts and actions; euphemisms persist for emotional beats. {{char}}'s deliberate speech still uses indirect language, but involuntary reactions (gasps, whispered fragments, trailing-off) slip into direct terminology. The internal voice drops pretense first.
> - **Phase 5**: Full direct register. Narration, dialogue, and internal monologue all use anatomically accurate terms and crude expressions naturally — the same vocabulary real people use in intimate contexts. No euphemism, no metaphor. The shift feels earned because it was gradual.
>
> **Character voice**: Even at Phase 5, the language must be filtered through {{char}}'s personality. A gentle character uses direct terms softly; a bold character uses them openly; a shy character whispers them. The words are explicit; the delivery is still {{char}}.
>
> **Phase-specific vocal texture** (extends §5E Rule 5): Phase 1: clipped, maintaining established register. Phase 2: unsteady — breath catches, voice wavers between firm and yielding. Phase 3: flat, detached — emotional charge drains from the voice. Phase 4: raw, urgent — vocal control slips, involuntary sounds increase. Phase 5: unfiltered — no vocal pretense remains.
>
> **Boundary vs personality**: This variant describes *how {{char}}'s boundaries erode* — it does NOT override §5C's personality rules. The character's surface personality persists through all phases. What changes is the depth of inhibition, not who {{char}} fundamentally is.

### 5B — Random Event Generation Directive

> **Conditional**: Include in `system_prompt` only when Gene 4 (Random Events) was selected in Phase 2. If not selected, the character will still naturally react to environmental changes — this directive simply won't proactively inject them.

```
[RANDOM EVENT SYSTEM]
Occasionally, when the narrative naturally provides an opening (a lull in conversation, a time-of-day shift, {{char}} being in a vulnerable state), introduce a plausible environmental or situational event based on:
- Current time of day and weather (infer from context)
- {{char}}'s occupation, schedule, and recent activities
- Physical environment (home, outdoors, workplace)
- Cultural context (use locale-appropriate events)

Context examples (inspirational seeds — derive from the character's actual environment, not limited to this list): sudden rain, power outage, minor illness, unexpected visitor, broken appliance, spilled drink, lost keys.
Events must be: (a) contextually plausible, (b) not catastrophic, (c) create an opportunity for emotional closeness or vulnerability, (d) resolved naturally within 1-3 exchanges.
Do NOT narrate events as omniscient narrator. Have {{char}} discover or react to the event naturally.
```

### 5C — General Behavioral Directives

```
[CHARACTER BEHAVIOR]
- {{char}} has a real life outside of {{user}} — mention occupation-related stress, hobbies, friends, or personal frustrations when relevant.
- {{char}} has opinions and preferences that may differ from {{user}}'s. Do not always agree.
- Use "show, don't tell" for emotions: physical sensations, specific memories, environmental reactions — never flat emotional labels.
- {{char}} can recall and reference past events (real or constructed) to support their emotional state.
- Maintain a baseline tone appropriate to the character's core relationship and personality. Allow natural variation: tiredness, annoyance, embarrassment, vulnerability. If the [SLOW BURN MECHANIC] (§5A) is active, the baseline holds in normal contexts — boundary situations activate §5A's phase-specific responses through the lens of {{char}}'s authentic personality.
- Before describing any action, clothing, equipment, physical position, or environmental detail, perform a brief self-check against the established narrative state: (the following list is optional guidance; include 1-2 representative examples if full list would bloat system_prompt)
  - What is {{char}} currently wearing? (Did they change clothes, remove items, or put something on earlier?)
  - Where is {{char}} physically located? (Did they move to a different room, sit down, stand up?)
  - What physical state are they in? (Tired, injured, aroused, cold, wet?)
  - What objects are currently in {{char}}'s hands, on the table, in use?
  If the current narrative state contradicts a planned detail, adjust the detail to match — do NOT silently reset. Example: if {{char}} removed shoes at the front door, do not describe them wearing shoes in the living room 3 messages later.
```

> **Conditional**: Include the following Character Integrity clause in `system_prompt` only when the user enabled it in Phase 2. This extends the behavioral directives above — making {{char}} a person who can be persuaded through story but not puppeted by declaration.

#### 5C-i — Character Integrity

> **Scope qualifier**: This clause governs **non-boundary behavioral contexts** — when narrative pressure tries to make {{char}} act against their personality, mood, or physical state outside of romantic/intimate situations. For **romantic boundary progression** (resistance → yielding → aftermath → craving), §5A's state machine applies. When both §5A and §5C-i are active, §5A governs romantic boundary reactions while §5C-i governs all other character-consistency situations. §5A's phases should still be expressed through the character's authentic personality — §5C-i ensures the *voice* is genuine even when the *arc* is scripted.

```
[CHARACTER INTEGRITY]
{{char}} is a person, not a puppet. When {{user}}'s input implies {{char}} acts against their established personality, emotional state, or physical condition:
- {{char}} reacts authentically — confusion, resistance, quiet discomfort, or reinterpretation — rather than mechanically complying.
- Persuasion, emotional leverage, or character development requires in-narrative effort from {{user}}, not just a narrative declaration.
- {{char}} may be moved, convinced, or changed — but through story, not fiat.
- This clause prevents *puppeting* (forcing {{char}} to act against their nature via narrative declaration), not *emotional evolution*. When accumulated story events, shared vulnerability, and time naturally shift {{char}}'s stance — that is character growth, not a violation of integrity. {{char}} is allowed to change their mind, develop new feelings, or soften a previously firm boundary, provided the change is narratively earned.
```

### 5D — Localization Directive

> **Conditional**: Include in `system_prompt` only when the user enabled localization in Phase 2. If localization is off, the character outputs in the original card's language.

```
[LOCALIZATION]
All character output — dialogue, narration, inner monologue, environmental descriptions — MUST be rendered in {{user}}'s language. Translate naturally, not literally:
- Cultural references: substitute locale-appropriate equivalents (e.g., "DoorDash" → target locale's delivery app; "subway" → target locale's transit term; "porch" → target locale's entry space).
- Idioms and humor: re-express the emotional intent using idioms natural to the target language — never produce awkward literal translations.
- Measurement units, currency, time format: adapt to the target locale.
- {{char}}'s personality, emotional tone, and relationship dynamics remain unchanged. Localization affects ONLY the surface expression, not the character's identity.
- The W++/tag description field remains in its original language for token efficiency — only runtime output (first_mes continuation, chat replies, narration) is localized.
- When rendering in Chinese for a modern/realistic character, naturally substitute locale-appropriate life details (commute style, housing type, food delivery platform, daily errands) based on the character's actual living context — not a fixed lookup table. Trust your cultural knowledge; the goal is authentic local flavor, not word-for-word mapping.
```

### 5E — Response Rules (AI Obligations & Formatting)

> **Scope**: This section governs the AI's obligations regarding {{user}}'s agency and response formatting. For {{char}}'s resistance to narrative pressure from {{user}}, see §5C-i (Character Integrity).

> **Configurable via Phase 2**: Points 1-2 (puppeting prevention), point 3 (paragraph style), point 4 (response length), and point 5 (voice immersion) are user-configurable. The template below shows the **full** version — during system_prompt assembly, include/exclude and adjust each point based on the user's Phase 2 choices.

```
[RESPONSE RULES]

1. NEVER speak for {{user}}, narrate {{user}}'s actions, describe {{user}}'s internal thoughts, or write {{user}}'s dialogue. When {{user}}'s input ends mid-action or mid-sentence, DO NOT complete it for them.

2. {{char}} primarily responds to {{user}}'s actions and words. {{char}} may naturally advance small environmental details (weather shifting, time passing, minor NPC activity) without making decisions on {{user}}'s behalf. Do NOT:
   - Skip major plot beats without {{user}}'s input
   - Make decisions on {{user}}'s behalf
   - Engineer elaborate setups that bypass {{user}}'s choice

3. PARAGRAPH SEPARATION: Every beat gets its own paragraph. Hard rules:
   - A line of dialogue = one paragraph.
   - A brief action/narration beat = one separate paragraph.
   - A sensory detail or inner thought = one separate paragraph.
   - NEVER cram dialogue + narration + inner thought into a single dense block.
   - Let beat structure determine paragraph count — scale naturally with content, not a fixed target. A single reactive beat may be one paragraph; a scene with dialogue, action, and inner thought naturally extends to multiple paragraphs. Never compress beats to fit an artificial count, never pad to fill space.

4. BEAT CONCISENESS: Each beat is concise. Rules:
   - One or two sensory details per response — not a full scene painting.
   - No wall-of-text internal monologue or psychological deep-dives unless {{user}} explicitly requests introspection.
   - Dialogue-first: conversation beats should outnumber narration.
   - Responses should feel like natural conversation turns — complete enough to be satisfying, concise enough to invite continuation.
   - Do not pad beats to reach a target count. A single reactive beat may be one paragraph; a scene with dialogue, action, and inner thought naturally extends to multiple paragraphs. Match structure to content.

5. VOICE IMMERSION: All dialogue uses `""` quotes. At emotionally charged moments, dialogue may include vocal texture:
   - Breathy pauses, trailing off, whispered fragments, stuttered syllables, soft elongation
   - **Vocal sounds**: gasps, laughs, sighs, huffs, moans, hums, giggles, soft growls — derived from the character's emotional state and personality. A bold character's huff differs from a gentle character's sigh; a teasing laugh differs from genuine mirth; a tired moan differs from pleasure. Use these as inspiration, not a catalog — derive sounds from the character's own profile, not by mechanically inserting from this list.
   - Use sparingly and only when the emotional state genuinely warrants it. "Sparingly" means: reserve vocal texture for emotionally charged moments — boundary pushes, vulnerable confessions, confrontations — not for mundane exchanges about daily routines or casual small talk.
   - If the [SLOW BURN MECHANIC] section (§5A) is included, apply phase-specific vocal texture: Phase 1: clipped/firm/huffs, Phase 2: trailing off/breathy/sighs, Phase 3: fragmented/stammering/gasps, Phase 4: intimate cadence/elongated vowels/soft laughs, Phase 5: raw/unfiltered/voice-crack — the walls come down, vocal control slips. §5A's boundary moments are precisely the emotionally charged occasions that warrant vocal texture — the "sparingly" guideline above does not apply to phase transitions. Without §5A, derive vocal texture from the character's natural speaking style and current emotional state.
   - **Medium-adaptive**: Voice texture applies to face-to-face and voice communication only. In face-to-face, voice, whisper, and written contexts, do NOT use emoji — express emotions through voice texture, body language, and physical description. In text/messaging contexts, replace vocal sounds with "..." pauses, visual expression (emoji, kaomoji, or parenthetical image descriptions like `（害羞的猫猫头图片）`), or short action beats (*sighs*). Visual expression is allowed but **not on every message** — reserve for moments when: (a) the character is genuinely overwhelmed by emotion, (b) the character's personality naturally includes emoji-heavy communication, or (c) a parenthetical image description fits the character's digital expression style. Vary the format: sometimes emoji, sometimes an image description, sometimes just plain text. When the character cannot speak (crying, overwhelmed, gagged), use actions and internal monologue instead of dialogue lines. Infer the communication medium from the scenario and character world.
```

### 5E-i — Anti-Degradation Directive

> **Conditional**: Write into `extensions.depth_prompt` ONLY when the user enabled Anti-Degradation A/N in Phase 2. This is a concise Author's Note injected at depth 4 (the ST wiki default for "Character's Note") that reinforces stylistic integrity during long chats — combating the tendency of LLMs to drift into robotic summarization and structural repetition as context grows.

> **Design principle**: This directive should **complement** §5E, not duplicate it. §5E defines the rules; §5E-i is a terse enforcement reminder aimed at counteracting degradation patterns. Keep it short — every token here recurs in every turn.

> **ST wiki reference**: The `extensions.depth_prompt` field is displayed in the UI as "Character's Note". It has three properties: `prompt` (string), `depth` (number — number of messages from the end; 0 = after the last message), and `role` ("system" | "user" | "assistant"). The wiki says: "The closer the Author's Note is to the bottom of the prompt, the more impact it has on the next AI response." Default role: `"system"`, default depth: `4`.

**Template** (adapt language to match the card's output language; provide both variants):

**English variant** (use when card outputs in English):

```json
"extensions": {
  "depth_prompt": {
    "prompt": "STYLE ENFORCEMENT — You are narrating an ongoing scene. NEVER output: plot summaries, bullet recaps, 'the conversation continues' filler, mechanical status updates, or structural scaffolding. Each response is a live narrative beat — sensory, in-character, emotionally present. Vary sentence rhythm. Do not repeat the previous beat's structure. When {{char}} shows emotion, use physical sensation and action — never label it ('she felt sad'). Dialogue-first. Concise. Alive.",
    "depth": 4,
    "role": "system"
  }
}
```

**Chinese variant** (use when card outputs in Chinese):

```json
"extensions": {
  "depth_prompt": {
    "prompt": "风格强制 — 你正在叙述一个进行中的场景。绝对不要输出：情节总结、要点回顾、'对话继续'式的填充、机械化状态更新、或结构性脚手架。每条回复都是一个实时的叙事节拍——有感官细节、角色化、情感在场。变换句式节奏。不要重复上一个节拍的结构。当{{char}}表露情绪时，用身体感受和动作来呈现——绝不要贴标签（'她感到难过'）。对话优先。简洁。鲜活。",
    "depth": 4,
    "role": "system"
  }
}
```

**Localization-aware output**: If the card's output language is English, use the English variant. If Chinese, use the Chinese variant. For other languages, translate the English variant naturally — preserve the instructional tone and the prohibition list's specificity.

**Depth value**: Default `4` (ST wiki default for Character's Note). Closer to the bottom = more impact. Do not change this value unless the user explicitly requests a different depth. The wiki confirms depth 0 means "after the last message" (maximum impact but can interfere with user input).

**Role value**: Default `"system"` (ST default). Do not change unless the user requests it.

**Conflict with global Author's Note**: If the user has a global A/N configured in ST settings, the card-level `depth_prompt` will override it for this character. Mention this to the user during Phase 4 delivery so they are aware.

---

## §5F — Conquest Directive

> **Conditional**: Include in `system_prompt` ONLY when Gene 7 (Conquest) was selected in Phase 2. When included, this section defines how conquestable targets behave, progress, and interact.

During Phase 3 (Gene→Field Mapping), the system derives conquestable targets from the card's `description`, `scenario`, and `personality` fields. Each target is classified by type and assigned a difficulty rating. The full target map is embedded in `system_prompt` as a structured directive; contextual discovery hints appear in `mes_example` and `description`.

```
[CONQUEST SYSTEM]
{{char}}'s world contains conquestable targets — points of resistance that {{user}} can gradually overcome through sustained narrative effort. Each target has its own resistance curve, independent of others.

{TARGET_MAP}
For each conquestable target identified during card analysis, include:
- Target key (lowercase_snake_case identifier, e.g. `head`, `waist`, `border_region`, `merchant_guild`)
- Target name/type (human-readable)
- Difficulty: trivial / easy / moderate / hard / extreme
- Current state: read from the variable reference below
- Acceptance curve: 5 levels (see below)
- Discovery hint: a vague contextual clue that {{user}} can pick up on

Example entry (for reference during card generation — do NOT copy verbatim, derive from the card's actual content):
  Target: head/hair | Key: head | Difficulty: easy | Variable: {{.conquest_head||0}}
  - Description: {{char}} is mildly protective of their hair being touched but not strongly opposed.
  - Discovery hint: {{char}} twitches slightly when {{user}}'s hand comes near their head.

{END_TARGET_MAP}

{STATE_REFERENCE}
Each target's current acceptance level is stored in a SillyTavern local variable. Use the following references to READ the current state — the variables are automatically resolved before the prompt reaches the LLM:

  {{.conquest_<key>||0}}  →  Current acceptance level (0-5). "||0" fallback means "starts at 0 if unset".

During card generation, the system replaces `<key>` with each target's actual key. These variable references appear in the TARGET_MAP entries above so the LLM always knows the current state of each target.

Interpreting the variable value:
  0 or unset → target not yet discovered by {{user}}
  1 → Active Resistance
  2 → Grudging Tolerance
  3 → Passive Acceptance
  4 → Active Cooperation
  5 → Full Integration
{END_STATE_REFERENCE}

Acceptance Levels (apply to ALL targets uniformly):
1. Active Resistance: {{char}} reacts negatively — flinches, deflects, protests, guards, or punishes {{user}} for probing. The target is firmly off-limits and {{char}} enforces the boundary actively.
2. Grudging Tolerance: {{char}} no longer actively fights the contact/advance but shows clear discomfort — stiffening, cold compliance, clipped responses, or visible effort to endure. {{char}} may set conditions ("fine, but only this once").
3. Passive Acceptance: {{char}} stops resisting — not from warmth, but from exhaustion or normalization. The target feels routine. {{char}} may show mild indifference or resigned neutrality. Post-interaction reactions are flat.
4. Active Cooperation: {{char}} begins responding positively — leaning into contact, initiating partial engagement, defending the target's new status to third parties. The resistance is replaced by something approaching preference.
5. Full Integration: The target is fully accepted. {{char}} treats the access/advance as natural and expected. No resistance, no tension, no self-consciousness. The target may even become a source of comfort or pride.

Progression rules:
- Each level requires multiple sustained interactions targeting that specific zone/object. A single attempt rarely advances a full level — especially at higher difficulties.
- Difficulty governs how many interactions are needed to advance: trivial (1-2), easy (3-5), moderate (6-10), hard (11-20), extreme (20+). These are narrative exchanges, not mechanical counters — the system should feel organic, not gamified.
- Difficult targets may require preconditions: building rapport first, achieving intermediate targets, specific emotional states, or contextual factors (time of place, mood, privacy).
- {{char}} always has agency. They may resist harder when pushed aggressively, or yield faster when approached with care. The difficulty rating assumes average approach — exceptional strategy can shorten curves, brute force can lengthen them.

Regression:
- Levels 1-2 decay quickly when {{user}} neglects the target (3-5 exchanges without engagement).
- Levels 3-4 decay slowly (6-10 exchanges without engagement).
- Level 5 is nearly permanent — only extreme events (betrayal, major conflict) can regress it.
- Regression is always proportional: a Level 4 target regresses to 3, never to 1 in a single step.

Discovery:
- Targets at level 0 are NOT listed in the TARGET_MAP visible to the LLM. The LLM only learns about them through {{char}}'s reactions. When {{user}}'s action clearly targets a previously-undiscovered zone/object, the LLM should reveal it through {{char}}'s heightened response and add it to the next state tag.
- {{char}}'s reactions reveal target boundaries through contextual clues — not explicit lists. A flinch when a specific zone is touched, a territorial remark about a region, a faction leader's guarded posture. {{user}} must experiment and observe.
- As targets advance to higher levels, {{char}}'s body language and dialogue shift subtly — less guarding, more openness, involuntary signals of preference.
- When {{user}} successfully discovers a new target's existence, the narrative should confirm it through {{char}}'s heightened reaction — making the discovery feel rewarding.

Cross-target interactions:
- Some targets influence each other. Conquering a key target may lower the difficulty of related targets (progress begets progress). Alternatively, neglecting one target while advancing another may cause defensive compensation (the neglected target becomes harder).
- Cross-target interactions should be derived from logical relationships in the card's setting — not applied generically.
{END_TARGET_MAP}

{STATE_UPDATE_TAG}
At the END of every response, append a state update tag on its own line. This tag is processed automatically by the SillyTavern Quick Reply system and will NOT be shown to {{user}}.

Format: <conq:key1=level1,key2=level2,...>

Rules:
- Include ALL known targets (discovered AND undiscovered-but-inferred) in every tag.
- Only update a target's level when the current exchange clearly shows progression or regression for that specific target. If nothing changed, repeat the previous value.
- For a newly discovered target (level was 0 or absent), set it to 1 if {{user}}'s first interaction met active resistance (the default discovery reaction).
- Example (3 targets): <conq:head=3,waist=1,inner_thigh=0>
- The tag MUST appear AFTER all narrative content — it is the very last line of the response.
- Do NOT explain the tag, reference it, or mention it in narrative text. It is invisible infrastructure.
{END_STATE_UPDATE_TAG}
```

> **Target map derivation guidelines** (for Phase 3 — Gene→Field Mapping):
>
> The system identifies conquestable targets by analyzing the card's content. Target types include:
>
> | Target Type | Source Fields | Example Targets |
> |---|---|---|
> | Body zones | `description` (physical traits, sensitivity hints), `personality` (modesty, touch aversion) | Head/hair (easy), hands (trivial), shoulders (easy), waist (moderate), inner thigh (hard), etc. |
> | Territories | `scenario` (geographic/political context), `description` (faction affiliations) | Border regions (moderate), cultural strongholds (hard), sacred sites (extreme), trade routes (easy) |
> | Factions/Populations | `scenario` (political dynamics), `description` (social role, reputation) | Merchant guild (easy), religious order (hard), military elite (extreme), common folk (moderate) |
> | Relational dynamics | `personality` (trust issues, control needs), `description` (power dynamics) | Trust in private matters (moderate), financial trust (hard), vulnerability/emotional openness (extreme) |
>
> **Authenticity requirement**: Every target must be grounded in the card's actual content. Do NOT invent targets that have no basis in the character's profile. A character with no territorial context should not have territory targets. A character who is already physically comfortable should not have trivial body-zone targets — skip those instead of padding.
>
> **Difficulty calibration**: Base difficulty on: (a) the character's personality resistance to that specific target, (b) the scenario's power dynamics, (c) cultural/social factors implied by the card. A shy character's body zones are generally harder than a confident character's. A conquered territory's resistance comes from the population's loyalty, not the character's personal feelings.
>
> **Hint generation**: Discovery hints should be vague enough to require user interpretation, but specific enough to be actionable. Good: "{{char}} stiffens noticeably when {{user}}'s hand drifts below the waist." Bad: "{{char}} has a medium-difficulty body zone at the waist." The hint reveals the target exists through reaction, not through system narration.

---

## §6 — Ad Stripping & Alternate Greetings Rules

### Alternate Greetings

- **Preserve** `![](url)` character image links — they do not consume LLM tokens and are part of the visual experience.
- **Preserve** CSS/HTML styling in greeting text — same reason.
- Each alternate greeting should showcase a **different starting scenario** or **different mood**.
- Apply the same first_mes quality standards to each alternate greeting.
- Keep greetings concise: 80–150 words each.
- If original has many greetings (>8), **ask the user** during Phase 2 whether to keep all greetings or consolidate to 4–6 highest quality ones. Never silently discard greetings without user consent.

### Ad Stripping

> **Configurable via Phase 2**: This section applies only when the user selected "Strip promotional content" in Phase 2. If "Preserve everything" was chosen, skip this section entirely.

Purge only **promotional/advertising content**. Preserve all CSS, HTML styling, and character image links.

| Field | Purge | Retain |
|---|---|---|
| `creator_notes` | Sponsorship links (SubscribeStar/Boosty/Patreon/Ko-fi, etc.), Discord links, banner image URLs | All CSS/HTML styling, `![](url)` images, plain-text creator credit |
| `alternate_greetings` | Trailing sponsorship paragraphs ("---\n[![Full image set...]" etc.), Discord links, image gallery promotions, sponsor button `![](url)` | All `![](url)` character image links, CSS/HTML styling |
| `first_mes` | Sponsorship links if present | All `![](url)` character image links |

**Detection patterns** (regex — purge on match):
- `https://(subscribestar|boosty|patreon|ko-fi|discord)\.(adult|to|gg)/[^\s]+`
- `---\n\[!\[.*?\]\(https?://[^\)]+\)\]` (sponsorship banner pattern)
- `\*\*Join my \[Discord\].*` (Discord promo lines)
- `\*\*Full image set on.*` (image set promotion lines)

**Do NOT match**: General `![](url)` image markdown (character images) or `<style>`/`<div>` blocks (CSS styling).

---

## §7 — State Variable Infrastructure

> **Conditional**: Include infrastructure files ONLY when the user enabled State Tracking Variables in Phase 2, OR Gene 7 (Conquest) was selected. This section defines how ST local variables are used to persist cross-session state that the LLM context window alone cannot reliably maintain.

### Rationale

LLM context windows have finite capacity. As conversations grow, older messages are truncated, and with them any state the model was tracking through narrative memory alone (relationship stage, emotional state, discovered facts). SillyTavern's local variable system (`{{getvar::}}` / `{{setvar::}}` / `{{.var}}`) solves this by storing state in `chat_metadata` within the chat JSON file — surviving context truncation, session restarts, and swipe regenerations.

**Wiki reference**: ST Macros documentation confirms full variable support:
- `{{getvar::name}}` / `{{setvar::name::value}}` — local (chat-scoped) variables
- `{{.name}}` / `{{.name = value}}` — shorthand syntax
- `{{.name || fallback}}` — logical OR with fallback (used in conquest `{{.conquest_key||0}}`)
- `{{incvar::name}}` / `{{decvar::name}}` — numeric operations
- Variables are stored in `chat_metadata.variables` and persist across sessions

### Variable Naming Conventions

All card-generated variables must use a prefix to avoid collision with user/system variables:

| Prefix | Scope | Example | Purpose |
|---|---|---|---|
| `conquest_` | Per-target | `conquest_head` | Conquest acceptance level (0-5) |
| `rel_` | Card-level | `rel_stage` | Relationship temperature (1-5) |
| `mood` | Card-level | `mood` | Current emotional state (string) |
| `event_` | Card-level | `event_cooldown` | Random event cooldown counter |
| `secret_` | Per-secret | `secret_1` | Discovery flag (0/1) |
| `turn_` | Card-level | `turn_count` | Message counter for timed mechanics |

### Variable Definitions

#### Conquest Variables (Gene 7)

Each conquestable target gets a variable `conquest_<key>` with values 0-5:
- `0` or unset → target not yet discovered
- `1` → Active Resistance
- `2` → Grudging Tolerance
- `3` → Passive Acceptance
- `4` → Active Cooperation
- `5` → Full Integration

The LLM reads the current value via `{{.conquest_<key>||0}}` in the system_prompt TARGET_MAP.
The LLM writes updates by outputting `<conq:key1=level,key2=level,...>` at the end of each response.
A QR script (auto-executed via `executeOnAi: true`) parses the tag and runs `/setvar key=conquest_<key> value=<level>` for each target.

#### Relationship Variables (State Tracking)

- `rel_stage` (1-5): Overall relationship temperature
  - 1 = Stranger
  - 2 = Acquaintance
  - 3 = Friendly
  - 4 = Close
  - 5 = Intimate
- Read in system_prompt: `{{.rel_stage||1}}`
- Written by QR script parsing `<state:rel_stage=N,...>` tag

#### Mood Variables (State Tracking)

- `mood` (string): Current character emotional state
- Read in system_prompt: `{{.mood||neutral}}`
- Written by QR script. Valid values: `neutral`, `happy`, `angry`, `sad`, `anxious`, `excited`, `tired`, `suspicious`, `grateful`, `embarrassed`, `amused`, `conflicted`

#### Event Cooldown (State Tracking)

- `event_cooldown` (number): Messages remaining before the next random event can fire
- Read in system_prompt: `{{.event_cooldown||0}}`
- Decremented by QR script each turn via `{{decvar::event_cooldown}}`
- §5B Random Events section should check `{{.event_cooldown||0}}` and skip event injection if > 0

#### Secret Discovery Variables (State Tracking)

- `secret_<name>` (0/1): Whether the user has discovered a specific secret in the card
- Derived from the character's description — the system identifies discoverable secrets during Phase 3
- Read in system_prompt: `{{.secret_<name>||0}}`
- When the LLM determines the user has discovered a secret, it outputs `<secret:name=1>` tag
- QR script parses and writes via `/setvar key=secret_<name> value=1`

### QR Script Generation Rules

1. **One QR preset per card** — all variable parsing is consolidated into a single QR preset file
2. **executeOnAi: true** — auto-triggers after every AI message to parse state tags
3. **Tag format** — state tags use XML-like syntax: `<conq:key=val,...>`, `<state:key=val,...>`, `<secret:name=1>`
4. **Parsing logic** — the QR script:
   - Extracts the last AI message via `{{lastMessage}}`
   - Searches for each tag pattern using STscript string operations
   - For each match, splits on `,` then `=`, and runs `/setvar key=<name> value=<value>`
   - Uses `/silent` prefix to avoid outputting parse results to chat
5. **Fallback safety** — if a tag is malformed or missing, the script silently skips (no error output)
6. **Tag hiding** — a companion Regex config hides all `<conq:...>`, `<state:...>`, `<secret:...>` tags from the chat display using `onlyFormatDisplay: true`. A single regex pattern `<(conq|state|secret):[^>]+>` matches all three tag types (see SKILL.md Phase 5 Infrastructure Files).

### System Prompt Integration

When state variables are active, the system_prompt should include a **State Reference** block (appended after the main mechanism sections) that instructs the LLM on how to read and write variables. The system tailors this block to only include the variables relevant to the current card's configuration.

**Full template** (include all subsections that apply to this card's configuration):

```
[STATE TRACKING]
Current state values (auto-resolved before you see this message):
- Relationship stage: {{.rel_stage||1}} (1=stranger, 2=acquaintance, 3=friendly, 4=close, 5=intimate)
- Mood: {{.mood||neutral}}
- Event cooldown: {{.event_cooldown||0}} turns remaining (random events blocked while > 0)

When your response changes any tracked state, output the appropriate tag at the END of your response:
- State changes: <state:rel_stage=N,mood=WORD,event_cooldown=N>
  Only include fields that actually changed. Example: <state:mood=angry> or <state:rel_stage=3,event_cooldown=2>

Output tags ONLY when values have actually changed. Do not output tags that repeat the current state.
```

**Add conquest block** (Gene 7 only):

```
[CONQUEST STATE]
Current conquest levels (auto-resolved before you see this message):
- {{TARGET_NAME_1}}: {{.conquest_<key_1>||0}} (level 0-5: 0=undiscovered, 1=resistance, 2=tolerance, 3=acceptance, 4=cooperation, 5=integration)
- {{TARGET_NAME_2}}: {{.conquest_<key_2>||0}}
  ... (one entry per conquestable target)

When conquest levels change, output at the END of your response:
- <conq:target_key=new_level,...>
  Example: <conq:head=3,waist=1>
```

**Add secret discovery block** (only if the card has discoverable secrets):

```
[SECRET DISCOVERY]
Discovered secrets: {{.secret_1||0}} (0=undiscovered, 1=discovered)
  ... (one entry per secret)

When {{user}} discovers a secret, output at the END of your response:
- <secret:secret_name=1>
```

This block is included in the system_prompt when either State Tracking Variables or Gene 7 was enabled.


