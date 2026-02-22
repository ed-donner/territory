"""Reference player strategy: random actions."""

import random

from api.models import StatusResponse


DIRECTIONS = ["north", "south", "east", "west"]


def choose_action(status: StatusResponse) -> dict:
    """Choose a random action for this tick.

    Returns a dict with keys matching TurnRequest fields:
    - action: str
    - direction: str (optional)
    - player_id: int (optional)
    """
    choice = random.choice(["move", "move", "move", "shoot", "shield"])

    if choice == "move":
        return {"action": "move", "direction": random.choice(DIRECTIONS)}
    elif choice == "shoot":
        return {"action": "shoot", "direction": random.choice(DIRECTIONS)}
    else:
        return {"action": "shield"}
