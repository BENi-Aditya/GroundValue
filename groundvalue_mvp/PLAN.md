# GroundValue MVP development plan

Owner: Aditya Tripathi. Updated 29 October 2026.

## Confirmed scope
Electronic City, Bengaluru apartment asking-price research. The user confirmed pre-event development is allowed. Streamlit is the chosen local interface. TinyFish remains central to discovery and browser extraction. Sample and live evidence remain separate.

## Completed
1. Comparison pipeline, evidence checks, duplicates, median estimate and observed band.
2. Streamlit form, CSV/HTML downloads, immutable SQLite report snapshots.
3. Detached server launcher and restartable Terminal launcher; localhost HTTP and WebSocket checks.
4. TinyFish Search discovery followed by direct-page browser extraction, seven-minute per-source cap, real action updates and cancellation.
5. Background research worker, duplicate-start guard, refresh/reconnect handling, Stop research and live preview.
6. NoBroker live validation: seven returned records, six accepted with method v3; six prices/areas cross-checked from page content. Saved live report available in the app.

## Next review checkpoints
- User tries the live studio and confirms the preview plays in their browser; embedded playback could not be visually tested here.
- Audit repeat runs, broader bedroom/area inputs and latency before promising repeatable coverage.
- Review the report layout and demo narrative with Aditya.
- Decide local laptop demo versus deployment; deployment needs multi-user isolation and durable job recovery.

## Known limits
Housing and 99acres remain experimental because of blocking/navigation problems. Data is asking prices from listings; it is not transaction evidence or an evaluated ML valuation model. No automatic enquiry or seller contact. TinyFish coding-agent installation remains separate from the working direct API integration; no persistent assistant-memory preference was written.
