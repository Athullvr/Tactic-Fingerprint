"""StatsBomb Open Data acquisition with a local, gitignored cache."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

RAW_ROOT = Path("data/raw")


def resolve_competition(competition: str, season: int) -> tuple[int, int]:
    """Return StatsBomb competition and season IDs matching human-readable inputs."""
    from statsbombpy import sb

    competitions = sb.competitions()
    names = competitions["competition_name"].astype(str).str.casefold()
    seasons = competitions["season_name"].astype(str)
    target = competitions[names.eq(competition.casefold()) & seasons.str.contains(str(season), regex=False)]
    if target.empty:
        raise ValueError(f"No open StatsBomb competition found for {competition!r}, season {season}.")
    row = target.iloc[0]
    return int(row["competition_id"]), int(row["season_id"])


def download_competition(competition: str, season: int, raw_root: Path = RAW_ROOT) -> Path:
    """Download event tables once and cache each match as JSON below ``raw_root``."""
    from statsbombpy import sb

    competition_id, season_id = resolve_competition(competition, season)
    destination = raw_root / f"{competition_id}_{season_id}"
    destination.mkdir(parents=True, exist_ok=True)
    manifest_path = destination / "manifest.json"
    if manifest_path.exists():
        return destination

    matches = sb.matches(competition_id=competition_id, season_id=season_id)
    match_ids: list[int] = []
    for match_id in matches["match_id"].astype(int):
        output = destination / f"{match_id}.json"
        if not output.exists():
            sb.events(match_id=match_id).to_json(output, orient="records")
        match_ids.append(int(match_id))
    manifest_path.write_text(json.dumps({"competition": competition, "season": season, "match_ids": match_ids}, indent=2), encoding="utf-8")
    return destination


def load_cached_events(competition: str, season: int, raw_root: Path = RAW_ROOT, download_missing: bool = True) -> pd.DataFrame:
    """Load all cached event JSON files, optionally obtaining a missing cache first."""
    try:
        competition_id, season_id = resolve_competition(competition, season)
        location = raw_root / f"{competition_id}_{season_id}"
    except ModuleNotFoundError:
        location = raw_root / f"{competition.replace(' ', '_')}_{season}"
    # A directory may exist while a previous event download is still running.
    # Only a manifest marks a cache as complete and safe to analyse.
    if not (location / "manifest.json").exists():
        if not download_missing:
            raise FileNotFoundError(f"No cached data at {location}")
        location = download_competition(competition, season, raw_root)
    files = sorted(location.glob("*.json"))
    if not files:
        raise FileNotFoundError(f"No event files in {location}")
    frames = [pd.read_json(path) for path in files if path.name != "manifest.json"]
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
