# ScentMatcher

A Flask prototype that recommends perfumes using Jaccard similarity between sets of listed fragrance notes. This is an interpretable content-based baseline, not a trained ML model.

## Run locally

Requires Python 3.10 or later.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app seed-demo
flask --app app run
```

Open http://127.0.0.1:5000 and search for `Demo Rose`. The four demonstration products are synthetic, not real perfumes. Seeding is repeatable without adding duplicate demo rows.

SQLite works by default. For MySQL, set `DATABASE_URL` to `mysql+pymysql://USER:PASSWORD@HOST/perfume_matching`, create the database separately, then run `flask --app app init-db`. Keep credentials outside source control. Existing database schema migration is not automated by this prototype.

## How matching works

1. Find an exact perfume name, ignoring case. Partial searches offer name choices.
2. Split notes on commas or semicolons, trim whitespace, normalize case, and remove duplicates.
3. Exclude the selected perfume and candidates without shared notes.
4. Rank by shared notes divided by the union of both sets, returning up to five candidates.

`Demo Rose` vs `Demo Garden` shares rose and musk: 2 / 4 = 0.5. These are constructed examples, not quality evaluation results. Multiword notes remain intact. Duplicate perfume names are reported as ambiguous.

## Limitations and next evaluation

Note aliases, concentration, note intensity, and top/heart/base structure are not modeled. Overlap does not establish perceptual similarity. All catalog rows are loaded in memory, suitable only for a small prototype. No user relevance benchmark or recommendation quality claims are provided.

Next: curate a licensed catalog and relevance labels, compare against random and simple popularity baselines, then report Recall@5 and nDCG@5 on held-out queries before adding more complex models.

## Checks

```bash
python -m unittest discover -s tests -v
```
