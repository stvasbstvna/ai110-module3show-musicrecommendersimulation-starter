# AI Interactions Log

## Agentic Workflow: Additional Attributes

**Prompt used:** “Expand the 10-song CSV to 20 diverse fictional songs. Add five or
more meaningful attributes with valid numeric ranges, update loading and scoring,
and verify that every row has the same headers.”

The agent added popularity, release decade, instrumentalness, speechiness, and
liveness (while retaining valence, danceability, and acousticness), expanded the
catalog to 20 songs, and made optional preferences contribute bounded similarity
points. I manually verified row counts, numeric conversion, 0–1 feature ranges, and
that the program loaded all 20 rows. Automated tests cover the typed fields.

## Agentic Workflow: Diversity and Fairness

**Prompt used:** “Add a transparent diversity rule that discourages repeated
artists and genres without permanently changing base scores. Include the penalty
in each explanation.”

The agent implemented sequential top-k selection with a 0.75 repeated-artist
penalty and 0.25 repeated-genre penalty. I checked that penalties only occur after
a related result is selected and added a focused test. This improves variety, but
the Model Card notes that it can demote a strong match.

## Design Pattern: Multiple Ranking Modes

**Pattern:** Strategy pattern represented by named weight configurations.

**Prompt used:** “Design balanced, genre-first, and energy-focused ranking
strategies without duplicating the scoring function. Make the mode selectable in a
user profile and reject invalid modes.”

AI suggested separate strategy classes and a weight-map alternative. I selected
the smaller weight-map design because all strategies use the same formula and only
the weights change. `MODE_WEIGHTS` holds the strategies, `score_song` selects one,
and `main.py` demonstrates all three. Tests confirm that modes change scores.

## Visual Output

**Prompt used:** “Create a dependency-free ASCII recommendation table containing
rank, title, artist, score, and exact scoring reasons.”

The agent added `print_table` and avoided a third-party formatting dependency. I
ran all four profiles and copied compact text transcripts to the README.

## Manual Review and Corrections

AI initially considered scoring higher raw energy as better. I rejected that rule:
a low-energy listener should not be pushed toward the loudest song. I used
`1 - abs(song value - target value)` instead and clamped similarity at zero. I also
verified deterministic tie-breaking, negative `k` validation, unknown-mode
validation, reason accuracy, and all eight tests.
