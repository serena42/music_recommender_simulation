# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

This is MY Jam 1.0

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

Algorithm recipe: this recommender uses additive point scoring and ranking. Each song earns raw points across four features: a genre match is worth up to 2.0 points, a mood match up to 1.0 point, energy closeness up to 1.0 point, and acousticness closeness up to 1.0 point, for a maximum possible score of 5.0. Genre and mood use partial credit when a song matches a lower-ranked preference. Energy and acousticness use a closeness function — the nearer the song's value is to the user's target, the more points it earns. The four contributions are summed into one total score, all songs are sorted highest to lowest, and the top k results are returned with short explanations of the strongest matched factors.

Weighting rationale: genre counts twice as much as mood (2.0 vs 1.0) because genre is a strong long-term taste signal — most listeners have hard genre preferences — while mood is contextual and shifts with situation. Energy and acousticness are continuous signals that serve as meaningful tiebreakers between songs that already match on genre and mood.

Potential biases: because genre carries 2.0 points and mood only 1.0, a song that perfectly matches the user's mood but sits in the wrong genre will always rank below a genre-matching song — even if the mood fit is strong. This means the system may over-prioritize genre and surface familiar-sounding songs over ones that would actually feel right in the moment. Additionally, since energy and acousticness are the only continuous signals scored, qualities like danceability, tempo, and valence earn no points — genres that tend to score low on energy and acousticness (blues, country, reggae) may be systematically under-recommended even for users with broadly compatible tastes.

Data flow:

```mermaid
flowchart TD
    A([User Preferences\ngenre · mood · energy · likes_acoustic]) --> B

    B[Load songs.csv\n18 songs → Song objects] --> C

    C{For each song in catalog} --> D

    D[Score the song\ngenre match   → up to 2.0 pts\nmood match    → up to 1.0 pts\nenergy close  → up to 1.0 pts\nacoustic close→ up to 0.5 pts\n─────────────────────\ntotal score   ≤ 4.5 pts] --> E

    E{More songs?}
    E -- Yes --> C
    E -- No  --> F

    F[Sort all scores\nhigh to low] --> G

    G([Top K Results\nsong · score · explanation])
```

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

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

**2. Binary Acoustic Preference Acts as Hard Filter (HIGH severity)**

Acoustic preference is a boolean that converts to target = 1.0 (likes) or 0.0 (dislikes).

- A user who dislikes acoustic music gets closeness = 1 - |0.0 - 0.9| = 0.1 for a highly acoustic song (only 0.1 points, ~2% of score).
- Even if that song perfectly matched genre, mood, energy, and mood (4.0 points), it scores 4.1 total.
- But a non-acoustic song with just genre match (2.0 points) will beat it because acoustic is treated like a hard filter, not a preference.
- **Effect:** Entire categories of music (acoustic-heavy genres like folk, blues, country for acoustic-disliker; electric heavy music for acoustic-lover) become essentially invisible.

**3. Energy Closeness Gap Narrows Recommendations for Flexible Users (MEDIUM severity)**

The closeness function uses a fixed max_range = 1.0 for energy (the full 0.0–1.0 scale).

- For a user with target_energy = 0.5 (middle ground), songs from 0.4 to 0.6 cluster at high closeness scores (0.8–1.0).
- Songs at 0.1 (very chill) or 0.9 (very energetic) score 0.6 closeness — good, but below the 0.7–1.0 band.
- **Effect:** Users with flexible energy preferences (who could enjoy both a relaxing song and an upbeat one) get biased toward the narrow 0.4–0.6 band. A user who says "I enjoy both chill and energetic songs" gets recommendations only from 0.4–0.6.

**4. Ranked Preference Decay Undervalues Secondary Tastes (MEDIUM severity)**

Ranked preferences decay: 1st = 1.0 credit, 2nd = 0.8, 3rd = 0.6, 4th+ = floor at 0.4.

- 1st genre choice: 1.0 × 2.0 = 2.0 points
- 4th genre choice: 0.4 × 2.0 = 0.8 points
- A song from a 4th-choice genre can score at most 0.8 + 1.0 + 1.0 + 1.0 = 3.8 points.
- A song from the 1st genre gets at least 2.0 + something else.
- **Effect:** Once users have 4+ genre preferences, lower-ranked ones barely matter. The "Everything Goes" adversarial profile (6 genres) effectively only uses the top 3.

**5. No Serendipity or Diversity Mechanism (MEDIUM severity)**

The algorithm is greedy—it returns the highest-scoring songs every time.

- Top-5 will likely cluster around the same genre, mood, and narrow energy band.
- **Effect:** Users never discover new artists or styles, only deeper dives into what they already know. Perfect filter bubble reinforcement.

**6. Missing Continuous Features (MEDIUM severity)**

Danceability and valence (positivity) are loaded from the dataset but never scored. Tempo (BPM) is never scored.

- Songs with high danceability (for dance lovers) or high valence (for happy listeners) cannot be recommended based on these traits.
- **Effect:** Entire patterns of taste go unaddressed. A user who wants upbeat music has no explicit way to signal that; they must infer it through energy and mood alone.

### Suggested Fixes

**Fix #1: Reduce Genre Weight & Add Diversity Penalty (addresses Filter Bubble #1 & #5)**

Change weights from (genre=2.0, mood=1.0, energy=1.0, acoustic=1.0) to (genre=1.0, mood=1.0, energy=1.0, acoustic=1.0).

Then add a diversity penalty to top-k selection: once a song is recommended, reduce the score of songs with the same genre by 0.3 × remaining_points. This encourages the top-5 to be more varied while still respecting preferences.

**Fix #2: Replace Boolean Acoustic with Spectrum (addresses Filter Bubble #2)**

Instead of `likes_acoustic: bool`, use `acoustic_preference: float in [0.0, 1.0]`, where 0.0 = "prefers non-acoustic" and 1.0 = "prefers acoustic."

Score acousticness exactly like energy: `_closeness(user.acoustic_preference, song.acousticness)`.

This removes the hard filter and allows nuance (e.g., "I slightly prefer acoustic" = 0.6).

**Fix #3: Adjust Energy Range Based on User Flexibility (addresses Filter Bubble #3)**

Accept an optional `energy_flexibility: float` parameter (default 0.5 = medium flexibility).

Use `max_range = 1.0 - (0.5 * energy_flexibility)` to adjust the closeness calculation. A user with flexibility=1.0 (very flexible) gets max_range=0.5, so energy values 0.25 and 0.75 still score 0.5 points. A user with flexibility=0.0 (rigid) gets max_range=1.0, so only much closer values score high.

**Fix #4: Slower Ranked Preference Decay (addresses Filter Bubble #4)**

Change the decay formula from `1.0 - (0.2 * idx)` to `0.8 ** idx` (exponential decay with base 0.8).

- 1st: 0.8^0 = 1.0
- 2nd: 0.8^1 = 0.8
- 3rd: 0.8^2 = 0.64
- 4th: 0.8^3 = 0.51
- 5th: 0.8^4 = 0.41

No hard floor; even distant preferences contribute meaningfully.

**Fix #5: Add a Diversity Bonus to Top-K Selection (addresses Filter Bubble #5)**

Rerank top-k after scoring: once a song enters the top-5, penalize the remaining songs if they share genre/mood with any already-selected song. Use a small penalty (~0.1 points per shared dimension) to encourage variety without breaking overall preference ordering.

**Fix #6: Score Danceability and Valence (addresses Filter Bubble #6)**

Add optional user preferences for `target_danceability: float` and `target_valence: float` (default = None, so they don't affect users who don't specify).

When specified, score them the same way as energy: `_closeness(target_danceability, song.danceability)`.

Assign small weights (0.2 and 0.1) so they're tie-breakers, not dominant.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

---

## 8. Future Work  

Ideas for how you would improve the model next.

**Immediate priority: mitigate filter bubbles identified in Section 6.**

- Implement diversity penalty in top-k selection to reduce genre/mood clustering.
- Replace boolean acoustic preference with a spectrum (0.0–1.0), removing the hard filter.
- Add user flexibility parameters for energy and mood so contextual preferences are supported.
- Introduce slower ranked preference decay (exponential instead of linear) so secondary tastes have real impact.
- Score missing features (danceability, valence) for users who care about them.

**Medium-term enhancements:**

- Treat the new multi-genre and multi-mood preference lists as a first step toward hybrid preference modeling, then combine them with behavior signals (likes, skips, and playlist history) when that data becomes available.
- A/B test different weight schemes to find the balance between personalization and serendipity.
- Add temporal context: users might want different energy/mood at different times of day or for different activities.
- Compare recommendations to real services (Spotify, Apple Music) to validate whether the system matches user expectations.

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

I asked Claude to help design a math-based scoring rule for my music recommender, and we chose a closeness approach for numeric features so songs score higher when they are nearer to the user’s target values, not simply higher or lower overall. For example, a song with energy very close to the user’s preferred energy gets more points than songs far above or below that target. We then combined numeric closeness with categorical matches (genre and mood) using additive point values, which keeps the model simple and interpretable. After comparing approaches, we moved from a normalized weight system (all weights summing to 1.0) to an explicit point recipe: genre is worth 2.0 points, mood 1.0, energy up to 1.0, and acousticness up to 0.5. The 2-to-1 genre-to-mood ratio was a deliberate design choice — genre tends to be a hard filter for most listeners while mood shifts with context. This process helped me understand how recommendation systems turn user preferences into measurable rules and how weight choices directly shape the final ranking.
