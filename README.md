# OOP Midterm #1

This is my midterm assignment. I used the concepts of the Zombie Game Simulation that DAn O'Keefe, Owen Bowers, and I worked on in assigment #2 to demonstrate how to keep **simulation logic independent from state storage**. The repository intentionally contains only **`Code.py`** and this **`README.md`**.

## How to run my code

**Requirements:** Python 3.10 or newer. No third-party packages or database installation are needed.

1. Open this GitHub repository and select **Code → Download ZIP**.
2. Extract the ZIP and open the extracted folder in VS Code, or open a terminal in the folder containing `Code.py`.
3. Run the JSON version (my chosen default):

```bash
python Code.py
```

On Windows, `py Code.py` may also work if the Python launcher is installed.

To choose the storage backend explicitly:

```bash
python Code.py --storage json --ticks 10
python Code.py --storage memory --ticks 10
python Code.py --storage both --ticks 10
```

The final command is the easiest way for my professor to verify **both implementations** with one run. A successful run prints `Save/load test: PASSED` for each backend, followed by `Both storage methods produced identical simulation states: PASSED`.

The JSON version writes a generated `game_state.json` file into the current folder; that file is output, not part of the source submission. Memory storage keeps its snapshot in a Python dictionary for the duration of the program; it does not create a file. The terminal prints the backend, restored tick count, and human and zombie counts. This assignment is a terminal demonstration rather than the graphical Tkinter version of the game.

## Storage methods I chose

- **JSON file storage (`JSONStorage`):** This is the method I personally chose as the program's default. It writes a snapshot into `game_state.json` and can load that snapshot again after the program has ended.
- **In-memory dictionary storage (`MemoryStorage`):** The second implementation holds the same snapshot in a Python dictionary. It is simple and fast for temporary data, but the snapshot disappears when the program exits.

Both classes are working examples of the same abstract interface; there is no PostgreSQL dependency or configuration.

## Detailed explanation of my design

### 1. Two distinct responsibilities

**Simulation layer:** `Agent` defines common properties such as position, speed, health, and whether an agent is alive. `Human`, `ArmedHuman`, and `Zombie` extend those behaviors. `SimulationPlayground` manages the arena, agents, and simulation steps. Its `step()` method applies the gameplay rules. None of these methods contain JSON file operations or dictionary-storage operations.

**State storage layer:** `StateStorage` is an abstract base class declaring the required methods `save_state(state)` and `load_state()`. `JSONStorage` writes and reads a JSON file; `MemoryStorage` saves and loads from a dictionary using `deepcopy` so stored snapshots do not accidentally change when live objects are modified.

### 2. What gets stored?

`SimulationPlayground.to_state()` creates an ordinary Python dictionary with three areas:

- **Agents:** each human, armed human, and zombie's type, position, speed, health, alive status, and relevant subclass attributes (for example, attack cooldowns).
- **Environment:** arena width and height.
- **Runtime:** simulation tick count and random seed.

`SimulationPlayground.from_state()` rebuilds the game objects from that snapshot. The code stores the random seed, not the random generator's exact internal state, so resuming the simulation does not guarantee identical future random choices.

### 3. How the layers communicate

```text
               Agent (abstract)
               /            \
         Human              Zombie
           |
       ArmedHuman

     SimulationPlayground
       (rules and state)
              |
              v
     SimulationController
       (save / restore)
              |
              v
     StateStorage (abstract)
          /           \
         v             v
    JSONStorage    MemoryStorage
     JSON file      Python dict
```

`SimulationController` receives a storage object when it is constructed. Its `save()` method calls `storage.save_state(simulation.to_state())`. Its `load()` method calls `storage.load_state()` and reconstructs a `SimulationPlayground` from the returned data. The controller uses the abstract method names; it does not need to inspect whether the backend is JSON or memory.

### 4. OOP principles in this design

- **Abstraction:** `StateStorage` describes storage behavior without exposing implementation details. `Agent` similarly defines a shared agent interface.
- **Inheritance:** `JSONStorage` and `MemoryStorage` inherit from `StateStorage`, and the human/zombie subclasses inherit common behavior from `Agent`.
- **Polymorphism:** Both storage classes provide the same `save_state()` and `load_state()` methods, allowing the same controller to use either instance.
- **Encapsulation and separation of concerns:** The file-writing details live in `JSONStorage`, while the in-memory dictionary belongs to `MemoryStorage`. Movement, attacks, and agent interactions stay in the simulation classes.
- **Dependency inversion / Strategy pattern:** High-level orchestration depends on the abstract `StateStorage` contract rather than hardcoding a storage type. The selected storage object acts as an interchangeable strategy.

## Justification: Why this effectively decouples the two layers

**1. I can change storage without rewriting gameplay.** To switch backends I change which object is passed to `SimulationController`: `JSONStorage("game_state.json")` or `MemoryStorage()`. The `Agent` subclasses, `SimulationPlayground.step()`, and the controller's save/load calls remain the same.

**2. The controller does not depend on file paths or dictionary internals.** It only calls `save_state()` and `load_state()`. Each concrete class is responsible for translating that contract into its own storage mechanism.

**3. The same snapshot format works for both.** State is represented as a dictionary of simple values, so the simulation does not need one set of gameplay rules for JSON and another for memory. The `to_state()`/`from_state()` boundary also keeps storage implementations away from mutable live agent objects.

**4. A third backend could be added without modifying the existing simulation logic.** For example, a database-backed class could inherit `StateStorage` and implement the same two methods. This is useful when deployment requirements change.

**5. Both implementations can be checked using the same demonstration.** I run the same initial simulation through two controllers. Each backend must save and restore its state correctly. With `--storage both`, the program also compares the two restored snapshots. This tests the claim that storage changes do not alter the simulation's saved result.

**Limitations:** This design decouples *persistence* from gameplay; the simulation still owns a live in-memory representation, as any running simulation must. Memory storage is temporary, and the current snapshot does not retain the random generator's full internal state.

## Two state storage solutions

Both implementations are in the single file `Code.py`, so the professor can inspect the implementation and run them without installing a database.

| Requirement | JSONStorage | MemoryStorage |
| --- | --- | --- |
| Implements `StateStorage` | Yes | Yes |
| Implements `save_state()` | Serializes to a JSON file | Deep-copies into a dictionary |
| Implements `load_state()` | Reads and parses the JSON file | Returns a deep copy from the dictionary |
| Retains state after program exits | Yes | No |
| Extra installation required | No | No |
| Demonstration command | `python Code.py --storage json` | `python Code.py --storage memory` |

**To verify both:** run `python Code.py --storage both`. The program runs the same simulation under each storage option, checks the saved state against its restored state, and checks that both backends return equivalent snapshots.

### Example expected ending

```text
Backend: json
Restored tick: 10
Humans: ...
Zombies: ...
Save/load test: PASSED
Backend: memory
Restored tick: 10
Humans: ...
Zombies: ...
Save/load test: PASSED
Both storage methods produced identical simulation states: PASSED
```

Population values can vary when the rules change. This is the intended output structure; the source code should be executed to confirm results on the target computer.
