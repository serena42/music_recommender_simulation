# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

MoodyClues 1.0

---

## 2. Intended Use  

This is an exploratory music recommender system built to help a user understand how more complex recommendation systems work. It generates simple content-based recommendations (songs that are similar in genre, mood, energy, acousticness, and optional danceability/valence targets) and explains why each song was chosen.

It assumes the user can provide a few clear preferences up front, such as favorite genre, mood, and target energy. It does not learn from long-term behavior like listens, skips, or playlist history.

This project is mainly for classroom exploration and model transparency, not for production use.

---

## 3. How the Model Works  

This recommender compares each song to a user's taste profile and gives the song a score.

The song features it uses are:

- genre
- mood
- energy
- acousticness
- optional danceability
- optional valence (positivity)

The user preferences it considers are:

- favorite and ranked genres
- favorite and ranked moods
- target energy plus how strict/flexible energy matching should be
- acoustic preference on a spectrum (not just yes/no)
- optional danceability and valence targets

How scoring works in plain language:

- Songs get points for matching genre and mood.
- Songs also get points when their energy and acoustic feel are close to what the user asked for.
- If the user provides danceability or valence targets, those add small bonus points as tie-breakers.
- After each song gets a total score, songs are sorted from highest to lowest and the top results are shown with an explanation.

What changed from the starter logic:

- Moved from simpler matching to additive weighted scoring.
- Added ranked preferences so second/third choices still matter.
- Replaced binary acoustic preference with a 0-1 spectrum.
- Added energy flexibility so users can be strict or broad about energy.
- Added optional danceability and valence tie-breakers.
- Added optional diversity-aware reranking for top-k to reduce repeated artists/genres.

Weighting rationale: genre counts more than mood because genre is usually a stronger long-term preference, while mood is more situational. Energy and acousticness help separate songs that might look similar on genre/mood alone.

Data flow:

```mermaid
flowchart TD
    A([User Preferences\ngenre · mood · energy · energy_flexibility · acoustic_preference\noptional: target_danceability · target_valence]) --> B

    B[Load songs.csv\n18 songs → Song objects] --> C

    C{For each song in catalog} --> D

    D[Score the song\ngenre match    → up to 2.0 pts\nmood match     → up to 1.0 pts\nenergy close   → up to 1.0 pts\nacoustic close → up to 1.0 pts\ndanceability   → up to 0.2 pts (optional)\nvalence        → up to 0.1 pts (optional)\n─────────────────────\ntotal score   ≤ 5.3 pts] --> E

    E{More songs?}
    E -- Yes --> C
    E -- No  --> F

    F[Sort all scores\nhigh to low] --> G

    G([Top K Results\nsong · score · explanation])
```

---

## 4. Data  

The recommender uses a small catalog of 18 songs stored in `data/songs.csv`.

Each song includes:

- basic metadata (title, artist, genre, mood)
- numeric audio-style attributes (energy, tempo, valence, danceability, acousticness)

The catalog includes a mix of genres and moods, such as pop, lofi, rock, ambient, jazz, synthwave, classical, hip hop, metal, reggae, country, edm, blues, and funk, plus moods like happy, chill, intense, focused, confident, peaceful, aggressive, euphoric, melancholic, and playful.

I expanded the catalog during development to improve variety and reduce obvious overfitting to only a few genres.

What is still missing:

- behavior data (likes, skips, repeat plays, playlist history)
- broader catalog scale (18 songs is intentionally small for classroom exploration)
- context signals (time of day, activity, recent listening session)

---

## 5. Strengths  

This system works best for users who can describe what they want right now in clear terms (genre, mood, energy, and acoustic feel).

Where it performs well:

- It responds clearly to profile changes. High-Energy Pop, Chill Lofi, and Pure Adrenaline produce noticeably different top results.
- It handles ranked preferences better than a strict one-label approach, so second/third choices can still show up.
- It gives transparent explanations, which makes it easy to understand why songs were recommended.
- It supports nuanced controls (acoustic spectrum, energy flexibility, optional danceability/valence) without making the system hard to interpret.

Patterns that matched intuition:

- Chill profiles surface calmer, more acoustic songs.
- High-energy profiles consistently surface faster, more intense songs.
- "Gym Hero" appears often for upbeat users because it matches strong numeric signals (high energy, low acousticness, high danceability), even when mood is not the absolute best match.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly.

### Critical Filter Bubbles Identified

**1. Genre/Mood Dominance Creates Genre Lock-In (HIGH severity)**

Genre and mood together account for 60% of the max possible score (3.0 out of 5.0 points). This creates a strong genre bubble:

- A song that matches the user's preferred genre earns +2.0 points (40% of total), regardless of how well it matches energy or mood.
- A song in a non-preferred genre can earn at most 3.0 points (mood + energy + acousticness), even if it's perfect on all other dimensions.
- **Effect:** Users are trapped in their favorite genre. A user who loves pop will rarely see rock, jazz, or metal songs, even if a rock song has the exact energy and mood they want right now.

**Example:** Ultra Chill user (low energy target = 0.1) who loves lofi will be recommended more lofi songs even if a 0.12-energy ambient song would be a better match. Both are essentially the same energy, but lofi gets +2.0 genre points while ambient gets only 0.4 (secondary genre preference), so lofi dominates.

**2. Binary Acoustic Preference Acts as Hard Filter (HIGH severity) — MITIGATED**

Status: implemented in commit `fdd829f`.

Acoustic preference is now a continuous value (`acoustic_preference` in [0.0, 1.0]) scored by closeness, instead of a boolean.

- 0.0 means strongly non-acoustic preference
- 1.0 means strongly acoustic preference
- Mid values (for example 0.4 to 0.6) express mixed or flexible taste
- Legacy boolean input is still accepted and mapped to 0.0/1.0 for backward compatibility

Effect: acousticness is now a tunable preference rather than a hard gate, reducing the chance of hiding whole families of songs.

**3. Energy Closeness Gap Narrows Recommendations for Flexible Users (MEDIUM severity) — MITIGATED**

Status: implemented in the current codebase (Fix #3 rollout).

Energy scoring now includes `energy_flexibility` in [0.0, 1.0]. The model maps this to a dynamic energy range:

- `max_range = 0.5 + (0.5 * energy_flexibility)`
- flexibility 0.0 (strict) -> max_range 0.5
- flexibility 1.0 (flexible) -> max_range 1.0

Effect: users who are flexible on energy preserve stronger scores for farther energy values, reducing over-concentration in a narrow mid-energy band.

**4. Ranked Preference Decay Undervalues Secondary Tastes (MEDIUM severity) — MITIGATED**

Status: implemented in commit `c353b73`.

Ranked preferences now decay exponentially: `0.8 ** idx`.

- 1st: 1.00
- 2nd: 0.80
- 3rd: 0.64
- 4th: 0.51
- 5th: 0.41

Effect: secondary preferences retain meaningful influence without an abrupt floor, reducing over-concentration on only top-ranked tastes.

**5. No Serendipity or Diversity Mechanism (MEDIUM severity) — MITIGATED**

Status: implemented in the current codebase (Challenge 3 rollout).

The algorithm now supports optional diversity-aware reranking after base scoring.

- During top-k selection, candidates receive repeat penalties based on how many already-selected songs share the same artist or genre.
- Default penalties: artist = 0.35, genre = 0.15.
- **Effect:** close-score results become more varied, reducing artist/genre clustering while preserving relevance-first behavior.

**6. Missing Continuous Features (MEDIUM severity) — PARTIALLY MITIGATED**

Status: implemented in the current codebase (Fix #6 rollout).

Danceability and valence are now supported as optional user targets and scored as low-weight tie-breakers:

- danceability weight: 0.2
- valence weight: 0.1

Effect: users can now explicitly signal "more danceable" or "more positive" preferences, improving fine-grained ranking among otherwise similar songs.

Residual gap: tempo (BPM) is still not scored.

### Suggested Fixes and Implementation Status

**Fix #1: Reduce Genre Weight & Add Diversity Penalty (addresses Filter Bubble #1 & #5) — PARTIALLY COMPLETED**

Change weights from (genre=2.0, mood=1.0, energy=1.0, acoustic=1.0) to (genre=1.0, mood=1.0, energy=1.0, acoustic=1.0).

Then add a diversity penalty to top-k selection: once a song is recommended, reduce the score of songs with the same genre by 0.3 × remaining_points. This encourages the top-5 to be more varied while still respecting preferences.

Current status: diversity reranking is implemented with configurable artist/genre repeat penalties. Genre weight is still 2.0 and remains future tuning work.

**Fix #2: Replace Boolean Acoustic with Spectrum (addresses Filter Bubble #2) — COMPLETED**

Instead of `likes_acoustic: bool`, use `acoustic_preference: float in [0.0, 1.0]`, where 0.0 = "prefers non-acoustic" and 1.0 = "prefers acoustic."

Score acousticness exactly like energy: `_closeness(user.acoustic_preference, song.acousticness)`.

This removes the hard filter and allows nuance (e.g., "I slightly prefer acoustic" = 0.6).

**Fix #3: Adjust Energy Range Based on User Flexibility (addresses Filter Bubble #3) — COMPLETED**

Accept an optional `energy_flexibility: float` parameter (default 0.5 = medium flexibility).

Use `max_range = 0.5 + (0.5 * energy_flexibility)` to adjust the closeness calculation. A user with flexibility=1.0 (very flexible) gets max_range=1.0, so farther energy values still retain credit. A user with flexibility=0.0 (rigid) gets max_range=0.5, so only closer values score highly.

**Fix #4: Slower Ranked Preference Decay (addresses Filter Bubble #4) — COMPLETED**

Change the decay formula from `1.0 - (0.2 * idx)` to `0.8 ** idx` (exponential decay with base 0.8).

- 1st: 0.8^0 = 1.0
- 2nd: 0.8^1 = 0.8
- 3rd: 0.8^2 = 0.64
- 4th: 0.8^3 = 0.51
- 5th: 0.8^4 = 0.41

No hard floor; even distant preferences contribute meaningfully.

**Fix #5: Add a Diversity Bonus to Top-K Selection (addresses Filter Bubble #5) — COMPLETED**

Reranking is now implemented as a greedy top-k selection pass after base scoring. At each step, remaining songs are adjusted with repeat penalties for already-selected artist and genre matches.

- adjusted score = base score - (artist_penalty x artist_repeat_count) - (genre_penalty x genre_repeat_count)
- defaults: artist_penalty = 0.35, genre_penalty = 0.15
- configurable through `diversify`, `artist_repeat_penalty`, and `genre_repeat_penalty`

**Fix #6: Score Danceability and Valence (addresses Filter Bubble #6) — COMPLETED**

Add optional user preferences for `target_danceability: float` and `target_valence: float` (default = None, so they don't affect users who don't specify).

When specified, score them the same way as energy: `_closeness(target_danceability, song.danceability)`.

Assign small weights (0.2 and 0.1) so they're tie-breakers, not dominant.

---

## 7. Evaluation  

I tested eight user profiles end-to-end:

- High-Energy Pop
- Chill Lofi
- Deep Intense Rock
- Conflicting Vibe (high energy + melancholic)
- Ultra Chill (very low energy)
- Pure Adrenaline (very high energy)
- Acoustic Rocker (unusual combo)
- Everything Goes (broad preferences)

What I looked for:

- Do top songs shift when energy, acoustic preference, and mood change?
- Do unusual profiles produce different results instead of copying one "default" list?
- Do optional danceability/valence preferences act as tie-breakers instead of dominating?

What surprised me:

- "Gym Hero" appears for multiple profiles, including Happy Pop users, because it is high energy, low acoustic, and fairly danceable. Even when mood is not a perfect match, those numeric features keep it competitive.
- The "Everything Goes" profile still leans toward pop/indie-pop near the top. That makes sense because genre still has the biggest weight, so broad users are not fully random.
- "Acoustic Rocker" shows why mixed preferences are hard: rock/metal songs can still win even when acoustic preference is high, because strong genre and mood matches carry a lot of weight.
- With diversity reranking enabled, broad profiles show fewer repeated artists/genres in top-k when song scores are close.

Simple checks I ran:

- Compared top-5 outputs across all profile pairs to verify that each profile meaningfully changes recommendations.
- Used targeted tests to verify that energy flexibility reduces penalty on farther energy values.
- Used targeted tests to verify that danceability/valence only affect ranking when explicitly provided.
- Added targeted tests that verify diversity reranking can reduce repeated artists/genres in close-score scenarios.

Scope note: this is a larger effort than the minimum assignment. In addition to the baseline recommender, it includes four implemented bias-mitigation upgrades and expanded automated test coverage.

---

## 8. Future Work  

Ideas for how you would improve the model next.

**Immediate priority: mitigate remaining filter bubbles identified in Section 6.**

- ✅ Introduced slower ranked preference decay (exponential instead of linear) so secondary tastes have real impact.
- ✅ Replaced boolean acoustic preference with a spectrum (0.0–1.0), removing the hard filter.
- ✅ Added user energy flexibility so contextual energy preferences are supported.
- ✅ Scored missing features (danceability, valence) for users who care about them.
- Tune the diversity penalty values and trigger conditions using user feedback.

**Medium-term enhancements:**

- Treat the new multi-genre and multi-mood preference lists as a first step toward hybrid preference modeling, then combine them with behavior signals (likes, skips, and playlist history) when that data becomes available.
- A/B test different weight schemes to find the balance between personalization and serendipity.
- Add temporal context: users might want different energy/mood at different times of day or for different activities.
- Compare recommendations to real services (Spotify, Apple Music) to validate whether the system matches user expectations.

---

## 9. Personal Reflection  

My biggest learning moment was realizing that recommendation quality is mostly about careful weighting, not complexity. When I changed the scoring rules (for example, ranked-preference decay and acoustic preference handling), the top songs changed immediately. That made it clear that even a simple model can strongly shape what a user hears.

Using AI tools helped me move faster when brainstorming fixes, drafting tests, and documenting tradeoffs. The biggest value was speed in exploring options. The moments I had to double-check were numerical assumptions and behavior claims. I repeatedly verified those with real profile runs and pytest results so I did not trust generated ideas blindly.

What surprised me most is how "real" the recommendations can feel even with a straightforward additive scoring algorithm. Songs like "Gym Hero" kept showing up for upbeat users, which initially looked suspicious. After checking the factors, it made sense: high energy, low acousticness, and strong danceability gave it a strong overall fit.

If I extended this project next, I would tune diversity penalties with user feedback, include tempo preferences as another optional feature, and run a small user study to compare perceived quality before and after diversity tuning.
