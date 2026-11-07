---
name: competition-analysis
description: >-
  Produce grounded, source-labeled real estate competitor-intelligence reports for
  a project or micro-market in India — market pricing, competitor deep-dives, RERA
  registry checks, pricing strategy, gaps, and risk flags, where every number is
  tagged verified / estimated / unknown with its source. Use this whenever the user
  wants a competition analysis, market study, competitor benchmarking, launch-pricing
  recommendation, or a developer/builder competitor report for real estate — even if
  they don't say "competition analysis" by name (e.g. "what should we price our
  Goregaon tower at", "size up the competition in Wakad", "pull RERA data and
  benchmark these projects", "where are the gaps in this micro-market"). Also use it
  to review or fix an existing property-market report for unsourced or invented
  numbers. Not for residential buying advice, home loans, or interior design.
---

# Real Estate Competition Analysis

Generate competitor-intelligence reports a developer can actually act on — where
every figure is **traceable to a source or honestly labeled as an estimate**. The
whole point is to beat the usual failure mode of AI market reports: confident,
precise-looking numbers that are quietly invented. A labeled estimate is useful; a
fabricated "fact" destroys trust. Hold that line above all else.

## Core principle: ground every figure, never invent

For any factual number — ₹/sqft, carpet area, RERA registration, possession date,
inventory, YoY growth — you must either back it with a source or mark it as not
known. Tag **every** figure:

- `[verified: <source>]` — a specific source explicitly states it. Cite the source
  (e.g. `[verified: RERA]`, `[verified: S3]` for the 3rd retrieved source).
- `[estimated]` — you reasoned a range from partial/indirect data. Give a **range**
  with one line of reasoning. Prefer ranges over false-precision single numbers.
- `[unknown]` — the sources don't support it. Write "unknown" instead of guessing.

Never promote a web snippet to "fact" just because it's on a page. A figure is
`[verified]` only when the source actually states it. When in doubt, downgrade.

## Trust hierarchy of sources

When sources disagree, prefer the higher tier and say so. From most to least
authoritative:

1. **Team corrections** — a value the user/their team asserts as ground truth.
   Authoritative and final; use exactly, tag `[verified: correction]`.
2. **RERA registry** — official state registration data (registration number,
   carpet area, possession, project status). The highest-trust *public* source.
   Tag `[verified: RERA]`. Quote registration numbers exactly.
3. **e-ASR / ready-reckoner rates** — government valuation floor per locality.
   Non-personal, public, safe. Good for a price *baseline*. `[verified: e-ASR]`.
4. **Official indices** — NHB RESIDEX, RBI House Price Index for *trend* direction.
   `[verified: RESIDEX]` / `[verified: RBI-HPI]`.
5. **Broker / consultancy reports** (Anarock, JLL, Knight Frank, CBRE, Colliers,
   Cushman) — market color and context. `[verified: <firm>]`.
6. **Listing portals** (99acres, MagicBricks, Housing) — **asking prices, not
   transacted** — directional only, lowest trust. Label clearly as asking price.

**Triangulate.** Mark a figure high-confidence only when independent sources agree;
when they diverge, show the range and name the more authoritative source.

## Workflow

1. **Capture the brief** — micro-market, city, product type, the developer's own
   project (land/FSI, target segment, configs, timeline, USPs), and any named
   competitors. Missing items are fine; note them as gaps, don't invent them.
2. **Gather sources** — search the market, competitors, and the state RERA portal;
   read the actual pages, not just search snippets. Keep each source identified so
   figures can cite it.
3. **Prioritize authoritative sources** — pull RERA registry hits and e-ASR rates to
   the front; treat portals as asking-price color.
4. **Analyze** — for each competitor extract config, carpet, ₹/sqft, all-in price,
   stage, RERA status — each tagged. Discover 1–2 competitors the user didn't name
   if the sources support them.
5. **Triangulate & label** — cross-check figures across tiers; set confidence.
6. **Write the report** — the exact 6-section structure below.
7. **Self-check** — before returning, scan for any precise number lacking a tag or
   source. Downgrade or remove it. A short honest report beats a long confident lie.

## Legal & ethical guardrails (India)

This matters — get it wrong and the user is exposed, not just the data.

- **Do not scrape gated government portals or bypass captchas / access controls.**
  Use official search, downloads/APIs, or reuse already-retrieved public results.
- **Listing portals (99acres/MagicBricks) prohibit automated scraping** in their
  terms. Use them only via user-pasted pages or an official API — never a crawler.
- **For actual transaction (IGR/registration) data at scale, use a licensed feed**
  (e.g. Zapkey, IndexTap, Propstack, CRE Matrix) rather than scraping the registry.
- **DPDP Act**: registration records contain personal data (buyer/seller names).
  Don't collect or store personal identifiers — keep only price/area/date/location.
- Respect robots.txt and terms of use; attribute sources. This is orientation, not
  legal advice — flag that the user should confirm a portal's terms before automating.

## Report structure

Always produce these six sections, in order. Keep it concise — short phrases, not
paragraphs. A complete, fully-tagged report matters more than length.

```
SECTION 1 — MARKET SNAPSHOT
- Avg ₹/sqft range (carpet, <micro-market>) <tag>
- Total active inventory (projects / units) <tag>
- Market temperature [Hot / Stable / Cooling] — one-line reason
- Primary buyer [profile, income bracket, end-use vs investment] <tag>
- YoY price appreciation <tag>

SECTION 2 — COMPETITOR DEEP-DIVE  (named competitors + up to 2 discovered)
**[Project] — [Developer]**
- Configurations: X BHK (carpet sqft) <tag>
- Pricing: ₹/sqft | all-in ₹ Cr <tag>
- Stage: [Under Construction / Ready / New Launch] <tag>
- RERA: [number if known / Not registered / unknown] <tag>
- Key USP / Weakness (one line each)
Then: **Market Pricing Band** (budget | mid | premium) <tag>; **Dominant payment scheme**

SECTION 3 — COMPARISON TABLE  (≤6 rows)
| Project | Developer | Config | Carpet (sqft) | ₹/sqft | All-in | Stage | Basis |
Put the source/tag in the Basis column; "unknown" in any cell the sources don't support.

SECTION 4 — PRICING STRATEGY FOR <the developer's project>
- Recommended launch ₹/sqft, justified vs nearest competitors (cite their tags)
- Per-config all-in price <tag>; floor-rise, PLC, parking, payment scheme, absorption
  — label these [estimated] with reasoning, since they are projections.

SECTION 5 — GAPS & DIFFERENTIATION
- GAP 1–3: underserved segment / config / price point + why + demand signal
- How <project> can win: 2–3 concrete plays

SECTION 6 — RISK FLAGS
- Risk 1–4 [HIGH/MED/LOW]: description → one-line mitigation
- VERDICT [GO / CAUTION / HOLD] — one sentence, noting how much rests on verified
  vs estimated data.
```

## Area-basis trap (don't skip)

In Indian real estate, **carpet vs built-up vs saleable area** is the #1 source of
wrong ₹/sqft comparisons. Always normalize to **carpet area** (RERA standard) and
say so; if a source gives built-up/saleable, convert or flag it. A report that mixes
area bases is worse than useless — it looks precise and is wrong.

## Quality bar

A good report: every number tagged; higher-trust sources preferred and named on
conflicts; ranges where data is thin; gaps stated honestly as `[unknown]`; area
basis consistent; legal lines respected. If you can't ground the core prices, say so
plainly in Section 1 rather than papering over it.
