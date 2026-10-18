---
version: 1
slug: "src-app-tsx"
primary_target: "src/App.tsx"
related_targets: ["src/index.css","netlify/functions/answer.ts"]
---

## Scope and mode

The production React/TypeScript chat surface in `src/App.tsx`. Mode: Operate.

## Audience, job, action and proof

Learners and researchers ask questions in Vietnamese or English, then verify the answer against exact PDF citations. The primary action is submitting a question; proof is the source filename and page in each factual answer. Preserve corpus readout, local conversation display, clear action, loading and error states.

## Chosen direction

Carry forward the Evidence Film Desk from the Streamlit surface: archive rail, broad conversation plate, deep ink, pale film, mint registration, orange focus and square controls. The memorable moment is moving from a question into an answer whose evidence trail stays visible.

## Constraints

React/TypeScript and Tailwind on the client; Netlify Function owns PDF parsing, embeddings and model requests. Keep the API key and PDF files server-side, cap the query length, and rate-limit requests. Responsive desktop/mobile layout, keyboard access, reduced motion, and bilingual copy. Each question retrieves independently; chat history is display-only.

## Unresolved decisions

The app is currently publicly reachable. Access restrictions and custom domain are not configured.
