import pytest
import datetime

import database
from habit import Habit
import analytics
from manager import DataManager, HabitNotFoundError
from habit_controller import HabitController, ValidationError

# Use an in-memory SQLite database for all tests
def setup_module(module):
    database.DB_NAME = ":memory:"

@pytest.fixture(autouse=True)
def fresh_db(monkeypatch, tmp_path):
    # Ensure each test gets its own in-memory DB
    monkeypatch.setattr(database, 'DB_NAME', ':memory:')
    # Initialize database schema
    import database as db_module
    db_module.initialize_database()
    yield

# Habit model tests
def test_habit_str_with_description():
    now = datetime.datetime(2025, 5, 18, 12, 0)
    h = Habit('Test', 'A habit', 'daily', created_on=now)
    s = str(h)
    assert 'Test' in s
    assert '(daily)' in s
    assert 'A habit' in s

def test_habit_str_without_description():
    h = Habit('Solo', '', 'weekly')
    s = str(h)
    assert s == 'Solo (weekly)'


def test_habit_invalid_schedule():
    with pytest.raises(ValueError):
        Habit('Bad', 'desc', 'monthly')

# DataManager tests
@pytest.fixture
def manager():
    return DataManager(skip_predefined=True)

def test_manager_add_get_delete_habit(manager):
    assert manager.add_habit('Run', 'Run daily', 'daily')
    h = manager.get_habit('Run')
    assert isinstance(h, Habit)
    assert h.name == 'Run'
    # Delete and verify
    assert manager.delete_habit('Run')
    assert manager.get_habit('Run') is None


def test_manager_log_and_get_completions(manager):
    manager.add_habit('Read', 'Read books', 'daily')
    now = datetime.datetime.now()
    assert manager.log_completion('Read', now)
    completions = manager.get_completions('Read')
    assert len(completions) == 1
    assert completions[0].date() == now.date()

# Analytics tests
def make_dates(days):
    today = datetime.date.today()
    return [datetime.datetime.combine(today - datetime.timedelta(days=d), datetime.time.min) for d in days]

def test_calculate_streak_daily():
    today = datetime.date.today()
    dates = make_dates([0, 1, 2, 4])  # missed day 3
    streak = analytics.calculate_streak(dates, 'daily')
    assert streak == 3


def test_calculate_streak_weekly():
    # Create dates spanning 3 consecutive weeks
    today = datetime.date.today()
    base = today - datetime.timedelta(days=today.weekday())
    dates = [datetime.datetime.combine(base - datetime.timedelta(weeks=i), datetime.time.min) for i in range(3)]
    streak = analytics.calculate_streak(dates, 'weekly')
    assert streak == 3


def test_get_current_and_longest_streak_for_habit():
    h = Habit('X', 'desc', 'daily')
    dates = make_dates([0, 1, 2, 5, 6])
    current = analytics.get_current_streak_for_habit(h, dates)
    longest = analytics.get_longest_streak_for_habit(h, dates)
    assert current == 3
    assert longest == 3


def test_get_habits_by_periodicity_valid():
    h1 = Habit('A', '', 'daily')
    h2 = Habit('B', '', 'weekly')
    result = analytics.get_habits_by_periodicity([h1, h2], 'weekly')
    assert result == [h2]


def test_get_habits_by_periodicity_invalid():
    with pytest.raises(ValueError):
        analytics.get_habits_by_periodicity([], 'monthly')


def test_find_struggling_habits():
    h1 = Habit('D', '', 'daily')
    h2 = Habit('W', '', 'weekly')
    # D has 5 completions in 7 days, expected 7 -> missed 2
    # W has 1 completion in 7 days, expected 2 -> missed 1
    today = datetime.date.today()
    comps = {
        'D': [datetime.datetime.combine(today - datetime.timedelta(days=i), datetime.time.min) for i in range(5)],
        'W': [datetime.datetime.combine(today - datetime.timedelta(days=today.weekday()), datetime.time.min)]
    }
    res = analytics.find_struggling_habits([h1, h2], comps, today - datetime.timedelta(days=6), today)
    assert res[0][0] == 'D' or res[0][0] == 'W'
    assert all(isinstance(x[1], int) for x in res)

# Controller tests
def test_controller_add_habit_and_validation():
    ctrl = HabitController(test_mode=True)
    assert ctrl.add_habit('Go', 'desc', 'daily')
    with pytest.raises(ValidationError):
        ctrl.add_habit('', 'desc', 'daily')
    with pytest.raises(ValidationError):
        ctrl.add_habit('Bad', 'desc', 'monthly')


def test_controller_view_all_and_by_schedule():
    ctrl = HabitController(test_mode=True)
    ctrl.add_habit('A', '', 'daily')
    ctrl.add_habit('B', '', 'weekly')
    out = ctrl.view_all_habits()
    assert 'Daily Habits:' in out
    assert 'Weekly Habits:' in out
    out2 = ctrl.view_habits_by_schedule('daily')
    assert 'Daily Habits:' in out2


def test_controller_view_habit_streak_and_errors():
    ctrl = HabitController(test_mode=True)
    with pytest.raises(HabitNotFoundError):
        ctrl.view_habit_streak('None')
    ctrl.add_habit('Z', '', 'daily')
    # No completions yet
    res = ctrl.view_habit_streak('Z')
    assert 'Current Streak: 0' in res
    assert 'No completions recorded' in res


def test_view_longest_and_delete_habit():
    ctrl = HabitController(test_mode=True)
    assert ctrl.view_longest_streak_all() == 'No habits defined to calculate streaks.'
    ctrl.add_habit('T', '', 'daily')
    assert ctrl.delete_habit('T')
    assert not ctrl.delete_habit('T')
