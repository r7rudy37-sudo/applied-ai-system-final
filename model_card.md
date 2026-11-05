# Model Card: VibeGuide 1.0

## Base Project and Intended Use
This extends AI110 Project 3, Music Recommender Simulation (VibeFinder). The base app scored and ranked 20 fictional songs using explicit genre, mood, and energy preferences. VibeGuide keeps that ranking component and adds an integrated validate-plan-rank-audit-filter workflow. Its intended use is classroom exploration of explainable recommendations and reliability. It is not a trained recommender or a mental-health tool.

## Data and Algorithm
The catalog has 20 synthetic rows, including ten starter rows and ten AI-generated additions. Each has ID, title, artist, genre, mood, energy, tempo, valence, danceability, and acousticness. The scoring rule uses genre, mood, energy, and optionally acoustic preference. There is no training dataset, private listening history, audio analysis, or external model call. Three strategies alter the weights. The new assistant validates input, checks catalog support, ranks, independently audits output, and refuses weak or unsupported requests. See the architecture source and actual JSON traces.

## Limitations and Biases
The catalog is small, fictional, and uneven. Exact genre and mood labels miss synonyms and related styles. The manually chosen weights and 0.70 support threshold can over-favor certain combinations or refuse a request a human could interpret. Artist diversity improves variety but does not establish demographic fairness. The numerical support value is an alignment measure, not a calibrated probability of enjoyment. The audit checks factual consistency with the rules, not whether the rules reflect real musical taste.

## Potential Misuse and Prevention
Someone could present these synthetic labels as facts about real music, describe the support score as a psychological assessment, or use recommendations to infer sensitive traits. Documentation explicitly identifies the data as synthetic and the scores as rule-based. The application requires explicit preferences, stores no listening history by default, makes no diagnostic claim, and refuses unknown fields. Saved traces are local and should not include real personal data when sharing a public repo. Production use would require consent, data minimization, deletion controls, and human review of inappropriate inferences.

## Reliability Testing Results
The saved run passed 42 automated tests, including five output-tampering cases, and 8/8 predefined end-to-end evaluation cases. The three valid profiles returned distinct top genres. Missing preferences, unknown genre, invalid numbers, unexpected fields, and a weak combined match refused with no results. Replaying the same requests gave identical outputs. These are results on the included synthetic test set, not an estimate of real-user accuracy.

## What Was Surprising in Testing
The base scorer can produce a plausible-looking list for an absent genre because other features still add points. The same metal/happy/0.8 input returned songs in the baseline and was refused in the extension. Another useful behavior is that the rock request returns two well-supported songs instead of inventing a third match. A fully correct score can therefore still be an inappropriate answer unless the system checks the request's support.

## Collaboration With AI: Accepted and Revised Suggestions
Codex wrote the implementation and documentation and executed the saved tests in response to the user's coursework request. This is AI-assisted work; no independent human listening study or manual review is claimed. AI helped turn the rubric into a modular workflow, add invalid-input tests and fault injection, and format reproducible evidence.

One accepted design was to validate against actual catalog labels and audit the exact scoring explanation before release. An alternative that was not used as written was a free-text/LLM intent parser: this version requires an explicit JSON preference object. That revision makes unsupported inputs visible and reproducible without an API key or a paid model. Another correction during testing renamed a pytest parameter from the reserved name request to payload; the tests were then rerun successfully. The implementation also filters support before rounding so a display rounding change cannot admit a below-threshold match.

## Future Improvements
Evaluate on consented, held-out preference judgments from real people. Add validated multi-label genres and synonyms while measuring coverage and false refusals. Calibrate support thresholds against an independent evaluation set rather than intuition. Expand the catalog and report diversity/relevance trade-offs. Preserve human review for musical suitability; deterministic tests alone are insufficient.

## Engineering Reflection
The central design lesson is that producing an answer and deciding whether the answer is supported are different tasks. The project makes that difference visible through separate ranking, auditing, and refusal decisions. The next extension should measure whether those decisions improve outcomes for real listeners, while avoiding unnecessary collection of personal information.
