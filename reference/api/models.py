"""Pydantic models for all Arena API request/response types."""

from typing import Literal

from pydantic import BaseModel


# --- Request models ---


class RegisterRequest(BaseModel):
    name: str
    entry_key: str


class TurnRequest(BaseModel):
    secret_id: str
    action: Literal["move", "shoot", "shield"]
    direction: Literal["north", "south", "east", "west"] | None = None
    support: int | None = None


# --- Response models ---


class GameSettings(BaseModel):
    grid_width: int
    grid_height: int
    tick_speed_ms: int
    max_round_seconds: int
    bullet_range: int


class RegisterResponse(BaseModel):
    success: bool
    player_id: int | None = None
    secret_id: str | None = None
    color: str | None = None
    game_settings: GameSettings | None = None
    error: str | None = None


class PlayerSelf(BaseModel):
    player_id: int
    name: str
    x: int
    y: int
    alive: bool
    tile_count: int
    supporting: int | None = None
    allied_with: list[int] = []


class PlayerPublic(BaseModel):
    player_id: int
    name: str
    tile_count: int
    alive: bool
    supporting: int | None = None
    allied_with: list[int] = []


class VisiblePlayer(BaseModel):
    player_id: int
    x: int
    y: int


class StatusResponse(BaseModel):
    success: bool
    game_active: bool = False
    tick: int = 0
    ticks_remaining: int = 0
    you: PlayerSelf | None = None
    players: list[PlayerPublic] = []
    grid: list[list[int]] = []
    visible_players: list[VisiblePlayer] = []
    error: str | None = None


class TurnResponse(BaseModel):
    success: bool
    message: str | None = None
    error: str | None = None
