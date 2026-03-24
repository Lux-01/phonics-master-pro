#!/usr/bin/env python3
"""
Scheduler for gold_coast_tracker
"""

import time
from datetime import datetime

class Scheduler:
    def __init__(self):
        self.jobs = []
    
    def add_job(self, func, interval_seconds):
        self.jobs.append({
            'func': func,
            'interval': interval_seconds,
            'last_run': None
        })
    
    def run(self):
        while True:
            now = datetime.now()
            for job in self.jobs:
                if job['last_run'] is None or                    (now - job['last_run']).seconds >= job['interval']:
                    job['func']()
                    job['last_run'] = now
            time.sleep(1)
