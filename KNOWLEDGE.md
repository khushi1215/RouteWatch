# RouteWatch: Knowledge Doc

A living decision record. Written as decisions get made, not reconstructed afterward. Every entry includes what was rejected and why, not just what won.

---

## 1. Project Definition

RouteWatch is a flight delay tracking and prediction tool for India-Europe air travel. A daily script collects live flight status data from a real API for a set of routes, builds a growing dataset over time, investigates and documents data quality problems as they surface, analyzes delay patterns, trains a model to estimate delay risk, and serves everything through a live, interactive web app.

It exists as a personal portfolio project, built to demonstrate a full pipeline from raw data collection through a deployed prediction feature, using genuinely self-collected data rather than a pre-packaged dataset. Aviation was chosen as the subject out of real personal interest in travel, not because it was assigned.

---

## 2. Tech Stack and Why

### API: Aviationstack
**Considered:** FlightAware, OAG
**Chosen:** Aviationstack
**Reasoning:** FlightAware and OAG are paid/enterprise products, not accessible for a self-funded project. Aviationstack has a usable free tier (100 requests/month) that returns the fields needed (scheduled/actual times, status, airline).

### Route scope: 3 active routes per phase, not 10+
**Considered:** tracking 10-15 routes at once for broader coverage
**Chosen:** 3 routes tracked daily per phase
**Reasoning:** the free API budget (100 requests/month, 1 request per route per day) means more routes directly means fewer requests per route. At 10+ routes, each route would only accumulate 7-10 flights, too few to draw any reliable conclusion. At 3 routes, each accumulates 30-50+ flights, enough for meaningful comparison. Depth over breadth was the deliberate tradeoff.

### Model: Logistic Regression over Random Forest
**Considered:** Random Forest (higher expressiveness, can capture non-linear feature interactions)
**Chosen:** Logistic Regression, with `class_weight='balanced'`
**Reasoning:** both models were trained on the identical train/test split and feature set for a fair comparison. Random Forest produced virtually identical performance (recall 0.88 vs 0.88, precision 0.58 vs 0.58 at the same dataset size). The added complexity bought nothing. Logistic Regression is simpler, faster to retrain, and its coefficients are directly interpretable, which let its predictions be cross-checked against manual EDA findings. Complexity should earn its place with a real performance gain, and here it didn't.

### Delay threshold: 15 minutes, industry standard
**Considered:** an arbitrary custom cutoff
**Chosen:** 15+ minutes late counts as delayed
**Reasoning:** this is the actual threshold used in US DOT and most airline delay reporting, so results are comparable to how the aviation industry itself measures delay, not a number invented for this project. The deployed app also includes an adjustable slider (5 to 60 minutes) so the threshold isn't hidden as a fixed assumption, but 15 remains the analyzed default.

### Secrets: `.env` file, not hardcoded
**Considered:** hardcoding the API key directly in the script
**Chosen:** environment variable loaded from a local `.env` file, excluded via `.gitignore`
**Reasoning:** a hardcoded key pushed to a public GitHub repo is immediately exposed and exploitable by anyone. This is a basic, well known security practice worth following from the start rather than fixing after the fact.

### Environment: `venv`
**Chosen:** an isolated Python virtual environment per project
**Reasoning:** keeps this project's package versions independent of anything else on the same machine, avoids version conflicts, and is standard practice in real development work.

### Frontend: Streamlit + Plotly
**Considered:** Streamlit's own built-in chart functions for the visualizations
**Chosen:** Plotly, embedded in Streamlit
**Reasoning:** Plotly gives full control over chart styling (colors, fonts, hover behavior) needed to match a custom light/dark theme. Streamlit's built-in charts are faster to write but don't expose enough styling control for a themed, polished result.

---

## 3. Data and System Overview

**Pipeline flow:** a daily script calls the API once per active route and appends the results to a single CSV file, `data/flights_log.csv`. The file is never overwritten, only appended to, so the dataset grows richer every day rather than losing history. A Jupyter notebook loads that CSV, cleans it, computes derived fields (real delay values, completion flags), runs the analysis, and trains the model. The deployed app reads the exact same CSV and recomputes the same derived fields fresh on load, so the notebook and the app are never out of sync with each other.

**Assumptions made early that turned out to need checking** (each is explained in full under Challenges below, listed here because this is where each of the four major bugs in this project actually originated):
- Assumed the API's own delay field could be trusted. It could not.
- Assumed the `flight_status` field reliably indicated whether a flight was complete. It did not, it lagged behind reality.
- Assumed timestamps were correctly labeled in UTC. They were local time, mislabeled.
- Assumed route plus date plus airline was enough to uniquely identify a flight. It was not, since an airline can run the same route more than once a day.

Naming these assumptions explicitly, rather than only the fixes, is deliberate: assumptions are exactly where bugs hide, whether or not they turn out to be wrong.

---

## 4. Discoveries and Findings

**One route is meaningfully less reliable than the others.** Across the Phase 1 dataset (442+ flights), one route consistently ran a 15 to 30%+ delay rate while the other two stayed near 0%. This gap held up and was re-confirmed multiple times as the dataset grew from dozens to hundreds of flights, not a one-time artifact.

**The delay is spread across airlines, not one carrier.** On the less reliable route, several different airlines each showed elevated delay rates. This points toward a route or airport-level factor rather than a single operator's problem, an important distinction for what the finding actually means.

**Departure hour matters more than expected.** A very early departure slot on the same route showed roughly 50% delay rate, versus 0% for a late-morning slot, backed by the largest single sample in the entire dataset.

**A finding that changed as more data came in, and was kept rather than quietly fixed.** An early read on one weekday's delay rate showed 0%, based on only 6 flights. Once the sample for that same day grew to 16 flights, the rate had shifted to 50%. Both numbers are documented, with the sample size next to each, rather than only showing the final "correct" one. Conclusions drawn from a small, growing dataset need to be held loosely and re-checked, not treated as settled the first time they're calculated.

**Departure delay and arrival delay are only moderately correlated, not strongly.** The Pearson correlation between the two came out to **r = 0.445**. Departing late does associate with arriving late, but roughly half the variation in arrival delay is explained by something else entirely, likely in-flight factors like headwinds or air traffic holding, not captured in this dataset. It would be inaccurate to claim one causes the other based on this alone.

**The trained model's coefficients independently agreed with the manual EDA findings.** The same route and departure-hour patterns that were found by hand also emerged as the strongest coefficients in the trained model, without being told to look for them. This is a useful cross-validation signal that the model learned a real pattern rather than noise.

---

## 5. Challenges and How They Were Solved

### The API's own delay field was unreliable

**Problem:** the API returns its own `dep_delay_min` field, but the numbers didn't line up with what seemed reasonable on inspection.

**Investigation:** cross-checked the API's reported delay against a delay calculated manually, actual timestamp minus scheduled timestamp, for the same flights. The two numbers didn't match, and there was no consistent offset between them.

**Fix:** stopped trusting the API's derived field entirely. Delay is now always calculated fresh from the two raw timestamps.

**Why this fix:** raw timestamps are the most primitive data available, less likely to carry a hidden calculation bug than a field someone else already processed. Recomputing from source is more transparent than trying to guess or correct the API's own logic.

### The flight status label lagged behind reality

**Problem:** some flights were labeled `scheduled` in the data despite already having a real departure timestamp recorded.

**Investigation:** checked how many `scheduled`-labeled rows had a non-empty actual departure time. Found a meaningful number, confirming the status field was stale, not reflecting what had actually happened yet.

**Fix:** built independent flags, `has_departed` and `has_arrived`, based on whether the raw timestamp fields were actually filled in, instead of trusting the status label at all. A flight only counts as complete, usable data if `has_arrived` is true.

**Why this fix:** the raw timestamp's presence or absence is a fact, not an interpretation. The status label is the API's own summary of that fact, and summaries can go stale. Checking the underlying fact directly removes that risk.

### Route plus date plus airline was not a unique flight identifier

**Problem:** an attempt to check for duplicate rows using route, date, and airline together produced suspiciously high counts, more rows per group than expected.

**Investigation:** realized an airline can run the same route more than once in a single day, a morning and an evening departure, for example. Route plus date plus airline doesn't distinguish between them. Checked the raw API response directly and found a `flight.iata` field, the actual flight number, that had never been captured.

**Fix:** started capturing the real flight number as its own column. Re-ran the duplicate check using route, date, and flight number together, every group returned a count of exactly one, confirming the earlier high counts were genuinely different flights, not duplicated data.

**Why this fix:** testing an assumption against real data, rather than trusting it, is what caught the problem in the first place. Going to the raw source for the correct identifier, instead of guessing or working around the flawed one, produces a fix that's actually correct rather than a patch that happens to look right.

### Timestamps were local time, mislabeled as UTC

**Problem:** a scheduled flight duration, calculated by naive subtraction of two timestamps, came out to roughly 6 hours for a route that realistically takes 8 to 9 hours.

**Investigation:** manually converted both timestamps to true UTC using the known timezone offset of each airport. The recalculated duration came out to a realistic 9 hours 45 minutes. This confirmed the API was returning each timestamp in local time at that airport, but labeling it with a UTC suffix instead of the correct local offset.

**Fix:** verified the scope of the impact rather than assuming the worst. Departure delay and arrival delay are each calculated from two timestamps at the *same* airport, so the mislabeling cancels out in that specific subtraction, meaning every delay-based finding up to that point remained valid. Only a calculation mixing timestamps from two different airports, like true flight duration, would actually be affected, and no such calculation had been made.

**Why this fix:** the instinct to redo everything after finding a bug is often wrong. Precisely scoping what is and isn't affected, rather than either ignoring the risk or overreacting to it, is the more defensible response.

### A CSV header bug silently skipped writing column names

**Problem:** the very first row of the data file was missing its header entirely.

**Investigation:** the collection script only wrote a header if the file didn't already exist. An empty file had been auto-created beforehand (by an editor opening it), which tricked the check into thinking the file, and its header, already existed.

**Fix:** changed the check to also verify the file has a non-zero size, not just that it exists.

**Why this fix:** a minimal, targeted correction to the actual logical gap, rather than a broader rewrite of the whole write routine.

### Schema evolution left old rows with fewer columns than new ones

**Problem:** as the collection script gained new fields over time (calculated delay values, then flight number), older rows in the CSV still only had the original, smaller set of columns. The file ended up with inconsistent row widths.

**Investigation:** confirmed this by counting fields per row across different days, early rows had 11, some middle rows had 13, later rows had the full 14.

**Fix:** wrote a one-time cleanup script that detects short rows and pads them with empty values in the correct position, preserving the newest field (airline) as the last column throughout.

**Why this fix:** old rows can't retroactively gain data that was never collected for them, so padding with genuinely empty values is the honest representation, not an attempt to fabricate missing history. A separate note documents that the two derived delay columns can always be recomputed fresh from raw timestamps regardless of when a row was collected, while the flight number field genuinely cannot be backfilled for older rows and remains a known, accepted gap.

### The theme toggle showed the wrong mode name

**Problem:** the light/dark mode switch consistently displayed the opposite of whatever mode was actually active.

**Investigation:** the label text was being computed *before* capturing what the toggle widget actually returned for that click, so it always displayed the *previous* render's state, a permanent one-step lag.

**Fix:** decoupled the mode-name text from the toggle widget's own label entirely. The text is now computed as a separate element, after the toggle's new value has already been captured in that same render.

**Why this fix:** the bug wasn't really about the toggle, it was about the order operations happened in. Fixing the actual sequencing, rather than trying to patch the label text itself, resolved it cleanly.

### Text was invisible in light mode, across three separate layers

**Problem:** switching to light mode left several pieces of text unreadable, custom labels, native dropdown and slider text, and chart axis labels.

**Investigation:** found this wasn't one bug but three, stacked in different rendering layers. Custom app text was controlled by CSS classes written for this app. The framework's own native widgets (dropdowns, sliders, buttons) render with their own internal styling, completely separate from the app's custom classes. The charting library renders its own SVG text, separate again from both of the above, and its axis tick labels had only a font family specified, not a color, so they fell back to a default that didn't match the theme.

**Fix:** applied theme-aware overrides at each layer individually, the custom CSS classes, explicit CSS targeting the framework's native widget selectors, and explicit color settings on the chart library's axis and hover tooltip configuration, plus a CSS fallback targeting the chart's rendered text directly as a safety net.

**Why this fix:** a single CSS theme applied to the page doesn't automatically cascade into a UI framework's own components or a separate charting library's rendering, since each maintains its own default styling system. Each layer needed to be checked and fixed on its own terms rather than assumed to inherit from the others.

### Deployment failed due to a Windows-only package

**Problem:** the deployed app failed to build with an error about a package called `pywinpty`.

**Investigation:** `pywinpty` is a Windows-only terminal helper package, part of a local Jupyter development environment, that had been captured into `requirements.txt` by running `pip freeze` on a local Windows machine. The deployment environment runs Linux and cannot build a Windows-specific package.

**Fix:** trimmed `requirements.txt` down to only the packages actually imported by the app and the collection script, rather than a full dump of everything installed locally for notebook work.

**Why this fix:** `requirements.txt` should describe what the deployed code needs to run, not a snapshot of an entire local development environment. The two are often different, and conflating them is what caused this failure.

### A newer library version broke on startup

**Problem:** after a fresh local reinstall, the app crashed immediately on startup with an internal error inside the web framework's own middleware.

**Investigation:** the error traced to an incompatibility between the newest release of the web framework and one of its own internal dependencies, a bug in that specific version combination, not in this project's code.

**Fix:** pinned the framework to a known stable version in `requirements.txt` instead of letting installs default to the newest release.

**Why this fix:** pinning a dependency version is a standard way to protect a working project from an upstream breaking change that has nothing to do with the project's own code.

### A virtual environment broke after the project folder was moved

**Problem:** after moving the project to a different folder, every command that used to work started failing with a "file not found" error pointing at the old folder path.

**Investigation:** virtual environments on Windows bake the absolute folder path into their activation scripts at creation time. Moving the folder doesn't update those scripts, so they keep pointing at a location that no longer exists.

**Fix:** deleted the old virtual environment and created a fresh one at the new location.

**Why this fix:** trying to manually patch every path reference inside a virtual environment is fragile and unnecessary, recreating it is fast and guaranteed correct.

---

## 6. Limitations

**Portfolio-scale dataset, not production-scale.** This is a deliberate tradeoff, prioritizing depth of understanding over raw dataset size, not an oversight.

**Single time-window snapshot per phase.** Each phase is collected over roughly a month. Seasonal effects like weather or holiday travel patterns can't yet be separated from genuine route-specific reliability.

**Flight number is only available from a certain point in the project onward.** Rows collected before that point remain usable for aggregate, route-level analysis, but cannot support any analysis requiring per-flight identity.

**The model's test set is small.** Results are re-evaluated as the dataset grows rather than treated as final. An early result that looked unusually strong was flagged with appropriate skepticism, and did in fact soften once more data came in, confirming that caution was warranted.

**The live prediction feature is a directional estimate, not a weather-aware forecast.** It's trained on a small, self-collected dataset using only four factors, route, airline, day of week, and departure hour. It does not account for weather, air traffic conditions, or aircraft rotation delays, all of which genuinely affect whether a real flight runs on time. This is stated directly next to every prediction in the app itself, not only here.

---

## 7. Changelog

**Day 1:** first successful data collection across the initial three routes.

**Day 2:** found the API's own delay field was unreliable, switched to calculating delay from raw timestamps.

**Day 3:** found the flight status field lagged behind reality, built independent completion flags. Also found route plus date plus airline wasn't a unique flight identifier, started capturing the real flight number.

**Day 4:** confirmed no true duplicate flights existed once checked with the correct identifier. Found and fixed two schema bugs from the pipeline evolving over multiple days.

**Day 5 to 11:** steady daily collection, crossed into a large enough sample size to move toward modeling.

**Day 12:** built the first baseline model, Logistic Regression, diagnosed and fixed weak recall on the delayed class using class weighting.

**Day 13:** reviewed model feature importance, found strong agreement with manual EDA findings. Investigated and resolved an apparent discrepancy between an early EDA finding and the model's own coefficients, the earlier finding had been based on a smaller sample that later shifted.

**Day 14:** re-evaluated the model with more data. A previously very strong recall score settled to a more realistic level, as had been anticipated and flagged in advance.

**Day 15:** refactored the analysis notebook into a clean, organized structure. Trained and compared a second model, Random Forest, against the baseline, and kept the simpler model after confirming equal performance.

**Day 17:** built and styled the live web app.

**Day 18:** deployed the app publicly. Diagnosed and fixed a deployment failure caused by an OS-specific package in the dependency file. Added a live prediction feature backed by the trained model, with a visible disclaimer.

**Day 20:** calculated the correlation between departure delay and arrival delay.

**Day 23 to 24:** found and fixed a theme toggle bug where the mode label lagged one step behind the actual state.

**Day 25:** the first phase of route tracking reached its target sample size and was marked complete.

**Day 26 onward:** switched to a new set of routes on a fresh monthly API quota, chosen deliberately for new geographic coverage rather than repeating the same three routes. From this point forward, routine daily data collection is not logged here individually, only genuinely new decisions, bugs, or findings are, to keep this document focused on reasoning rather than a repetitive activity log.

**Later:** fixed a light-mode text visibility bug spanning three separate styling layers (custom CSS, framework native widgets, and chart library rendering). Pinned the web framework's version after a newer release broke on startup due to an internal incompatibility. Rebuilt the virtual environment after the project folder was moved to a new location, which had broken all its activation scripts.
