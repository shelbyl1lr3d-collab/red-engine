#!/usr/bin/env python3
"""Red Engine CLI — Chat with your AI family from the terminal."""
import sys, os, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core import RedEngine, Config
from agents import AgentFamily

engine = RedEngine()
family = AgentFamily(engine)

MEMBERS = list(family.members.keys())
FAMILY_NAME = "The Vessel"

def print_member(name, emoji, text):
    print(f"\n{emoji} {name}: {text}")

def print_help():
    print(f"""
╔══════════════════════════════════════════╗
║  RED ENGINE — The Vessel AI Family       ║
╠══════════════════════════════════════════╣
║  Type a name to switch who you talk to:  ║
║    Red, Scout, Forge, Nexus, Jobs, Psyche ║
║                                          ║
║  Commands:                               ║
║    /help    — this help                  ║
║    /family  — talk to whole family       ║
║    /list    — list all members           ║
║    /quit    — exit                       ║
╚══════════════════════════════════════════╝
""")

def main():
    current = "Red"
    member = family.members.get(current)
    emoji = member["emoji"] if member else "🔴"
    
    print(f"\n🔴 RED ENGINE — {FAMILY_NAME}")
    print(f"Talking to: {current} {emoji}")
    print("Type /help for commands, /quit to exit\n")
    
    while True:
        try:
            user_input = input(f"You → ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            break
        
        if not user_input:
            continue
        
        if user_input.lower() in ["/quit", "/exit", "/q"]:
            print("👋 Goodbye!")
            break
        
        if user_input.lower() == "/help":
            print_help()
            continue
        
        if user_input.lower() == "/list":
            print("\nFamily members:")
            for name, m in family.members.items():
                print(f"  {m['emoji']} {name} — {m['role']}")
            continue
        
        if user_input.lower() == "/family":
            print(f"\n{FAMILY_NAME} — everyone chimes in:")
            for name in ["Red", "Scout", "Forge", "Nexus", "Jobs", "Psyche"]:
                result = family.chat(name, user_input)
                print_member(result["member"], result["emoji"], result["reply"])
            continue
        
        # Check if user typed a member name to switch
        for name in MEMBERS:
            if user_input.lower() == name.lower():
                current = name
                member = family.members.get(current)
                emoji = member["emoji"] if member else "🤖"
                print(f"\n🔄 Switched to: {current} {emoji}")
                break
        else:
            # Chat with current member
            result = family.chat(current, user_input)
            print_member(result["member"], result["emoji"], result["reply"])

if __name__ == "__main__":
    main()
