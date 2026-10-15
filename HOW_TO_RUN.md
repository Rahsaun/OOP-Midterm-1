# How to Run OOP Midterm #1

Only two files are needed from this repository: `OOP_Midterm_1.py` and `HOW_TO_RUN.md`.

## Get started

1. Open the repository and use **Code → Download ZIP**, then extract the ZIP.
2. Open the extracted folder in VS Code.
3. Open **Terminal → New Terminal**.
4. Make sure Python 3.10 or newer is installed: `python --version` (or `py --version` on Windows).

## Run the program

In the terminal, from the folder containing the Python file:

```bash
python OOP_Midterm_1.py --storage json --ticks 10
```

Windows users can run `py OOP_Midterm_1.py --storage json --ticks 10` instead.

The program creates humans and zombies, runs 10 simulation steps, saves the game state to a locally generated `game_state.json`, restores the snapshot, and compares it to the original. Expected final message: `Save/load test: PASSED`. The JSON file is generated output, not an extra source file to add to GitHub.

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
python OOP_Midterm_1.py --storage postgres --ticks 10
```

macOS/Linux:

```bash
export DATABASE_URL='postgresql://YOUR_USER:YOUR_PASSWORD@localhost:5432/YOUR_DATABASE'
python OOP_Midterm_1.py --storage postgres --ticks 10
```

## What it demonstrates

The `SimulationController` class depends on the abstract `StateStorage` interface. `JSONStorage` and `PostgreSQLStorage` both implement `save_state()` and `load_state()`, so storage can change without changing agent behavior.

**Note:** This is a terminal-based class assignment, not the original Tkinter graphical game. PostgreSQL functionality needs an available database to test.
