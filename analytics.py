# analytics.py - Functional programming for habit analytics
import datetime
from habit import Habit

# Helper function for calculating streaks
def calculate_streak(dates, schedule):
    """
    Count how many days or weeks in a row a habit was done.

    Args:
        dates (list of datetime.datetime): Completion timestamps.
        schedule (str): 'daily' or 'weekly'.
    Returns:
        int: The current streak length.
    """
    if not dates:
        return 0

    # Convert timestamps to dates and remove duplicates
    unique_dates = sorted({d.date() for d in dates}, reverse=True)

    # Daily streak logic
    if schedule == "daily":
        today = datetime.date.today()
        # If last completion is before yesterday, streak is 0
        if unique_dates[0] < today - datetime.timedelta(days=1):
            return 0
        # Start streak count
        streak = 1
        for previous, current in zip(unique_dates, unique_dates[1:]):
            if (previous - current).days == 1:
                streak += 1
            else:
                break
        return streak

    # Weekly streak logic
    if schedule == "weekly":
        today = datetime.date.today()
        # If no completion in last 7 days, streak is 0
        if (today - unique_dates[0]).days > 7:
            return 0
        # Group by ISO calendar week
        weeks = sorted({d.isocalendar()[:2] for d in unique_dates}, reverse=True)
        streak = 1
        for prev_week, curr_week in zip(weeks, weeks[1:]):
            # Compare year and week number
            if prev_week[0] == curr_week[0] and prev_week[1] - curr_week[1] == 1:
                streak += 1
            else:
                break
        return streak

    # Should not reach here due to validation
    raise ValueError(f"Unknown schedule: {schedule}")


def get_current_streak_for_habit(habit: Habit, completions: list):
    """
    Return the current streak for a given habit.
    """
    return calculate_streak(completions, habit.schedule)


def get_longest_streak_for_habit(habit: Habit, completions: list):
    """
    Compute the longest streak ever achieved for a habit.
    """
    # Convert to unique sorted dates oldest->newest
    unique_dates = sorted({d.date() for d in completions})
    if not unique_dates:
        return 0

    # Daily longest logic
    if habit.schedule == "daily":
        longest = current = 1
        for prev, curr in zip(unique_dates, unique_dates[1:]):
            if (curr - prev).days == 1:
                current += 1
                longest = max(longest, current)
            else:
                current = 1
        return longest

    # Weekly longest logic
    if habit.schedule == "weekly":
        # Group by ISO week
        weeks = sorted({d.isocalendar()[:2] for d in unique_dates})
        longest = current = 1
        for prev_week, curr_week in zip(weeks, weeks[1:]):
            if prev_week[0] == curr_week[0] and curr_week[1] - prev_week[1] == 1:
                current += 1
                longest = max(longest, current)
            else:
                current = 1
        return longest

    # Should not reach here due to validation
    raise ValueError(f"Unknown schedule: {habit.schedule}")


def get_habits_by_periodicity(habits: list, schedule: str):
    """
    Filter habits by 'daily' or 'weekly'.

    Raises ValueError for invalid schedule.
    """
    # Validate schedule argument
    if schedule not in ("daily", "weekly"):
        raise ValueError("Schedule must be 'daily' or 'weekly'")
    # Return matching habits
    return [h for h in habits if h.schedule == schedule]


def find_struggling_habits(habits: list, all_completions: dict, period_start=None, period_end=None):
    """
    Identify habits with most missed completions in a period.

    Returns a list of tuples (habit_name, missed_count), sorted descending.
    """
    if not habits:
        return []

    # Default to last 30 days
    today = datetime.date.today()
    period_end = period_end or today
    period_start = period_start or (period_end - datetime.timedelta(days=30))

    results = []
    for habit in habits:
        completions = all_completions.get(habit.name, [])
        # Count completions in range
        count = sum(
            1 for c in completions
            if period_start <= c.date() <= period_end
        )
        # Expected counts
        days = (period_end - period_start).days + 1
        expected = days if habit.schedule == "daily" else (days // 7 + 1)
        missed = max(0, expected - count)
        results.append((habit.name, missed))
    # Sort by most missed
    return sorted(results, key=lambda x: x[1], reverse=True)


def get_longest_streak_all(habits: list, all_completions: dict):
    """
    Return the maximum longest streak across all habits.
    """
    if not habits:
        return 0
    return max(
        get_longest_streak_for_habit(h, all_completions.get(h.name, []))
        for h in habits
    )
