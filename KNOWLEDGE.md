# RouteWatch — Complete Project Knowledge Doc

---

## 1. What is this project?

- A self-collected flight tracking + delay analysis tool for India–Europe routes
- Tracks real, live flight data daily via API, builds own dataset over weeks
- Goal: understand and (eventually) predict delay risk on specific routes

## 2. Why does this project exist?

- Needed a genuine Data Science portfolio project.
- Didn't want a generic/copied project (Titanic, churn prediction, common Kaggle flight-delay clones)

## 3. Why flight delay prediction specifically?

- Real problem, not academic toy — airlines/travelers genuinely care
- Rich feature set (airline, route, time, season) — enough depth without needing deep learning
- I already have aviation domain interest/knowledge from a prior project idea (Aviora)

## 4. Why NOT the common Kaggle 2015 US flight delay dataset?

- Checked: it's overused — many near-identical student/portfolio repos use it
- Using it would make this project indistinguishable from dozens of others
- Free, ready-made *international* flight delay data doesn't exist (only US mandates public delay reporting)
- **Decision: self-collect data instead** — nobody else has this exact dataset

## 5. Why self-collected data instead of any downloadable dataset?

- Originality — this data doesn't exist pre-made for these specific routes
- Learn the *full* pipeline — real jobs involve messy live data, not clean CSVs
- Genuine story of persistence/initiative — valuable given no work experience yet

## 6. Project name: "RouteWatch"

- Simple, professional, describes function (watching specific routes over time)

## 7. Why these 3 specific routes?

**Routes chosen: BOM→FRA, DEL→CDG, BLR→AMS**

- Comparison value: 3 different European hubs (Germany/France/Netherlands) — not just Germany, richer analysis
- 3 different Indian metro cities — avoids one city's local quirks skewing results
- **Why only 3, not 10-15:**
  - Free API tier = 100 requests/month; 3 routes × daily = ~90/month, fits budget
  - 10+ routes would mean either paid plan or less-frequent checks (worse data quality)
  - Depth over breadth: 3 routes → ~30-50 landed flights each (usable); 15 routes → ~7-10 each (too few to conclude anything)
  - Deliberate portfolio scope: prioritizes finishing + understanding deeply over maximum coverage

## 8. Data source: Aviationstack API

- Free tier available (no cost barrier)
- Returns needed fields: scheduled/actual times, status, airline
- Alternatives (FlightAware, OAG) are paid/enterprise — not accessible for a student project

## 9. Tech stack (and why each)

| Tool | Why |
|---|---|
| Python | Most in-demand DS language (confirmed via job market check) |
| pandas | Data manipulation/cleaning |
| requests | API calls |
| python-dotenv | Load secrets from `.env` safely |
| scikit-learn | ML models (once modeling phase starts) |
| matplotlib/seaborn | Visualization |
| Jupyter (via VS Code) | Interactive, step-by-step data exploration |
| venv | Isolate this project's packages from others on my machine |
| Git/GitHub | Version control, portfolio visibility |

## 10. Why a virtual environment (venv)?

- Keeps this project's package versions separate from other projects — avoids version conflicts
- Standard, expected practice in real software/data jobs

## 11. Why is the API key in `.env`, not hardcoded?

- Same lesson as a security fix made on another portfolio project (E-Library): hardcoded secrets in code pushed to GitHub = publicly exposed, exploitable
- `.env` keeps the key out of code; `.gitignore` ensures `.env` is never pushed
- Reusable interview point: "I follow the practice of never committing secrets to version control"

## 12. Why append to CSV daily instead of overwriting?

- Overwriting = lose all previous days' data, no growing history
- Appending = dataset richness grows every day — needed for eventual model training

## 13. The header-row bug (and fix)

- **Bug found:** script only wrote a CSV header if file didn't exist; an empty auto-created file tricked it into skipping the header
- **Fix:** check `os.path.getsize(CSV_FILE) > 0` in addition to file existence
- **Lesson:** always verify a "file exists" check accounts for empty files too

## 14. Why filter to only completed flights before analysis?

- Concept: **target leakage / label availability**
- `scheduled`/`active` flights have no known outcome yet — including them would corrupt statistics with unknowns
- Only flights with a real, final outcome are valid training data

## 15. Data Quality Finding #1 — API's own delay field is unreliable

- Compared API's `dep_delay_min` field against manually calculated delay (actual timestamp − scheduled timestamp)
- **They didn't match** (e.g., API said 9 min, real gap was 24 min) — no consistent pattern/offset either
- **Decision:** stopped trusting the API's derived field; calculate delay myself from raw timestamps instead
- **Interview point:** "I found a data quality issue in my source, diagnosed it via cross-verification against raw data, and built my own reliable feature instead of blindly trusting the provided field."

## 16. Why `pd.to_datetime()` before doing date math?

- Raw CSV timestamps load as plain text, not real dates, to pandas
- Can't subtract text to get a time difference
- `pd.to_datetime()` converts text → real datetime objects Python can do math on

## 17. Data Quality Finding #2 — `flight_status` label lags behind reality

- Found 28 flights labeled `scheduled` that already had a real `dep_actual` timestamp (i.e., already departed)
- The status label hadn't updated yet — API staleness, not truth
- **Decision:** built independent boolean flags (`has_departed`, `has_arrived`) from raw timestamp presence, instead of trusting the status label
- **New rule:** a flight only counts as "complete, usable training data" if `has_arrived == True` — regardless of what `flight_status` says
- **Interview point:** two independent, self-found data quality issues in the first two real sessions — shows careful, skeptical analysis, not blind trust in a data source

## 18. Formalizing delay calculation into the collection script

- Originally, delay recalculation only existed inside the Jupyter notebook (temporary, has to be redone every time)
- **Decision:** moved the logic into `collect_data.py` itself via a `calculate_delay()` function — so every future day's data is analysis-ready *at collection time*, not as an afterthought
- **Lesson:** good pipelines calculate derived values during ingestion, not as a manual notebook patch

## 19. Departure delay vs arrival delay — why calculate both?

- Departure delay = did the flight *leave* late
- Arrival delay = did it *arrive* late (what actually affects a traveler — missed connections etc.)
- A flight can depart late but make up time in the air — arrival delay is the more meaningful outcome
- Calculating both lets us compare whether departure delay reliably predicts arrival delay

## 20. Known limitations (to state proactively, not hide)

- Small dataset scale (portfolio-scope, not production-scale) — deliberate tradeoff for depth of understanding
- Single month snapshot — can't yet separate "route-specific" patterns from "this month's unusual events" (weather, strikes, etc.)
- Timezone handling assumed correct (timestamps appear UTC-normalized via `+00:00` suffix) but not yet explicitly verified

## 21. Data Quality Finding #3 — route+date+airline is not a unique flight identifier

- Attempted deduplication check by grouping on route + flight_date + airline
- Found suspiciously high counts (e.g., 7 rows for one route/date/airline combination)
- **Realized the identifier was flawed:** an airline can fly the same route multiple times a day (e.g., a morning and evening flight) — route+date+airline doesn't uniquely identify a single flight
- Inspected the raw API response directly (`data['data'][0]['flight']`) to check what identifying fields actually exist
- Found a `flight.iata` field (e.g., `LH757`) — the true flight number — that had never been captured in the CSV
- **Fix:** added `flight_number` as a saved column in `collect_data.py`, going forward
- **Limitation:** only applies to data collected from this point onward — the earlier ~127 rows lack a flight number and can't be deduplicated the same reliable way. Accepted as a normal part of iterative pipeline improvement — the pipeline gets more correct over time as gaps are discovered.
- **Interview point:** demonstrates recognizing a flawed assumption (route+date+airline as a unique key) by testing it against real data rather than assuming it was correct, then going to the raw API source to find the actual correct identifier instead of guessing or working around it superficially
- **Resolution confirmed:** re-ran the same duplicate check using route+flight_date+flight_number — every group returned count of exactly 1. This confirms the earlier high counts were genuinely different flights (same airline, same route, same day, different flight numbers), not duplicate data. No rows needed to be dropped — but the investigation was still necessary, since assuming either way without checking would have been a guess, not a verified conclusion.
- **Secondary bug found and fixed:** the CSV header row had been written once, before `flight_number` was added to the script — so newer rows had 14 values but the header only listed 13 column names. This caused GitHub to fail rendering the CSV as a table, and would have caused column misalignment issues in pandas too. Fixed by manually correcting the header row to match the actual data.

## 22. Schema evolution — historical rows had inconsistent column counts

- As `collect_data.py` was improved over Days 1-4 (adding `calculated_dep_delay`, `calculated_arr_delay`, then `flight_number`), older rows in the CSV were written with fewer columns than the current header expects
- Result: Day 1-2 rows had 11 columns, some Day 3 rows had 13, Day 4 rows have the full 14 — inconsistent row widths in the same file
- This caused GitHub's CSV table renderer to fail, and would have caused column misalignment when loading into pandas
- **Fix:** wrote a one-time cleanup script that reads every row, detects short rows, and pads them with empty values in the correct position (inserting blanks for the newer columns while keeping `airline` as the last field) so every row consistently has 14 columns
- **Lesson:** this is a normal consequence of iteratively improving a data pipeline over multiple collection days — old records don't retroactively gain new fields on their own. A cleanup/migration step is needed whenever a pipeline's schema changes mid-collection.
- **Interview point:** understanding schema evolution and writing a migration fix for historical records is a real data engineering skill, not just a one-off bug fix
- **Handling the two affected fields differently, based on whether backfilling is possible:**
  - `calculated_dep_delay`/`calculated_arr_delay`: these are **always recomputed fresh in pandas** from raw timestamps (`dep_scheduled`, `dep_actual`, `arr_scheduled`, `arr_actual`) during analysis, rather than trusted from the CSV column — since raw timestamps exist for every row regardless of collection date, this works uniformly for old and new rows alike. The CSV's own calculated columns are just a convenience record, not the analysis source of truth.
  - `flight_number`: genuinely cannot be backfilled — the API wasn't asked to return it for older snapshots, and that information is permanently lost for those rows. **Accepted limitation:** rows collected before Day 4 remain usable for route/airline/time-based aggregate analysis, but excluded from any analysis requiring per-flight identity (e.g., tracking one specific flight's full history)

## 23. Progress log

| Date | Landed/Complete flights | Total rows | Key event |
|---|---|---|---|
| Day 1 | ~10 (est.) | 36 | First successful collection, 3 routes |
| Day 2 | 29 | 67 | Found delay-field mismatch (Finding #1) |
| Day 3 | 57 | 127 | Found status-lag issue (Finding #2), added `calculate_delay()` to script |
| Day 3 (cont.) | 57 | 127 | Found deduplication flaw (Finding #3) — route+date+airline not unique, added `flight_number` capture to script |
| Day 4 | TBD | 152 | First collection with flight_number included; confirmed no true duplicates existed; found and fixed 2 schema bugs (header/row column mismatch from pipeline evolving over time) |

## 24. Still to come (will update as we go)

- Continue daily collection until dataset is large enough for modeling (target: 200-300+ complete flights)
- Full EDA: delay patterns by route, airline, day of week, time of day
- Feature engineering
- Handle class imbalance (check delayed vs on-time ratio once more data exists)
- Model choice: classification (delayed/not, using 15+ min industry-standard threshold) over regression — reasoning: more robust/interpretable given dataset size
- Model training + evaluation (precision/recall/F1/ROC-AUC, not just accuracy)
- Feature importance / interpretability
- Optional: simple Streamlit interface
- Write final README with full narrative

---

*Next update: after next data collection + analysis.*