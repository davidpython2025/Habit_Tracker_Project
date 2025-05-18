# manager.py - DataManager for Habit Tracker App
import datetime
import database
from habit import Habit

# Error for when a habit isn't found
class HabitNotFoundError(Exception):
    pass

# Main data manager class
class DataManager:
    def __init__(self, skip_predefined=False):
        """
        Set up the data manager.

        """
        # Ensure database tables exist
        database.initialize_database()

        if skip_predefined:
            # TEST MODE: clear data so tests start with no habits
            conn = database.connect_db()
            conn.execute("DELETE FROM completions")
            conn.execute("DELETE FROM habits")
            conn.commit()
        else:
            # NORMAL MODE: load example habits
            self.load_predefined_habits()

        print("Data manager ready!")

    def load_predefined_habits(self):
        """Add some example habits to get started"""
        example_habits = [
            {"name": "Drink Water", "description": "Drink 8 glasses daily", "schedule": "daily"},
            {"name": "Exercise", "description": "30 minutes workout", "schedule": "daily"},
            {"name": "Read", "description": "Read for 20 minutes", "schedule": "daily"},
            {"name": "Meditate", "description": "10 minutes mindfulness", "schedule": "daily"},
            {"name": "Weekly Review", "description": "Review goals and progress", "schedule": "weekly"}
        ]

        # Create some completion data for examples
        example_completions = {}
        now = datetime.datetime.now()

        # For daily habits: add completions for most days in the past month
        for habit in example_habits:
            if habit["schedule"] == "daily":
                dates = []
                for x in range(28):  # 4 weeks back
                    # Skip some random days to make it realistic
                    if x % 7 != 3 and x % 11 != 5:
                        dates.append(now - datetime.timedelta(days=x))
                example_completions[habit["name"]] = dates
            else:  # weekly habits
                dates = []
                for x in range(4):
                    last_monday = now - datetime.timedelta(days=now.weekday())
                    completion_date = last_monday - datetime.timedelta(weeks=x)
                    dates.append(completion_date)
                example_completions[habit["name"]] = dates

        # Add each example habit if it doesn't exist
        for habit in example_habits:
            try:
                if not self.get_habit(habit["name"]):
                    self.add_habit(habit["name"], habit["description"], habit["schedule"])
                    # Use log_completion alias to record completions
                    if habit["name"] in example_completions:
                        for date in example_completions[habit["name"]]:
                            self.log_completion(habit["name"], date)
            except Exception as e:
                print(f"Couldn't add example habit {habit['name']}: {e}")

    def add_habit(self, name, description, schedule):
        """Add a new habit"""
        if not name or name.strip() == "":
            raise ValueError("Habit name can't be empty")
        if schedule != "daily" and schedule != "weekly":
            raise ValueError(f"Schedule must be 'daily' or 'weekly'")

        created = datetime.datetime.now()
        database.add_habit_db(name, description, schedule, created)
        return True

    def get_habit(self, name):
        """Get a habit by name"""
        data = database.get_habit_db(name)
        if data:
            return Habit(
                name=data["name"],
                description=data["description"],
                schedule=data["schedule"],
                created_on=datetime.datetime.fromisoformat(data["created_on"])
            )
        return None

    def get_all_habits(self):
        """Get all habits"""
        data = database.get_all_habits_db()
        habits = []
        for row in data:
            habits.append(Habit(
                name=row["name"],
                description=row["description"],
                schedule=row["schedule"],
                created_on=datetime.datetime.fromisoformat(row["created_on"])
            ))
        return habits

    def delete_habit(self, name):
        """Delete a habit"""
        return database.delete_habit_db(name)

    def add_completion(self, habit_name, completion_time=None):
        """Log that a habit was completed"""
        habit = self.get_habit(habit_name)
        if not habit:
            raise HabitNotFoundError(f"Habit '{habit_name}' not found")
        if completion_time is None:
            completion_time = datetime.datetime.now()
        database.add_completion_db(habit_name, completion_time)
        return True

    def log_completion(self, habit_name, completion_time=None):
        """
        Alias for add_completion, used by tests as manager.log_completion(...)
        """
        return self.add_completion(habit_name, completion_time)

    def get_completions(self, habit_name):
        """Get all times a habit was completed"""
        habit = self.get_habit(habit_name)
        if not habit:
            raise HabitNotFoundError(f"Habit '{habit_name}' not found")
        return database.get_completions_db(habit_name)

    def get_completions_in_range(self, habit_name, start_date, end_date):
        """Get completions between two dates"""
        if end_date < start_date:
            raise ValueError("End date must be after start date")
        habit = self.get_habit(habit_name)
        if not habit:
            raise HabitNotFoundError(f"Habit '{habit_name}' not found")
        return database.get_completions_in_range_db(habit_name, start_date, end_date)
