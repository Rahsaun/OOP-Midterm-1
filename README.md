# OOP Midterm #1 — Zombie Simulation State Storage Architecture

This is a **standalone class assignment** based on the *concepts* in the supplied Zombie Game. It does **not** import or modify the original project or repository.

## Assignment question
How can an object-oriented architecture keep simulation rules separate from storage so that different persistence backends can be substituted without changing the simulation?

## Design

```text
Agent (abstract)
  ├─ Human ─ ArmedHuman
  └─ Zombie

SimulationPlayground
  ├─ environment: width, height
  ├─ agents: humans, zombies
  └─ runtime: tick_count

SimulationController ── uses ──> StateStorage (abstract)
                                      ├─ JSONStorage
                                      └─ PostgreSQLStorage
```

The **simulation layer** holds agent behavior, movement, damage, and round updates; no SQL or file reading appears in those rules. The **storage layer** contains the abstract `StateStorage` interface and two independent implementations. `SimulationController` coordinates persistence and snapshots, but depends only on the interface. Both backends receive the same JSON-compatible dictionary representing agent attributes, arena dimensions and current tick.

This uses **abstraction** (abstract classes), **inheritance** (agent types and storage adapters), **polymorphism** (backends implement the same methods), and the **dependency inversion principle** (the controller depends on `StateStorage`, not on PostgreSQL or JSON directly). It is an example of the **Strategy pattern**.

## Files

| File | Role |
| --- | --- |
| `simulation.py` | Agent subclasses, rules, snapshot conversion, storage-independent controller |
| `storage.py` | Abstract interface, JSON file implementation, PostgreSQL implementation |
| `demo.py` | Run a simulation, save it, load it, and verify it |
| `tests/test_storage.py` | Tests identical controller behavior using two storage implementations |
| `requirements-postgres.txt` | Optional PostgreSQL driver |

## Run without a database

Requires Python 3.10 or newer. In the repository directory:

```bash
python demo.py --storage json --ticks 10
python -m unittest discover -s tests -v
```

This creates `game_state.json` (excluded from Git) and confirms that saved data can be restored.

## Run with PostgreSQL

A running PostgreSQL server and a database you are authorized to use are required.

```bash
python -m pip install -r requirements-postgres.txt
# Set DATABASE_URL in your shell, e.g., a postgresql://... connection URI.
python demo.py --storage postgres --ticks 10
```

The adapter creates a `simulation_state` table if necessary and updates a single saved snapshot. **Do not commit database passwords or `.env` files.**

## What the demonstration proves

The exact same `SimulationController` calls `save_state()` and `load_state()` no matter which backend it receives. Changing `JSONStorage(...)` to `PostgreSQLStorage(...)` changes **only application setup**, not the simulation rules. The file-backed demonstration works offline; PostgreSQL needs a running local or hosted database.

## Scope and limitations

- This is a focused, headless adaptation of the provided Zombie Game, not a full copy of its Tkinter UI or 10,000-agent multiprocessing engine.
- Saved snapshots include agent type, position, health, subtype attributes, arena size, and tick count. Python's internal random-generator state is not stored, so after loading, future wandering randomness is not guaranteed to exactly replay the original sequence.
- PostgreSQL is implemented but its integration must be tested against an available database.
- JSON storage uses an atomic replacement of the snapshot file. PostgreSQL stores one current snapshot rather than a run-history database.
