# Verification — 29 October 2026

Final automated suite: 33 tests passed.

## Observed and fixed

- The reported connection-refused error coincided with no listener on port 8501. The server was restarted with a detached launcher. Its exact original exit cause was not captured.
- The root page, `/_stcore/health` and `/_stcore/host-config` returned HTTP 200 on localhost and 127.0.0.1.
- The actual localhost Streamlit WebSocket endpoint completed its handshake using the `streamlit` subprotocol.
- Streamlit AppTest loaded the saved real report: zero exceptions, six accepted records, ₹80.00 lakh estimate.
- Worker tests cover duplicate start prevention, stopping, isolated snapshots and deduplicated actions.
- UI tests cover the sample walkthrough, incompatible area basis, active research across reruns, Stop research, and completed-report recovery on reconnect.
- Extraction tests cover source URL restrictions, malformed fields, duplicate conflicts, source label variants, and exclusion of rentals or incompatible area bases.
- Client tests cover response contracts, schema keyword compatibility, preview/step forwarding, cancelled requests, no automatic job resubmission, and confirmed versus unconfirmed cancellation.

## Live evidence

TinyFish Agent run: `48f9d7fe-b34a-447a-b5f7-0f872031dac7`.
Seven NoBroker records returned. Six accepted after method-v3 normalization; one excluded. Six accepted asking prices / built-up areas cross-checked against separate live TinyFish Fetch page content:

| Property | Asking price INR | Built-up sq ft |
| --- | ---: | ---: |
| Country Site | 9,000,000 | 1,200 |
| Nandana Royal | 8,000,000 | 1,200 |
| Agani Velocity | 7,500,000 | 1,200 |
| Neeladri Castle | 8,000,000 | 1,200 |
| Celebrity Classic Layout | 9,500,000 | 1,390 |
| Hongirana | 6,000,000 | 1,100 |

Median rate: ₹6,666.67/sq ft. Target area: 1,200 sq ft. Estimate: ₹8,000,000. Linear percentile band: ₹7,625,000–₹8,151,079.14. This is an observed asking-price comparison, not a sale-price confidence interval.

## Limits

No full visual Chromium sign-off: the available Chromium build failed to launch in this environment. Automated Streamlit rendering and actual HTTP/WebSocket checks passed. Preview URLs were observed from real provider runs and the iframe rendering path was exercised in AppTest; embedded video playback was not visually verified here.

Housing direct pages were reported blocked; 99acres navigation previously looped. The source list does not imply guaranteed access. A provider run can finish successfully with insufficient comparable evidence, and the app then withholds the estimate.
