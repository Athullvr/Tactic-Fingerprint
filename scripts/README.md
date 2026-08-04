# Tactic Fingerprint Generator

Tactic Fingerprint Generator turns StatsBomb Open Data match events into a numerical **Tactical DNA Signature**: a profile of how a football team occupies space, progresses the ball, presses, and circulates possession. It deliberately does not model results, xG, or win probability.

```
StatsBomb Open Data (local cache)
          |
          v
cleaned events -> per-team match features -> season Tactical DNA Signatures
                                                   |             |
                                                   v             v
                                           PCA / clustering   Streamlit explorer
```

## Setup

Use Python 3.10 or later:

```bash
pip install -r requirements.txt
python scripts/download_data.py --competition "Champions League" --season 2015
python scripts/run_pipeline.py --competition "Champions League" --season 2015 --mode season
streamlit run src/dashboard/app.py
```

The downloader uses `statsbombpy` and stores its cache exclusively in `data/raw/`. That directory is gitignored by design. Do not commit raw StatsBomb events; download them locally and comply with the [StatsBomb Open Data licence](https://github.com/statsbomb/open-data). Only compact derived outputs belong in `data/processed/`.

## What the signature means

- **Possession share** is a team’s share of possession-related events.
- **Average pass length** and **long-pass ratio** describe directness.
- **Forward-pass ratio** measures progression rather than circulation.
- **Circulation tempo** estimates completed passes per possession minute.
- **Action height** approximates how high defensive actions occur.
- **Width dispersion** captures whether actions are spread across the pitch.
- **30 zone-action shares** preserve the team’s territorial footprint on a 6×5 pitch grid.

Per-match signatures support tactical-variance work. Season signatures hold the mean and standard deviation of every feature across matches. The intelligence layer standardises these vectors before PCA, similarity scoring, and k-means clustering.

## Development

Run the fully offline synthetic test suite with:

```bash
pytest
```

`config/settings.yaml` contains pitch/grid dimensions, feature settings, and analysis defaults. Pipeline logic lives in `src/`; notebooks are intentionally reserved for exploration.

## Web product MVP

The repository now includes a production-oriented web layer while retaining Python for analytics:

```bash
# Terminal 1: serve derived tactical data
uvicorn src.api.app:app --reload --port 8000

# Terminal 2: serve the Next.js interface
cd web
npm install
npm run dev
```

The API exposes derived signatures only (`/health`, `/teams`, `/teams/{team}`, `/compare`, `/embedding`). The web interface provides team selection, two-team radar comparison, territorial footprint, tactical summaries, and similarity navigation. It is deliberately separated from the raw-data pipeline so visitors never trigger StatsBomb downloads.

For Vercel, the season pipeline also writes `web/public/data/tactical.json`, a small static derived-data payload. This makes the Next.js site deployable by itself; configure Vercel's **Root Directory** as `web/` and deploy. Re-run the season pipeline before a new deployment whenever the underlying competition data changes.
