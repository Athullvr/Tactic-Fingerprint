# Tactic Fingerprint Generator

Tactic Fingerprint Generator turns StatsBomb Open Data match events into a numerical **Tactical DNA Signature**: a profile of how a football team occupies space, progresses the ball, presses, and circulates possession. It deliberately does not model results, xG, or win probability.

**Live website:** [web-theta-dusky-20.vercel.app](https://web-theta-dusky-20.vercel.app)

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

The repository includes a production-oriented Next.js web layer while retaining Python for analytics. The public deployment is available at [web-theta-dusky-20.vercel.app](https://web-theta-dusky-20.vercel.app).

```bash
# Terminal 1: serve derived tactical data
uvicorn src.api.app:app --reload --port 8000

# Terminal 2: serve the Next.js interface
cd web
npm install
npm run dev
```

The FastAPI service exposes derived signatures only (`/health`, `/teams`, `/teams/{team}`, `/compare`, `/embedding`). The web interface is a standalone static-data deployment and provides team selection, two-team radar comparison, territorial footprint, tactical summaries, and similarity navigation. It is deliberately separated from the raw-data pipeline so visitors never trigger StatsBomb downloads.

### Tactical intelligence features

- **Explained similarity:** nearest-neighbour results state the two tactical dimensions that most closely match.
- **Peer-relative archetypes:** profiles are tagged transparently as high-control press, direct transition, wide progression, low territorial block, or balanced system.
- **Data confidence:** every profile shows the number of matches analysed and a sample-size label.
- **Cross-source comparison:** users can compare teams across the available competition and season sources.
- **Shareable analysis:** selections are encoded in the URL and can be copied directly from the site.
- **Style timeline:** match-by-match possession, directness, and defensive-height lines reveal whether a team keeps a stable identity or adapts across the available sample.

For Vercel, the season pipeline also writes `web/public/data/tactical.json`, a small static derived-data payload. This makes the Next.js site deployable by itself; configure Vercel's **Root Directory** as `web/` and deploy. Re-run the season pipeline before a new deployment whenever the underlying competition data changes.

### Current data scope

The deployed dataset combines the 2023-24 1. Bundesliga sample (18 clubs) with the original 2015 Champions League sample (Atletico Madrid and Real Madrid), giving the explorer 20 profiles. Dataset, team, and comparison controls let visitors switch between sources. Add further entries to `SOURCES` in `scripts/build_explorer_dataset.py` to extend coverage with more StatsBomb Open Data competitions and seasons.

```bash
python scripts/build_explorer_dataset.py
cd web
npx vercel --prod
```
