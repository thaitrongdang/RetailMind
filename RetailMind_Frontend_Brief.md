# RetailMind — Frontend Design Integration Brief

Version: 1.0 | Date: 2026-10-03

## 1. Purpose and document roles

Implement RetailMind's six-page analytics and recommendation application using the visual language in `DESIGN.md` (Factory — Style Reference). Translate that language into an operational dashboard suited to the actual product specification.

Read these documents before frontend work:

1. `AGENTS.md`: execution workflow and current user direction.
2. `RetailMind_Codex_Plan.md`: product scope, data definitions, evaluation and API requirements.
3. This brief: RetailMind-specific design decisions and resolutions of conflicting source instructions.
4. `DESIGN.md`: palette, typography, shapes and aesthetic reference.

For frontend decisions, this brief takes precedence over contradictory style examples in `DESIGN.md`. Product correctness and actual user instructions take precedence over visual preferences. Explain any material deviation in the decision log. These documents do not override higher-priority environment instructions.

The source file is a written style reference, not a full screen design or verified source implementation. Without screenshots or a Figma design, implement a coherent interpretation and do not claim pixel-exact reproduction of Factory.

## 2. Visual direction

RetailMind should feel like a calm, precise analytical instrument: near-black canvas, warm neutral text, thin boundaries, regular-weight typography and restrained functional orange/green signals. Visual hierarchy comes from spacing, contrast and readable data. The dominant content is the real product: metrics, histories, recommendations, charts and evaluation evidence.

Preserve:

- Canvas `#101010`, raised dark surface `#1d1a18` and warm neutral grays.
- Primary text `#eeeeee`, with occasional light `#eeeeee` panels and dark text.
- Geist for general UI and Geist Mono for concise labels, IDs, units and code.
- Mostly weights 400 and 500, modest radii and restrained 1px borders.
- Neutral primary buttons and short, quiet transitions.
- Consistent semantic tokens and shared reusable components.

Avoid decorative gradients, neon glows, diffuse shadows, glass effects, giant marketing headlines inside the dashboard, fake product imagery, invented partner logos, pricing sections and copied Factory branding.

## 3. Resolve source conflicts before coding

| Source issue | RetailMind decision |
| --- | --- |
| Button radius 3px throughout, but one example says 9999px | Use 3px for rectangular action buttons. Do not create pill CTAs from that example. |
| Marketing layout prohibits a sidebar | Use a persistent desktop sidebar for six app pages, plus a compact top context bar. |
| 96px+ marketing section gaps | Use 24–32px between dashboard panels; reserve larger space for page-level transitions if useful. |
| 72px marketing headline | Use approximately 28–36px page titles and 32–40px metric values, responsive to space. |
| Nearly all labels uppercase at 12px with line-height 1 | Reserve that treatment for short metadata labels. Use readable sentence-case body text, table values and longer explanations. |
| Accent colors described as decorative, status colors and trend colors | Make color roles explicit. Orange is attention/accent; green is success/confirmed state. A chart series color identifies the series, not automatically a positive or negative result. |
| Light button text initially described as light on light | Use `#101010` text on `#fafafa` buttons and light panels. |
| Very faint dark dividers | Use faint dividers only for nonessential decoration. Necessary controls, selection and focus must be perceptible through appropriate contrast and additional cues. |
| Status pulse presented as live | Show genuine service readiness if observed. Label dataset context as historical; do not imply live retail data. |
| macOS window frame and noise texture | Omit fake window chrome in the actual app. Omit texture behind tables, charts and reading content. |

## 4. Semantic token contract

Define these roles once in the chosen framework's theme mechanism. Components must not scatter independent hex values and spacing decisions throughout the code.

| Role | Initial value | Application |
| --- | --- | --- |
| Canvas | `#101010` | App background |
| Surface | `#1d1a18` | Sidebar wells, dark panels, inputs |
| Decorative border | `#3d3a39` | Nonessential panel separation |
| Strong boundary | `#8a8380` | Controls requiring visible boundaries; verify adjacent contrast |
| Primary text | `#eeeeee` | Text on dark surfaces |
| Secondary text | `#b8b3b0` | Supporting explanations and labels |
| Muted text | `#8a8380` | Less prominent text on dark backgrounds, subject to contrast checks |
| Light surface | `#eeeeee` | One focal summary or action panel where appropriate |
| Text on light | `#101010` | All primary text on light surfaces |
| Secondary text on light | `#4d4947` | Supporting text on light panels |
| High-emphasis button | `#fafafa` / `#101010` | Neutral light fill / dark label |
| Signal | `#ee6018` | Attention, selected indicator, limited chart accent |
| Success | `#a0ca92` | Confirmed/ready state, explicitly favorable outcome |

Spacing: use a base rhythm of 8px; 8/16/24/32px cover most component relationships. A 4px micro-gap is allowed for compact icon/text alignment. Panel padding 20–24px on desktop and 16px on narrow screens. Radius: buttons/inputs 3px, standard cards 10px, exceptional large containers up to 20px.

Typography: body 14–16px, compact metadata 12px, page title 28–36px, metric values 32–40px. Preserve readable line heights; avoid dense uppercase paragraphs and tight tracking on small numeric tables. Use tabular figures for aligned numbers. If Geist is unavailable, use the declared system/Inter fallback without blocking the app; check the actual rendered layout.

Prefer dark cards for ordinary data panels. Use a light panel selectively to focus attention on a primary finding, recommendation summary or evaluation result. Do not make every KPI a bright white card.

## 5. App shell and responsive behavior

### Desktop

- Sidebar approximately 224–248px wide with RetailMind wordmark and six navigation entries.
- Active entry indicated by shape/border plus text, not color alone.
- Top context bar with page title, snapshot selector, cutoff information and genuine API/model readiness where available.
- Main content uses available width with roughly 24–32px gutters; avoid imposing a 1200px total app width if it makes tables cramped. Constrain long prose independently.
- Consistent location for global snapshot selection. The selected snapshot is visible on every page.

### Tablet and mobile

- Around 1024px, allow collapsible navigation and fewer grid columns; tune breakpoints to the actual chosen framework and content.
- Around 768px, use one-column panels, a navigation drawer and stacked controls.
- Wide tables may scroll inside their own container. The entire page must not overflow horizontally.
- Charts must resize without cropped labels. Keep legends and units accessible.
- Touch controls should remain comfortably usable; avoid copying tiny marketing hit areas.

Navigation and snapshot changes must preserve valid context without silently mixing data from different cutoffs. If a filter is page-local, label its scope.

## 6. Page-specific composition

### Overview

Lead with the snapshot/cutoff and dataset context. Show a compact KPI strip for documented transaction values, sales invoices, identified customers and products. Below it, give the time-series chart more space than secondary summaries. A secondary column or row holds product popularity and country distribution. Place concise KPI definitions near the numbers through help text or a definitions drawer. Label GBP and distinguish positive sales from eligible adjustments.

### Customers

Customer search/selection comes first. Show profile summary and RFM, then purchase history and recommendation results. Recommendations include rank, product code, description as of cutoff, repeat-item marker, actual serving model and expandable evidence. Put the model selector close to the recommendation panel. Keep customer-not-found, low-history fallback and explicit new-customer mode distinct. On small screens stack history above recommendations.

### Historical Replay

Make the chosen supported snapshot, cutoff and 30-day horizon unmistakable. Present history and the generated ranking first. Use an explicit `Reveal outcomes` action to show future purchases and matches. Reveal must not recompute or alter the earlier recommendations using the outcome. Use labels/icons in addition to color to show matched and unmatched items. Keep the visual emphasis on the history-to-prediction-to-outcome relationship.

### Products

Use a searchable code/description table or list and a focused detail area for the selected product. Show as-of-cutoff description, historical popularity and ItemCF neighbors where available. Prefer typography and concise data displays over decorative product-image cards; the source does not provide trustworthy images. Do not imply stock availability.

### Model Evaluation

Show split, cutoff, horizon, cohort counts and comparison protocol above the result table. Include measured Recall@10, NDCG@10, HitRate@10 and coverage with appropriate definitions. Label validation versus test. Give one prominent light summary panel to the evidence-based model selection or result. Add cohort analysis and failure examples below. Avoid progress bars that misrepresent unbounded or non-percentage scores.

### Data Quality

Lead with input/accepted/excluded counts and reconciliation. Present missingness, cancellations, invalid values and source duplicate flags in auditable tables or charts. Include reason-code explanations and traceable sample rows. This is a data audit workspace, so prioritize readable dense content and filters over giant decorative status tiles.

## 7. Shared components

Build or adapt reusable equivalents of:

- AppShell, Sidebar/NavItem and SnapshotSelector.
- PageHeader with context metadata.
- MetricTile with value, unit, definition and optional meaningful trend.
- Panel with title, description and action area.
- SearchInput, Select, NeutralButton and visible focus treatment.
- DataTable with consistent numeric alignment and explicit sort/filter behavior where supported.
- ChartContainer with title, units, legend, empty state and table alternative where useful.
- ModelSelector, RecommendationTable and EvidenceDisclosure.
- StatusBadge with icon/text and honest status semantics.
- LoadingState, EmptyState, ErrorState and RetryAction.
- ExportAction including snapshot/model/evaluation metadata.

Adapt this contract to the existing frontend rather than creating incompatible parallel component systems.

## 8. Chart and status semantics

Use neutral axes/gridlines and readable light labels. For charts with up to three models, a fixed mapping such as Popularity = pale neutral, ItemCF = orange and ALS = green is acceptable. In that chart, colors identify models and must not imply that ALS is best. Preserve mapping across pages and always show names/legend or direct labels. For more categories, prefer grouped panels, selected categories, line patterns or neutral shades before inventing a rainbow palette.

Do not label a rising metric favorable without considering its meaning: rising sales and rising cancellations have different interpretations. If no valid comparable period exists, omit delta/sparkline rather than inventing it. Mark unavailable metrics as unavailable with a reason, not zero.

Confirmed matches can use green plus a check/text. Attention or partial fallback can use orange plus a label. Error states must be explicit through an error icon, wording and actionable next step; a decorative red accent is not mandatory. All meanings must remain understandable without color.

## 9. Accessibility and motion

Target normal text contrast of at least 4.5:1 and qualifying large text of at least 3:1. Necessary UI boundaries and graphical information should meet applicable non-text contrast requirements. Test actual adjacent colors and states rather than assuming source tokens are accessible everywhere.

Specific source-token checks, calculated from the supplied hex colors:

- `#8a8380` on `#101010`: approximately 5.11:1.
- `#8a8380` on `#eeeeee`: approximately 3.21:1; unsuitable for normal-size essential text.
- `#1d1a18` against `#101010`: approximately 1.10:1; not a sufficient sole visual cue for a necessary control boundary.
- `#3d3a39` against `#101010`: approximately 1.69:1; use as a decorative divider, not the sole required control indicator.

Use keyboard-accessible navigation, labeled inputs, visible focus and understandable error messages. Light surfaces have their own dark foreground tokens. Dense table text must not be forced to 12px uppercase. Honor reduced-motion preferences. Use restrained 150–200ms transitions only where helpful; omit marquee, parallax, pulsing historic-data labels and spring effects.

Reference standards:

- W3C text contrast: https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html
- W3C non-text contrast: https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html

These targets and initial token checks do not constitute a completed accessibility audit of an implementation.

## 10. Framework decision

Inspect the existing frontend and project state before selecting tools. Streamlit is the original project default, not a claim that it can reproduce every custom reference precisely. If it supports the agreed design adequately, implement supported theme/layout features first and minimize fragile CSS selectors tied to undocumented internals.

If a separate web frontend is needed for the required visual control, explain the concrete limitations and cost of changing frameworks, resolve any material user preference and keep FastAPI as the domain interface. Do not silently replace a working stack, duplicate model logic in JavaScript or add a server framework solely because the reference includes Tailwind examples. A style file's CSS snippets are not evidence that a particular framework is required.

## 11. Implementation sequence and review evidence

1. Inspect current source, available endpoints, dependencies and documents.
2. Record a concise adaptation plan and stack decision with identified conflicts.
3. Implement central tokens, app shell and core shared components.
4. Build Overview and Customers as representative visual checkpoints: they exercise charts, KPI tiles, tables, input controls and recommendation evidence.
5. Run the actual app, inspect desktop and narrow-screen renderings and fix visible problems. Produce screenshots for the user. Continue independent work; an optional visual-feedback checkpoint is not a mandatory stop for permission.
6. Carry the same component system through the remaining four pages, adapting their layouts to their tasks.
7. Verify real API wiring, snapshot behavior, loading/empty/error paths, keyboard navigation and exports.
8. Record results, screenshots, limitations and any remaining user-dependent assets in progress.

Fixtures may be used during development if visibly labeled synthetic. Final screenshots and completion claims must distinguish fixtures from real processed data. Do not invent metrics, customer histories, trained-model readiness or live updates to make the dashboard look complete.

## 12. Acceptance checklist

- All six pages share the same tokens, fonts, controls and context presentation.
- Factory's visual language is recognizable without copying its marketing navigation/content.
- No inconsistent pill buttons, random accents, diffuse shadows or decorative gradients.
- Dense data is readable, numeric columns align and charts have correct units/legends.
- Light panels use dark text and verified contrast.
- Responsive layout works without global horizontal overflow.
- Focus, selection, warning and error states are understandable beyond color.
- All required data/evaluation semantics from the original plan are preserved.
- Actual API data is integrated; placeholders and missing models are honest and clear.
- Visual checks and functional results are documented with evidence.

## 13. Paste-ready instruction for the implementing agent

```text
Read AGENTS.md, RetailMind_Codex_Plan.md, DESIGN.md and
RetailMind_Frontend_Brief.md completely, then inspect the existing workspace.

Use DESIGN.md as the visual style reference and RetailMind_Frontend_Brief.md
as the RetailMind-specific adaptation. Preserve the product and temporal
evaluation requirements. Resolve the documented source contradictions as
specified in the brief; do not copy Factory's marketing layout into the app.

Implement consistent tokens and shared components, then build Overview and
Customers as visual checkpoints before extending the system across all six
pages. Run and inspect the actual interface at desktop and narrow widths,
fix rendering and interaction problems, and provide screenshots plus actual
verification results. Continue independent work while inputs are pending.

Inspect the current frontend before choosing or changing its framework.
Record material stack decisions and any limitations. Never fabricate data,
metrics, model readiness or claims of pixel-exact reproduction.
```
