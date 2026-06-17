#!/usr/bin/env python3
"""
Red Engine V2 - AI Family Desktop Application

A simple desktop application for interacting with the AI family.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
from datetime import datetime
from pathlib

class RedEngineDesktopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 Red Engine V2 - AI Family Desktop")
        self.root.geometry("800x600")
        self.root.configure(bg="#1a1a1a")
        
        # Your AI Family Members
        self.family_members = [
            {"name": "Red", "role": "Coordinator", "emoji": "🔴", "color": "#ff3333"},
            {"name": "Scout", "role": "Web Scout", "emoji": "🔍", "color": "#00ff88"},
            {"name": "Forge", "role": "Game Builder", "emoji": "⚒️", "color": "#ff8800"},
            {"name": "Nexus", "role": "Trader", "emoji": "🧮", "color": "#ffff00"},
            {"name": "Jobs", "role": "Income Creator", "emoji": "💼", "color": "#ff8844"},
            {"name": "Psyche", "role": "Pattern Analyst", "emoji": "🧠", "color": "#aa00ff"}
        ]
        
        # Initialize data
        self.family_state = {
            "members": self.family_members,
            "online_count": 6,
            "total_members": 6,
            "chat_history": {},
            "last_message": None
        }
        
        # Create GUI
        self.create_gui()
        
    def create_gui(self):
        """Create the main GUI interface"""
        # Create main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(header_frame, text="🎮 Red Engine V2 - AI Family Desktop", 
                 font=("Arial", 16, "bold"), foreground="#ff3333").pack()
        ttk.Label(header_frame, text="Interact with your AI family", 
                 font=("Arial", 10), foreground="#888").pack()
        
        # Family members section
        members_frame = ttk.LabelFrame(main_frame, text="🤖 AI Family Members", padding="10")
        members_frame.pack(fill=tk.X, pady=10)
        
        # Create buttons for each family member
        buttons_frame = ttk.Frame(members_frame)
        buttons_frame.pack(fill=tk.X)
        
        for member in self.family_members:
            btn = ttk.Button(buttons_frame, text=f"{member['emoji']} {member['name']} - {member['role']}",
                           command=lambda m=member: self.open_chat(m),
                           background=member['color'] if member['color'].startswith('#') else None)
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        
        # Chat section
        chat_frame = ttk.LabelFrame(main_frame, text="💬 Family Chat", padding="10")
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(chat_frame, height=15, width=80,
                                                      font=("Courier", 10), wrap=tk.WORD)
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Message input
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill=tk.X, pady=10)
        
        self.message_input = ttk.Entry(input_frame, font=("Arial", 12))
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        send_btn = ttk.Button(input_frame, text="Send", command=self.send_message,
                           style="Accent.TButton")
        send_btn.pack(side=tk.RIGHT, padx=5)
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Ready", font=("Arial", 9))
        self.status_label.pack(side=tk.LEFT)
        
        self.time_label = ttk.Label(status_frame, text="", font=("Arial", 9))
        self.time_label.pack(side=tk.RIGHT)
        
        # Initialize chat
        self.update_clock()
        self.display_welcome_message()
    
    def update_clock(self):
        """Update the clock in status bar"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_clock)
    
    def display_welcome_message(self):
        """Display welcome message in chat"""
        self.chat_display.insert(tk.END, "🤖 Red: Welcome to the AI Family Desktop! How can I help you today?\n")
        self.chat_display.see(tk.END)
    
    def open_chat(self, member):
        """Open chat with specific family member"""
        self.chat_display.insert(tk.END, f"{'='*50}\n")
        self.chat_display.insert(tk.END, f"💬 Chat with {member['emoji']} {member['name']} ({member['role']})\n")
        self.chat_display.insert(tk.END, f"{'='*50}\n\n")
        self.chat_display.see(tk.END)
    
    def send_message(self):
        """Send a message in the family chat"""
        message = self.message_input.get().strip()
        if message:
            # Add user message
            self.chat_display.insert(tk.END, f"👤 You: {message}\n\n")
            
            # Get response from first family member
            response = f"🤖 {self.family_members[0]['emoji']} {self.family_members[0]['name']}: I'll help you with that! Let me think about your request...\n\n"
            self.chat_display.insert(tk.END, response)
            
            # Clear input
            self.message_input.delete(0, tk.END)
            self.chat_display.see(tk.END)
    
    def run(self):
        """Run the application"""
        self.root.mainloop()

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = RedEngineDesktopApp(root)
    root.mainloop()
