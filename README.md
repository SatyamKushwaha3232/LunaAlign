# SIH26166 — LUNA UI

LunaAlgin is a local full-stack demo for **multi-modal, sun-angle and scale-invariant correspondence using Chandrayaan-2 OHRC, TMC-2 and IIRS imagery**.

## Stack
- React + Vite
- React Router
- Lucide React icons
- Custom responsive CSS
- FastAPI + OpenCV processing backend

## Run

In one terminal:

```powershell
cd backend
.\venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

In a second terminal:

```powershell
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Open `http://127.0.0.1:5173`.

## Deployment with Docker

Install Docker Desktop, then from the project root run:

```powershell
docker compose up --build -d
```

Open `http://localhost:8080`. The frontend is served by Nginx and proxies API, input and output requests to FastAPI; no browser-side `localhost:8001` configuration is needed in the deployed stack. Uploaded datasets and job outputs persist in the `luna_data` Docker volume.

## Pages
- `/` — Mission overview
- `/correspondence` — Upload reference/moving images and configure a run
- `/datasets` — Dataset catalog
- `/results` — Match/registration analytics
- `/settings` — Engine defaults

## API

- `POST /api/v1/datasets/upload`
- `POST /api/v1/correspondence`
- `GET /api/v1/correspondence/jobs/{job_id}`
- `GET /api/v1/correspondence/results/{job_id}`
- `POST /api/v1/correspondence/report/{job_id}` - generates a job-specific scientific PDF report
- `GET /api/v1/datasets`

## Real Chandrayaan-2 data workflow

1. Register/login to the official [ISRO Science Data Archive (PRADAN)](https://pradan.issdc.gov.in/ch2/index.xhtml), then use MapBrowse or table browse to locate overlapping OHRC/TMC-2/IIRS observations.
2. Download a product ZIP **with its XML label**. OHRC and TMC-2 archives include `data`, `geometry`, and `browse`; IIRS products are PDS4 binary cubes with XML labels.
3. For the current classical image pipeline, use TMC-2 derived ortho/GeoTIFF products where available, or export a single calibrated OHRC/IIRS band to TIFF/PNG. Keep the matching `.xml` beside the image and use the same basename, for example `product.tif` + `product.xml`.
4. Upload the image from the Correspondence page. LunaAlgin reads the image header and merges product ID, sensor, acquisition timestamp, resolution, sun azimuth/elevation, and available coordinates from the XML. Missing fields remain `null`.
5. Run one same-sensor pair first, then an OHRC ↔ TMC-2 pair. Record the generated `result.json` values in the benchmark table; do not use estimated values.

The archive is PDS4-based and requires login for product downloads. The [ISSDC Chandrayaan-2 FAQ](https://pradan.issdc.gov.in/ch2/faq.xhtml) documents that OHRC, TMC-2 and IIRS products provide corresponding XML labels; it also notes that TMC-2 derived products may be GeoTIFF. The [Chandrayaan Data Explorer](https://chmapbrowse.issdc.gov.in/) lists the instrument resolution context: OHRC 28 cm, TMC 5 m, and IIRS 80 m.

## Demo validation and report

Use **Run synthetic ground-truth test** from the Correspondence page when real imagery is not yet available. It creates a deterministic lunar-like crater scene, applies a known transformation, and reports corner RMSE between the recovered and known transforms. On Results, select **Download scientific PDF report** to create a job-specific report containing input metadata, metrics, transformation, confidence, output maps, and (when applicable) synthetic validation.

MongoDB is optional for the offline demo and defaults to disabled. Set `MONGODB_ENABLED=true` in `backend/.env` only after your Atlas credentials have been verified.

## Vercel deployment

Deploy the `frontend` directory as the Vercel project root. Add `VITE_API_BASE_URL` in Vercel Environment Variables with the public Render backend URL.
