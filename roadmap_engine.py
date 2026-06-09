import json
import os
import sys
from datetime import datetime

class RoadmapEngine:
    def __init__(self, roadmap_dir="/home/ubuntu/sujata-fashion-test-stylist"):
        self.roadmap_dir = roadmap_dir
        self.roadmap_file = os.path.join(roadmap_dir, "roadmap_index.md")
        self.state_file = os.path.join(roadmap_dir, "progress_state.json")
        self.log_file = os.path.join(roadmap_dir, "roadmap_execution.log")

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        with open(self.log_file, 'a') as f:
            f.write(log_entry)
        print(log_entry.strip())

    def load_roadmap(self):
        if not os.path.exists(self.roadmap_file):
            raise FileNotFoundError(f"Roadmap file missing: {self.roadmap_file}")
        
        steps = []
        with open(self.roadmap_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line.startswith("- ") and any(char.isdigit() for char in line):
                    # Extracting "1. [STAGE 1] ..."
                    parts = line[2:].split('. ', 1)
                    if len(parts) == 2:
                        steps.append(parts[1].strip())
        return steps

    def load_state(self):
        if not os.path.exists(self.state_file):
            self.log("State file missing. Creating default state.", "WARNING")
            self.create_default_state()
        
        with open(self.state_file, 'r') as f:
            return json.load(f)

    def create_default_state(self):
        state = {
            "current_step": 1,
            "last_run_at": None,
            "status": "active",
            "error_log": []
        }
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def save_state(self, state):
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def get_current_task(self):
        state = self.load_state()
        roadmap = self.load_roadmap()
        idx = state['current_step'] - 1
        
        if idx < 0 or idx >= len(roadmap):
            return None, state

        return roadmap[idx], state

    def advance_step(self):
        state = self.load_state()
        state['current_step'] += 1
        state['last_run_at'] = datetime.now().isoformat()
        state['status'] = "active"
        self.save_state(state)
        self.log(f"Advanced to step {state['current_step']}")

    def report_error(self, error_msg):
        state = self.load_state()
        state['status'] = "error"
        state['error_log'].append({
            "timestamp": datetime.now().isoformat(),
            "error": error_msg
        })
        self.save_state(state)
        self.log(f"Error reported: {error_msg}", "ERROR")

if __name__ == "__main__":
    engine = RoadmapEngine()
    
    if len(sys.argv) < 2:
        print("Usage: roadmap_engine.py [get_task|advance|report_error|status]")
        sys.exit(1)

    cmd = sys.argv[1]

    try:
        if cmd == "get_task":
            task, state = engine.get_current_task()
            if task:
                print(json.dumps({"task": task, "step": state['current_step'], "state": state}))
            else:
                print(json.dumps({"error": "No more tasks in roadmap."}))
        
        elif cmd == "advance":
            engine.advance_step()
            print("OK")

        elif cmd == "report_error":
            error = sys.argv[2] if len(sys.argv) > 2 else "Unknown error"
            engine.report_error(error)
            print("OK")

        elif cmd == "status":
            state = engine.load_state()
            print(json.dumps(state))
        
        else:
            print(f"Unknown command: {cmd}")
            sys.exit(1)

    except Exception as e:
        engine.log(f"Engine failure: {str(e)}", "CRITICAL")
        sys.exit(1)
