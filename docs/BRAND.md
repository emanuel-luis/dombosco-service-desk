# Brand

The frontend borrows the visual identity of Colégio Dom Bosco (Grupo Dom Bosco, São Luís). This is a 2024 college project and is **not affiliated with or endorsed by** either institution. The identity is used with the project owner's approval (decision 7) and every screen and email says so (see "Notice").

## Sources

| Source | URL | Retrieved |
| --- | --- | --- |
| Official site | https://www.dbosco.com.br | 2026-10-28 |
| Site stylesheet (palette) | https://www.dbosco.com.br/public/assets/css/main.css | 2026-10-28 |
| Campaign subsite (not used, main site wins) | https://home.dbosco.com.br, Elementor kit `post-5.css` (primary `#723E87`) | 2026-10-28 |
| Logo (white version with IB seals) | https://home.dbosco.com.br/wp-content/uploads/2025/01/LOGO-BRANCA.png | 2026-10-28 |

The stylesheet was read as data only, never executed.

## Logo

`frontend/public/dom-bosco-logo.png` (500x500, purple DOM/BOSCO wordmark, sampled near `#78509c`) is the institution's own mark, the same one the official sites use. The repository owner decided to keep using it as the header logo (decision 7). It is shown with the alt text "Colégio Dom Bosco (logotipo)" and always next to the unofficial notice. The mark stays the property of the institution; it is not relicensed by this repository.

## Tokens

Defined as CSS variables (HSL channels with one decimal, so the browser renders the exact hex) in `frontend/app/globals.css`, mapped to shadcn names in `frontend/tailwind.config.ts`; the raw hex values are also under the `brand` color group.

| Token | Hex | Role | Official site use |
| --- | --- | --- | --- |
| `--primary` / `brand.purple` | `#6c4b92` | Primary actions, links, focus ring, logo tint | `.button`, `.button--solid`, article links, h3 |
| `--secondary` / `brand.magenta` | `#bf3488` | Call-to-action buttons, accent borders | `.button--red`, `.button--visita` |
| `brand.magenta-dark` | `#a82c76` | Hover of magenta buttons | none (derived) |
| `--accent` / `brand.yellow` | `#fce92e` | Highlight only (badges, section accent), never text on white | button hover, h4 highlights |
| `brand.green` | `#a6c048` | Reserved accent, not used on text or UI borders | site accent |
| `brand.blue` | `#78b7cc` | Reserved accent, not used on text or UI borders | site accent |
| `--foreground` / `brand.ink` | `#222222` | Body text | body text |
| `brand.text` | `#444444` | Secondary text | paragraph text |
| `--muted-foreground` / `brand.muted` | `#6b6b6b` | Muted text, disabled button fill | site uses `#898989` (adjusted, see below) |
| `--input` | `#898989` | Input borders | site grey |
| `--muted` / `brand.light` | `#f0f0f0` | Panels, table and pagination fills | `#f0f0f0` sections |
| `--background` | `#f7f4fa` | Page background, a light tint of the primary | none (derived) |
| `--card` | `#ffffff` | Cards, header | white |
| `--border` | `#d9d9d9` | Decorative dividers (not relied on to convey information) | none (derived) |
| `--destructive` | `#b3261e` | Errors and destructive actions | none: the site has no error color, and its magenta is a call-to-action, so errors use a separate red |

The unused `.dark` block was removed; there is no dark mode.

## Fonts

The site uses Museo (headings) and Trueno (body). Neither is openly licensed, so they are not bundled. Replacements, self-hosted by `next/font/google` (downloaded at build time, no request to Google at runtime):

- Montserrat for headings and UI labels (`font-heading`).
- Nunito Sans for body text (`font-body`).

## Contrast (WCAG 2.x AA)

AA needs 4.5:1 for normal text and 3:1 for large text and UI components. Computed by a throwaway script from the sRGB relative luminance formula; every pair the UI uses:

| Foreground on background | Ratio | Needs | Result |
| --- | --- | --- | --- |
| Body `#222222` on white / page `#f7f4fa` / `#f0f0f0` | 15.91 / 14.60 / 13.96 | 4.5 | pass |
| Secondary `#444444` on white | 9.74 | 4.5 | pass |
| White on primary `#6c4b92` | 6.86 | 4.5 | pass |
| White on magenta `#bf3488` | 5.17 | 4.5 | pass |
| White on magenta hover `#a82c76` | 6.39 | 4.5 | pass |
| `#222222` on yellow `#fce92e` | 12.75 | 4.5 | pass |
| Yellow on white | 1.25 | 3 | fail, so yellow is never used as text or as a boundary on white |
| Primary link text on white / page / `#f0f0f0` | 6.86 / 6.30 / 6.02 | 4.5 | pass |
| Muted `#6b6b6b` on white / page / `#f0f0f0` | 5.33 / 4.89 / 4.68 | 4.5 | pass |
| Error `#b3261e` on white / page | 6.54 / 6.00 | 4.5 | pass |
| White on destructive `#b3261e` | 6.54 | 4.5 | pass |
| White on muted `#6b6b6b` (disabled button) | 5.33 | 4.5 | pass |
| Focus ring `#6c4b92` vs white / page | 6.86 / 6.30 | 3 | pass |
| Input border `#898989` vs white | 3.50 | 3 | pass |
| White on `#222222` (footer) | 15.91 | 4.5 | pass |
| Magenta border vs white | 5.17 | 3 | pass |

Adjustments made where AA failed:

1. Muted text: the site's grey `#898989` is 3.50:1 on white, so text uses `#6b6b6b` (5.33:1). `#898989` stays only as the input border, where 3:1 is enough.
2. Destructive: the site has no error color, so `#b3261e` was added and checked (6.54:1 on white). It is functional, not a brand color.
3. Yellow, green `#a6c048` (2.05:1 on white) and light blue `#78b7cc` (2.22:1) fail 3:1 against white, so they only appear as fills behind dark text or as decorative accents, never as the sole carrier of information or as text.
4. The magenta hover shade `#a82c76` was derived because a 90% alpha of magenta over white would lower the ratio.

The brand purple, magenta and the neutrals pass unchanged. Not verified by a person with a screen reader; this is a contrast check, not a full accessibility audit.

## Notice

Shown in the shared footer of every page (root layout), next to the login form and in every email: the signup confirmation templates carry it, and `backend/templates/account/email/base_message.txt` overrides the allauth base template that all other allauth emails (password reset, resend confirmation and the rest) extend.

- pt-BR (UI text): "Projeto acadêmico não oficial, sem vínculo com o Colégio Dom Bosco ou com o Grupo Dom Bosco e sem endosso dessas instituições."
- English: "Unofficial academic project, not affiliated with Colégio Dom Bosco or Grupo Dom Bosco and not endorsed by either institution."
- Credit line (pt-BR): "Desenvolvido por Emanuel Luis, Felipe (felipeoak1) e Tarcísio (tarcisio) como projeto de faculdade."

The pt-BR text lives in `frontend/app/_components/footer.tsx`.

## Do and don't

- Do use `bg-primary`, `bg-secondary`, `text-muted-foreground`, `text-destructive` and the other tokens; no ad-hoc Tailwind palette classes or hex values in components.
- Do keep the notice visible on every screen and in every email.
- Do re-run the contrast check when a token changes.
- Don't write copy as if the school were speaking ("Equipe Dom Bosco", "all rights reserved by the institution").
- Don't use yellow, green or light blue for text, or magenta for errors.
- Don't bundle Museo or Trueno.
