# GroundValue - Execution Plan

**Project**: Property valuation web app using TinyFish for comparable property research  
**Timeline**: 4.5 hours on November 1, 2026 (11:00 AM - 4:00 PM)  
**Owner**: Aditya Tripathi  
**Version**: 1.0 (Created October 28, 2026)

---

## Executive Summary

GroundValue is a web application that researches residential property listings and produces traceable asking-price estimates. Users input apartment details (location, size), TinyFish scrapes comparable listings from property websites, and Python validates/calculates a median-based estimate with full evidence traceability.

**Critical Success Factors:**
1. TinyFish successfully extracts data from at least 1-2 property websites
2. End-to-end flow works: form → research → calculation → report
3. Transparent failure handling (show source failures, insufficient data)
4. Reproducible calculations with audit trail

---

## Phase-by-Phase Execution Plan

### Phase 1: Project Setup & Infrastructure (30 min)
**Goal**: Working Python environment ready for development

**Tasks:**
- [ ] Create project directory structure
- [ ] Initialize Git repository
- [ ] Set up virtual environment
- [ ] Install dependencies: `streamlit`, `numpy`, `pandas`, `requests`, `python-dotenv`
- [ ] Create `.env.example` for TinyFish API key
- [ ] Set up basic module structure:
  ```
  groundvalue/
  ├── app.py                 # Streamlit entry point
  ├── tinyfish_client.py     # TinyFish API integration
  ├── research.py            # Job orchestration
  ├── normalise.py           # Data cleaning & validation
  ├── estimate.py            # Calculation engine
  ├── storage.py             # SQLite operations
  ├── report.py              # Report generation
  ├── config.py              # Configuration constants
  └── tests/
      └── fixtures/          # Test data
  ```

**Deliverables:**
- Working Python environment
- Basic module scaffolds with docstrings
- Configuration file with supported localities, timeouts

**Exit Criteria:** Can import all modules without errors

---

### Phase 2: TinyFish Integration & Source Testing (1 hour)
**Goal**: Prove TinyFish can extract usable property data from real websites

**Critical First Step**: This is the primary risk. If TinyFish cannot extract data, the entire project fails.

**Tasks:**
- [ ] Review TinyFish API documentation (endpoints, structured output)
- [ ] Test authentication with API key
- [ ] Identify 2-3 candidate property websites:
  - 99acres.com
  - MagicBricks.com
  - Housing.com
- [ ] Design structured output schema for listings:
  ```json
  {
    "listings": [
      {
        "source_url": "string",
        "title": "string",
        "project": "string | null",
        "locality": "string",
        "bedrooms": "integer | null",
        "transaction_type": "string",
        "price_raw": "string",
        "area_raw": "string",
        "area_basis": "string | null",
        "listed_at": "string | null"
      }
    ]
  }
  ```
- [ ] Write task prompts for TinyFish:
  - "Navigate to [URL], search for 2 BHK apartments for sale in Electronic City, Bengaluru"
  - "Extract up to 10 property listings with price, area, locality"
  - "Open detail pages if needed, return null for missing fields"
- [ ] Implement `tinyfish_client.py`:
  - `run_automation()` - POST to /v1/automation/run-sse
  - `stream_events()` - Parse SSE stream
  - `get_run_status()` - Fallback polling endpoint
  - Error handling for auth failures, timeouts
- [ ] Test live extraction from 1 website
- [ ] Manually verify 5-10 extracted records against source pages
- [ ] Save successful response as fixture for testing

**Implementation Gate**: Must successfully extract ≥5 valid property records from at least 1 website before proceeding.

**Deliverables:**
- Working TinyFish client with SSE streaming
- Validated extraction from 1-2 property websites
- Test fixtures with real extraction examples
- Documentation of which sources work

**Exit Criteria:** 
- Can trigger TinyFish run programmatically
- Receive structured property data back
- Fields match source pages (price, area, locality verified)

---

### Phase 3: Data Normalization & Validation (45 min)
**Goal**: Clean and validate extracted data with proper rule enforcement

**Tasks:**
- [ ] Implement `normalise.py` with functions:
  - `parse_inr_price()` - Convert "75 lakh", "1.5 crore" to rupees
  - `parse_area()` - Extract number and unit from area strings
  - `convert_to_sqft()` - Convert m² to sq ft (× 10.7639)
  - `validate_listing()` - Apply acceptance rules
  - `detect_duplicates()` - Group by project/locality/size/price
  - `normalize_area_basis()` - Standardize "carpet/built-up/super built-up"

**Validation Rules:**
1. Must be "sale" transaction (not rental)
2. Must be residential apartment (not plot/commercial)
3. Must match target locality exactly
4. Must match target bedroom count
5. Must have valid positive price in INR
6. Must have valid positive area
7. Must have same area basis as target (or explicitly null)
8. Must be within ±25% of target area size
9. Exclude "price on request" or ambiguous ranges

**Duplicate Detection Heuristic:**
- Normalize project name (lowercase, remove spaces/punctuation)
- Create tuple: (project, locality, bedrooms, floor(area/10), floor(price/100000))
- Group listings with matching tuples
- Keep only one representative per group
- Flag uncertain duplicates for inspection

**Edge Cases:**
- Missing area basis → exclude with reason "unknown area basis"
- Multiple prices listed → take first parseable one
- Different units within same listing → parse both, prioritize sq ft
- Extreme outliers (>3σ from median) → flag but don't auto-exclude

**Deliverables:**
- Robust parsing for Indian real estate text formats
- Clear validation with exclusion reasons tracked
- Duplicate detection algorithm
- Unit tests with edge cases

**Exit Criteria:**
- Can parse "75 lakh" → 7,500,000
- Can parse "100 m²" → 1,076.39 sq ft
- Correctly excludes rentals, wrong bedrooms, wrong locality
- Deduplicates same property listed on multiple sites

---

### Phase 4: Database Schema & Storage (30 min)
**Goal**: Persistent storage for requests, research runs, and evidence

**SQLite Schema:**

```sql
-- Property requests from users
CREATE TABLE requests (
    request_id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    city TEXT NOT NULL,
    locality TEXT NOT NULL,
    property_type TEXT NOT NULL,
    bedrooms INTEGER NOT NULL,
    area REAL NOT NULL,
    area_unit TEXT NOT NULL,
    area_basis TEXT NOT NULL,
    project TEXT,
    age_years INTEGER,
    floor INTEGER,
    amenities TEXT,
    user_asking_price REAL
);

-- TinyFish jobs per source
CREATE TABLE jobs (
    job_id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL,
    source_domain TEXT NOT NULL,
    starting_url TEXT NOT NULL,
    provider_run_id TEXT,
    status TEXT NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    failure_reason TEXT,
    FOREIGN KEY (request_id) REFERENCES requests(request_id)
);

-- Raw listings from TinyFish
CREATE TABLE listings (
    listing_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    source_url TEXT NOT NULL,
    source_domain TEXT NOT NULL,
    title TEXT,
    project TEXT,
    locality TEXT,
    bedrooms INTEGER,
    transaction_type TEXT,
    price_raw TEXT,
    area_raw TEXT,
    area_basis TEXT,
    listed_at TEXT,
    retrieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(job_id)
);

-- Normalized and validated evidence
CREATE TABLE evidence (
    evidence_id TEXT PRIMARY KEY,
    listing_id TEXT NOT NULL,
    request_id TEXT NOT NULL,
    price_inr REAL,
    area_sqft REAL,
    rate_inr_sqft REAL,
    area_basis TEXT,
    is_valid BOOLEAN NOT NULL,
    validation_flags TEXT,
    duplicate_group TEXT,
    inclusion_reason TEXT,
    exclusion_reason TEXT,
    FOREIGN KEY (listing_id) REFERENCES listings(listing_id),
    FOREIGN KEY (request_id) REFERENCES requests(request_id)
);

-- Generated reports
CREATE TABLE reports (
    report_id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL,
    version INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    method_version TEXT NOT NULL,
    included_count INTEGER NOT NULL,
    excluded_count INTEGER NOT NULL,
    median_rate REAL,
    p25_rate REAL,
    p75_rate REAL,
    estimated_price REAL,
    lower_band REAL,
    upper_band REAL,
    warnings TEXT,
    FOREIGN KEY (request_id) REFERENCES requests(request_id)
);
```

**Tasks:**
- [ ] Implement `storage.py` with functions:
  - `init_db()` - Create tables if not exist
  - `save_request()`, `get_request()`
  - `save_job()`, `update_job_status()`
  - `save_listing()`, `get_listings_for_job()`
  - `save_evidence()`, `get_evidence_for_request()`
  - `save_report()`, `get_latest_report()`
- [ ] Add indexes for common queries
- [ ] Implement report versioning (increment on refresh)

**Deliverables:**
- Complete SQLite schema
- CRUD operations for all entities
- Connection pooling/management
- Migration-ready structure

**Exit Criteria:**
- Can store and retrieve all data types
- Foreign key constraints enforced
- No data loss on concurrent access

---

### Phase 5: Estimation Engine (45 min)
**Goal**: Calculate reproducible median-based estimates with proper filtering

**Calculation Method:**
1. Filter evidence to "valid" records only
2. Further filter by matching rules:
   - Same locality as target
   - Same bedroom count as target
   - Same area basis as target (or all null)
   - Area within ±25% of target area
3. Calculate rate per sq ft for each: `rate = price_inr / area_sqft`
4. If <5 comparable properties remain → return "insufficient evidence"
5. Calculate statistics using NumPy:
   - `median_rate = np.median(rates)`
   - `p25_rate = np.percentile(rates, 25, method='linear')`
   - `p75_rate = np.percentile(rates, 75, method='linear')`
6. Apply to target:
   - `estimated_price = target_area_sqft × median_rate`
   - `lower_band = target_area_sqft × p25_rate`
   - `upper_band = target_area_sqft × p75_rate`

**Tasks:**
- [ ] Implement `estimate.py` with functions:
  - `filter_comparables()` - Apply matching rules
  - `calculate_rates()` - Price per sq ft
  - `calculate_estimate()` - Main estimation logic
  - `generate_warnings()` - Quality indicators
- [ ] Track which evidence influenced calculation
- [ ] Generate warning messages:
  - Single source only (if one source failed)
  - Wide price spread (if IQR > 50% of median)
  - Old listings (if >50% have unknown dates)
  - Small sample (if n < 10)
  - Area basis uncertainty
  - Unresolved conflicts

**Test with PRD Example:**
```python
# Input: 1,200 sq ft target
comparables = [
    {"price": 7080000, "area": 1200},  # Rate: 5900
    {"price": 7200000, "area": 1200},  # Rate: 6000
    {"price": 7440000, "area": 1200},  # Rate: 6200
    {"price": 7800000, "area": 1200},  # Rate: 6500
    {"price": 8280000, "area": 1200},  # Rate: 6900
]

# Expected output:
# Median rate: 6200
# Estimate: 74,40,000 (74.4 lakh)
# Band: 72,00,000 - 78,00,000 (72-78 lakh)
```

**Deliverables:**
- Deterministic calculation engine
- Reproducible results (same inputs → same outputs)
- Clear evidence trail (which listings influenced result)
- Quality warnings based on evidence

**Exit Criteria:**
- PRD example returns exactly 74.4 lakh with 72-78 lakh band
- <5 comparables returns "insufficient evidence"
- Calculation is repeatable (same result on re-run)

---

### Phase 6: Research Orchestration (30 min)
**Goal**: Manage multi-source jobs with timeouts and failure handling

**Tasks:**
- [ ] Implement `research.py` with functions:
  - `create_research_plan()` - Generate jobs for each configured source
  - `execute_job()` - Run single TinyFish job with timeout
  - `orchestrate_research()` - Manage parallel/sequential execution
  - `handle_timeout()` - Cancel TinyFish runs at deadline
  - `retry_transient_failure()` - Retry logic (max 1 retry)
- [ ] Configuration:
  - Per-source timeout: 180 seconds
  - Overall timeout: 300 seconds (5 minutes)
  - Max records per source: 10
  - Supported sources: list of (domain, starting_url, task_prompt)
- [ ] State machine for job status:
  - QUEUED → RUNNING → COMPLETED
  - QUEUED → RUNNING → FAILED
  - RUNNING → CANCELLED (on timeout)
- [ ] Partial success handling:
  - If 1 of 2 sources fails but ≥5 valid properties remain
  - Generate report with "single source warning"
  - Show failed source in evidence report

**Deliverables:**
- Multi-source job orchestration
- Timeout enforcement with cancellation
- Retry logic for transient failures
- State tracking for UI updates

**Exit Criteria:**
- Can run 2 sources in parallel or sequence
- Enforces 180s per source, 300s total
- Returns partial results on single source failure
- Cancels remote TinyFish runs on timeout

---

### Phase 7: Streamlit UI - Property Request Form (30 min)
**Goal**: Screen 1 - User input with validation

**Form Fields:**
- City: Fixed to "Bengaluru" (dropdown disabled for MVP)
- Locality: Text input (only "Electronic City" supported initially)
- Property Type: Fixed to "Apartment" 
- Bedrooms: Number input (1-5 BHK)
- Area: Number input (positive only)
- Area Unit: Radio ("sq ft" / "sq m")
- Area Basis: Required dropdown ("Carpet" / "Built-up" / "Super Built-up")
- Project Name: Optional text input
- Age: Optional number input (years)
- Floor: Optional number input
- Amenities: Optional text area
- Your Asking Price: Optional number input (for comparison)

**Validation:**
- [ ] Check locality is in supported list (config)
- [ ] Validate positive area and bedroom count
- [ ] Show error if unsupported locality entered
- [ ] Disable "Research Property" button while validation fails
- [ ] Convert units to internal format (always store as sq ft)
- [ ] Generate request_id (UUID)

**UI Text:**
```
"GroundValue - Property Research"

"Enter your property details to research comparable listings."

[Coverage Notice]
"Currently supported: Electronic City, Bengaluru"

[Form]

[Button: Research Property]

"This will search selected property websites and calculate an 
indicative asking-price estimate based on similar listings."
```

**Deliverables:**
- Clean form UI with proper labels
- Client-side validation
- Coverage limitations clearly stated
- Submit creates request in database

**Exit Criteria:**
- Form validates before submission
- Shows error for unsupported coverage
- Generates request record in SQLite

---

### Phase 8: Streamlit UI - Research Progress (30 min)
**Goal**: Screen 2 - Real-time progress display

**Display Elements:**
- [ ] Progress bar for overall research
- [ ] Per-source status cards:
  ```
  [Source: 99acres.com]
  Status: Running... (45s elapsed)
  Records fetched: 7
  Records validated: 5
  
  [Source: MagicBricks.com]
  Status: Queued
  ```
- [ ] Event log (scrollable):
  ```
  11:23:45 - Started research for Electronic City
  11:23:46 - Launched job for 99acres.com
  11:23:47 - TinyFish navigating to search page
  11:24:05 - Extracted 7 listings
  11:24:06 - Validated: 5 passed, 2 excluded (wrong locality)
  11:24:07 - Launched job for MagicBricks.com
  ...
  ```
- [ ] Disable duplicate submissions (check for active jobs)
- [ ] Cancel button (calls TinyFish cancellation)
- [ ] Auto-refresh every 2 seconds while jobs running

**State Updates:**
- Poll database for job status updates
- Show TinyFish events if SSE streaming works
- Transition to report screen when all jobs complete/fail

**Deliverables:**
- Live progress display
- Event log with timestamps
- Source-level status tracking
- Prevents duplicate submissions

**Exit Criteria:**
- Updates in real-time as research progresses
- Shows both successful and failed sources
- Transitions to report when complete

---

### Phase 9: Streamlit UI - Evidence Report (45 min)
**Goal**: Screen 3 - Display estimate and traceable evidence

**Report Layout:**

**1. Estimate Summary (top)**
```
┌─────────────────────────────────────────────────────┐
│ Indicative Asking Price Estimate                    │
│                                                      │
│ ₹ 74,40,000 (74.4 lakh)                            │
│                                                      │
│ Observed comparison band: ₹ 72-78 lakh              │
│                                                      │
│ Based on 5 similar advertised properties with a     │
│ median rate of ₹ 6,200 per sq ft, applied to your │
│ 1,200 sq ft property.                               │
└─────────────────────────────────────────────────────┘
```

**2. Quality Indicators**
- Number of comparable properties used
- Number of sources (with failed source warnings)
- Area basis matches
- Date coverage (% with known listing dates)
- Price spread indicator

**3. Comparable Properties Table**
- Source URL (clickable)
- Project name
- Locality
- Bedrooms
- Area (sq ft)
- Area basis
- Asking price (INR)
- Rate per sq ft
- Retrieved at timestamp

**4. Exclusions Section** (collapsible)
- List excluded listings with reasons:
  - "Wrong locality (Whitefield, not Electronic City)"
  - "Rental listing (not for sale)"
  - "Missing area basis"
  - "Area outside ±25% range"
  - "Duplicate of listing #3"

**5. Source Status**
- Success: 99acres.com (7 fetched, 5 used)
- Failed: MagicBricks.com (timeout after 180s)

**6. Downloads**
- [Download HTML Report]
- [Download Evidence CSV]

**Insufficient Evidence Case:**
```
┌─────────────────────────────────────────────────────┐
│ Insufficient Evidence                                │
│                                                      │
│ Only 3 comparable properties found. At least 5 are  │
│ needed to calculate a reliable estimate.            │
│                                                      │
│ Reasons for low matches:                            │
│ - MagicBricks.com failed (connection timeout)       │
│ - 4 listings excluded for wrong area basis          │
│ - 2 listings excluded as duplicates                 │
└─────────────────────────────────────────────────────┘
```

**Tasks:**
- [ ] Implement `report.py`:
  - `format_currency()` - Display ₹ 74,40,000 (74.4 lakh)
  - `generate_html_report()` - Standalone HTML file
  - `generate_csv_export()` - Evidence spreadsheet
- [ ] Display calculation methodology
- [ ] Make source URLs clickable (open in new tab)
- [ ] Show exclusion reasons clearly
- [ ] Handle insufficient evidence case
- [ ] Implement downloads with proper escaping

**Deliverables:**
- Clear estimate display with explanation
- Traceable evidence table
- Exclusion transparency
- HTML/CSV exports
- Insufficient evidence handling

**Exit Criteria:**
- User can see estimate and click through to source pages
- Can download report offline
- Exclusions are transparent and justified
- Shows clear message when data insufficient

---

### Phase 10: Testing & Validation (45 min)
**Goal**: Verify all acceptance tests from PRD

**Test Suite:**

1. **Live Integration Test**
   - [ ] Trigger real TinyFish job
   - [ ] Verify records returned with source URLs
   - [ ] Confirm not using cached fixtures
   - Label any fixture-based tests clearly

2. **Extraction Audit**
   - [ ] Manually verify 10 source pages
   - [ ] Check price matches extracted value
   - [ ] Check area matches extracted value
   - [ ] Check locality matches extracted value
   - [ ] Check area basis matches extracted value
   - [ ] Document mismatches and fix parsing

3. **Currency and Units Test**
   ```python
   assert parse_inr_price("75 lakh") == 7500000
   assert parse_inr_price("1.5 crore") == 15000000
   assert convert_to_sqft(100, "sqm") == 1076.39
   ```

4. **Area Mismatch Test**
   - [ ] Create request with "carpet" area basis
   - [ ] Mix carpet and super built-up in evidence
   - [ ] Verify super built-up excluded from estimate
   - [ ] Verify exclusion reason shown

5. **Duplicate Evidence Test**
   - [ ] Same URL appears twice → counted once
   - [ ] Same property on different sites → grouped
   - [ ] One representative kept per duplicate group

6. **Minimum Evidence Test**
   - [ ] 4 valid comparables → no estimate, show message
   - [ ] 5 valid comparables → estimate generated

7. **Math Regression Test**
   - [ ] Use PRD example data (page 5)
   - [ ] Verify returns 74.4 lakh
   - [ ] Verify band is 72-78 lakh
   - [ ] Verify median rate is 6200

8. **Failure and Timeout Test**
   - [ ] Simulate source timeout
   - [ ] Verify failed source shown in report
   - [ ] Verify partial report if ≥5 valid remain
   - [ ] Verify "insufficient evidence" if <5 remain

9. **Repeatability Test**
   - [ ] Run calculation twice with same evidence
   - [ ] Verify identical numeric results
   - [ ] Verify same listings included/excluded

**Test Data:**
- [ ] Create fixture with 10 valid listings
- [ ] Create fixture with insufficient data
- [ ] Create fixture with duplicates
- [ ] Create fixture with area basis conflicts

**Metrics to Collect:**
- Successful run rate
- Field extraction accuracy (per field)
- Elapsed time (by phase)
- API cost per run

**Deliverables:**
- All 9 acceptance tests passing
- Test fixtures for regression testing
- Documented test results
- Known issues log

**Exit Criteria:**
- All PRD acceptance tests pass
- Math regression test returns exact values
- Happy path and failure path both verified

---

### Phase 11: Demo Preparation & Documentation (30 min)
**Goal**: Ready for 4:00 PM demo with clear narrative

**Demo Script:**

1. **Introduction** (1 min)
   - "GroundValue researches property listings and calculates traceable asking-price estimates"
   - Show the problem: manual research is time-consuming and inconsistent

2. **Submit Request** (1 min)
   - Show form with 2 BHK, 1200 sq ft apartment in Electronic City
   - Click "Research Property"

3. **Show Research Progress** (1 min)
   - Point out real TinyFish agent activity
   - Show sources being queried
   - Show record counts updating

4. **Review One Source Listing** (2 min)
   - Click through to actual property website
   - Show the listing on 99acres.com
   - Compare displayed price/area with extracted values
   - "This is the actual source - we link back to it"

5. **Explain Estimate** (2 min)
   - Show the comparable properties table
   - "5 similar properties, median rate ₹6,200/sq ft"
   - "Applied to your 1,200 sq ft property = ₹74.4 lakh"
   - Point to 72-78 lakh band

6. **Show Transparency** (1 min)
   - Expand exclusions section
   - "2 listings excluded as duplicates"
   - "3 listings excluded for wrong area basis"
   - "This is why we excluded them"

7. **Demonstrate Failure Handling** (1 min)
   - Submit request that will fail (no coverage)
   - OR show cached example of insufficient evidence
   - "We tell you clearly when we don't have enough data"

8. **Conclusion** (1 min)
   - "Every number traces back to a real listing"
   - "We show our work, not a black box"
   - Future: expand cities, add transaction data, ML models

**Supporting Materials:**
- [ ] README.md with setup instructions
- [ ] DEMO_CHECKLIST.md with pre-flight checks
- [ ] Test cases document
- [ ] Architecture diagram (optional but helpful)
- [ ] Known limitations documented

**Pre-Demo Checklist:**
- [ ] API key loaded and working
- [ ] Database populated with one cached successful run
- [ ] Sources confirmed accessible (not blocked)
- [ ] Form pre-filled with working example
- [ ] Browser has source website open in tab for quick comparison
- [ ] Backup plan if live API fails (use cached run)

**Deliverables:**
- Demo script with timing
- Pre-flight checklist
- Setup documentation
- Known issues documented
- Backup plan for API failure

**Exit Criteria:**
- Demo runs smoothly in <10 minutes
- Shows end-to-end flow convincingly
- Demonstrates transparency and traceability
- Has fallback if live API fails

---

## Time Budget for November 1st Build

| Time | Phase | Duration |
|------|-------|----------|
| 10:00-11:00 | Official workshop (account setup) | 1h |
| 11:00-11:30 | Phase 1: Project Setup | 30m |
| 11:30-12:30 | Phase 2: TinyFish Integration ⚠️ CRITICAL | 1h |
| 12:30-13:00 | Phase 3: Normalization | 30m |
| 13:00-13:30 | 🍽️ Lunch + Phase 4: Database | 30m |
| 13:30-14:00 | Phase 5: Estimation Engine | 30m |
| 14:00-14:30 | Phase 6: Research Orchestration | 30m |
| 14:30-15:00 | Phase 7-9: Streamlit UI (all 3 screens) | 30m |
| 15:00-15:30 | Phase 10: Testing | 30m |
| 15:30-16:00 | Phase 11: Demo Prep + Buffer | 30m |
| 16:00-17:00 | Official demos and judging | 1h |

**Total Coding Time: 4.5 hours (11:00 AM - 3:30 PM)**

---

## Critical Path & Risk Mitigation

### Critical Path Items (Cannot Proceed Without)
1. ⚠️ **TinyFish source validation** (Phase 2) - THE PRIMARY RISK
   - If no source works, entire project fails
   - Test this FIRST on November 1st
   - Fallback: demonstrate with fixtures if API fails during demo

2. **Estimation math correctness** (Phase 5)
   - Must match PRD example exactly
   - Build against fixtures first to decouple from API

3. **End-to-end flow** (Phases 7-9)
   - Form → research → report must work
   - Better to have ugly UI that works than pretty UI that's incomplete

### Things We Can Cut If Time Runs Short
1. Second source (operate with 1 source only)
2. CSV export (keep HTML only)
3. Refresh functionality
4. Visual polish on UI
5. Browser preview of source pages
6. Project/age/amenity fields
7. Fancy progress animations

### Things We Must NOT Cut
1. Source attribution (URLs must be visible)
2. Exclusion transparency (must show why listings excluded)
3. Insufficient evidence handling (must not invent data)
4. Validation rules (must enforce area basis, locality matching)
5. Real TinyFish integration (fixtures only for testing, not demo)

---

## Configuration Files Needed

### config.py
```python
# Supported coverage
SUPPORTED_CITIES = ["Bengaluru"]
SUPPORTED_LOCALITIES = {
    "Bengaluru": ["Electronic City"]
}

# Timeouts
SOURCE_TIMEOUT_SECONDS = 180  # 3 minutes per source
TOTAL_TIMEOUT_SECONDS = 300   # 5 minutes overall
MAX_RECORDS_PER_SOURCE = 10
MAX_RETRY_ATTEMPTS = 1

# Estimation rules
MIN_COMPARABLES_FOR_ESTIMATE = 5
MAX_AREA_DEVIATION_PERCENT = 25  # ±25%
SQFT_PER_SQM = 10.7639

# Source configuration
SOURCES = [
    {
        "domain": "99acres.com",
        "start_url": "https://www.99acres.com/search/property/buy/bangalore-south?keyword=Electronic%20City",
        "task_prompt": "Search for 2 BHK apartments for sale in Electronic City. Extract up to 10 listings with price, area, and locality details."
    },
    {
        "domain": "magicbricks.com",
        "start_url": "https://www.magicbricks.com/property-for-sale/residential-real-estate?bedroom=2&proptype=Multistorey-Apartment,Builder-Floor-Apartment,Penthouse,Studio-Apartment,Residential-House,Villa&cityName=Bangalore&locality=Electronic-City",
        "task_prompt": "Search for 2 BHK apartments for sale in Electronic City, Bangalore. Extract up to 10 listings with asking price, area in sqft or sqm, and exact locality."
    }
]

# TinyFish API
TINYFISH_API_BASE = "https://agent.tinyfish.ai/v1"
TINYFISH_SSE_ENDPOINT = "/automation/run-sse"
TINYFISH_STATUS_ENDPOINT = "/automation/run"
```

### .env.example
```bash
TINYFISH_API_KEY=your_api_key_here
DATABASE_PATH=./groundvalue.db
LOG_LEVEL=INFO
```

---

## Success Metrics

### Must Achieve (Minimum Viable Prototype)
- [ ] TinyFish extracts ≥5 valid listings from 1 source
- [ ] Form → research → report flow works end-to-end
- [ ] Calculation matches PRD example (74.4 lakh)
- [ ] Source URLs visible and clickable
- [ ] Exclusion reasons shown
- [ ] Insufficient evidence case handled gracefully
- [ ] Demo completes in <10 minutes

### Should Achieve (Target Goals)
- [ ] TinyFish extracts from 2 sources
- [ ] >80% field extraction accuracy
- [ ] Duplicate detection working
- [ ] HTML/CSV exports
- [ ] All 9 acceptance tests pass
- [ ] <5 minute research time

### Could Achieve (Stretch Goals)
- [ ] Refresh functionality
- [ ] Report versioning
- [ ] Visual source preview
- [ ] Project/amenity filtering

---

## Open Decisions Requiring Mentors (11:00-11:30 AM)

1. **Source Access**: Which property websites are confirmed accessible and permitted?
   - Test 99acres, MagicBricks, Housing.com
   - Confirm no blocking/CAPTCHA issues

2. **API Budget**: How many event credits available for testing + demo?
   - Need at least 10-15 test runs before demo
   - Need 2-3 runs during demo

3. **Preparation Rules**: Can we pre-build the project structure before November 1st?
   - Is this PRD-based planning allowed?
   - Can we test TinyFish integration before the event?

4. **Cross-Submission**: Can same code be submitted to both TinyFish finale and iHack?
   - Different submission deadlines
   - Different evaluation criteria

---

## Next Steps (Before November 1st)

### Immediate (Today - October 28)
- [ ] Review this execution plan
- [ ] Identify any gaps or concerns
- [ ] Confirm TinyFish API access
- [ ] Test basic authentication

### By October 30
- [ ] Manually research 2-3 property websites
- [ ] Document HTML structure and data patterns
- [ ] Prepare task prompt templates
- [ ] Create test fixtures with realistic data

### Morning of November 1 (Before 11:00 AM)
- [ ] Verify API key works
- [ ] Set up development environment
- [ ] Have PRD and execution plan open
- [ ] Join workshop with questions ready

---

## Post-Event: iHack Expansion Path

The TinyFish prototype is the foundation. For the full Hero Housing iHack submission:

1. **Data Expansion** (Week 1-2)
   - Secure transaction dataset (actual sale prices)
   - Add geospatial data (distance to amenities, transit)
   - Add regulatory data (zoning, approvals)

2. **Model Development** (Week 2-3)
   - Baseline: median comparable (already built)
   - Linear regression with property attributes
   - Gradient boosting (XGBoost/LightGBM)
   - Time-based test split (no data leakage)

3. **Validation** (Week 3)
   - Measure MAE, MAPE against held-out test set
   - Compare to baseline and existing AVMs if available
   - Generate prediction intervals
   - Evaluate by locality and property type

4. **Production Features** (Week 4)
   - Lender workflow UI
   - Human review queue for uncertain cases
   - Model explainability (SHAP values)
   - Audit trail and compliance logging
   - Scheduled data refresh

5. **Scale & Cities** (Week 5)
   - Add Mumbai, Delhi NCR, Hyderabad
   - Commercial property types
   - API for integration with lending systems

---

## Contact & Resources

**Owner**: Aditya Tripathi  
**Event Date**: November 1, 2026  
**Event**: Swim with TinyFish @ Scaler School of Technology

**Documentation:**
- TinyFish Docs: https://docs.tinyfish.ai/
- TinyFish Event: https://thenymble.com/events/swim-with-tinyfish-scaler-school-of-technology
- Hero Housing Brief: [Google Slides link in PRD]

**Repository Structure** (to be created):
```
groundvalue/
├── README.md
├── EXECUTION_PLAN.md (this file)
├── requirements.txt
├── .env.example
├── .gitignore
├── app.py
├── config.py
├── tinyfish_client.py
├── research.py
├── normalise.py
├── estimate.py
├── storage.py
├── report.py
├── tests/
│   ├── test_normalise.py
│   ├── test_estimate.py
│   └── fixtures/
│       ├── sample_tinyfish_response.json
│       └── sample_listings.json
└── docs/
    ├── DEMO_SCRIPT.md
    └── ARCHITECTURE.md
```

---

## Conclusion

This execution plan provides a structured approach to building GroundValue in 4.5 hours. The critical path focuses on proving TinyFish integration first, then building calculation and UI layers. Success requires disciplined time management and willingness to cut non-essential features if needed.

**Remember**: 
- Transparent failure is better than opaque success
- Source attribution is non-negotiable
- A working single-source prototype beats an incomplete multi-source attempt
- The calculation must be reproducible and explainable

Good luck with the build! 🚀
