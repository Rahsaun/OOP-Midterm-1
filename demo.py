"""Run the same simulation with JSON or PostgreSQL storage.

Examples:
  python demo.py --storage json
  DATABASE_URL='postgresql://...' python demo.py --storage postgres
"""
import argparse
import os

from simulation import SimulationController, SimulationPlayground
from storage import JSONStorage, PostgreSQLStorage


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--storage", choices=("json", "postgres"), default="json")
    parser.add_argument("--ticks", type=int, default=10)
    parser.add_argument("--file", default="game_state.json")
    args = parser.parse_args()

    if args.ticks < 0:
        parser.error("--ticks must be nonnegative")
    if args.storage == "postgres":
        storage = PostgreSQLStorage(os.environ.get("DATABASE_URL", ""))
    else:
        storage = JSONStorage(args.file)

    game = SimulationController(storage, SimulationPlayground())
    game.simulation.populate(regular=20, armed=5, zombies=8)
    game.run(args.ticks)
    game.save()
    original = game.simulation.to_state()

    restored = SimulationController(storage)
    assert restored.load(), "Stored state should exist"
    assert restored.simulation.to_state() == original, "Round-trip state mismatch"
    print(f"Backend: {args.storage}")
    print(f"Restored tick: {restored.simulation.tick_count}")
    print(f"Humans: {len(restored.simulation.humans)}")
    print(f"Zombies: {len(restored.simulation.zombies)}")
    print("Save/load test: PASSED")


if __name__ == "__main__":
    main()
