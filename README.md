# SIH26166 — LUNA UI

Frontend prototype for **Multi-modal, Sun angle and scale invariant image correspondence using Chandrayaan-2 optical images (OHRC, TMC and IIRS)**.

## Stack
- React + Vite
- React Router
- Lucide React icons
- Custom responsive CSS
- No backend dependency in this UI phase

## Run

```bash
npm install
npm run dev
```

Open the Vite URL shown in the terminal.

## Pages
- `/` — Mission overview
- `/correspondence` — Upload reference/moving images and configure a run
- `/datasets` — Dataset catalog
- `/results` — Match/registration analytics
- `/settings` — Engine defaults

## Backend integration points
The UI is intentionally ready for a FastAPI backend. The main API calls to add in the backend phase are:

- `POST /api/v1/datasets/upload`
- `POST /api/v1/correspondence`
- `GET /api/v1/jobs/{job_id}`
- `GET /api/v1/results/{job_id}`
- `GET /api/v1/datasets`
