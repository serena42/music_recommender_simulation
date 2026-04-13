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

This recommender uses both a scoring rule and a ranking rule. The scoring rule evaluates one song at a time and gives it a relevance score based on genre match, mood match, and how close numeric features (like energy and acousticness) are to the user's preferences. The ranking rule then compares all song scores, sorts them from highest to lowest, and returns the top results. We need both parts because scoring tells us how well each individual song fits, while ranking turns those individual scores into a final recommendation list.

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

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

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

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

One next step is to treat the new multi-genre and multi-mood preference lists as a first step toward hybrid preference modeling, then combine them with behavior signals (likes, skips, and playlist history) when that data becomes available.

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

I asked Copilot to help design a math-based scoring rule for my music recommender, and we chose a closeness approach for numeric features so songs score higher when they are nearer to the user’s target values, not simply higher or lower overall. For example, a song with energy very close to the user’s preferred energy gets more points than songs far above or below that target. We then combined numeric closeness with categorical matches (genre and mood) using a weighted sum, which keeps the model simple and interpretable. We set genre to be slightly more important than mood because it usually represents a stronger long-term taste signal, while mood can vary by context. This process helped me understand how recommendation systems turn user preferences into measurable rules and how weight choices directly shape the final ranking.
