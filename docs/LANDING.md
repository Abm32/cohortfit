# Landing page

Edviro-inspired marketing surface for cohortfit at `/`. The interactive audit viewer lives at `/app`.

## Routes

| Path | Purpose |
|------|---------|
| `/` | Static marketing landing — no audit math |
| `/app` | Sample report + live offline demo audit |

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
