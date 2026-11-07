# Hosted GroundValue

Vercel serves the landing page, Flask API and working research workspace from the same origin. Streamlit is retained only for the legacy local app.

## Private workspace

Set `GROUNDVALUE_ACCESS_TOKEN` and `TINYFISH_API_KEY` as server-only Vercel environment variables. The browser supplies the workspace key in an Authorization header. Never place either credential in a public bundle or a repository.

The linked private Vercel Blob store supplies `BLOB_READ_WRITE_TOKEN`. Production, Preview and Development each use separate snapshot prefixes. The current deployment is a single-team workspace. Everyone holding its workspace key has the same access; it is not a multi-tenant lender production service.

## Persistence and concurrency

Each API request restores the most recent immutable SQLite snapshot into a temporary per-request file. A conditional-create Blob lock serializes access across Vercel instances. Mutations upload a new snapshot before a successful response. Locks expire after six minutes to recover from a terminated invocation. Requests fail closed when storage is unavailable. Historical snapshots remain private and are retained.

This bounded prototype architecture prioritises reliable recovery for the submission. A relational database is the appropriate next step for large datasets, high concurrency and tenant isolation. Snapshot listing and database size grow with usage.

## Research lifecycle

TinyFish owns the remote browser job. Requests prepare a source, submit it once, then poll the persisted provider run ID. A submitted job continues after the browser closes. Reopening the workspace collects the result and starts the next selected source if needed. An ambiguous submission is marked failed and never automatically resubmitted, to avoid duplicate paid calls. Stop requests attempt remote cancellation and record any unconfirmed cancellation.

No browser session keeps the job alive. The app still depends on provider availability, account credits and host/storage limits. Multi-source progression resumes when a user opens the workspace.

## Checks

The test suite covers local functionality, model splitting, audit history and exports, and cloud research restart recovery, ambiguous submissions and transient polling failure. Live private storage was checked by saving and reloading an archived test property in Development. Provider research calls in unit tests are mocked to avoid chargeable duplicate runs.
