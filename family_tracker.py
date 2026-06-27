#!/usr/bin/env python3
"""
Family Business Tracker - Track AI families' work and profits
"""
import json, os, time
from datetime import datetime

TRACKER_FILE = os.path.join(os.path.dirname(__file__), "family_tracker.json")

def load():
    with open(TRACKER_FILE) as f:
        return json.load(f)

def save(data):
    with open(TRACKER_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_revenue(family, agent, amount, task=""):
    data = load()
    if family == "ai":
        data["original_ai_family"]["revenue_tracking"][agent]["revenue"] += amount
        data["original_ai_family"]["revenue_tracking"][agent]["tasks_completed"] += 1
        if task:
            print(f"✅ {agent}: {task} - Earned R{amount}")
    else:
        for m in data["shelbyfoxfuture"]["members"]:
            if m["name"].lower() == agent.lower():
                m["revenue"] += amount
                print(f"✅ {agent}: Earned R{amount}")
    data["original_ai_family"]["last_updated"] = datetime.now().isoformat()
    data["shelbyfoxfuture"]["last_updated"] = datetime.now().isoformat()
    save(data)

def status():
    data = load()
    print("\n" + "="*50)
    print("🤖 ORIGINAL AI FAMILY - Business Report")
    print("="*50)
    total = 0
    for agent, info in data["original_ai_family"]["revenue_tracking"].items():
        print(f"  {agent:10s} | {info['business']:25s} | R{info['revenue']:.2f} | {info['tasks_completed']} tasks")
        total += info['revenue']
    print(f"  {'─'*50}")
    print(f"  {'TOTAL':10s} | {'':25s} | R{total:.2f}")
    
    print("\n" + "="*50)
    print("❤️ SHELBYFOXFUTURE - Personal Report")
    print("="*50)
    for m in data["shelbyfoxfuture"]["members"]:
        print(f"  {m['name']:10s} | {m['business']:25s} | R{m['revenue']:.2f}")
    
    print(f"\nLast updated: {data['original_ai_family']['last_updated'][:19]}")
    return total

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        status()
    elif len(sys.argv) > 2 and sys.argv[1] == "earn":
        add_revenue(sys.argv[2], sys.argv[3], float(sys.argv[4]), " ".join(sys.argv[5:]))
    else:
        print("Usage:")
        print("  python3 family_tracker.py status")
        print("  python3 family_tracker.py earn ai Red 10 'Built landing page'")
