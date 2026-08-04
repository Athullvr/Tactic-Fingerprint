from __future__ import annotations

import pandas as pd
import pytest


@pytest.fixture
def events() -> pd.DataFrame:
    """A small cleaned event table with two teams and known coordinates."""
    return pd.DataFrame([
        {"match_id": 1, "team": "Alpha", "event_type": "Pass", "minute": 1, "x": .10, "y": .20, "end_x": .50, "end_y": .20, "pass_outcome": None},
        {"match_id": 1, "team": "Alpha", "event_type": "Pass", "minute": 3, "x": .50, "y": .80, "end_x": .80, "end_y": .80, "pass_outcome": None},
        {"match_id": 1, "team": "Alpha", "event_type": "Carry", "minute": 4, "x": .70, "y": .50, "end_x": None, "end_y": None, "pass_outcome": None},
        {"match_id": 1, "team": "Alpha", "event_type": "Pressure", "minute": 5, "x": .75, "y": .35, "end_x": None, "end_y": None, "pass_outcome": None},
        {"match_id": 1, "team": "Beta", "event_type": "Pass", "minute": 1, "x": .30, "y": .40, "end_x": .20, "end_y": .40, "pass_outcome": None},
        {"match_id": 1, "team": "Beta", "event_type": "Ball Receipt*", "minute": 2, "x": .25, "y": .50, "end_x": None, "end_y": None, "pass_outcome": None},
        {"match_id": 1, "team": "Beta", "event_type": "Ball Recovery", "minute": 5, "x": .20, "y": .60, "end_x": None, "end_y": None, "pass_outcome": None},
    ])
