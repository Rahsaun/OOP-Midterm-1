# How to Run OOP Midterm #1

These instructions are for the **standalone OOP Midterm #1 repository**. You do not need the original Zombie Game repository.

## 1. Get the code

1. Open [OOP-Midterm-1](https://github.com/Rahsaun/OOP-Midterm-1).
2. Select **Code → Download ZIP** and extract it, or clone the repository with Git:
   ```bash
   git clone https://github.com/Rahsaun/OOP-Midterm-1.git
   cd OOP-Midterm-1
   ```
3. Open the **OOP-Midterm-1** folder in Visual Studio Code (VS Code).

If you downloaded a ZIP, open the extracted folder rather than using the `cd` command above.

## 2. Verify Python

Use **Python 3.10 or newer**. In VS Code, open **Terminal → New Terminal** and run:

```bash
python --version
```

On Windows, if `python` is not recognized, try `py --version` and use `py` instead of `python` in subsequent commands. Make sure the terminal is in the folder containing `demo.py`.

## 3. Run the JSON-storage demo (recommended first)

No additional Python packages or database are required.

```bash
python demo.py --storage json --ticks 10
```

On Windows you can use:

```powershell
py demo.py --storage json --ticks 10
```

The program:
1. Creates humans, armed humans, and zombies.
2. Runs 10 simulation ticks.
3. Saves the **complete snapshot** to `game_state.json`.
4. Loads that snapshot through a new controller.
5. Checks whether the restored snapshot matches the saved version.

You should see output shaped like:

```text
Backend: json
Restored tick: 10
Humans: <number>
Zombies: <number>
Save/load test: PASSED
```

The population values depend on the simulation. The `game_state.json` file is intentionally ignored by Git.

## 4. Run automated tests

In the same terminal:

```bash
python -m unittest discover -s tests -v
```

Or on Windows:

```powershell
py -m unittest discover -s tests -v
```

The tests verify that the **same SimulationController code** works with both JSON file storage and a simple in-memory test implementation, and that loading a nonexistent file is handled cleanly.

**Note:** The automated suite does not connect to PostgreSQL. PostgreSQL must be tested separately using the optional steps below.

## 5. Optional: Run with PostgreSQL

You only need this section if you want to demonstrate the database-based implementation. Have a PostgreSQL server running and a database account with permission to create a table and write rows.

Install the PostgreSQL driver:

```bash
python -m pip install -r requirements-postgres.txt
```

Set a `DATABASE_URL` environment variable using your **own** connection details. Do **not** put passwords into Python source code or commit them to GitHub.

**Windows PowerShell** (replace placeholder values locally):

```powershell
$env:DATABASE_URL = "postgresql://YOUR_USER:YOUR_PASSWORD@localhost:5432/YOUR_DATABASE"
python demo.py --storage postgres --ticks 10
```

**macOS or Linux**:

```bash
export DATABASE_URL='postgresql://YOUR_USER:YOUR_PASSWORD@localhost:5432/YOUR_DATABASE'
python demo.py --storage postgres --ticks 10
```

The program creates the `simulation_state` table if it does not exist, saves a snapshot, restores it, and checks that the restored snapshot matches. If it cannot connect, check that PostgreSQL is running, the database exists, the credentials are correct, and your user has table permissions.

## 6. What each Python file does

| File | What it does |
| --- | --- |
| `demo.py` | Entry point: selects storage, runs the game, saves, and reloads |
| `simulation.py` | `Agent` subclasses, game rules, snapshots, and `SimulationController` |
| `storage.py` | `StateStorage` abstract interface and JSON/PostgreSQL implementations |
| `tests/test_storage.py` | Automated tests for saving and loading |
| `requirements-postgres.txt` | Optional database-driver installation |

## 7. Why this meets the OOP assignment

`SimulationController` depends on the abstract `StateStorage` contract, not a specific database or file format. Both `JSONStorage` and `PostgreSQLStorage` implement the same `save_state()` and `load_state()` methods. The simulation's agent behavior does not change when the storage implementation changes.

This is a **headless** version of the original Zombie Game concepts: it does not open the original Tkinter graphical interface or use its multiprocessing engine.

## Troubleshooting

- **`python` not found:** Install Python 3.10+ or try `py` on Windows.
- **`can't open file 'demo.py'`:** Open the terminal in the repository's root folder.
- **`ModuleNotFoundError: psycopg`:** Install `requirements-postgres.txt` if using PostgreSQL.
- **PostgreSQL connection error:** Verify the server, database name, user, password, and permissions.
- **No graphical window appears:** This assignment's demo runs in the terminal by design.
