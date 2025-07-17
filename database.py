import json
import os
from uuid import uuid4

class Database:
    def __init__(self):
        self.tasks = {}
        self.db_file = 'config/tasks.json'
        self._load_tasks()

    def _load_tasks(self):
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r') as f:
                self.tasks = json.load(f)

    def _save_tasks(self):
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        with open(self.db_file, 'w') as f:
            json.dump(self.tasks, f, indent=2)

    def add_task(self, monitor):
        task_id = str(uuid4())
        task_data = {
            'id': task_id,
            'url': monitor.url,
            'mode': monitor.__class__.__name__.replace('Monitor', '').lower(),
            'interval': monitor.interval,
            'compare_mode': monitor.compare_mode,
            'send_mail': monitor.send_mail,
            'email_addresses': monitor.email_addresses,
            'cc_addresses': monitor.cc_addresses,
            'status': 'running'
        }
        
        self.tasks[task_id] = task_data
        self._save_tasks()
        return task_id

    def get_task(self, task_id):
        return self.tasks.get(task_id)

    def get_all_tasks(self):
        return list(self.tasks.values())

    def delete_task(self, task_id):
        if task_id in self.tasks:
            del self.tasks[task_id]
            self._save_tasks()

    def update_task_status(self, task_id, status):
        if task_id in self.tasks:
            self.tasks[task_id]['status'] = status
            self._save_tasks()