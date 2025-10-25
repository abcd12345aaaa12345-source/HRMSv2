import os
import json


class DataManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
            cls._instance.employees = []
            cls._instance.tasks = []
            cls._instance.events = {}
            cls._instance.documents = []
            cls._instance.load_all_data()
        return cls._instance

    def load_all_data(self):
        try:
            if os.path.exists("data/staff_data.json"):
                with open("data/staff_data.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.employees = data.get("employees", [])

            if os.path.exists("data/tasks_data.json"):
                with open("data/tasks_data.json", "r", encoding="utf-8") as f:
                    self.tasks = json.load(f)

            if os.path.exists("data/calendar_events.json"):
                with open("data/calendar_events.json", "r", encoding="utf-8") as f:
                    self.events = json.load(f)

            if os.path.exists("data/documents_data.json"):
                with open("data/documents_data.json", "r", encoding="utf-8") as f:
                    self.documents = json.load(f)

        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")

    def save_all_data(self):
        try:
            os.makedirs("data", exist_ok=True)

            with open("data/staff_data.json", "w", encoding="utf-8") as f:
                json.dump({"employees": self.employees},
                          f, ensure_ascii=False, indent=2)

            with open("data/tasks_data.json", "w", encoding="utf-8") as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)

            with open("data/calendar_events.json", "w", encoding="utf-8") as f:
                json.dump(self.events, f, ensure_ascii=False, indent=2)

            with open("data/documents_data.json", "w", encoding="utf-8") as f:
                json.dump(self.documents, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Ошибка сохранения данных: {e}")

    def get_employee_by_id(self, emp_id):
        return next(
            (emp for emp in self.employees if emp["id"] == emp_id),
            None)

    def get_tasks_by_assignee(self, assignee_id):
        return [task for task in self.tasks if task.get(
            "assignee_id") == assignee_id]

    def get_events_by_assignee(self, assignee_id):
        all_events = []
        for date_events in self.events.values():
            for event in date_events:
                if event.get("assignee_id") == assignee_id:
                    all_events.append(event)
        return all_events