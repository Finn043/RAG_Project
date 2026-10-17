---
name: BJJ Research Assistant
description: A source-grounded research desk for Brazilian Jiu-Jitsu literature.
colors:
  ink-deep: "#06171d"
  ink-panel: "#09232b"
  ink-raised: "#10343d"
  film: "#e8f2ef"
  film-bright: "#f4faf7"
  film-muted: "#b9ccc8"
  registration-mint: "#42e8c8"
  signal-orange: "#ff6b35"
typography:
  display:
    fontFamily: "Barlow Condensed, sans-serif"
    fontSize: "clamp(3.25rem, 7vw, 5.8rem)"
    fontWeight: 600
    lineHeight: 0.82
    letterSpacing: "-0.035em"
  body:
    fontFamily: "Atkinson Hyperlegible, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.65
  label:
    fontFamily: "Barlow Condensed, sans-serif"
    fontSize: "0.78rem"
    fontWeight: 600
    letterSpacing: "0.11em"
rounded:
  square: "0px"
spacing:
  compact: "0.6rem"
  base: "1rem"
  section: "1.6rem"
components:
  button-primary:
    backgroundColor: "{colors.registration-mint}"
    textColor: "{colors.ink-deep}"
    rounded: "{rounded.square}"
    height: "2.7rem"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.film}"
    rounded: "{rounded.square}"
    height: "2.7rem"
  input-query:
    backgroundColor: "{colors.ink-panel}"
    textColor: "{colors.film-bright}"
    rounded: "{rounded.square}"
    height: "3.4rem"
  surface-chat:
    backgroundColor: "{colors.ink-raised}"
    textColor: "{colors.film}"
    rounded: "{rounded.square}"
    padding: "1.25rem 1.35rem"
---

# Design System: BJJ Research Assistant

## Overview

**Creative North Star: “The Evidence Film Desk”**

The interface treats research as material to inspect. A deep ink workbench holds one illuminated conversation plate, while small registration lines and restrained signal colors make system state visible. The visual character comes from the contrast between the dark archive rail and the pale, readable evidence surface; it does not imitate a physical film texture.

The system is dense where corpus status and controls need to be scanned, then gives answers a broad reading measure. Motion is reserved for one scan pass on entry and short control-state transitions. The mobile view collapses the corpus rail so the welcome, conversation and question field remain usable without a sideways layout.

**Key Characteristics:**

- Deep ink surfaces with a mint registration accent.
- Square, ruled controls and conversation plates.
- Condensed display type paired with a highly legible body face.
- Citation text remains the visual focus of each answer.

## Colors

The palette uses deep blue-green ink as the work surface, pale film tones for reading, mint for registration and orange for attention or focus.

### Primary

- **Registration Mint** (`{colors.registration-mint}`): Marks active controls, important labels and registration geometry.
- **Signal Orange** (`{colors.signal-orange}`): Reserved for keyboard focus, error or pending-state marks.

### Neutral

- **Deep Ink** (`{colors.ink-deep}`): Main page ground.
- **Archive Ink** (`{colors.ink-panel}`): Sidebar and query field surface.
- **Raised Ink** (`{colors.ink-raised}`): Avatar and raised interface details.
- **Film** (`{colors.film}`): Main readable text.
- **Bright Film** (`{colors.film-bright}`): Display type and emphasis.
- **Muted Film** (`{colors.film-muted}`): Secondary explanatory text.

**The Signal-Role Rule.** Mint marks active structure; orange marks attention. Do not swap their roles casually.

## Typography

**Display Font:** Barlow Condensed (with sans-serif fallback)

**Body Font:** Atkinson Hyperlegible (with sans-serif fallback)

**Label Font:** Barlow Condensed

**Character:** The condensed display face gives the product name a tall, measured silhouette. Atkinson Hyperlegible carries questions and long citations with clear letterforms.

### Hierarchy

- **Display** (600, responsive 3.25–5.8rem, 0.82 line-height): Product title.
- **Body** (400, 1rem, 1.65 line-height): Questions, welcome and answer text; keep answers near 72ch where possible.
- **Label** (600, 0.78rem, 0.11em tracking, uppercase): Corpus and conversation status.

**The Two-Face Rule.** Keep Barlow Condensed for display and compact labels; use Atkinson Hyperlegible for sentences and citations.

## Layout

On desktop, a fixed-width corpus rail anchors a broad central work surface. The main content is capped at 1100px with generous horizontal padding; the query field stays at the bottom of the chat surface. On screens at or below 800px, the sidebar starts collapsed, the heading and description stack, and the content padding contracts to 1rem. Body copy uses a readable 72ch maximum. Spacing groups controls tightly and separates the title, conversation and query field more generously.

## Elevation & Depth

Depth is primarily tonal: ink panels, fine borders and inset rules distinguish surfaces. The page ground stays uninterrupted; registration marks live on controls and content rather than as a repeating background texture. The query field receives one broad, soft shadow to lift the active question from the page. Conversation plates use a faint inset top rule instead of a card border.

### Shadow Vocabulary

- **Query lift** (`0 22px 54px rgba(0, 8, 10, 0.32)`): Separates the fixed question field from the page ground.

## Shapes

Controls and plates use square corners. Thin mint registration lines and small corner marks establish structure; avoid pill shapes and heavy borders for primary surfaces.

## Components

### Buttons

Buttons are square and clearly state their action. The query submit control uses mint against deep ink. Secondary actions use a transparent ground with a thin mint-tinted border; hover fills the surface with mint and changes the label to deep ink. Keyboard focus uses a visible orange outline.

### Cards / Containers

Conversation messages sit on a lightly raised ink plane with a fine inset top rule and a small registration corner. User messages shift right and receive a mint-tinted ground; assistant messages keep the neutral raised ground.

### Inputs / Fields

The question field uses a deep panel with a 1px mint outline, square corners and bright readable text. Focus adds a 3px orange outline with a 3px offset. Placeholder text stays pale enough to read against the panel.

### Navigation

The corpus rail uses compact status rows and tabular counts. It is expanded on wide layouts and begins collapsed on mobile. A dedicated clear-conversation control remains available in the rail.

### Corpus Readout

PDF, page and chunk counts share one ruled row. Pipeline details are secondary, aligned as short status lines with a single registration mark.

## Do's and Don'ts

### Do:

- **Do** keep source citations visible and readable inside answers.
- **Do** reserve mint for active structure and orange for attention or focus.
- **Do** respect `prefers-reduced-motion` and keep content visible when motion is disabled.
- **Do** keep the mobile sidebar collapsed initially.

### Don't:

- **Don't** use gradients on display text.
- **Don't** add decorative textures that reduce citation contrast.
- **Don't** use rounded chat bubbles or nested card shells.
- **Don't** let color be the only signal for focus, loading or error.
