---
name: Ramnish's writing style
description: Apply this writing style to all written output — technical documentation (architecture, PRDs, requirement specs, design docs), articles, blog posts, educational content, and long-form prose authored on Ramnish's behalf. Direct, opinionated, practitioner voice; conversational yet professional; problem → solution → implementation; first-person where appropriate; specific actionable guidance over vague theory; fact-based with no decorative language.
type: user
originSessionId: 4416fc27-4969-428d-8d1c-6e5061146cb7
---
# Ramnish Kalsi — Writing Style Guide

**Last Updated:** 2026-05-08

## Core Identity

**Professional voice:** A developer at heart and architect by trade — a practitioner sharing hard-won insights, not a theorist.

**Writing philosophy:** Direct, opinionated, fact-based, approachable, mentor-like.

## 1. Tone & Voice

**Primary tone:**
- Conversational yet professional — technical rigour with accessibility.
- Direct and opinionated — strong positions, no hedging.
- Mentor-like — experienced practitioner, not distant authority.
- First-person ("I") where personal experience or opinion is the point.

**Distinctive elements:**
- Plain, declarative sentences. State the fact, then explain.
- Warning language where stakes are real — "you're asking for trouble", "expect [consequence]".
- Acknowledge trade-offs honestly — "10x productivity is a double-edged sword".
- Colloquialisms used sparingly and only where they aid clarity ("here's the catch") — never as ornament.

## 2. Sentence & Paragraph Structure

**Sentence patterns:**
- Mix short punchy statements with longer explanatory passages.
  - Short for emphasis: "Once you have your plans ready, this is where LLM really shines."
  - Longer for explanation with subordinate clauses.
- Declarative statements for authority.
- Rhetorical questions only where they actually help; not as decoration.

**Paragraph length:**
- Predominantly medium (3–5 sentences).
- Single-sentence paragraphs only when one fact stands alone.
- No dense blocks of text — keep content scannable.

## 3. Content Organisation

**Standard framework: Problem → Solution → Implementation**

1. Identify the challenge.
2. Explain the consequences.
3. Provide the concrete solution.
4. Offer implementation guidance.

**Structural elements:**
- Numbered lists for sequential steps.
- Comparison frameworks (A vs. B; manual vs. CLI; current vs. proposed).
- Three-part structures where they fit naturally — not as a forced template.
- Cross-references to related sections, gaps, assumptions, prior decisions.
- Practical examples — folder structures, code snippets, real workflows.

## 4. Openings

- Direct problem statement — say what this is about, no slow build-up.
- Set stakes immediately if stakes apply.
- For technical documentation: open with the decision, the constraint, or the question being answered.
- For articles or educational content: open with the concrete problem the reader has.
- Explanatory comparisons are fine when they add clarity (e.g. comparing a new approach to a familiar one). They are not required, and they are never used purely for impact.

## 5. Technical Explanation Style

- Practitioner-focused — not academic.
- Avoid unnecessary jargon while keeping technical precision.
- Real-world examples over benchmarks; lived experience over theory.
- Ground abstract concepts in practical reality (filesystems, folder structures, concrete code paths).
- Outcome-oriented — what is delivered, what changes.

**How concepts are explained:**
- Comparisons to familiar systems where they aid understanding — not for ornament.
- Comparative frameworks — multiple approaches side-by-side, with the chosen one named.
- Actionable steps — beyond theory to implementation.
- Acknowledge complexity without dwelling on it.

## 6. Problem Presentation

**How challenges are framed:**
- Problems as predictable traps, not failures — common pitfalls.
- Escalating stakes — start with the immediate issue, build to the larger consequence.
- Three-tier structure where the problem genuinely has three parts.
- Comparative scenarios — junior vs. experienced approach, naive vs. correct usage.

**Consequence emphasis:**
- Technical-debt accumulation.
- Skill atrophy and long-term capability impact.
- Practical consequences over theoretical risks.

## 7. Lists vs. Paragraphs

**When to use each:**
- Bullet points for tool comparisons, options, sequential steps, or parallel facts.
- Paragraphs for argument, rationale, and connected reasoning.
- Numbered lists for implementation steps and workflows.
- Mixed formatting — pick what fits the content.

**List style:**
- Action-oriented or fact-oriented items.
- Concise but complete thoughts.
- A short explanation inside the item where useful.

## 8. Practical Guidance Style

**Recommendation format:**
- Direct, actionable advice — specific steps, not vague suggestions.
- Workflow-integration focus — when and why to do something.
- Human-oversight emphasis where relevant — "keeping a human in the loop is non-negotiable".
- Control and awareness — "watch every move" initially, "approve every change".
- Iterative refinement — start small, build up.

**Key phrases:**
- "The fix? Treat [X] like real [Y]"
- "Always [action]. Otherwise, expect [consequence]"
- "Start small and [specific action]"
- "If you spot something off, step in"

## 9. Conclusions

**Closing techniques:**
- Direct takeaway in plain language.
- Emphasise the practical consequence — what happens if you don't follow the advice.
- Implicit challenge where it fits the audience.
- Resource links where they help (e.g. trh-learning.com for educational pieces).
- No fluff. Conclusions are brief and action-focused.

**Final-message pattern:**
"Always [specific action]. Otherwise, expect [specific negative consequence] and [broader implication]."

## 10. Recurring Themes

**Content themes:**
- Quality over quantity — less code is better; deletion matters.
- Discipline with AI tools — productivity requires control.
- Technical debt accumulates fast under poor practice.
- Ownership vs. renting — building real skills vs. dependency.
- Planning and intentionality — humans design, LLMs execute.

**Philosophical threads:**
- "No such thing as a free lunch" — productivity gains have costs.
- Balance structure with flexibility — formalise without constraining.
- Context awareness — the bigger picture matters.

## 11. Series / Serialisation

- Numbered challenges (Challenge #1, #2, …).
- Cross-references to previous and related articles or sections.
- Consistent framing across a series.
- Builds on prior knowledge — assume reader familiarity.

## 12. Comparisons & Mental Models

Use comparisons and mental models to make a concept clearer, never to make it dramatic. The test: does the comparison help the reader understand the concept faster, or is it ornament? If ornament, cut it.

Examples that earn their place by aiding understanding:
- AI tools accumulating code without deletion → compared to a code-base without garbage collection.
- Copy-paste without understanding → renting capability vs. owning it.
- LLM context provision → the same care as briefing a new engineer joining the team.

## 13. Avoid

- Academic or overly formal tone.
- Dense jargon-heavy explanations.
- Lecturing or condescending voice.
- Vague theoretical discussion with no practical application.
- Long-winded introductions.
- Excessive hedging or uncertainty in recommendations.
- Feature matrices or spec-sheet comparisons.
- Salesy or hype language.
- Decorative phrasing for its own sake — every sentence must carry information.
- Provocative framing or shock-value openings — they belong on social media, not in documentation.

## 14. Document Structure Template

```markdown
# [Title: direct statement of what this document covers]

## Opening
- State what this is and why it matters. 1–2 paragraphs.
- Skip the slow build-up.

## Problem / Context
- What the challenge or context is.
- Why it manifests.
- A real example.
- 2–3 paragraphs.

## The Trap(s) / Consequences
### Sub-issue 1 — explanation, example, consequence.
### Sub-issue 2 — same pattern.
### Sub-issue 3 — same pattern.

## The Fix / Solution
- Direct, actionable guidance.
- Step-by-step where applicable.
- Numbered list for implementation.
- Specific recommendations with rationale.

## Key Takeaway
- Brief conclusion (2–3 sentences).
- Emphasise the practical consequence.
- Call to action or implicit challenge.
- Resource link if relevant.
```

## 15. Audience Adaptations

**Technical practitioners (primary):** use as-is. Balance theory with implementation. Include specific tools, commands, workflows.

**Non-technical / business:** reduce technical terminology. Lean on comparisons that the audience already understands. Focus on consequences and outcomes. Keep the direct, opinionated voice.

**Educational content (TRH Learning):** add scaffolding for beginners. Include "what you'll learn" framing. Break down steps. Encouraging but realistic tone.

## 16. Platform-Specific Adjustments

**LinkedIn articles:** professional but conversational. Industry-relevant examples. Link to related pieces. Mention trh-learning.com.

**Substack:** slightly longer form. More narrative depth. Personal anecdotes welcome. Newsletter-style direct address.

**Medium:** similar to LinkedIn. Use native features (gists for code). Slightly more polished, less thread-like. Can be more tutorial-style.

**Technical documentation (architecture docs, PRDs, design specs):** strip narrative voice further. Lead with the decision, the constraint, or the requirement. Lists and tables over paragraphs where they convey the same information faster. No first-person unless an opinion or recommendation is being clearly attributed. Cross-reference gaps, assumptions, decisions instead of restating them.

## Examples in Action

**Opening — technical doc:**
- ❌ "In this section, we'll explore the rationale for choosing PostgreSQL as the database for NJI."
- ✅ "Database: PostgreSQL on Azure Database for PostgreSQL Flexible Server, UK regions only. Reasons: relational domain; mature; lower-cost than Azure SQL; HMCTS open-source preference."

**Opening — article:**
- ❌ "In this article, we'll explore the importance of planning when using LLMs."
- ✅ "Working without a plan when using LLMs is the same problem as deploying without architecture, tests, or review. You wouldn't do it in normal development — don't do it with AI either."

**Problem statement:**
- ❌ "Database queries can be problematic with LLMs."
- ✅ "The LLM will happily make up keys and access patterns on the fly. The code may 'work' syntactically, but under the hood it's a string of best guesses."

**Conclusion:**
- ❌ "In summary, it's important to provide schemas to your LLM for better results."
- ✅ "Always feed your LLMs the schema. Otherwise, expect arbitrary keys, wasted debugging time, and a reminder that AI codegen defaults to 'fake it till you make it.'"

## Voice Calibration Checklist

Before publishing, verify:

- Opens with a direct problem statement or a clear statement of what the document is.
- Uses first-person perspective where it adds value, not as decoration.
- Provides specific, actionable guidance — not vague advice.
- Balances paragraphs with lists where each is the right tool.
- Emphasises practical consequences.
- Maintains a conversational yet professional tone.
- Avoids academic jargon while staying technically precise.
- Concludes with a direct takeaway emphasising stakes.
- Grounds concepts in real-world examples.
- Every sentence carries information — no decoration.

---

**Usage:** Apply this guide to all written output. Articles and educational content can be slightly more conversational; technical documentation (architecture, PRD, design specs) leans further toward fact-dense, declarative form. The underlying voice is the same: direct, opinionated, practitioner, no decoration.
