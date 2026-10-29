# QuickDesk design system

Light theme is the default. Product UI should use the semantic utilities from `src/index.css`, not one-off palette colors.

## Theme

Tokens live in `src/index.css`.

- Static choices (font, radius) are in `@theme`.
- Colors and shadows that change with theme are CSS variables, exposed to Tailwind with `@theme inline`.
- Light applies with no attribute. Dark applies with `<html data-theme="dark">`.
- The `dark:` variant follows that same attribute.

Use utilities such as `bg-canvas`, `bg-surface`, `text-foreground`, `text-muted`, `text-subtle`, `border-border`, `bg-brand`, `text-brand-foreground`, and `shadow-sm`.

Status, priority, and category colors follow the same pattern: `text-status-open`, `bg-status-open-subtle`, `text-priority-high`, `text-category-it`, and their `-subtle` backgrounds.

Spacing, type size, and breakpoints stay on Tailwind’s default scale. Body copy is `text-sm`. Page titles are `text-3xl font-semibold tracking-tight`. Section titles are `text-lg font-semibold tracking-tight`.

## Components

Reuse the small primitives in `src/components/ui` instead of restyling raw controls:

- `Button` — `primary`, `secondary`, `ghost`, `danger`; sizes `sm` and `md`; `loading` and `disabled`
- `TextField`, `TextArea`, `SelectField` — label, hint, and error
- `Badge` — feedback, ticket status, priority, and category
- `Card`, `Alert`, `Metric`
- `Table`, `THead`, `TBody`, `Tr`, `Th`, `Td`

`src/showcase/DesignSystemShowcase.tsx` is a temporary reference. Replace it when real pages are built.

## Accessibility

Text and status pairs target WCAG AA. Focus uses a 2px `focus` outline. `prefers-reduced-motion` shortens transitions and animations.
