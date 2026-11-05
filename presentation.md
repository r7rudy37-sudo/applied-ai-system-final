# VibeGuide: Six-Minute Presentation

Prepared presentation script and demo plan for AI110. This is preparation material; it does not claim a live presentation has been delivered.

## Slide 1 — The Problem (0:00–0:45)

**On the slide**
- A plausible recommendation can still be unsupported.
- Goal: explain a recommendation and know when to refuse.
- Base: Project 3, Music Recommender Simulation.

**Speaker notes**
My project is VibeGuide, a reliable music recommendation assistant. It extends the earlier VibeFinder simulation. The original app could compare a listener's preferred genre, mood, and energy with a small catalog. It produced a score and explained every contribution. That made the ranking understandable, but it did not answer a separate question: is there enough evidence in this catalog to answer the request at all? The extension adds checks before and after ranking so an unsupported request does not receive a confident-looking list.

## Slide 2 — Original System and Data (0:45–1:30)

**On the slide**
- 20 fictional songs, explicit user preferences.
- Genre match + mood match + energy proximity.
- Three weight strategies and artist variety.
- Scores are rule-based points, not enjoyment probabilities.

**Speaker notes**
The catalog contains twenty synthetic songs, not measurements of real recordings. A genre match adds points, a mood match adds points, and energy earns more when it is close to the requested value. Low energy is therefore just as valid as high energy. The original system has genre-first, mood-first, and energy-first strategies. A separate artist penalty can prevent one artist from dominating the list. These choices let us inspect the rules, but none of them proves that a real listener will enjoy the result.

## Slide 3 — The Extension (1:30–2:20)

**On the slide**
Input → validate → check coverage → rank → audit → filter → return/refuse.

Show `diagrams/architecture.mmd` or the rendered diagram in README.

**Speaker notes**
The new component is an integrated reliability mechanism. It requires explicit genre, mood, and energy inputs instead of guessing missing preferences. It checks whether the requested labels exist in the catalog, scores candidates with the original recommender, and then audits the result. The audit checks the original record, unique song ID, numeric score, artist penalty, and exact explanation. Finally, the system filters results below a support threshold. A failure returns a clear refusal and no recommendations. The application records a short decision trace so a reviewer can inspect the workflow.

## Slide 4 — Reproducible Demo (2:20–3:40)

Run these commands from the repository root, or show the committed outputs in README:

```bash
python -m src.app --request '{"genre":"pop","mood":"happy","energy":0.8}'
python -m src.app --request '{"genre":"lofi","mood":"chill","energy":0.35}'
python -m src.app --request '{"genre":"metal","mood":"happy","energy":0.8}'
```

**Speaker notes**
The pop request returns supported pop tracks with the actual scoring explanation. Changing the same fields to lofi, chill, and lower energy produces a different first result. Now the important negative case: the catalog has no metal songs. The original scorer still returned a list because mood and energy could add points. VibeGuide refuses that same request. This is a meaningful behavior change, not just a warning added beneath an irrelevant list. The rock example in the README also returns two supported tracks rather than adding an unrelated third track just to fill the requested count.

## Slide 5 — Reliability Evidence (3:40–4:30)

**On the slide**
- 42 automated tests passed.
- 8/8 predefined evaluation cases passed.
- Same-input replay checked.
- Five injected output faults failed closed.

```bash
python evaluate.py
python -m pytest -q
```

**Speaker notes**
The tests check ordinary rankings and deliberately bad inputs. They also inject five output faults: an invented ID, a changed title, a wrong score, a false explanation, and a duplicate song. Each must cause the audit to refuse the answer. The end-to-end evaluation includes three supported profiles and five invalid or unsupported requests. All eight cases passed, and replaying each request produced the same result. The full inputs, expected status, actual output, and action traces are committed as JSON. Passing these tests establishes behavior on this catalog; it is not a real-world accuracy estimate.

## Slide 6 — Trade-Offs and AI Collaboration (4:30–5:20)

**On the slide**
- Explicit JSON instead of an LLM intent parser.
- Refusal instead of silently filling every result slot.
- Synthetic data limits what can be claimed.
- AI-assisted implementation; automated verification disclosed.

**Speaker notes**
One accepted design was to independently recompute the score and explanation instead of trusting the output. One revised alternative was a free-text or LLM parser: I kept explicit JSON preferences so input behavior can be reproduced without an API key. Codex assisted with implementation, documentation, and executing the checks. The evidence describes those actual automated actions and does not claim independent human listening tests. There are still limitations. Exact labels miss synonyms, weights are hand chosen, and a support threshold can refuse a request that a human could interpret. Artist variety does not prove broader fairness.

## Slide 7 — What Comes Next (5:20–6:00)

**On the slide**
- Collect consented listener feedback.
- Evaluate held-out preferences and false refusals.
- Add validated multi-label genres.
- Keep humans responsible for suitability.

**Speaker notes**
The next step would be evaluating against consented real preference judgments, not simply adding more complexity. A larger catalog and multi-label genres could improve coverage, but I would measure both incorrect answers and unnecessary refusals. I would also compare relevance and variety instead of claiming one penalty solves fairness. The engineering lesson is that generating a ranked list and deciding whether the list is supported are separate responsibilities. This project makes that distinction inspectable through clear components, meaningful failure cases, and reproducible evidence.

## Portfolio Artifact

Repository: https://github.com/r7rudy37-sudo/applied-ai-system-final

This project demonstrates the ability to extend a working baseline, make refusal behavior explicit, audit generated output against source data, and test failures deliberately. The next professional step is to measure whether these safeguards improve real user outcomes while minimizing collection of personal information.
