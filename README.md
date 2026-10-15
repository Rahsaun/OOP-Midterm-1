# How to Run OOP Midterm #1

This repository has two files: **`Code.py`** (the runnable program) and **`README.md`** (these instructions).

## Get started

1. Open the repository and use **Code → Download ZIP**, then extract the ZIP.
2. Open the extracted folder in VS Code.
3. Open **Terminal → New Terminal**.
4. Make sure Python 3.10 or newer is installed: `python --version` (or `py --version` on Windows).

## Run the program

In the terminal, from the folder containing the Python file:

```bash
python Code.py --storage json --ticks 10
```

Windows users can run `py Code.py --storage json --ticks 10` instead.

## What should happen?

The program:

1. Creates humans and zombies.
2. Runs the simulation for **10 steps**.
3. Saves the simulation state to a local `game_state.json` file.
4. Loads the saved simulation state.
5. Verifies that the restored state matches the original.

Successful output ends with:

```text
Save/load test: PASSED
```

The program also prints the storage backend, tick number, and human/zombie counts. The JSON file is generated data, not an additional source file to add to GitHub.

## Optional PostgreSQL demonstration

You can also use the second storage implementation if you have a PostgreSQL server and database.

Install the driver:

```bash
python -m pip install "psycopg[binary]"
```

Provide your **own** connection string in an environment variable (never commit credentials).

Windows PowerShell:

```powershell
$env:DATABASE_URL="postgresql://YOUR_USER:YOUR_PASSWORD@localhost:5432/YOUR_DATABASE"
python Code.py --storage postgres --ticks 10
```

macOS/Linux:

```bash
export DATABASE_URL='postgresql://YOUR_USER:YOUR_PASSWORD@localhost:5432/YOUR_DATABASE'
python Code.py --storage postgres --ticks 10
```

## What it demonstrates

The `SimulationController` class depends on the abstract `StateStorage` interface. `JSONStorage` and `PostgreSQLStorage` both implement `save_state()` and `load_state()`, so storage can change without changing agent behavior.

**Note:** This is a terminal-based class assignment, not the original Tkinter graphical game. PostgreSQL functionality needs an available database to test.
