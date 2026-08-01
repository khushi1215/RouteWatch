# RouteWatch: Complete Project Knowledge Doc

---

## 1. What is this project?

- A self-collected flight tracking + delay analysis tool for India–Europe routes
- Tracks real, live flight data daily via API, builds own dataset over weeks
- Goal: understand and (eventually) predict delay risk on specific routes

## 2. Why does this project exist?

- Needed a genuine Data Science portfolio project
- Didn't want a generic/copied project (Titanic, churn prediction, common Kaggle flight-delay clones)
- Europe has always been high on my travel bucket list, wanted a project rooted in genuine personal curiosity, not an assigned topic

## 3. Why flight delay prediction specifically?

- Real problem, not academic toy, airlines/travelers genuinely care
- Rich feature set (airline, route, time, season), enough depth without needing deep learning
- I already have aviation domain interest/knowledge from a prior project idea (Aviora)

## 4. Why NOT the common Kaggle 2015 US flight delay dataset?

- Checked: it's overused, many near-identical student/portfolio repos use it
- Using it would make this project indistinguishable from dozens of others
- Free, ready-made *international* flight delay data doesn't exist (only US mandates public delay reporting)
- **Decision: self-collect data instead**, nobody else has this exact dataset

## 5. Why self-collected data instead of any downloadable dataset?

- Originality, this data doesn't exist pre-made for these specific routes
- Learn the *full* pipeline, real jobs involve messy live data, not clean CSVs
- Genuine story of persistence/initiative, valuable given no work experience yet

## 6. Project name: "RouteWatch"

- Simple, professional, describes function (watching specific routes over time)

## 7. Why these 3 specific routes?

**Routes chosen: BOM→FRA, DEL→CDG, BLR→AMS**

- Comparison value: 3 different European hubs (Germany/France/Netherlands), richer analysis than a single-country focus
- 3 different Indian metro cities, avoids one city's local quirks skewing results
- Reflects genuine interest in exploring different parts of Europe, not just one destination
- **Why only 3, not 10-15:**
 - Free API tier = 100 requests/month. 3 routes x daily = ~90/month, fits budget
 - 10+ routes would mean either paid plan or less-frequent checks (worse data quality)
 - Depth over breadth: 3 routes → ~30-50 landed flights each (usable). 15 routes → ~7-10 each (too few to conclude anything)
 - Deliberate portfolio scope: prioritizes finishing + understanding deeply over maximum coverage

## 8. Data source: Aviationstack API

- Free tier available (no cost barrier)
- Returns needed fields: scheduled/actual times, status, airline
- Alternatives (FlightAware, OAG) are paid/enterprise, not accessible for a student project

## 9. Tech stack (and why each)

| Tool | Why |
|---|---|
| Python | Most in-demand DS language (confirmed via job market check) |
| pandas | Data manipulation/cleaning |
| requests | API calls |
| python-dotenv | Load secrets from .env safely |
| scikit-learn | ML models (once modeling phase starts) |
| matplotlib/seaborn | Visualization |
| Jupyter (via VS Code) | Interactive, step-by-step data exploration |
| venv | Isolate this project's packages from others on my machine |
| Git/GitHub | Version control, portfolio visibility |

## 10. Why a virtual environment (venv)?

- Keeps this project's package versions separate from other projects, avoids version conflicts
- Standard, expected practice in real software/data jobs

## 11. Why is the API key in .env, not hardcoded?

- Same lesson as a security fix made on another portfolio project (E-Library): hardcoded secrets in code pushed to GitHub = publicly exposed, exploitable
- .env keeps the key out of code. .gitignore ensures .env is never pushed
- Reusable interview point: "I follow the practice of never committing secrets to version control"

## 12. Why append to CSV daily instead of overwriting?

- Overwriting = lose all previous days' data, no growing history
- Appending = dataset richness grows every day, needed for eventual model training

## 13. The header-row bug (and fix)

- **Bug found:** script only wrote a CSV header if file didn't exist. An empty auto-created file tricked it into skipping the header
- **Fix:** check file size in addition to file existence
- **Lesson:** always verify a "file exists" check accounts for empty files too

## 14. Why filter to only completed flights before analysis?

- Concept: **target leakage / label availability**
- scheduled/active flights have no known outcome yet, including them would corrupt statistics with unknowns
- Only flights with a real, final outcome are valid training data

## 15. Data Quality Finding #1: API's own delay field is unreliable

- Compared API's dep_delay_min field against manually calculated delay (actual timestamp - scheduled timestamp)
- **They didn't match** (e.g. API said 9 min, real gap was 24 min), no consistent pattern/offset either
- **Decision:** stopped trusting the API's derived field. Calculate delay myself from raw timestamps instead
- **Interview point:** "I found a data quality issue in my source, diagnosed it via cross-verification against raw data, and built my own reliable feature instead of blindly trusting the provided field."

## 16. Why pd.to_datetime() before doing date math?

- Raw CSV timestamps load as plain text, not real dates, to pandas
- Can't subtract text to get a time difference
- pd.to_datetime() converts text into real datetime objects Python can do math on

## 17. Data Quality Finding #2: flight_status label lags behind reality

- Found 28 flights labeled scheduled that already had a real dep_actual timestamp (i.e. already departed)
- The status label hadn't updated yet, API staleness, not truth
- **Decision:** built independent boolean flags (has_departed, has_arrived) from raw timestamp presence, instead of trusting the status label
- **New rule:** a flight only counts as "complete, usable training data" if has_arrived == True, regardless of what flight_status says
- **Interview point:** two independent, self-found data quality issues in the first two real sessions, shows careful, skeptical analysis, not blind trust in a data source

## 18. Formalizing delay calculation into the collection script

- Originally, delay recalculation only existed inside the Jupyter notebook (temporary, has to be redone every time)
- **Decision:** moved the logic into collect_data.py itself via a calculate_delay() function, so every future day's data is analysis-ready at collection time, not as an afterthought
- **Lesson:** good pipelines calculate derived values during ingestion, not as a manual notebook patch

## 19. Departure delay vs arrival delay: why calculate both?

- Departure delay = did the flight leave late
- Arrival delay = did it arrive late (what actually affects a traveler, missed connections etc.)
- A flight can depart late but make up time in the air, arrival delay is the more meaningful outcome
- Calculating both lets us compare whether departure delay reliably predicts arrival delay

## 20. Known limitations (to state proactively: not hide)

- Small dataset scale (portfolio-scope, not production-scale), deliberate tradeoff for depth of understanding
- Single month snapshot, can't yet separate "route-specific" patterns from "this month's unusual events" (weather, strikes, etc.)
- ~~Timezone handling assumed correct~~, verified and resolved, see Finding #4 (Section 27): timestamps are actually local time mislabeled as UTC, but this does not affect within-airport delay calculations already used in analysis

## 21. Data Quality Finding #3: route+date+airline is not a unique flight identifier

- Attempted deduplication check by grouping on route + flight_date + airline
- Found suspiciously high counts (e.g. 7 rows for one route/date/airline combination)
- **Realized the identifier was flawed:** an airline can fly the same route multiple times a day (e.g. a morning and evening flight), route+date+airline doesn't uniquely identify a single flight
- Inspected the raw API response directly to check what identifying fields actually exist
- Found a flight.iata field (e.g. LH757), the true flight number, that had never been captured in the CSV
- **Fix:** added flight_number as a saved column in collect_data.py, going forward
- **Interview point:** demonstrates recognizing a flawed assumption (route+date+airline as a unique key) by testing it against real data rather than assuming it was correct, then going to the raw API source to find the actual correct identifier instead of guessing or working around it superficially
- **Resolution confirmed:** re-ran the same duplicate check using route+flight_date+flight_number, every group returned count of exactly 1. This confirms the earlier high counts were genuinely different flights (same airline, same route, same day, different flight numbers), not duplicate data. No rows needed to be dropped, but the investigation was still necessary, since assuming either way without checking would have been a guess, not a verified conclusion.
- **Secondary bug found and fixed:** the CSV header row had been written once, before flight_number was added to the script, so newer rows had 14 values but the header only listed 13 column names. This caused GitHub to fail rendering the CSV as a table, and would have caused column misalignment issues in pandas too. Fixed by manually correcting the header row to match the actual data.

## 22. Schema evolution: historical rows had inconsistent column counts

- As collect_data.py was improved over Days 1-4 (adding calculated_dep_delay, calculated_arr_delay, then flight_number), older rows in the CSV were written with fewer columns than the current header expects
- Result: Day 1-2 rows had 11 columns, some Day 3 rows had 13, Day 4 rows have the full 14, inconsistent row widths in the same file
- This caused GitHub's CSV table renderer to fail, and would have caused column misalignment when loading into pandas
- **Fix:** wrote a one-time cleanup script that reads every row, detects short rows, and pads them with empty values in the correct position (inserting blanks for the newer columns while keeping airline as the last field) so every row consistently has 14 columns
- **Lesson:** this is a normal consequence of iteratively improving a data pipeline over multiple collection days, old records don't retroactively gain new fields on their own. A cleanup/migration step is needed whenever a pipeline's schema changes mid-collection.
- **Interview point:** understanding schema evolution and writing a migration fix for historical records is a real data engineering skill, not just a one-off bug fix
- **Handling the two affected fields differently, based on whether backfilling is possible:**
 - calculated_dep_delay/calculated_arr_delay: these are always recomputed fresh in pandas from raw timestamps during analysis, rather than trusted from the CSV column, since raw timestamps exist for every row regardless of collection date, this works uniformly for old and new rows alike. The CSV's own calculated columns are just a convenience record, not the analysis source of truth.
 - flight_number: genuinely cannot be backfilled, the API wasn't asked to return it for older snapshots, and that information is permanently lost for those rows. **Accepted limitation:** rows collected before Day 4 remain usable for route/airline/time-based aggregate analysis, but excluded from any analysis requiring per-flight identity (e.g. tracking one specific flight's full history)

## 23. Progress log

| Date | Landed/Complete flights | Total rows | Key event |
|---|---|---|---|
| Day 1 | ~10 (est.) | 36 | First successful collection, 3 routes |
| Day 2 | 29 | 67 | Found delay-field mismatch (Finding #1) |
| Day 3 | 57 | 127 | Found status-lag issue (Finding #2), added calculate_delay() to script |
| Day 3 (cont.) | 57 | 127 | Found deduplication flaw (Finding #3), route+date+airline not unique, added flight_number capture to script |
| Day 4 | TBD | 152 | First collection with flight_number included. Confirmed no true duplicates existed. Found and fixed 2 schema bugs (header/row column mismatch from pipeline evolving over time) |
| Day 5 | 84 | 178 | Continued daily collection, steady growth toward 200-300 target |
| Day 6 (checkpoint) | 120 | 232 | Confirmed BOM-FRA delay pattern still holding with more data. Broke down by airline (delays spread across carriers, not one airline) |
| Day 7-8 | Not individually logged | Not individually logged | Continued daily collection without a dedicated analysis checkpoint each day |
| Day 9 (checkpoint) | 146 | 265 | Analyzed BOM-FRA by day-of-week and departure hour. Found 2 AM slot has 51.7% delay rate (largest, most reliable sample in dataset). Found and resolved Finding #4 (timezone mislabeling) |
| Day 11 | 201 | 353 | Crossed into 200-300 complete-flight target range. Ready to move toward feature engineering / modeling phase soon |
| Day 12 | 214 | 381 | Started modeling phase: built train/test split, trained first baseline Logistic Regression, diagnosed and fixed weak recall on delayed class via class_weight balancing |
| Day 13 | 232 | 408 | Examined model feature importance (strong agreement with EDA). Investigated and resolved a Saturday delay-rate discrepancy between model and earlier EDA finding. Rebuilt feature set with corrected airline grouping. Re-evaluated model (perfect recall on delayed class, held with appropriate caution given small test set) |
| Day 14 | 247 | TBD | Re-evaluated model with more data, recall dropped from 1.00 to 0.88, precision from 0.73 to 0.58, confirming the Day 13 caution that the perfect score was a small-sample artifact |
| Day 15 | 260 | 465 | Continued daily collection. Refactored and cleaned up the exploration notebook into a clear, organized 6-section structure. Trained and compared a Random Forest model against the Logistic Regression baseline, decided to keep the simpler model |
| Day 16 | 282 | 497 | Continued daily collection |
| Day 17 | 297 | 522 | Built and styled the Streamlit app (departure-board theme, light/dark toggle, adjustable delay threshold, mobile-responsive layout). Calculated departure-to-arrival delay correlation (r=0.445). Fixed several silently-failed KNOWLEDGE.md edits from earlier sessions and re-verified content |
| Day 18 | 318 | 549 | Published the app live on Streamlit Community Cloud. Fixed a deployment failure (pywinpty, a Windows-only package pulled in by pip freeze, cannot build on Linux) by trimming requirements.txt to actual runtime dependencies. Added a live "predict my flight" feature backed by the same trained model, with a visible disclaimer about the small dataset and limited features. Fixed light-mode contrast and mislabeling bugs on the theme toggle |
| Day 19 | Not recorded | Not recorded | Continued daily collection, shape numbers not logged this day |
| Day 20 | 350 | 603 | Continued daily collection. Pulled current model and EDA numbers for resume use (delay rate by route: BOM-FRA 33.1%, BLR-AMS 0%, DEL-CDG 5.8% at 339 flights, recall on delayed class 90% with Logistic Regression) |
| Day 21 | 369 | 634 | Continued daily collection |
| Day 22 | 391 | 667 | Continued daily collection |
| Day 23 | 414 | 697 | Continued daily collection. Added a live "predict my flight" feature to the app, backed by a model retrained inside the app itself (cached, retrains only when data changes). Fixed two theme bugs: the toggle label was showing the wrong mode name, and light mode had several invisible text elements because Streamlit's own native widget labels (dropdowns, sliders, buttons) are separate from the app's custom CSS classes and were not being overridden |
| Day 24 | 425 | 722 | Continued daily collection. Diagnosed and fixed the actual root cause of the toggle label bug, a one-render lag where the label text was computed before capturing the toggle's new value each click. Decoupled the mode indicator text from the widget's own label to fix it properly |

## 24. First EDA finding: BOM-FRA is meaningfully less reliable than the other two routes

- Started real EDA at 84 complete flights (didn't wait for full target, reasonable to explore early and refine as data grows)
- Using the industry-standard 15+ minute threshold for "delayed":
 - BLR-AMS: 0% delayed (0/21 flights)
 - DEL-CDG: 0% delayed (0/38 flights)
 - BOM-FRA: 32% delayed (8/25 flights)
- **BOM-FRA stands out as the clear outlier here**, both in delay rate and in earlier mean/median disagreement (suggesting more variable/inconsistent performance, not just a few outliers)
- **Caveat, held honestly:** sample sizes (21-38 flights/route) are still moderate, not large, this is an early signal worth continuing to track, not yet a statistically bulletproof conclusion. Will re-run this exact analysis weekly as more data accumulates to see if the pattern holds.
- **Why raw mean/median wasn't enough on its own:** averaging early and on-time flights together obscures the more practically useful question, "how often does this route actually run late?" The binary delay-rate metric answers that directly and is what the aviation industry itself standardizes on.

## 25. BOM-FRA time-based patterns: day of week and departure hour

- At ~146 complete flights, checked day-of-week and departure-hour patterns specifically for BOM-FRA
- **Day of week:** Monday/Saturday/Sunday showed 0% delay early on. Wednesday showed 36% (largest weekday sample). Tuesday and Friday looked dramatic (83%, 100%) but rested on very small samples (3-6 flights) and were not treated as reliable standalone figures
- **General, more defensible takeaway at the time:** delays clustered on weekdays (Tue-Fri), weekends and Monday looked clean, though this Saturday figure specifically was later found to shift substantially as more data came in (see Section 30)
- **Departure hour (stronger finding, larger sample):** only 3 distinct scheduled departure hours exist for BOM-FRA (2 AM, 8 AM, 11 AM). 2 AM showed 51.7% delayed (largest sample in the dataset, 29 flights), 8 AM 25%, 11 AM 0%
- **Plausible explanation (hypothesis, not proven):** very early departures may face tighter aircraft turnaround, reduced ground staff at 2 AM, or delays cascading from earlier in the day/night, framed as a hypothesis worth investigating, not a stated fact
- **Interview point:** distinguishing findings backed by large samples from those resting on a handful of data points is core statistical literacy, not all numbers in an early analysis deserve equal confidence

## 26. Data Quality Finding #4: timestamps are local time, mislabeled as UTC

- Followed up on an open limitation flagged since Day 1: timezone handling was assumed correct but never explicitly verified
- Took one BOM-FRA flight and checked scheduled flight duration: naive subtraction gave 6h15m, but a real BOM-FRA direct flight takes roughly 8-9 hours, a clear red flag
- Manually converted both timestamps to true UTC using known airport timezones (Mumbai UTC+5:30, Frankfurt UTC+2 in summer): recalculated duration came to 9h45m, a realistic flight time
- **Conclusion:** the API returns each timestamp in local time at that airport, but labels it with a +00:00 (UTC) suffix instead of the correct local offset, a mislabeling bug in the data source, not a value error
- **Impact assessed carefully:** departure delay and arrival delay are each computed from two timestamps at the *same* airport, so the mislabeling cancels out, every route/airline/day/hour finding so far remains valid and unaffected. Any calculation mixing departure and arrival timestamps together (e.g. true flight duration) would be wrong if attempted, but no such calculation has been made
- **Interview point:** verifying a flagged assumption rather than leaving it permanently unresolved, then precisely scoping which existing results are and are not affected, is stronger practice than either ignoring the risk or redoing everything unnecessarily

## 27. Feature engineering: grouping rare airlines before encoding

- Built initial feature set via one-hot encoding (route, airline, dep_hour, day_of_week, is_weekend), first attempt produced 24 columns
- Flagged a concern: several airlines (Alitalia, DHL Air, Lufthansa Cargo, Cathay Pacific) had only 2-8 flights each, meaning their one-hot columns would be almost entirely False, risking overfitting to near-noise rather than real patterns
- **Decision:** grouped any airline with fewer than 10 flights into a single "Other" category before encoding
- **Result:** reduced to 21-22 features (count shifts slightly as the dataset grows and airlines cross the 10-flight threshold), every remaining category backed by a meaningful sample size
- **is_weekend as a simpler complement to day_of_week:** given day-of-week findings had shakier confidence on individual days at the time, including a simpler binary weekday/weekend flag gives the model a more robust, lower-variance signal alongside the more granular day feature
- **Interview point:** recognizing when a categorical feature has too many rare levels for the available data, and choosing a principled way to consolidate them, is standard, important feature engineering practice

## 28. First baseline model: Logistic Regression

- At 214 complete flights (176 not delayed, 38 delayed, roughly 18% delay rate, moderately imbalanced), built the first model
- **Train/test split:** 80/20, stratified on the target to preserve the delay ratio in both sets
- **Why Logistic Regression first:** simple, fast, interpretable, establishes a baseline before trying anything more complex
- **First attempt (default settings):** accuracy 0.84, but recall on the delayed class was only 0.25, missing 75% of real delays despite looking "accurate" overall. Direct demonstration of why accuracy alone is misleading under class imbalance
- **Fix tried:** class_weight='balanced', tells the model to weight the minority (delayed) class more heavily during training
- **Result:** recall on delayed class jumped from 0.25 to 0.88, precision 0.70, F1 improved from 0.36 to 0.78, overall accuracy improved to 0.91
- **Honesty check, held deliberately:** test set was only 43 flights with just 8 delayed, a single flight's outcome swings these percentages by over 12 percentage points. A genuinely promising early result, not yet proof of a robust model
- **Interview point:** diagnosing a specific weakness (poor recall on the minority class), understanding why (imbalance not being accounted for), then applying a targeted fix and verifying it worked, is a methodical modeling approach

## 29. Model feature importance, and a finding that changed with more data

- Examined Logistic Regression coefficients on the balanced model
- **Strong agreement with EDA:** route_BOM-FRA was the single strongest delay-pushing feature, route_BLR-AMS the strongest on-time-pushing feature, the model independently learned the same core pattern found by hand in EDA, a good validation signal
- **dep_hour** showed later departure hours associated with lower delay risk, directionally consistent with the BOM-FRA 2 AM vs 11 AM finding
- **Discrepancy found and investigated, not smoothed over:** the model's day_of_week_Saturday coefficient was positive (pushes toward delay), which seemed to contradict the earlier EDA finding that BOM-FRA Saturdays were 0% delayed
- **Resolution:** re-ran the day-of-week-by-route breakdown with the larger, current dataset, BOM-FRA Saturday had risen to 50% delayed (8/16 flights), up from an earlier small-sample 0% based on only 6 flights. BLR-AMS and DEL-CDG remained 0% delayed on Saturday. The model's coefficient was correct for the current data, the earlier EDA finding was accurate for its own smaller sample, but had since been superseded as more data came in
- **Interview point:** a finding that's true for 6 data points may not hold at 16, that's not a mistake, it's exactly why findings need re-checking as data grows rather than being treated as permanently settled. Investigating an apparent model/EDA discrepancy rather than ignoring it demonstrates rigor

## 30. Model re-evaluated at 232 complete flights: with corrected feature set

- Rebuilt the feature set with more data (232 complete flights) and confirmed the airline-grouping fix was correctly applied
- Re-trained the balanced Logistic Regression: precision 0.73, **recall 1.00**, F1 0.84, overall accuracy 0.94, caught all 8 delayed test flights, 3 false alarms
- **Held with deliberate caution, not pure celebration:** a perfect 100% recall on only 8 delayed test examples is a result to treat skeptically. Two honest possibilities: the features genuinely capture a strong pattern, or the test set is still small enough that a lucky split is entirely plausible
- **Plan stated at the time:** continue tracking this metric as data grows, a single perfect score on 8 examples is not, by itself, proof of anything definitive
- **Interview point:** treating an unexpectedly perfect result with more scrutiny, not less, is a mark of statistical maturity

## 31. Prediction confirmed: model performance settled with more data

- At 247 complete flights, re-ran the exact same balanced Logistic Regression pipeline
- **Result:** recall on delayed class dropped from the earlier 1.00 to 0.88 (7/8 caught), precision dropped from 0.73 to 0.58 (5 false alarms, up from 3), overall accuracy dropped from 0.94 to 0.88
- **This directly confirms the caution flagged in Section 31:** the earlier perfect recall was, as suspected, partly a small-test-set artifact. Performance settled to a more realistic, still genuinely solid level (0.88 recall) rather than the possibly-lucky perfect score seen before
- **Interview point:** being able to say "I predicted this result would soften with more data, and it did" is a stronger story than either reporting the perfect score without caveats, or never checking whether it held up

## 32. Second model tried: Random Forest compared against Logistic Regression

- At 260 complete flights, trained a Random Forest classifier (100 trees, class_weight='balanced') on the identical train/test split and feature set as the Logistic Regression baseline, for a fair comparison
- **Result:** virtually identical performance, precision 0.58, recall 0.88, F1 0.70, accuracy 0.88, nearly matching Logistic Regression at the same data size
- **Interpretation:** Random Forest's ability to model non-linear feature interactions did not produce a meaningful improvement over the simpler linear model at this dataset size (~260 flights), a normal, expected outcome in small-data settings
- **Decision: kept Logistic Regression as the primary/reported model.** Given equal performance, the simpler, faster, more directly interpretable model (already cross-validated against EDA findings) is the better choice
- **Interview point:** trying a more complex model and choosing not to adopt it, because it didn't outperform a simpler baseline, demonstrates disciplined model selection, added complexity should earn its place with genuine performance gains

## 33. Departure delay vs arrival delay: how related are they?

- Question worth answering directly rather than assuming: does a late departure actually predict a late arrival, or are they fairly independent?
- Calculated the Pearson correlation between actual_dep_delay_min and actual_arr_delay_min for BOM-FRA: **r = 0.445**
- **Interpretation:** a moderate, positive relationship, not a strong or near-perfect one. Departing late does somewhat associate with arriving late, but roughly half the variation in arrival delay isn't explained by departure delay at all, likely reflecting in-flight factors (headwinds, air traffic holding, rerouting) not captured in this dataset
- **Why this matters for how findings are stated:** it would be inaccurate to claim late departures "cause" late arrivals based on this data alone. The precise claim is that the two are moderately correlated, not causally proven
- **Interview point:** distinguishing correlation from causation, and stating a precise correlation coefficient rather than a vague "they're related" claim, shows real statistical precision

## 34. Market research: RouteWatch against current Data Scientist job demand

- Researched current (2026) skill demand for Data Scientist, Data Analyst, and GenAI/AI Engineer roles across job postings and industry reports, to guide what future projects should target rather than picking randomly
- Key market findings worth recording: Python appears in 57% of Data Scientist postings, Machine Learning in 69%, SQL in 30%. NLP demand nearly quadrupled from 5% to 19% of postings in a year. 57% of postings now want versatile, cross-domain candidates rather than narrow specialists
- **Checked RouteWatch against this list directly.** Confirmed strengths: Python throughout, real trained and evaluated ML models (Logistic Regression, Random Forest), scikit-learn, statistics and probability reasoning (correlation, class imbalance, sample-size discipline), genuine deployment (live Streamlit app with a working prediction feature), strong documentation and communication
- **Confirmed real gaps, not filled by this project:** no SQL anywhere (data lives in CSV, never touched a database), no cloud platform used (Streamlit Community Cloud is not the same as AWS/Azure/GCP), no NLP/LLM component at all
- **Decision:** rather than trying to retrofit these gaps into RouteWatch, treat them as deliberate targets for future projects. Plan is to build 2-3 projects per role (Data Scientist, Data Analyst, GenAI/AI Engineer) over time, with each new project in a domain chosen specifically to cover a gap left by the previous one in that same domain
- **Interview point:** being able to say "I researched current market demand, audited my own project against it, and used the gaps to plan my next project" is a stronger, more deliberate portfolio story than building projects one at a time without a clear throughline connecting them

## 35. Closing the gap between a trained model and an actually usable app

- Realized the deployed app only showed historical, descriptive statistics (delay rate by route, by hour) and never let anyone actually use the trained model to get a prediction for a hypothetical future flight. The model existed, got evaluated, and then sat unused.
- **Added a "predict my flight" feature:** pick a route, airline, day of week, and departure hour, get the model's live predicted probability of delay
- **Model is retrained inside the app itself** (using the same feature engineering and Logistic Regression setup as the notebook), cached so it only retrains when the underlying data actually changes, not on every click
- **A visible, un-hideable disclaimer sits next to the prediction**, stating plainly that this is a small self-collected dataset with only 4 factors, does not account for weather, air traffic, or aircraft rotation delays, and should be read as a historical pattern, not a forecast
- **Why add a caveated prediction rather than either hiding the model or presenting it overconfidently:** real production delay-prediction systems also aren't perfect even with far more data and features. The honest move is not to avoid exposing a limited model, it is to be explicit about exactly how limited it is, the same principle applied throughout this project's other findings

## 36. Two theme bugs found while testing light mode

- **Bug 1: toggle label showed the wrong mode name.** An earlier version had a static label ("Dark mode") regardless of which theme was actually active. Fixed by making the label read the current session state and display the mode that is actually showing.
- **Bug 2: several text elements were invisible in light mode.** Streamlit renders its own native widget labels (selectbox labels, slider tick values, button text) using its own internal styling, completely separate from this app's custom CSS classes. These were never overridden, so they kept a color suited to the dark theme and disappeared against the light background.
- **Fix:** added explicit CSS overrides targeting Streamlit's own internal widget selectors (label text, slider value display, select box text, button text) so they follow the same theme colors as the rest of the app, in both modes
- **Interview point:** a real, sometimes-overlooked lesson when styling apps built on top of a framework like Streamlit: the framework's own default component chrome does not automatically inherit a custom theme just because most of the page has been restyled. Every native component needs to be checked and, if needed, explicitly overridden.

## 37. Still to come (will update as we go)

- Continue daily collection until API request budget (100/month) is used up
- Port Random Forest comparison code from scratch notebook into the clean explore.ipynb
- Deduplicate historical flights using flight_number now that it's consistently captured
- Consider expanding hour-of-day and day-of-week analysis to the other two routes, not just BOM-FRA
- Finalize README and Streamlit app once data collection winds down
- Future Data Scientist project #2 (separate chat/project) should target SQL, a cloud platform, and an NLP/LLM component, the three gaps identified in Section 34

---

*Next update: after next data collection + analysis.*
