# Model Card: VibeCompass 1.0

## 1. Model Name

**VibeCompass 1.0**

## 2. Goal, Intended Use, and Non-Intended Use

VibeCompass suggests five songs whose attributes match a stated taste profile. It
is a classroom simulation for learning how scoring and ranking work. It assumes
users can describe a target “vibe.” It is not trained machine learning, should not
be used to make claims about people, and is not suitable for commercial decisions.

## 3. Algorithm Summary

The system awards fixed points for matching genre and mood. It awards partial
points when energy, tempo, and optional audio features are close to the user's
targets. It scores every song, sorts the results, and then slightly lowers repeated
artists and genres. Balanced, genre-first, and energy-focused strategies change the
weights without changing the catalog. Every displayed explanation reports the
actual points used.

## 4. Data Used

The CSV contains 20 fictional songs across pop, lofi, rock, ambient, jazz,
synthwave, indie pop, folk, EDM, blues, R&B, hip-hop, classical, reggae, metal,
and indie. Every song has 15 fields: identity fields plus genre, mood, energy,
tempo, valence, danceability, acousticness, popularity, release decade,
instrumentalness, speechiness, and liveness. It lacks lyrics, language, culture,
real listening history, and enough songs to represent any genre well.

## 5. Strengths and Observed Behavior

The system is deterministic, transparent, and easy to inspect. Happy pop correctly
selects “Sunrise City,” chill lofi selects “Library Rain,” and intense rock selects
“Storm Runner.” Partial numerical similarity allows useful cross-genre discoveries.
The diversity rule stops one artist from occupying the list without explanation.

## 6. Limitations and Bias

Handwritten labels reduce music to a few numbers and exact categories. A small
catalog means genres with several entries have more chances to appear, while a
genre with one entry has no within-genre variety. Fixed weights can create a filter
bubble by rewarding known labels and overlooking a surprising song with a similar
sound. The adversarial sad/high-energy profile exposes a weakness: “Chrome Pulse”
wins through EDM, energy, and tempo even though its euphoric mood conflicts with
sadness. Popularity is available but disabled by default so already-popular songs
do not automatically receive more exposure.

## 7. Evaluation Process

I loaded all 20 rows, ran eight automated tests, and requested five songs for four
profiles: High-Energy Happy Pop, Chill Acoustic Lofi, Deep Intense Rock, and the
conflicting Adversarial Sad Workout. I checked ordering, score types, exact reason
strings, multiple strategies, diversity penalties, invalid inputs, and CSV numeric
conversion. I also compared genre-first with energy-focus as a controlled weight
experiment.

Pairwise profile comparisons:

- Pop vs. lofi: pop favors danceable, happy tracks; lofi favors quiet, acoustic tracks.
- Pop vs. rock: both value energy, but rock's faster tempo and liveness move “Storm Runner” first.
- Pop vs. adversarial: happy mood helps pop, while the conflicting profile rewards EDM and speed.
- Lofi vs. rock: their energy and tempo targets point in opposite directions, producing almost disjoint lists.
- Lofi vs. adversarial: lofi's acoustic target favors “Library Rain”; the workout target favors electronic intensity.
- Rock vs. adversarial: both favor high energy, but rock adds intense mood/liveness while the adversarial profile asks for sad valence.

The surprising result was “Gym Hero” appearing in both pop and rock lists. This
makes sense: it is pop and extremely energetic, and the rock profile's
energy-focused strategy deliberately allows cross-genre matches.

## 8. Ideas for Improvement

1. Learn weights from likes, skips, and repeated listening instead of choosing them.
2. Expand the catalog and use multi-label genres and moods.
3. Add novelty and artist-history controls that adapt to each listener.

## 9. Personal Reflection

The biggest lesson was that a small scoring choice can visibly change an entire
ranking. AI accelerated the initial implementation and suggested useful edge cases,
but I double-checked every claim by running the program and tests. I rejected the
idea of rewarding raw energy because it would always prefer louder music; closeness
to a target better represents preference. It surprised me that a transparent,
non-learning formula could still produce recommendations that felt reasonable.
Next I would compare these rules with collaborative filtering on anonymous
listening events.
