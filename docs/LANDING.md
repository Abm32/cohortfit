# Landing page

Edviro-inspired marketing surface for cohortfit at `/`. The interactive audit viewer lives at `/app`.

## Routes

| Path | Purpose |
|------|---------|
| `/` | Marketing landing. No audit engine call — the ancestry mixer interpolates between the two pinned Tier 0 rates (0% SAS → 6.40% EUR, 100% SAS → 3.55%) client-side, and the WebGL helix is decorative |
| `/app` | Audit workbench. Opens empty; dataset cards, JSON paste, prose extract, and **Load sample report** each fetch on demand |

## Local development (PowerShell)

```powershell
pip install -e ".[web,dev]"
cd web
npm install
npm run dev
```

In a second terminal:

```powershell
cohortfit serve --port 8000
```

Open `http://localhost:5173/` for the landing page and `http://localhost:5173/app` for the audit viewer. Vite proxies `/api` to the Python server.

### Troubleshooting

If Vite reports `Failed to resolve import "@react-three/fiber"`, dependencies were not installed (often after a network error during `npm install`). From `web/`:

```powershell
npm install
npm run dev
```

The hero 3D helix requires `@react-three/fiber` and `three` — both are listed in `package.json`.

## Build

```powershell
cd web
npm run build
```

Output goes to `web/dist/`. Serve via `cohortfit serve` or any static host with SPA fallback to `index.html`.

## Design

- Cream background (`#F8F7F2`), charcoal dark sections (`#0C0E0B`), forest green accents
- Components under `web/src/components/landing/`
- Styles in `web/src/landing.css` (imported from `main.tsx`)

See also [UI.md](UI.md) for the audit report viewer.
