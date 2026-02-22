import argparse
import time

from api.client import ArenaClient
from strategy import choose_action

ARENA = "https://territory-arena.fly.dev"


def main():
    parser = argparse.ArgumentParser(description="Territory Arena Reference Player")
    parser.add_argument("--name", required=True, help="Team/player name")
    parser.add_argument("--entry", default="arena", help="Entry key (default: arena)")
    parser.add_argument("--server", default=ARENA, help="Arena server URL")
    args = parser.parse_args()

    client = ArenaClient(args.server)

    while True:
        reg = client.register(args.name, args.entry)
        if not reg.success:
            print(f"Registration failed: {reg.error}, retrying...")
            time.sleep(3.0)
            continue

        secret_id = reg.secret_id
        print(f"Registered as '{args.name}' (player {reg.player_id})")

        status = client.get_status(secret_id)
        while not status.game_active:
            time.sleep(1.0)
            status = client.get_status(secret_id)

        current_tick = status.tick
        while True:
            status = client.get_status(secret_id, after_tick=current_tick)
            if not status.success or not status.game_active or not status.you.alive:
                break
            current_tick = status.tick
            action = choose_action(status)
            result = client.submit_turn(secret_id=secret_id, **action)
            if not result.success:
                print(f"Turn error: {result.error}")

        while True:
            time.sleep(2.0)
            status = client.get_status(secret_id)
            if not status.success or not status.game_active:
                break
        time.sleep(2.0)


if __name__ == "__main__":
    main()
