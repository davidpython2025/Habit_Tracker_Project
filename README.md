# Habit Tracker App

A simple, CLI-based application to help you build and maintain daily and weekly habits. Track your progress, view streaks, and identify habits you might be struggling with.

---

## Table of Contents

1. [Features](#features)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Usage](#usage)

   * [Running the App](#running-the-app)
   * [Command-Line Menu](#command-line-menu)
5. [Testing](#testing)
6. [Project Structure](#project-structure)
7. [Examples and Test Fixtures](#examples-and-test-fixtures)
8. [References](#references)

---

## Features

* **Add new habits**: Create daily or weekly habits with a name and optional description.
* **Log completions**: Mark habits as done for today or specify a custom date.
* **View habits**: List all habits or filter by schedule (daily/weekly).
* **Track streaks**:

  * Current streak for each habit.
  * Longest streak ever achieved.
  * Overall longest streak across all habits.
* **Identify struggling habits**: See which habits have the most missed completions over a custom period.
* **Persistent storage**: All data is stored locally in an SQLite database (`habits.db`).
* **Unit-tested**: Core functionality covered by a pytest suite.

---

## Requirements

* Python 3.7 or later
* No external libraries required (uses Python standard library)

---

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/davidpython2025/Habit_Tracker_Project
   cd habit-tracker-app
   ```
2. (Optional) Create a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate     # Windows
   ```
3. Install any dependencies (none needed beyond standard library).

---

## Usage

### Running the App

1. Ensure you are in the project directory.
2. Run the main script:

   ```bash
   python main.py
   ```
3. On first run, the database (`habits.db`) is initialized automatically.

### Command-Line Menu

After launching, follow the on-screen menu:

```
===========================================
           Habit Tracker Menu
===========================================
1. Add New Habit
2. Mark Habit as Complete
3. View All Habits
4. View Habits by Schedule (Daily/Weekly)
5. View Habit Streak
6. View Longest Overall Streak
7. View Struggling Habits
8. Delete Habit
0. Exit
-------------------------------------------
```

* **Add New Habit**: Enter a name, optional description, and choose `daily` or `weekly`.
* **Mark Habit as Complete**: Pick a habit by number or name, then confirm the date.
* **View All Habits**: See all habits grouped by schedule.
* **View Habits by Schedule**: Filter to only `daily` or `weekly` habits.
* **View Habit Streak**: Select a habit to see current and longest streaks, plus last completion date.
* **View Longest Overall Streak**: Displays the habit(s) with the highest streak count.
* **View Struggling Habits**: Choose a period (7, 14, 30, 60, or 90 days) to find missed-completion counts.
* **Delete Habit**: Remove a habit permanently from the database.

---

## Testing

Run the automated test suite with pytest:

```bash
pytest test_habit_tracker.py
```

The tests use an **in-memory** SQLite database to ensure a clean state for each test:

* Habit model validation
* DataManager CRUD operations
* Analytics functions (streak calculations, filtering)
* Controller integration and validation

---

## Project Structure

```
├── analytics.py          # Functional streak and analysis functions
├── cli.py                # Command-line interface and menus
├── database.py           # SQLite persistence layer
├── habit.py              # Habit class definition (OOP model)
├── habit_controller.py   # Business logic connecting CLI and data layer
├── manager.py            # DataManager: high-level data operations
├── main.py               # Entry point: setup + launch CLI
├── test_habit_tracker.py # Unit tests covering core functionality
└── README.md             # This file
```

---

## Examples and Test Fixtures

The app ships with 5 predefined example habits (4 daily, 1 weekly) and 4 weeks of fixture completions for quick testing. You can see these in `manager.py` under `load_predefined_habits()`.

---


## References

* Python 3 [`sqlite3`](https://docs.python.org/3/library/sqlite3.html)
* Python [`datetime`](https://docs.python.org/3/library/datetime.html)
* pytest documentation: [https://docs.pytest.org/](https://docs.pytest.org/)
* Professor Pumperla's videos shared on myCampus
* Python documentation for datetime module
* Stack Overflow (for help with weekly calculations)
