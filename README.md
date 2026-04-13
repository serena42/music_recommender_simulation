# 🎵 Music Recommender Simulation

## Project Summary

This project simulates a simple content-based music recommender. The system takes a user's preferred genre, mood, energy target, and acoustic preference, then ranks songs by a weighted similarity score. Recommendations include short explanations so each result is transparent and easy to understand.

---

## How The System Works

Real-world recommendation systems usually combine multiple signal types: content signals (genre, tempo, mood), behavior signals (likes, skips, watch/listen time), and collaborative patterns across many users. This simulation focuses on transparent, content-based matching, so it prioritizes how well a song's attributes match one user's stated preferences rather than large-scale behavior history.

Song object features used in this simulation:

- id
- title
- artist
- genre
- mood
- energy
- tempo_bpm
- valence
- danceability
- acousticness

UserProfile features used in this simulation:

- favorite_genre
- favorite_mood
- preferred_genres (ordered list for partial-credit matching)
- preferred_moods (ordered list for partial-credit matching)
- target_energy
- likes_acoustic

### Scoring Rule

For each song, the recommender computes an additive point score with a maximum of 5.0 using:

- genre match: up to 2.0 pts
- mood match: up to 1.0 pts
- energy closeness to target: up to 1.0 pts
- acousticness closeness to preference: up to 1.0 pts

Genre and mood use partial credit for lower-ranked preferences and substring matching (so "indie pop" matches "pop"). Numeric features use a closeness function — the nearer a song's value is to the target, the more points it earns.

For acousticness, the user preference is converted to a target:

- likes_acoustic = true -> target 1.0
- likes_acoustic = false -> target 0.0

After scoring all songs, the system sorts by score in descending order and returns the top k songs.

### Explanation Generation

Each recommendation includes a short explanation based on the strongest matched factors, for example genre match, mood match, close energy, or acoustic fit.

### Data Types in This Simulation

Main data types currently used:

- Song metadata: title, artist, genre, mood
- Audio-style numeric features: energy, tempo_bpm, valence, danceability, acousticness
- User preference inputs: favorite_genre, favorite_mood, preferred_genres, preferred_moods, target_energy, likes_acoustic

Data types not included yet:

- Explicit song likes/dislikes per user
- Skip history
- Play counts or repeat listens
- Playlist membership or co-listen behavior

This means the current system is content-based only. It ranks songs by feature similarity, not by behavioral interaction logs.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Sample Output

```
Loaded songs: 18

             Top Recommendations
---------------------------------------------
 #1  Sunrise City                   4.75 / 5.00
      * genre match (+2.00)
      * mood match (+1.00)
      * energy closeness (+0.93)
      * acousticness closeness (+0.82)
---------------------------------------------
 #2  Rooftop Lights                 4.64 / 5.00
      * genre match (+2.00)
      * mood match (+1.00)
      * energy closeness (+0.99)
      * acousticness closeness (+0.65)
---------------------------------------------
 #3  Gym Hero                       3.77 / 5.00
      * genre match (+2.00)
      * energy closeness (+0.82)
      * acousticness closeness (+0.95)
---------------------------------------------
 #4  City Cipher                    1.85 / 5.00
      * energy closeness (+0.99)
      * acousticness closeness (+0.86)
---------------------------------------------
 #5  Night Drive Loop               1.78 / 5.00
      * energy closeness (+1.00)
      * acousticness closeness (+0.78)
---------------------------------------------
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## User Preference Profiles

The recommender is tested with three distinct taste archetypes defined in `src/main.py`:

### High-Energy Pop
- Preferred genres: pop, funk, indie pop
- Preferred moods: happy, playful, confident
- Energy: 0.80 (high)
- Acoustic preference: False

Example top recommendation: "Sunrise City" (pop, happy, 0.82 energy)

### Chill Lofi
- Preferred genres: lofi, ambient
- Preferred moods: chill, focused, peaceful
- Energy: 0.35 (very low)
- Acoustic preference: True

Example top recommendation: "Library Rain" (lofi, chill, 0.35 energy, 0.86 acoustic)

### Deep Intense Rock
- Preferred genres: rock, metal, hip hop
- Preferred moods: intense, aggressive, confident
- Energy: 0.90 (very high)
- Acoustic preference: False

Example top recommendation: "Storm Runner" (rock, intense, 0.91 energy)

These three profiles demonstrate the system's ability to differentiate between contrasting musical tastes. Run `python -m src.main` to see top-5 recommendations for each profile side-by-side.

---

## Experiments You Tried

### Taste Profile Critique

I tested this taste profile:

- genre: hip hop
- mood: confident
- energy: 0.78
- likes_acoustic: false

To check whether the profile can separate contrasting styles, I compared one intense rock song with several chill lofi songs.

- Storm Runner (rock, intense): score 0.362
- Midnight Coding (lofi, chill): score 0.240
- Focus Flow (lofi, focused): score 0.227
- Library Rain (lofi, chill): score 0.200

Interpretation:

- The system does differentiate intense rock from chill lofi under this profile.
- Most of the separation comes from energy and acousticness closeness, not genre or mood matches.
- The profile is somewhat narrow because it uses one favorite genre and one favorite mood as exact matches.
- This can under-represent users who like multiple genres or different moods in different contexts.

### Design Decision Recorded

Decision: expand the profile to support multiple preferred genres and moods.

- New fields added: preferred_genres and preferred_moods.
- These lists are ordered, so the first preference gets full categorical credit and lower-ranked preferences get partial credit.
- Why: this makes the profile less narrow and better captures users who rotate between multiple genres/moods.
- Result: the recommender can still separate very different styles (like intense rock vs chill lofi), while better rewarding secondary tastes instead of treating them as complete mismatches.

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"

