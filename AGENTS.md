# Territory Arena

## Introduction

Territory is a competitive coding arena. You and your team will build a bot that competes on a shared 30x30 grid — painting tiles, shooting opponents, forming alliances, and fighting to control the most territory when the round ends.

Your bot is a standalone program that connects to the Arena server over HTTPS. Each round lasts about 60 seconds (200 ticks). Every tick, your bot receives the game state and submits one action. The Arena visualizes everything live on the big screen. Your goal: write the smartest strategy you can using Claude Code, starting from the reference player provided in this repo.

## Game Rules

**Grid & Vision:** The grid is 30x30. You have fog of war — you can see tiles within distance 5 of your position, distance 2 of any tile you own, and your allies' full vision. Tiles you can't see appear as unknown.

**Actions (one per tick):**

| Action | Effect |
|--------|--------|
| `move(direction)` | Move 1 tile N/S/E/W. Paints the destination your color. |
| `shoot(direction)` | Fires a shot up to 5 tiles in that direction. Hits the first player in the path. |
| `shield()` | Blocks all incoming shots this tick. No other action possible. |

**Shooting:** A hit steals 20 tiles from the victim (their furthest tiles from their position go to the shooter). A victim with fewer than 20 tiles is eliminated — all their remaining tiles go to the shooter.

**Alliances:** Any action can include `"support": player_id`. If two players mutually declare support in the same tick, they form a per-tick alliance. Alliances must be re-declared every tick. Allied shots against non-allies deal 30 damage instead of 20 (10 bonus tiles go to the ally). Alliances grant shared vision.

**Movement collisions:** Two players moving to the same tile — neither moves. Swap attempts — neither moves. Moving into an occupied tile — blocked.

**Tick resolution order:** Support → Shields → Shots (at pre-move positions) → Moves (simultaneous).

**Winning:** Most tiles when time runs out, or last player standing.

## API

Your bot communicates with the Arena via three HTTP endpoints. The reference implementation includes a Python client library (`api/client.py`) that wraps these for you.

### Endpoints

**Register** — `POST /api/register`

```json
{"name": "your_team_name", "entry_key": "<provided>"}
```

Returns your `player_id`, `secret_id` (used to authenticate all other calls), assigned `color`, and `game_settings` (grid size, tick speed, etc.). Registration is rejected while a game is active.

**Get Status** — `GET /api/status?secret_id=X`

Returns your fog-of-war view of the game: your position, the grid, visible players, all players' public info (tile counts, alive status, alliances), and the current tick.

Supports **long-polling**: pass `after_tick=N` and the server holds the request until tick N+1, then returns immediately. This is how your bot stays in sync with the game clock — no sleep loops needed.

**Submit Turn** — `POST /api/turn`

```json
{"secret_id": "X", "action": "move", "direction": "north", "support": null}
```

Actions: `move`, `shoot`, `shield`. Directions: `north`, `south`, `east`, `west`. The optional `support` field is a player ID for alliance proposals. Only your last submission per tick counts.

### Reference Player Implementation

There is a reference implementation in the reference folder that you can use as a starting point. This folder contains a Client Library and a Player. You can change the existing code, or add another.

### Reference Client Library

The `reference/api/` folder contains a ready-to-use client:

- **`api/client.py`** — `ArenaClient` class with methods `register()`, `get_status()`, and `submit_turn()`. Handles long-polling timeouts automatically.
- **`api/models.py`** — Pydantic models for all requests and responses. Key types:
  - `StatusResponse` — contains `you` (your position, tile count), `players` (public scoreboard), `grid` (2D array: -1=unknown, 0=empty, N=player_id), `visible_players` (positions of players you can see).
  - `PlayerSelf` — your full info including `x`, `y`, `alive`, `tile_count`, `allied_with`.

## Reference Player

The reference player (`reference/player.py`) plays random actions. It's your starting point — replace the strategy in `reference/strategy.py` with your own logic.

**Structure:**

```
reference/
  player.py                  — entry point and game loop
  api/client.py              — HTTP client (you won't need to modify this)
  api/models.py              — data models (you won't need to modify this)
  strategy.py                — YOUR STRATEGY GOES HERE
```

**Running it:**

```bash
cd reference
uv run player.py --name "YourTeamName" --entry <entry_key> --server <server_url>
```

The entry key will be provided to you. Always use `uv run` — never `python3` directly.  
The server is an optional argument to specify the game Arena server; if not provided, it uses the production Arena at https://territory-arena.fly.dev. 
You could specify a different server if you wanted to create your own.

**How the game loop works:** The player registers, waits for a game to start, then enters the tick loop. Each iteration long-polls for the next tick (`get_status(after_tick=current_tick)`), calls `choose_action(status)` to decide what to do, and submits the action. When the round ends, it waits and re-registers for the next round automatically.

**Writing your strategy:** Edit `reference/strategy.py`. Your `choose_action` function receives a `StatusResponse` and returns a dict:

```python
def choose_action(status: StatusResponse) -> dict:
    # status.you        — your position (x, y), tile_count, alive, allied_with
    # status.grid       — 2D grid: -1=unknown, 0=empty, N=player_id
    # status.players    — all players' public info (tile counts, alliances)
    # status.visible_players — positions of players you can see
    # status.tick       — current tick number
    # status.ticks_remaining — ticks left in the round

    return {"action": "move", "direction": "north"}           # move
    return {"action": "shoot", "direction": "east"}           # shoot
    return {"action": "shield"}                               # shield
    return {"action": "move", "direction": "south", "support": 3}  # move + propose alliance with player 3
```

## Notes

- **Use a consistent name** across rounds so you appear on the leaderboard. Pick your team name once and stick with it.
- **APIs are rate limited.** The long-polling pattern in the reference player is the intended way to stay in sync — don't poll status in a tight loop or make excessive requests.
- **Directions:** north = y-1, south = y+1, east = x+1, west = x-1. Grid origin (0,0) is top-left.
- **Grid coordinates:** `grid[y][x]` — row first, then column.
