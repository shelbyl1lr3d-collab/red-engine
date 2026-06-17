import os, sys, json
from datetime import datetime
from typing import Dict, List

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    HAS_TK = True
except ImportError:
    HAS_TK = False

class RedEngineGUI:
    def __init__(self, engine):
        self.engine = engine
        if not HAS_TK:
            raise RuntimeError("tkinter not available — use web UI instead")
        self.root = tk.Tk()
        self.root.title("Red Engine V2 - Control Center")
        self.root.geometry("1200x800")
        
        # Initialize modules
        self.lead_finder = engine.get("lead_finder")
        self.affiliate_updater = engine.get("affiliate_updater")
        self.game_cloner = engine.get("game_cloner")
        self.config_vault = engine.get("config_vault")
        
        # Create GUI
        self._create_gui()
        
    def _create_gui(self):
        """Create the main GUI interface."""
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self._create_lead_finder_tab()
        self._create_affiliate_updater_tab()
        self._create_game_cloner_tab()
        self._create_config_vault_tab()
        self._create_system_tab()
        
    def _create_lead_finder_tab(self):
        """Create the Lead Finder tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🔍 Lead Finder")
        
        # Main frame
        main_frame = ttk.Frame(tab, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Search section
        search_frame = ttk.LabelFrame(main_frame, text="Search for Leads", padding=15)
        search_frame.pack(fill="x", pady=10)
        
        ttk.Label(search_frame, text="Query:").grid(row=0, column=0, sticky="w", pady=5)
        self.job_query_var = tk.StringVar(value="Looking for music animator or crypto developer")
        ttk.Entry(search_frame, textvariable=self.job_query_var, width=60).grid(row=0, column=1, pady=5)
        
        ttk.Label(search_frame, text="Category:").grid(row=1, column=0, sticky="w", pady=5)
        self.category_var = tk.StringVar(value="all")
        categories = ["all", "freelance", "crypto", "music", "tech", "remote"]
        ttk.Combobox(search_frame, textvariable=self.category_var, values=categories, state="readonly").grid(row=1, column=1, pady=5)
        
        ttk.Button(search_frame, text="Find Leads & Emails", 
                  command=self._run_job_scraper, bg="#ffcc00", fg="black").grid(row=2, column=0, columnspan=2, pady=10)
        
        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="Found Leads", padding=15)
        results_frame.pack(fill="both", expand=True, pady=10)
        
        # Results text area
        self.results_text = tk.Text(results_frame, height=20, width=80)
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Export button
        ttk.Button(main_frame, text="Export Leads", command=self._export_leads).pack(pady=10)
        
    def _create_affiliate_updater_tab(self):
        """Create the Affiliate Updater tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📈 Affiliate Updater")
        
        main_frame = ttk.Frame(tab, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Links section
        links_frame = ttk.LabelFrame(main_frame, text="Affiliate Links", padding=15)
        links_frame.pack(fill="x", pady=10)
        
        # Create dynamic link entries
        self.link_entries = []
        self.link_entries_frame = links_frame
        
        for i in range(3):
            row_frame = ttk.Frame(self.link_entries_frame)
            row_frame.pack(fill="x", pady=5)
            
            name_entry = ttk.Entry(row_frame, width=20)
            name_entry.insert(0, f"Product {i+1}")
            name_entry.pack(side="left", padx=5)
            
            url_entry = ttk.Entry(row_frame, width=40)
            url_entry.insert(0, "https://example.com/product")
            url_entry.pack(side="left", padx=5)
            
            self.link_entries.append((name_entry, url_entry))
        
        ttk.Button(links_frame, text="Add More Links", 
                  command=self._add_link_entry).pack(pady=5)
        
        # Video section
        video_frame = ttk.LabelFrame(main_frame, text="Video File", padding=15)
        video_frame.pack(fill="x", pady=10)
        
        self.video_path_var = tk.StringVar(value="")
        ttk.Entry(video_frame, textvariable=self.video_path_var, width=50).pack(side="left", padx=5)
        ttk.Button(video_frame, text="Browse", command=self._browse_video).pack(side="left", padx=5)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=20)
        
        ttk.Button(button_frame, text="Update Monthly Landing Page", 
                  command=self._update_affiliate_page, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(pady=5)
        
        # Status section
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding=15)
        status_frame.pack(fill="x", pady=10)
        
        self.status_text = tk.Text(status_frame, height=10, width=80)
        status_scrollbar = ttk.Scrollbar(status_frame, orient="vertical", command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=status_scrollbar.set)
        
        self.status_text.pack(side="left", fill="both", expand=True)
        status_scrollbar.pack(side="right", fill="y")
        
    def _create_game_cloner_tab(self):
        """Create the Game Cloner tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🎮 Game Cloner")
        
        main_frame = ttk.Frame(tab, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Template section
        template_frame = ttk.LabelFrame(main_frame, text="Template Configuration", padding=15)
        template_frame.pack(fill="x", pady=10)
        
        ttk.Label(template_frame, text="Template Repository URL:").grid(row=0, column=0, sticky="w", pady=5)
        self.template_url_var = tk.StringVar(value="https://github.com/example/clean-flappy-bird-template")
        ttk.Entry(template_frame, textvariable=self.template_url_var, width=60).grid(row=0, column=1, pady=5)
        
        ttk.Label(template_frame, text="Output Game Name:").grid(row=1, column=0, sticky="w", pady=5)
        self.game_name_var = tk.StringVar(value="Flappy_Jessica_Rabbit")
        ttk.Entry(template_frame, textvariable=self.game_name_var, width=60).grid(row=1, column=1, pady=5)
        
        # Assets section
        assets_frame = ttk.LabelFrame(main_frame, text="Custom Assets", padding=15)
        assets_frame.pack(fill="x", pady=10)
        
        ttk.Label(assets_frame, text="Character Image:").grid(row=0, column=0, sticky="w", pady=5)
        self.character_path_var = tk.StringVar(value="")
        ttk.Entry(assets_frame, textvariable=self.character_path_var, width=50).grid(row=0, column=1, pady=5)
        ttk.Button(assets_frame, text="Browse", command=self._browse_character).pack(side="right", padx=5)
        
        ttk.Label(assets_frame, text="Background Image:").grid(row=1, column=0, sticky="w", pady=5)
        self.background_path_var = tk.StringVar(value="")
        ttk.Entry(assets_frame, textvariable=self.background_path_var, width=50).grid(row=1, column=1, pady=5)
        ttk.Button(assets_frame, text="Browse", command=self._browse_background).pack(side="right", padx=5)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=20)
        
        ttk.Button(button_frame, text="Clone & Re-theme Game", 
                  command=self._clone_game, bg="#2196F3", fg="white", font=("Arial", 10, "bold")).pack(pady=5)
        
        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="Cloning Results", padding=15)
        results_frame.pack(fill="x", pady=10)
        
        self.clone_results_text = tk.Text(results_frame, height=15, width=80)
        clone_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.clone_results_text.yview)
        self.clone_results_text.configure(yscrollcommand=clone_scrollbar.set)
        
        self.clone_results_text.pack(side="left", fill="both", expand=True)
        clone_scrollbar.pack(side="right", fill="y")
        
    def _create_config_vault_tab(self):
        """Create the Config Vault tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🔑 Config Vault")
        
        main_frame = ttk.Frame(tab, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Vault info section
        info_frame = ttk.LabelFrame(main_frame, text="Vault Information", padding=15)
        info_frame.pack(fill="x", pady=10)
        
        self.vault_info_text = tk.Text(info_frame, height=10, width=80)
        vault_info_scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=self.vault_info_text.yview)
        self.vault_info_text.configure(yscrollcommand=vault_info_scrollbar.set)
        
        self.vault_info_text.pack(side="left", fill="both", expand=True)
        vault_info_scrollbar.pack(side="right", fill="y")
        
        # Key management section
        key_frame = ttk.LabelFrame(main_frame, text="Key Management", padding=15)
        key_frame.pack(fill="x", pady=10)
        
        ttk.Label(key_frame, text="Key Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.key_name_var = tk.StringVar()
        ttk.Entry(key_frame, textvariable=self.key_name_var, width=30).grid(row=0, column=1, pady=5)
        
        ttk.Label(key_frame, text="Value:").grid(row=1, column=0, sticky="w", pady=5)
        self.key_value_var = tk.StringVar()
        ttk.Entry(key_frame, textvariable=self.key_value_var, width=50).grid(row=1, column=1, pady=5)
        
        ttk.Label(key_frame, text="Category:").grid(row=2, column=0, sticky="w", pady=5)
        self.key_category_var = tk.StringVar(value="general")
        categories = ["general", "video", "youtube", "crypto", "marketing", "ad_network"]
        ttk.Combobox(key_frame, textvariable=self.key_category_var, values=categories, state="readonly").grid(row=2, column=1, pady=5)
        
        ttk.Label(key_frame, text="Description:").grid(row=3, column=0, sticky="w", pady=5)
        self.key_desc_var = tk.StringVar()
        ttk.Entry(key_frame, textvariable=self.key_desc_var, width=50).grid(row=3, column=1, pady=5)
        
        button_frame = ttk.Frame(key_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Add Key", command=self._add_key).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Refresh Vault", command=self._refresh_vault).pack(side="left", padx=5)
        
        # Keys list section
        keys_frame = ttk.LabelFrame(main_frame, text="Stored Keys", padding=15)
        keys_frame.pack(fill="x", pady=10)
        
        self.keys_text = tk.Text(keys_frame, height=15, width=80)
        keys_scrollbar = ttk.Scrollbar(keys_frame, orient="vertical", command=self.keys_text.yview)
        self.keys_text.configure(yscrollcommand=keys_scrollbar.set)
        
        self.keys_text.pack(side="left", fill="both", expand=True)
        keys_scrollbar.pack(side="right", fill="y")
        
    def _create_system_tab(self):
        """Create the System Status tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📊 System Status")
        
        main_frame = ttk.Frame(tab, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Engine status
        status_frame = ttk.LabelFrame(main_frame, text="Engine Status", padding=15)
        status_frame.pack(fill="x", pady=10)
        
        self.status_text = tk.Text(status_frame, height=10, width=80)
        status_scrollbar = ttk.Scrollbar(status_frame, orient="vertical", command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=status_scrollbar.set)
        
        self.status_text.pack(side="left", fill="both", expand=True)
        status_scrollbar.pack(side="right", fill="y")
        
        # Update button
        ttk.Button(main_frame, text="Refresh Status", command=self._update_system_status).pack(pady=10)
        
    def _run_job_scraper(self):
        """Run the job scraper."""
        query = self.job_query_var.get()
        category = self.category_var.get()
        
        if not query:
            messagebox.showwarning("Warning", "Please enter a search query")
            return
        
        try:
            result = self.lead_finder.search_jobs(query, category)
            
            # Display results
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"Search Results for '{query}' (Category: {category})\n")
            self.results_text.insert(tk.END, f"Found {result['count']} leads:\n\n")
            
            for i, lead in enumerate(result['leads'][:10], 1):
                self.results_text.insert(tk.END, f"{i}. {lead['title']}\n")
                self.results_text.insert(tk.END, f"   Email: {lead.get('email', 'N/A')}\n")
                self.results_text.insert(tk.END, f"   URL: {lead['url']}\n")
                self.results_text.insert(tk.END, f"   Snippet: {lead['snippet'][:100]}...\n\n")
            
            messagebox.showinfo("Success", f"Found {result['count']} leads!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to search jobs: {str(e)}")
    
    def _export_leads(self):
        """Export leads to file."""
        try:
            leads = self.lead_finder.get_cached_leads()
            if not leads:
                messagebox.showwarning("Warning", "No leads to export")
                return
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json"), ("Text files", "*.txt")]
            )
            
            if file_path:
                if file_path.endswith(".csv"):
                    content = self.lead_finder.export_leads("csv")
                else:
                    content = self.lead_finder.export_leads("json")
                
                with open(file_path, "w") as f:
                    f.write(content)
                
                messagebox.showinfo("Success", f"Leads exported to {file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export leads: {str(e)}")
    
    def _browse_video(self):
        """Browse for video file."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Video files", "*.mp4;*.avi;*.mov"), ("All files", "*")]
        )
        if file_path:
            self.video_path_var.set(file_path)
    
    def _browse_character(self):
        """Browse for character image."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif")]
        )
        if file_path:
            self.character_path_var.set(file_path)
    
    def _browse_background(self):
        """Browse for background image."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif")]
        )
        if file_path:
            self.background_path_var.set(file_path)
    
    def _add_link_entry(self):
        """Add more link entry fields."""
        row_frame = ttk.Frame(self.link_entries_frame)
        row_frame.pack(fill="x", pady=5)
        
        name_entry = ttk.Entry(row_frame, width=20)
        name_entry.insert(0, f"Product {len(self.link_entries) + 1}")
        name_entry.pack(side="left", padx=5)
        
        url_entry = ttk.Entry(row_frame, width=40)
        url_entry.insert(0, "https://example.com/product")
        url_entry.pack(side="left", padx=5)
        
        self.link_entries.append((name_entry, url_entry))
    
    def _update_affiliate_page(self):
        """Update the affiliate landing page."""
        # Collect links
        new_links = {}
        for name_entry, url_entry in self.link_entries:
            name = name_entry.get()
            url = url_entry.get()
            if name and url:
                new_links[name] = url
        
        if not new_links:
            messagebox.showwarning("Warning", "Please add at least one affiliate link")
            return
        
        try:
            result = self.affiliate_updater.update_monthly_landing_page(
                new_links, self.video_path_var.get()
            )
            
            # Update status
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END, f"Affiliate Page Update Status:\n")
            self.status_text.insert(tk.END, f"Status: {result['status']}\n")
            self.status_text.insert(tk.END, f"Links Updated: {result['links_updated']}\n")
            self.status_text.insert(tk.END, f"Backup Created: {result['backup_created']}\n")
            
            if result['deployed']['status'] == 'success':
                messagebox.showinfo("Success", "Affiliate page updated and deployed successfully!")
            else:
                messagebox.showwarning("Warning", f"Page updated but deployment failed: {result['deployed']['message']}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update affiliate page: {str(e)}")
    
    def _clone_game(self):
        """Clone and retheme a game."""
        template_url = self.template_url_var.get()
        game_name = self.game_name_var.get()
        character_path = self.character_path_var.get()
        background_path = self.background_path_var.get()
        
        if not template_url or not game_name:
            messagebox.showwarning("Warning", "Please provide template URL and game name")
            return
        
        try:
            result = self.game_cloner.clone_and_retheme_game(
                template_url, game_name, character_path, background_path
            )
            
            # Display results
            self.clone_results_text.delete(1.0, tk.END)
            self.clone_results_text.insert(tk.END, f"Game Cloning Results:\n")
            self.clone_results_text.insert(tk.END, f"Status: Success\n")
            self.clone_results_text.insert(tk.END, f"Game Name: {result['game_name']}\n")
            self.clone_results_text.insert(tk.END, f"Path: {result['path']}\n")
            self.clone_results_text.insert(tk.END, f"Template: {result['template_repo']}\n")
            self.clone_results_text.insert(tk.END, f"Character: {result['character_image']}\n")
            self.clone_results_text.insert(tk.END, f"Background: {result['background_image']}\n")
            self.clone_results_text.insert(tk.END, f"Ads Injected: {result['ads_injected']}\n")
            self.clone_results_text.insert(tk.END, f"Timestamp: {result['timestamp']}\n")
            
            messagebox.showinfo("Success", f"Game '{game_name}' cloned and re-themed successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clone game: {str(e)}")
    
    def _add_key(self):
        """Add a key to the config vault."""
        key_name = self.key_name_var.get()
        key_value = self.key_value_var.get()
        key_category = self.key_category_var.get()
        key_desc = self.key_desc_var.get()
        
        if not key_name or not key_value:
            messagebox.showwarning("Warning", "Please provide key name and value")
            return
        
        try:
            result = self.config_vault.add_key(key_name, key_value, key_desc, key_category)
            
            # Clear form
            self.key_name_var.set("")
            self.key_value_var.set("")
            self.key_desc_var.set("")
            
            messagebox.showinfo("Success", f"Key '{key_name}' added to vault!")
            
            # Refresh keys list
            self._refresh_vault()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add key: {str(e)}")
    
    def _refresh_vault(self):
        """Refresh the vault information and keys list."""
        try:
            # Update vault info
            vault_info = self.config_vault.list_keys()
            self.vault_info_text.delete(1.0, tk.END)
            self.vault_info_text.insert(tk.END, f"Vault Information:\n")
            self.vault_info_text.insert(tk.END, f"Total Keys: {vault_info['total_keys']}\n")
            self.vault_info_text.insert(tk.END, f"Categories: {', '.join(vault_info['categories'])}\n\n")
            
            # Update keys list
            self.keys_text.delete(1.0, tk.END)
            for key_name, key_data in vault_info['keys'].items():
                self.keys_text.insert(tk.END, f"{key_name}:\n")
                self.keys_text.insert(tk.END, f"  Description: {key_data['description']}\n")
                self.keys_text.insert(tk.END, f"  Category: {key_data['category']}\n")
                self.keys_text.insert(tk.END, f"  Added: {key_data['added_at']}\n")
                self.keys_text.insert(tk.END, f"  Last Accessed: {key_data['last_accessed']}\n")
                self.keys_text.insert(tk.END, f"  Access Count: {key_data['access_count']}\n\n")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh vault: {str(e)}")
    
    def _update_system_status(self):
        """Update the system status."""
        try:
            status = self.engine.status
            
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END, f"System Status:\n")
            self.status_text.insert(tk.END, f"Running: {status['running']}\n")
            self.status_text.insert(tk.END, f"Version: {status['version']}\n")
            self.status_text.insert(tk.END, f"Goal: ${status['goal']}\n")
            self.status_text.insert(tk.END, f"Modules Loaded: {', '.join(status['modules_loaded'])}\n\n")
            
            # Get recent logs
            logs = self.engine.get_logs(10)
            self.status_text.insert(tk.END, f"Recent Logs:\n")
            for log in logs:
                self.status_text.insert(tk.END, f"[{log['time']}] {log['level']}: {log['message']}\n")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update system status: {str(e)}")
    
    def run(self):
        """Run the GUI application."""
        # Initialize modules
        if not self.lead_finder:
            self.engine.register("lead_finder", self.lead_finder)
        if not self.affiliate_updater:
            self.engine.register("affiliate_updater", self.affiliate_updater)
        if not self.game_cloner:
            self.engine.register("game_cloner", self.game_cloner)
        if not self.config_vault:
            self.engine.register("config_vault", self.config_vault)
        
        # Start the application
        self.root.mainloop()