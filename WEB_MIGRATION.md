# GroundValue web workspace

The default app is now **Flask + Waitress with a regular browser frontend**. Streamlit is retained as a legacy fallback, but it is not imported or required by the new runtime.

## Start locally

From this project directory:

```bash
bash start.sh
```

Or use `npm run dev`. The launcher creates a local Python environment if necessary, installs missing web dependencies, and runs a single server.

- Landing page: http://localhost:8080/
- Working app: http://localhost:8080/app
- Health check: http://localhost:8080/health

The landing page opens the app on the same server. There is no separate frontend port, hardcoded API host, React CDN dependency, or Streamlit connection to keep alive. The optional web fonts can fail without breaking the application.

## Preserved workflows

Property creation/search/filtering; source selection; real TinyFish background research; live provider preview where available; cancellation; saved source events; comparable filtering and excluded evidence; median asking-price estimates; version selection; rename; HTML/CSV/Excel/JSON export. Existing SQLite property/run tables are reused without destructive migration. Archive/restore replaces irreversible removal from the visible library.

New workflows: evidence citations across seven categories, append-only review decisions linked to a research version, model predictions with provenance, transaction CSV validation/import, regularized log-price model training, temporal/building-separated evaluation, matched median-rate baseline, empirical interval coverage, and a model workspace with truthful empty states.

## What inactivity means

The browser has no idle session timeout. Research runs in a server worker and survives navigation, tab closure and reconnecting clients. Source research retains its existing bounded provider timeout. A server restart does not resume or replay paid calls: saved running jobs become **interrupted**, with provider references retained for inspection.

The server must stay running. Computer sleep, machine shutdown, a hosting provider's scale-to-zero policy, or process termination can still interrupt execution. Use an always-on service with persistent disk for continuous availability. Do not use free sleeping hosting or static-only Vercel hosting for this Python backend.

## Storage and access

- Default database: `groundvalue_mvp/data/reports.sqlite3`.
- Set `GROUNDVALUE_DB` to use an existing database or mounted persistent volume.
- `TINYFISH_API_KEY` remains server-side; the existing local `.env` loader still works.
- Default binding is `127.0.0.1:8080`.
- External binding requires `GROUNDVALUE_ACCESS_TOKEN`. The browser asks for this shared workspace key and retains it in that tab's session storage. It is not included in URLs.
- This is a single shared workspace, not a multi-tenant identity system. Reviewer names are self-declared. Do not represent them as authenticated signatures.
- Mutating cross-origin requests are rejected. There is no permissive CORS setting in the new app.

## Always-on deployment preparation

The included Dockerfile runs the web-only dependency set and a non-root process. Use one server instance; the current research manager supports one active research job per process. Mount persistent storage at `/data`, supply secrets through the deployment environment, and put HTTPS in front of the service. Configure automatic process restarts and an always-on plan. A public service has **not** been deployed or paid for by this migration.

```bash
docker build -t groundvalue .
# Supply GROUNDVALUE_ACCESS_TOKEN and TINYFISH_API_KEY through your secret manager/environment.
docker run --restart unless-stopped -p 8080:8080 \
  -e GROUNDVALUE_ACCESS_TOKEN -e TINYFISH_API_KEY \
  -v groundvalue-data:/data groundvalue
```

For migration to a new machine, back up the SQLite database while no research is writing, and restore it into the persistent volume. This project contains two working copies; their databases are intentionally not merged or overwritten. The parent workspace server was used for the browser verification and displays its existing saved properties.

## Model/data limits

The user has no transaction dataset yet. No trained production model, real accuracy result, imagery pipeline, official-record integration, AVM superiority or regulatory approval is claimed. The implemented training pipeline requires a cited, authorized CSV, at least 120 valid rows, and at least 60/20/20 usable training/calibration/test observations after date and building exclusions. These are prototype minimums, not evidence of statistical adequacy.

Training-only preprocessing, segment checks, out-of-range rejection, versioned coefficients, dataset hashes and per-prediction inputs are recorded. Calibrated intervals report observed held-out coverage; distribution shift may invalidate future coverage. Supporting evidence citations are context, not automatically verified facts or silently merged model inputs.

## Verification

Run from `groundvalue_mvp` with the development environment (legacy Streamlit tests need the legacy dependencies):

```bash
.venv/bin/python -m unittest discover -s tests
```

The web runtime itself only requires `requirements-web.txt`. Model tests use synthetic fixtures solely to test code correctness; those fixtures and their metrics are not inserted into the user workspace. No new paid TinyFish session was started during migration QA.
