# Personal Introduction Site - Design Brief

## Project Goal
A beautiful, minimal personal introduction website for a Data Scientist and AI/ML Engineer.

## Aesthetic
- **Style:** Minimalist, clean, airy. Professional but personal.
- **Colors:** Off-white background (#fafafa), dark gray text (#1a1a1a), one accent color for links (e.g., muted blue #4a6fa5).
- **Typography:** Serif for headings (e.g., Playfair Display), sans-serif for body (e.g., Inter).
- **Layout:** Single column, centered, max-width 680px. Generous padding.

## Sections (In Order)
1. **Hero:** Your name as a large headline. One-sentence tagline describing you as a Data Scientist / AI Engineer.
2. **About:** A short paragraph (2-3 sentences) about your work and interests.
3. **Links:** A clean row of links to your LinkedIn and GitHub profiles. Must be easily tappable on mobile.

## Technical Requirements
- **Stack:** Plain HTML + Tailwind CSS (via CLI).
- **File:** `index.html` at the root.
- **Responsive:** Mobile-first. Include viewport meta tag. Use Tailwind prefixes (sm:, md:).
- **No Horizontal Scroll:** Ensure no overflow on 320px screens.