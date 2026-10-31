# GroundValue

A local TinyFish-powered property research MVP for Electronic City, Bengaluru.

## Start on this Mac

```bash
cd /Users/tripathd/Documents/Codex/2026-10-27/new-chat-2/groundvalue
.venv/bin/python start_local.py
```

Open http://localhost:8501. The launcher detaches the server from the temporary command session, writes startup output to `data/server.log`, and verifies the health endpoint before reporting success. Running it again reuses a responding server. It is not an operating-system service: relaunch after reboot or if the server stops.

Alternatively, double-click `Start-GroundValue.command` and keep that Terminal window open.

## Try the verified live report

Select **Live TinyFish**, then **Open latest saved live report**. The development machine has the validated 29 October 2026 report saved locally. Opening it does not spend credits or fetch new data. A portable HTML copy is included in `examples/validated-live-report.html`.

To perform fresh research, choose **NoBroker**, 2 bedrooms, 1,200 sq ft and **Built-up**, then **Research live properties**. Actual results can change. TinyFish credits are used only when a new run is started. Allow up to seven minutes of browsing per source plus discovery; at most two sources can be selected.

The live studio shows elapsed time, real browser actions, a read-only TinyFish browser preview when supplied, source run identifiers, and a Stop research button. Browser previews expire. If the iframe cannot load, use its external preview link. There is no simulated completion percentage.

Research runs in a background worker. Refreshing or reconnecting resumes the view while the server remains alive; it does not submit a new paid job. One research job can run at a time on this local app. The stop signal cancels the current provider run and skips remaining sources; it may take a pending HTTP request plus cancellation request to finish. Cancellation confirmation is recorded when the API provides it. Server restarts cannot recover an in-memory worker; the provider run has its own duration cap.

## Live validation

On 29 October 2026, TinyFish completed a NoBroker browser run and returned seven listings. After correcting real-source label normalization (Resale, Builtup Area, 2 BHK Flat, explicit sub-locality notation), six passed the comparison rules and one was excluded because its extracted locality did not establish Electronic City. The same captured raw records were reprocessed with method v3; no evidence values were edited to manufacture a result.

For 2 BHK / 1,200 sq ft / Built-up, the report produced ₹80 lakh with a ₹76.25–81.51 lakh observed comparison band. All six accepted prices and built-up areas were checked against a separate live TinyFish Fetch retrieval. This validates extraction and calculation for that run, not market accuracy, seller claims, or availability. The evidence is from one source and spans different buildings, ages and furnishing levels.

Housing.com blocked the direct listing browser run. Earlier homepage searches on Housing and 99acres timed out or looped. Those sources remain experimental; an empty or failed source never causes sample data to be substituted. NoBroker is the default live source.

## How it works

1. TinyFish Search discovers public sale pages or individual listing URLs.
2. TinyFish Agent visits the discovered pages and extracts original fields. Search snippets are not used as valuation evidence.
3. The backend validates URLs, explicit locality labels, apartment type, sale/resale, bedrooms, area basis, and the ±25% size window. It removes duplicates and flags conflicts.
4. At least five accepted records are required. The median asking rate per sq ft is multiplied by the target area; the observed band uses linear 25th/75th percentiles.
5. SQLite saves immutable report snapshots. HTML and CSV exports retain evidence mode. Sample mode is explicitly synthetic.

## Fresh installation

Use Python 3.11 or later on macOS. Create `.venv`, then install `requirements.txt`. Set `TINYFISH_API_KEY=your_key` in a private `.env` beside `app.py`, or provide the environment variable. Never share the key. The source archive excludes credentials, virtual environments, browser captures, logs, and local databases.

## Verification and limitations

Run `.venv/bin/python -m unittest discover -s tests -v`. Tests mock provider requests and do not spend credits. See `VERIFICATION.md` for the checked behavior and the limits of visual testing.

This is an asking-price research prototype, not a trained valuation model or a bank appraisal. It binds to loopback and shares one worker among local sessions; it is not a multi-user production deployment.

API references checked 29 October 2026:
- https://docs.tinyfish.ai/agent-api/reference
- https://docs.tinyfish.ai/search-api/reference
- https://docs.tinyfish.ai/key-concepts/structured-output
- https://docs.tinyfish.ai/live-preview
- https://docs.streamlit.io/develop/api-reference/execution-flow/st.fragment

## Property library redesign

Restart the launcher after upgrading so the research worker loads the new persistent-run hooks. The app opens to a light-themed property library; the small appearance button switches to neutral dark mode. Research is live-only. Existing live reports import once into projects; synthetic reports are not imported. Current research coverage remains Electronic City sale apartments. Addresses/notes are project metadata, not geocoded inputs.

Projects and complete run snapshots use additional tables in the existing SQLite database. Removing a project archives it, preserving its history. Excel exports contain six sheets with inline-string text cells (no user-supplied formulas). The browser viewer only displays provider-supplied streaming URLs while the run is active. Server restarts interrupt local workers; an unmatched saved running session is explicitly labeled as potentially interrupted.
