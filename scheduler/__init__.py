import os, json, time, threading
from datetime import datetime, timedelta
from typing import Dict, List

class MonthlyScheduler:
    def __init__(self, engine):
        self.engine = engine
        self.config = engine.config
        self.scheduler_file = os.path.join(os.path.dirname(__file__), "scheduler_state.json")
        self.tasks_file = os.path.join(os.path.dirname(__file__), "scheduled_tasks.json")
        self._load_state()
        self._load_tasks()

    def _load_state(self):
        """Load scheduler state."""
        if os.path.exists(self.scheduler_file):
            with open(self.scheduler_file) as f:
                self.state = json.load(f)
        else:
            self.state = {
                "last_monthly_run": None,
                "last_weekly_run": None,
                "next_scheduled_run": None,
                "total_runs": 0
            }

    def _save_state(self):
        """Save scheduler state."""
        with open(self.scheduler_file, "w") as f:
            json.dump(self.state, f, indent=2)

    def _load_tasks(self):
        """Load scheduled tasks from config."""
        self.tasks = {
            "monthly": [],
            "weekly": [],
            "daily": []
        }
        
        # Monthly tasks
        monthly_tasks = self.config.get("scheduler.monthly_tasks", [])
        if monthly_tasks:
            self.tasks["monthly"].extend(monthly_tasks)
        
        # Weekly tasks
        weekly_tasks = self.config.get("scheduler.weekly_tasks", [])
        if weekly_tasks:
            self.tasks["weekly"].extend(weekly_tasks)
        
        # Daily tasks
        daily_tasks = self.config.get("scheduler.daily_tasks", [])
        if daily_tasks:
            self.tasks["daily"].extend(daily_tasks)

    def run_monthly_tasks(self) -> Dict:
        """Run all monthly scheduled tasks."""
        self.engine.log("Scheduler: Running monthly tasks")
        
        now = datetime.now()
        self.state["last_monthly_run"] = now.isoformat()
        self.state["total_runs"] += 1
        
        results = {
            "timestamp": now.isoformat(),
            "tasks_run": [],
            "success_count": 0,
            "error_count": 0
        }
        
        for task in self.tasks["monthly"]:
            task_result = self._run_task(task)
            results["tasks_run"].append(task_result)
            if task_result.get("status") == "success":
                results["success_count"] += 1
            else:
                results["error_count"] += 1
        
        self._save_state()
        return results

    def run_weekly_tasks(self) -> Dict:
        """Run all weekly scheduled tasks."""
        self.engine.log("Scheduler: Running weekly tasks")
        
        now = datetime.now()
        self.state["last_weekly_run"] = now.isoformat()
        self.state["total_runs"] += 1
        
        results = {
            "timestamp": now.isoformat(),
            "tasks_run": [],
            "success_count": 0,
            "error_count": 0
        }
        
        for task in self.tasks["weekly"]:
            task_result = self._run_task(task)
            results["tasks_run"].append(task_result)
            if task_result.get("status") == "success":
                results["success_count"] += 1
            else:
                results["error_count"] += 1
        
        self._save_state()
        return results

    def run_daily_tasks(self) -> Dict:
        """Run all daily scheduled tasks."""
        self.engine.log("Scheduler: Running daily tasks")
        
        now = datetime.now()
        results = {
            "timestamp": now.isoformat(),
            "tasks_run": [],
            "success_count": 0,
            "error_count": 0
        }
        
        for task in self.tasks["daily"]:
            task_result = self._run_task(task)
            results["tasks_run"].append(task_result)
            if task_result.get("status") == "success":
                results["success_count"] += 1
            else:
                results["error_count"] += 1
        
        return results

    def _run_task(self, task: Dict) -> Dict:
        """Run a single scheduled task."""
        task_name = task.get("name")
        task_type = task.get("type")
        
        try:
            if task_type == "affiliate_update":
                return self._run_affiliate_update_task(task)
            elif task_type == "game_clone":
                return self._run_game_clone_task(task)
            elif task_type == "lead_search":
                return self._run_lead_search_task(task)
            elif task_type == "video_generate":
                return self._run_video_generate_task(task)
            else:
                return {"name": task_name, "type": task_type, "status": "error", "message": f"Unknown task type: {task_type}"}
        except Exception as e:
            return {"name": task_name, "type": task_type, "status": "error", "message": str(e)}

    def _run_affiliate_update_task(self, task: Dict) -> Dict:
        """Run affiliate update task."""
        affiliate_updater = self.engine.get("affiliate_updater")
        if not affiliate_updater:
            return {"name": task["name"], "status": "error", "message": "Affiliate updater module not loaded"}
        
        # Get links from config
        links = task.get("links", {})
        
        result = affiliate_updater.update_monthly_landing_page(links)
        return {"name": task["name"], "status": result.get("status", "success"), "result": result}

    def _run_game_clone_task(self, task: Dict) -> Dict:
        """Run game clone task."""
        game_cloner = self.engine.get("game_cloner")
        if not game_cloner:
            return {"name": task["name"], "status": "error", "message": "Game cloner module not loaded"}
        
        # Get parameters from config
        template_repo = task.get("template_repo")
        game_name = task.get("game_name")
        character_img = task.get("character_img")
        background_img = task.get("background_img")
        
        if not template_repo or not game_name:
            return {"name": task["name"], "status": "error", "message": "Missing required parameters"}
        
        result = game_cloner.clone_and_retheme_game(
            template_repo, game_name, character_img, background_img
        )
        return {"name": task["name"], "status": "success" if "error" not in result else "error", "result": result}

    def _run_lead_search_task(self, task: Dict) -> Dict:
        """Run lead search task."""
        lead_finder = self.engine.get("lead_finder")
        if not lead_finder:
            return {"name": task["name"], "status": "error", "message": "Lead finder module not loaded"}
        
        # Get search parameters
        query = task.get("query")
        category = task.get("category", "all")
        
        if not query:
            return {"name": task["name"], "status": "error", "message": "Missing query parameter"}
        
        result = lead_finder.search_jobs(query, category)
        return {"name": task["name"], "status": "success", "result": result}

    def _run_video_generate_task(self, task: Dict) -> Dict:
        """Run video generation task."""
        music_video = self.engine.get("music_video")
        if not music_video:
            return {"name": task["name"], "status": "error", "message": "Music video module not loaded"}
        
        # Get parameters
        audio_path = task.get("audio_path")
        title = task.get("title", "Generated Music Video")
        
        if not audio_path:
            return {"name": task["name"], "status": "error", "message": "Missing audio_path parameter"}
        
        result = music_video.generate(audio_path, title)
        return {"name": task["name"], "status": "success" if "error" not in result else "error", "result": result}

    def get_status(self) -> Dict:
        """Get scheduler status."""
        now = datetime.now()
        
        status = {
            "last_monthly_run": self.state.get("last_monthly_run"),
            "last_weekly_run": self.state.get("last_weekly_run"),
            "total_runs": self.state.get("total_runs", 0),
            "next_monthly_run": self._calculate_next_run("monthly"),
            "next_weekly_run": self._calculate_next_run("weekly"),
            "tasks": self.tasks
        }
        
        return status

    def _calculate_next_run(self, frequency: str) -> str:
        """Calculate next run time for a task frequency."""
        if frequency == "monthly":
            last_run = self.state.get("last_monthly_run")
            if last_run:
                last_date = datetime.fromisoformat(last_run)
                next_date = last_date + timedelta(days=30)
                return next_date.isoformat()
            else:
                next_date = datetime.now() + timedelta(days=30)
                return next_date.isoformat()
        elif frequency == "weekly":
            last_run = self.state.get("last_weekly_run")
            if last_run:
                last_date = datetime.fromisoformat(last_run)
                next_date = last_date + timedelta(days=7)
                return next_date.isoformat()
            else:
                next_date = datetime.now() + timedelta(days=7)
                return next_date.isoformat()
        
        return None

    def is_time_for_task(self, frequency: str) -> bool:
        """Check if it's time to run a task of the given frequency."""
        next_run = self._calculate_next_run(frequency)
        if not next_run:
            return False
        
        now = datetime.now().isoformat()
        return now >= next_run

    def add_task(self, name: str, task_type: str, parameters: Dict) -> Dict:
        """Add a new scheduled task."""
        task = {
            "name": name,
            "type": task_type,
            "parameters": parameters,
            "added_at": datetime.now().isoformat()
        }
        
        self.tasks[task_type].append(task)
        
        # Save to file
        with open(self.tasks_file, "w") as f:
            json.dump(self.tasks, f, indent=2)
        
        return {"status": "success", "task": task}

    def remove_task(self, task_type: str, task_name: str) -> Dict:
        """Remove a scheduled task."""
        if task_type not in self.tasks:
            return {"status": "error", "message": f"Unknown task type: {task_type}"}
        
        self.tasks[task_type] = [t for t in self.tasks[task_type] if t["name"] != task_name]
        
        # Save to file
        with open(self.tasks_file, "w") as f:
            json.dump(self.tasks, f, indent=2)
        
        return {"status": "success", "message": f"Task '{task_name}' removed"}