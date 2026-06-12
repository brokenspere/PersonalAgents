---
name: interactive-html-docs
description: "Create interactive HTML documentation pages with tabs, expandable sections, and popups. Use when: creating docs in HTML format, building interactive single-file documentation, making architecture diagrams, generating spec/design docs as HTML. CRITICAL: uses pure CSS only (no JavaScript) to ensure compatibility with Microsoft Teams preview, email clients, SharePoint, and any restricted CSP environment."
argument-hint: "Describe the documentation content and structure"
---

# Interactive HTML Documentation (Pure CSS)

## When to Use

- User asks to create documentation in HTML format
- User wants interactive docs (tabs, expandable panels, popups)
- User needs docs viewable in Microsoft Teams, email, SharePoint, or other restricted environments
- User wants a single-file HTML doc with rich interactivity

## Critical Constraint

**NEVER use JavaScript.** Many preview environments (Teams, Outlook, SharePoint, GitHub markdown preview) strip `<script>` tags entirely. All interactivity MUST be pure CSS + native HTML.

## Pure CSS Interaction Patterns

### Tabs (Radio Input Pattern)

Use hidden radio inputs as state, labels as tab buttons, and CSS `:checked` sibling selectors to show/hide panels.

```html
<div class="tabs-wrapper">
  <!-- Hidden radio inputs (state holders) -->
  <input type="radio" name="tabs" id="tab-one" checked>
  <input type="radio" name="tabs" id="tab-two">

  <!-- Tab navigation (labels targeting radios) -->
  <div class="tabs-nav">
    <label for="tab-one">First Tab</label>
    <label for="tab-two">Second Tab</label>
  </div>

  <!-- Tab panels (siblings of inputs) -->
  <div class="content">
    <div class="tab-panel" id="panel-one">...</div>
    <div class="tab-panel" id="panel-two">...</div>
  </div>
</div>
```

```css
.tabs-wrapper input[type="radio"] { display: none; }
.tab-panel { display: none; }

#tab-one:checked ~ .tabs-nav label[for="tab-one"],
#tab-two:checked ~ .tabs-nav label[for="tab-two"] {
  color: var(--accent);
  border-bottom-color: var(--accent);
}

#tab-one:checked ~ .content #panel-one,
#tab-two:checked ~ .content #panel-two {
  display: block;
}
```

**Key rules:**
- Radio inputs MUST be siblings of `.tabs-nav` and `.content`
- Use `~` (general sibling combinator) not `+` (adjacent)
- Panel IDs must differ from radio IDs (e.g., `tab-X` vs `panel-X`)

### Expandable Sections (Details/Summary)

Use native `<details>` element — works everywhere, no CSS needed for basic functionality.

```html
<details class="component-card">
  <summary>
    <h4>Component Title</h4>
    <p>Brief description</p>
  </summary>
  <div class="component-details">
    <!-- Expanded content here -->
  </div>
</details>
```

Style the open state with `details[open]` selector:

```css
.component-card[open] {
  background: rgba(2, 195, 154, 0.1);
  border-color: var(--accent);
}

/* Hide default marker */
.component-card summary { list-style: none; }
.component-card summary::-webkit-details-marker { display: none; }
.component-card summary::marker { display: none; content: ''; }
```

### Accordion (Only One Open)

For exclusive accordion behavior, use hidden radio inputs + labels wrapping content with max-height transitions.

### Hover Tooltips

```css
.tooltip { position: relative; }
.tooltip::after {
  content: attr(data-tip);
  position: absolute;
  bottom: 100%;
  opacity: 0;
  transition: opacity 0.2s;
}
.tooltip:hover::after { opacity: 1; }
```

## Document Structure Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Document Title]</title>
  <style>
    /* CSS variables for theming */
    :root {
      --primary: #1E2761;
      --accent: #02C39A;
      --bg: #0F172A;
      --surface: #1E293B;
      --text: #F1F5F9;
      --text-muted: #94A3B8;
      --border: #334155;
    }

    /* Reset + base */
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; background: var(--bg); color: var(--text); }

    /* Tab system CSS */
    /* ... (radio input pattern) ... */

    /* Responsive */
    @media (max-width: 768px) { /* mobile overrides */ }
  </style>
</head>
<body>
  <!-- Header -->
  <!-- Tabs wrapper with radio inputs -->
  <!-- Content panels -->
  <!-- NO <script> tags -->
</body>
</html>
```

## Checklist Before Delivery

- [ ] Zero `<script>` tags in the file
- [ ] All tabs use radio input + `:checked` selectors
- [ ] Expandable panels use `<details>/<summary>`
- [ ] Test: first tab visible by default (`checked` attribute)
- [ ] Test: clicking labels switches panels (CSS sibling selectors)
- [ ] Responsive: works on mobile viewports
- [ ] Self-contained: single HTML file, no external dependencies
- [ ] Proper HTML entities used (`&amp;`, `&lt;`, etc.)

## Common Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| Tabs don't switch | Radio inputs not siblings of nav/content | Move inputs to be direct children of wrapper |
| All panels visible | Missing `display: none` on `.tab-panel` | Add base rule hiding all panels |
| Details won't expand | CSS overriding pointer-events on summary | Ensure `cursor: pointer` and no `pointer-events: none` |
| Broken in Teams | Any JS present | Remove ALL script tags |
| Broken in email | External CSS/fonts | Inline all styles, use system fonts |
