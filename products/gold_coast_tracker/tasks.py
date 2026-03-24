#!/usr/bin/env python3
"""
Task definitions for gold_coast_tracker
"""

class TaskManager:
    def __init__(self):
        self.tasks = []
    
    def add_task(self, name, func, schedule=None):
        self.tasks.append({
            'name': name,
            'func': func,
            'schedule': schedule
        })
    
    def run_task(self, name):
        for task in self.tasks:
            if task['name'] == name:
                return task['func']()
        return None
