import os
import sys
import time
import uuid
import json
import customtkinter as ctk
from PIL import Image
import riot_logic
from third_party_apps import THIRD_PARTY_APPS

def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", None)
    if not base_path: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- GLASS-HEX THEME COLORS ---
OBSIDIAN = "#0D0D0D"
NEON_PURPLE = "#BF00FF"
HEXTECH_GOLD = "#D4AF37"
GLASS_PANE = "#121216"     
GLASS_HOVER = "#24103A"    
RED_GLASS = "#330A0A"      
WHITE = "#ECE8E1"

# --- GAME CONSTANTS ---
RANKS_VALORANT =["", "Unranked", "Iron", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Ascendant", "Immortal", "Radiant"]
RANKS_OW =["", "Unranked", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "Grand Master", "Champion", "Top 500"]
RANKS_LOL =["", "Unranked", "Iron", "Bronze", "Silver", "Gold", "Platinum", "Emerald", "Diamond", "Master", "Grandmaster", "Challenger"]
REGIONS_LOL =["NA", "EUW", "EUNE", "KR", "JP", "OCE", "LAN", "LAS", "TR", "BR", "SEA", "MENA"]

class RiotSwitcherApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        riot_logic.setup_profiles_folder()
        self.resource_path = resource_path("assets")
        os.makedirs(self.resource_path, exist_ok=True)

        self.title("Riovert Profile Manager")
        self.geometry("1100x700") 
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")
        self.configure(fg_color=OBSIDIAN)
        
        icon_path = os.path.join(self.resource_path, "Riovert.ico")
        try: self.iconbitmap(icon_path)
        except Exception: pass 

        # ASSETS
        self.BTN_WIDTH = 220
        self.BTN_HEIGHT = 330
        self.bg_img = self.load_image("bg.png", (1100, 700))
        self.val_img = self.load_image("Valorant.jpg", (220, 330))
        self.euw_img = self.load_image("LOLeuw.png", (220, 330))
        self.eune_img = self.load_image("LOLeune.png", (220, 330))
        self.overwatch_img = self.load_image("Overwatch.jpg", (220, 330))
        self.bnet_img = self.load_image("Battlenet.jpg", (220, 330))
        self.riot_games_img = self.load_image("Riot Games.jpg", (220, 330))
        self.add_img = self.load_image("AddNew.png", (220, 330))     
        
        # STATE
        self.helper_options = {app["display"]: key for key, app in THIRD_PARTY_APPS.items()}
        self.selected_helper = ctk.StringVar(value=self.load_saved_helper())
        
        self._switching = False
        self._pulse_active = True
        
        self.current_service = None 
        self.setup_queue =[]       
        self.current_setup_idx = 0

        self.build_ui_layout()
        self.start_pfp_pulse()
        self.show_home()

    def load_saved_helper(self):
        config_path = os.path.join(riot_logic.RIOVERT_DIR, "config.json")
        try:
            with open(config_path, "r") as f: return json.load(f).get("selected_helper", "Porofessor Standalone")
        except: return "Porofessor Standalone"

    def save_helper_choice(self, choice):
        config_path = os.path.join(riot_logic.RIOVERT_DIR, "config.json")
        try:
            data = {}
            if os.path.exists(config_path):
                with open(config_path, "r") as f: data = json.load(f)
            data["selected_helper"] = choice
            with open(config_path, "w") as f: json.dump(data, f)
        except: pass

    def load_image(self, filename, size):
        path = os.path.join(self.resource_path, filename)
        if os.path.exists(path):
            try: return ctk.CTkImage(light_image=Image.open(path), dark_image=Image.open(path), size=size)
            except: pass
        return None

    # --- UI ARCHITECTURE ---
    def build_ui_layout(self):
        if self.bg_img:
            self.bg_label = ctk.CTkLabel(self, text="", image=self.bg_img)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.glitch_overlay = ctk.CTkFrame(self, fg_color=NEON_PURPLE, corner_radius=0)
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True)

        self.home_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.dashboard_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.setup_init_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.setup_loop_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.settings_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")

        self.build_home_screen()
        self.build_dashboard_screen()
        self.build_setup_init_screen()
        self.build_setup_loop_screen()
        self.build_settings_screen()

        # Global Kill Switch & Ticker
        self.bottom_bar = ctk.CTkFrame(self, fg_color="#000000", height=45, corner_radius=0)
        self.bottom_bar.pack(side="bottom", fill="x")
        self.status_label = ctk.CTkLabel(self.bottom_bar, text=">[SYSTEM] IDLE", font=ctk.CTkFont("Consolas", 14, "bold"), text_color=HEXTECH_GOLD)
        self.status_label.pack(side="left", padx=15, pady=8)
        self.kill_switch_btn = ctk.CTkButton(
            self.bottom_bar, text="TERMINATE ALL PROCESSES", font=ctk.CTkFont("Segoe UI Black", 12), text_color=WHITE,
            fg_color="#DA0000", border_width=1, border_color="#550A0A", hover_color="#550A0A", height=35, corner_radius=4, command=self.trigger_kill_switch
        )
        self.kill_switch_btn.pack(side="right", padx=15, pady=5)

    def log_status(self, text):
        self.status_label.configure(text=f"> {text.upper()}")
        self.update()

    def trigger_glitch(self, callback, color=NEON_PURPLE):
        self.glitch_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.glitch_overlay.configure(fg_color=color)
        self.update()
        time.sleep(0.05)
        self.glitch_overlay.configure(fg_color=WHITE)
        self.update()
        time.sleep(0.05)
        self.glitch_overlay.configure(fg_color=OBSIDIAN)
        self.update()
        callback()
        self.glitch_overlay.place_forget()
        self.update()

    def switch_frame(self, target_frame):
        self.home_frame.pack_forget()
        self.dashboard_frame.pack_forget()
        self.setup_init_frame.pack_forget()
        self.setup_loop_frame.pack_forget()
        self.settings_frame.pack_forget()
        target_frame.pack(fill="both", expand=True)

    def show_home(self): self.trigger_glitch(lambda: self.switch_frame(self.home_frame))
    def show_setup_init(self): self.trigger_glitch(lambda: self.switch_frame(self.setup_init_frame))
    def show_settings(self): self.trigger_glitch(lambda: self.switch_frame(self.settings_frame))

    def show_dashboard(self, service):
        if service is None:
            self.log_status("[ERR] SERVICE NOT SELECTED. RETURNING HOME.")
            self.show_home()
            return
        self.current_service = service
        self.refresh_dashboard()
        self.trigger_glitch(lambda: self.switch_frame(self.dashboard_frame))
        self.log_status(f"[SYSTEM] {service.upper()} COMMAND CENTER ONLINE.")

    # --- SCREEN 1: HOME (GAME SELECTION) ---
    def build_home_screen(self):
        center_wrapper = ctk.CTkFrame(self.home_frame, fg_color="transparent")
        center_wrapper.pack(expand=True, anchor="center")

        header = ctk.CTkLabel(center_wrapper, text="GAME SELECTION", font=ctk.CTkFont("Segoe UI Black", 40, "bold"), text_color=HEXTECH_GOLD)
        header.pack(pady=(0, 10))
        ctk.CTkFrame(center_wrapper, fg_color=NEON_PURPLE, height=2, width=350).pack(pady=(0, 50))

        cards_container = ctk.CTkFrame(center_wrapper, fg_color="transparent")
        cards_container.pack()

        riot_card = ctk.CTkButton(
            cards_container, text="RIOT CLIENT\n(Valorant, League)", image=self.riot_games_img,
            width=250, height=350, corner_radius=15, fg_color=GLASS_PANE if not self.riot_games_img else "transparent",
            font=ctk.CTkFont("Segoe UI Black", 18), text_color=WHITE, border_width=2, border_color="#333344",
            compound="bottom", command=lambda: self.show_dashboard("riot")
        )
        riot_card.pack(side="left", padx=15)

        bnet_card = ctk.CTkButton(
            cards_container, text="BATTLE.NET\n(Overwatch)", image=self.bnet_img,
            width=250, height=350, corner_radius=15, fg_color=GLASS_PANE if not self.bnet_img else "transparent",
            font=ctk.CTkFont("Segoe UI Black", 18), text_color=WHITE, border_width=2, border_color="#333344",
            compound="bottom", command=lambda: self.show_dashboard("bnet")
        )
        bnet_card.pack(side="left", padx=15)

        add_card = ctk.CTkButton(
            cards_container, text="+ ADD NEW", image=self.add_img,
            width=250, height=350, corner_radius=15, fg_color=GLASS_PANE if not self.add_img else "transparent",
            font=ctk.CTkFont("Segoe UI Black", 24), text_color=HEXTECH_GOLD, border_width=2, border_color=NEON_PURPLE, hover_color=GLASS_HOVER,
            compound="bottom", command=self.show_setup_init
        )
        add_card.pack(side="left", padx=15)
        
        self.bind_shard_hover([riot_card, bnet_card, add_card])

    # --- SCREEN 2: DASHBOARD ---
    def build_dashboard_screen(self):
        self.sidebar = ctk.CTkFrame(self.dashboard_frame, width=80, fg_color=GLASS_PANE, corner_radius=0, border_width=1, border_color="#1E1E24")
        self.sidebar.pack(side="left", fill="y")
        
        self.home_btn = ctk.CTkButton(self.sidebar, text="⌂\nHome", font=ctk.CTkFont(size=20), width=50, height=60, fg_color="transparent", text_color=WHITE, hover_color="#22222A", command=self.show_home)
        self.home_btn.pack(side="top", pady=25)
        
        self.pfp_border = ctk.CTkFrame(self.sidebar, width=15, height=15, corner_radius=8, fg_color=NEON_PURPLE)
        self.pfp_border.pack(side="top", pady=10)

        self.settings_btn = ctk.CTkButton(self.sidebar, text="⚙", font=ctk.CTkFont(size=28), width=50, height=50, fg_color="transparent", text_color=HEXTECH_GOLD, hover_color="#22222A", command=self.show_settings)
        self.settings_btn.pack(side="bottom", pady=20)
        
        self.add_btn = ctk.CTkButton(self.sidebar, text="➕", font=ctk.CTkFont(size=26, weight="bold"), width=50, height=50, fg_color="transparent", text_color=WHITE, hover_color=GLASS_HOVER, border_width=1, border_color="#555", command=self.show_setup_init)
        self.add_btn.pack(side="bottom", pady=10)

        self.hud_area = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        self.hud_area.pack(side="right", fill="both", expand=True, padx=30, pady=30)

        self.helper_ui_container = ctk.CTkFrame(self.hud_area, fg_color="transparent")
        self.helper_ui_container.pack(side="top", fill="x", pady=(0, 20))
        ctk.CTkLabel(self.helper_ui_container, text="ACTIVE HELPER:", font=ctk.CTkFont("Consolas", 14, "bold"), text_color=HEXTECH_GOLD).pack(side="left")
        self.helper_dropdown = ctk.CTkOptionMenu(self.helper_ui_container, variable=self.selected_helper, values=list(self.helper_options.keys()), fg_color=GLASS_PANE, button_color=NEON_PURPLE, button_hover_color="#8A00E6", font=ctk.CTkFont("Segoe UI", 14, "bold"), dropdown_font=ctk.CTkFont("Segoe UI", 13), width=250, height=40, command=self.save_helper_choice)
        self.helper_dropdown.pack(side="left", padx=15)
        
        # Changed to "Switch Helper" logic via button
        ctk.CTkButton(self.helper_ui_container, text="Switch Helper", width=120, height=40, fg_color=GLASS_PANE, border_width=1, border_color=NEON_PURPLE, hover_color=NEON_PURPLE, text_color=WHITE, font=ctk.CTkFont("Segoe UI", 12, "bold"), command=self.switch_helper).pack(side="left", padx=10)

        ctk.CTkButton(self.helper_ui_container, text="Terminate Helpers", width=140, height=40, fg_color="#550000", border_width=1, border_color="#AA0000", hover_color="#AA0000", text_color=WHITE, font=ctk.CTkFont("Segoe UI", 12, "bold"), command=self.terminate_helpers).pack(side="left", padx=10)

        self.shards_container = ctk.CTkScrollableFrame(
            self.hud_area, fg_color="transparent", orientation="horizontal",
            scrollbar_button_color="#1E1E24", scrollbar_button_hover_color=NEON_PURPLE, scrollbar_fg_color="transparent"
        )
        self.shards_container.pack(side="top", fill="both", expand=True)

    def refresh_dashboard(self):
        if self.current_service == "bnet":
            self.helper_ui_container.pack_forget()
        else:
            self.helper_ui_container.pack_forget()
            self.helper_ui_container.pack(side="top", fill="x", pady=(0, 20))

        for widget in self.shards_container.winfo_children(): widget.destroy()

        self.shards_inner_wrapper = ctk.CTkFrame(self.shards_container, fg_color="transparent")
        self.shards_inner_wrapper.pack(expand=True, anchor="center")

        profiles = riot_logic.get_profiles_by_service(self.current_service)
        self.shard_btns =[]

        if not profiles:
            service_name = self.current_service.upper() if self.current_service else "SERVICE"
            ctk.CTkLabel(self.shards_inner_wrapper, text=f"NO {service_name} PROFILES FOUND.\nCLICK '+' TO ADD.", font=ctk.CTkFont("Segoe UI Black", 20), text_color="#555").pack(pady=100, padx=100)
            return

        for pid, data in profiles.items():
            shard = ctk.CTkFrame(self.shards_inner_wrapper, fg_color="transparent")
            shard.pack(side="left", padx=15, pady=20)

            img = self.bnet_img
            if data["game"] == "valorant": img = self.val_img
            elif data["game"] == "overwatch": img = self.overwatch_img
            elif data["game"] == "lol":
                img = self.eune_img if data.get("region") == "EUNE" else self.euw_img
            
            btn = ctk.CTkButton(
                shard, text="" if img else data["name"], image=img,
                width=220, height=330, corner_radius=15, fg_color=GLASS_PANE if not img else "transparent", 
                font=ctk.CTkFont("Segoe UI Black", 18), text_color=WHITE, border_width=2, border_color="#222233",
                command=lambda p=pid, g=data["game"]: self.switch_and_launch(p, g)
            )
            btn.pack(pady=5)
            self.shard_btns.append(btn)
            
            display_title = data['name']
            if data.get('region'): display_title = f"[{data['region']}] {display_title}"
            rank_display = f"\n{data['rank']}" if data['rank'].strip() else ""
            
            ctk.CTkLabel(shard, text=f"{display_title}{rank_display}", font=ctk.CTkFont("Consolas", 14, "bold"), text_color=HEXTECH_GOLD).pack()
            ctk.CTkButton(shard, text="DELETE", fg_color=RED_GLASS, hover_color="#550A0A", text_color=WHITE, height=25, width=100, command=lambda p=pid: self.delete_and_refresh(p)).pack(pady=5)
            
        self.bind_shard_hover(self.shard_btns)

    def delete_and_refresh(self, pid):
        riot_logic.delete_profile(pid)
        self.refresh_dashboard()

    # --- SCREEN 3: SETUP INITIALIZER ---
    def build_setup_init_screen(self):
        card = ctk.CTkFrame(self.setup_init_frame, fg_color=GLASS_PANE, corner_radius=15, border_width=1, border_color=NEON_PURPLE)
        card.pack(expand=True, anchor="center", ipadx=60, ipady=40)

        ctk.CTkLabel(card, text="ADD NEW PROFILES", font=ctk.CTkFont("Segoe UI Black", 24), text_color=WHITE).pack(pady=(20, 20))
        
        ctk.CTkLabel(card, text="Select Game Service:", font=ctk.CTkFont("Segoe UI", 14)).pack(pady=5)
        self.setup_service_var = ctk.StringVar(value="riot")
        ctk.CTkOptionMenu(card, variable=self.setup_service_var, values=["riot", "bnet"], fg_color=OBSIDIAN, button_color=NEON_PURPLE, width=250).pack(pady=5)

        ctk.CTkLabel(card, text="Number of Accounts to Add:", font=ctk.CTkFont("Segoe UI", 14)).pack(pady=(20, 5))
        self.setup_count_var = ctk.StringVar(value="1")
        ctk.CTkOptionMenu(card, variable=self.setup_count_var, values=[str(i) for i in range(1, 11)], fg_color=OBSIDIAN, button_color=HEXTECH_GOLD, width=250).pack(pady=5)

        ctk.CTkButton(card, text="START WIZARD", fg_color=NEON_PURPLE, hover_color="#8A00E6", font=ctk.CTkFont("Segoe UI Black", 14), height=45, width=250, command=self.start_setup_loop).pack(pady=40)
        ctk.CTkButton(card, text="CANCEL", fg_color="transparent", text_color="#888", hover_color="#222", command=self.show_home).pack()

    def start_setup_loop(self):
        service = self.setup_service_var.get()
        count = int(self.setup_count_var.get())
        self.setup_queue = [service] * count
        self.current_setup_idx = 0
        self.process_setup_loop()

    # --- SCREEN 4: SETUP LOOP WIZARD ---
    def build_setup_loop_screen(self):
        self.loop_card = ctk.CTkFrame(self.setup_loop_frame, fg_color=GLASS_PANE, corner_radius=15, border_width=1, border_color=HEXTECH_GOLD)
        self.loop_card.pack(expand=True, anchor="center", ipadx=60, ipady=40)

        self.loop_title = ctk.CTkLabel(self.loop_card, text="AWAITING CONNECTION", font=ctk.CTkFont("Segoe UI Black", 22), text_color=HEXTECH_GOLD)
        self.loop_title.pack(pady=(20, 10))

        self.setup_name_entry = ctk.CTkEntry(self.loop_card, placeholder_text="Profile Name (e.g. My Smurf)", width=300, fg_color=OBSIDIAN, border_color=NEON_PURPLE)
        self.setup_name_entry.pack(pady=10)

        self.setup_game_var = ctk.StringVar(value="valorant")
        self.setup_game_dropdown = ctk.CTkOptionMenu(self.loop_card, variable=self.setup_game_var, values=["valorant", "lol", "overwatch"], width=300, fg_color=OBSIDIAN, command=self.on_setup_game_changed)
        self.setup_game_dropdown.pack(pady=10)

        self.setup_region_var = ctk.StringVar(value="EUW")
        self.setup_region_dropdown = ctk.CTkOptionMenu(self.loop_card, variable=self.setup_region_var, values=REGIONS_LOL, width=300, fg_color=OBSIDIAN, button_color=NEON_PURPLE)
        
        self.setup_rank_var = ctk.StringVar(value="")
        self.setup_rank_dropdown = ctk.CTkOptionMenu(self.loop_card, variable=self.setup_rank_var, values=RANKS_VALORANT, width=300, fg_color=OBSIDIAN, button_color=HEXTECH_GOLD)
        self.setup_rank_dropdown.pack(pady=10)

        instructions = ("1. Log into the Client.\n2. CRITICAL: Check 'Stay Signed In'.\n3. Close Client manually (X)\nfrom the system tray & Task Manager.\n4. Fill info & Click Complete.")
        ctk.CTkLabel(self.loop_card, text=instructions, font=ctk.CTkFont("Consolas", 13), text_color=WHITE, justify="center").pack(pady=15)

        self.loop_btn = ctk.CTkButton(self.loop_card, text="COMPLETE & VALIDATE", fg_color=NEON_PURPLE, hover_color="#8A00E6", text_color=WHITE, font=ctk.CTkFont("Segoe UI Black", 14), height=45, width=250, command=self.validate_setup_loop)
        self.loop_btn.pack(pady=20)

    def on_setup_game_changed(self, choice):
        self.setup_region_dropdown.pack_forget()
        self.setup_rank_dropdown.pack_forget()

        if choice == "valorant":
            self.setup_rank_dropdown.configure(values=RANKS_VALORANT)
        elif choice == "lol":
            self.setup_rank_dropdown.configure(values=RANKS_LOL)
            self.setup_region_dropdown.pack(pady=10)
        elif choice == "overwatch":
            self.setup_rank_dropdown.configure(values=RANKS_OW)
            
        self.setup_rank_var.set("")
        self.setup_rank_dropdown.pack(pady=10)

    def process_setup_loop(self):
        if self.current_setup_idx >= len(self.setup_queue):
            self.log_status("[SYSTEM] WIZARD COMPLETE.")
            self.show_home()
            return

        service = self.setup_queue[self.current_setup_idx]
        self.trigger_glitch(lambda: self.switch_frame(self.setup_loop_frame))
        
        if service == "riot":
            self.setup_game_dropdown.configure(values=["valorant", "lol"])
            self.setup_game_var.set("valorant")
            self.on_setup_game_changed("valorant")
        elif service == "bnet":
            self.setup_game_dropdown.configure(values=["overwatch"])
            self.setup_game_var.set("overwatch")
            self.on_setup_game_changed("overwatch")
            
        self.setup_name_entry.delete(0, 'end')

        self.loop_title.configure(text=f"AWAITING: {service.upper()}[{self.current_setup_idx+1}/{len(self.setup_queue)}]")
        self.log_status(f"[AWAITING] PREPARING ENVIRONMENT FOR ACCOUNT {self.current_setup_idx+1}...")
        
        riot_logic.request_graceful_shutdown()
        self.after(3000, lambda s=service: self._finish_prep(s))

    def _finish_prep(self, service):
        riot_logic.force_kill_all_services()
        riot_logic.prepare_setup(service)
        self.log_status("[AWAITING LOGIN] PLEASE LOG IN & FILL INFO.")

    def validate_setup_loop(self):
        name = self.setup_name_entry.get().strip()
        if not name:
            self.log_status("[ERR] PROFILE NAME CANNOT BE EMPTY.")
            return

        service = self.setup_queue[self.current_setup_idx]
        self.loop_btn.configure(state="disabled", text="FLUSHING TO DISK (4s)...")
        self.log_status("[VALIDATING] SAVING TO DISK...")
        
        riot_logic.request_graceful_shutdown(service)
        self.after(4000, lambda: self._finish_validate_loop(service, name))

    def _finish_validate_loop(self, service, name):
        riot_logic.force_kill_all_services()
        
        if riot_logic.validate_active_auth(service):
            pid = str(uuid.uuid4())[:8] 
            riot_logic.capture_target_profile(pid, service)
            
            region = self.setup_region_var.get() if self.setup_game_var.get() == "lol" else ""
            riot_logic.save_profile(pid, name, service, self.setup_game_var.get(), self.setup_rank_var.get(), region)
            
            self.log_status(f"[SUCCESS] '{name}' SAVED.")
            self.current_setup_idx += 1
            self.loop_btn.configure(state="normal", text="COMPLETE & VALIDATE")
            self.process_setup_loop()
        else:
            self.log_status(f"[CRITICAL ERR] AUTH CORRUPT. YOU MUST CHECK 'STAY SIGNED IN'.")
            self.loop_btn.configure(state="normal", text="COMPLETE & VALIDATE")
            riot_logic.request_graceful_shutdown(service)
            self.after(2000, lambda s=service: self._finish_prep(s))

    # --- SCREEN 5: SETTINGS ---
    def build_settings_screen(self):
        card = ctk.CTkFrame(self.settings_frame, fg_color=GLASS_PANE, corner_radius=15, border_width=1, border_color=HEXTECH_GOLD)
        card.pack(expand=True, anchor="center", ipadx=60, ipady=40)

        ctk.CTkLabel(card, text="SYSTEM DIAGNOSTICS", font=ctk.CTkFont("Segoe UI Black", 20), text_color=HEXTECH_GOLD).pack(pady=(20, 20))
        
        ctk.CTkButton(card, text="Check & Validate All Profiles", height=45, font=ctk.CTkFont("Segoe UI", 13, "bold"), fg_color=OBSIDIAN, border_color=NEON_PURPLE, border_width=1, hover_color=NEON_PURPLE, command=self.settings_validate).pack(pady=10, fill="x", padx=40)
        ctk.CTkButton(card, text="Re-Setup All Profiles", height=45, font=ctk.CTkFont("Segoe UI", 13, "bold"), fg_color=OBSIDIAN, border_color=HEXTECH_GOLD, border_width=1, hover_color=HEXTECH_GOLD, text_color=WHITE, command=self.settings_resetup).pack(pady=10, fill="x", padx=40)
        ctk.CTkButton(card, text="Delete ALL Profiles (WIPE)", height=45, font=ctk.CTkFont("Segoe UI", 13, "bold"), fg_color="#FF3333", hover_color="#990000", command=self.settings_wipe).pack(pady=10, fill="x", padx=40)

        ctk.CTkButton(card, text="RETURN", height=45, font=ctk.CTkFont("Segoe UI", 12, "bold"), fg_color="transparent", border_color="#555", border_width=1, hover_color="#222", command=self.show_home).pack(pady=(30, 0), fill="x", padx=40)

    def settings_validate(self):
        profiles = riot_logic.get_all_profiles()
        if not profiles:
            self.log_status("[DIAGNOSTICS] NO PROFILES CONFIGURED.")
            return
            
        results =[]
        for pid, data in profiles.items():
            is_valid = riot_logic.validate_saved_auth(pid, data["service"])
            if not is_valid:
                tracker_path = os.path.join(riot_logic.RIOT_CLIENT_DIR if data["service"] == "riot" else riot_logic.BNET_ROAMING_DIR, "active_profile.txt")
                try:
                    if open(tracker_path).read().strip() == pid:
                        is_valid = riot_logic.validate_active_auth(data["service"])
                except: pass
                
            status = "VALID" if is_valid else "CORRUPT/MISSING"
            results.append(f"{data['name']}: {status}")
            
        self.log_status(f"[DIAGNOSTICS] {' | '.join(results)}")

    def settings_resetup(self):
        self.show_setup_init()

    def settings_wipe(self):
        self.log_status("[SYSTEM] INITIATING WIPE PROTOCOL...")
        riot_logic.request_graceful_shutdown()
        self.after(3000, self._finish_wipe)

    def _finish_wipe(self):
        riot_logic.force_kill_all_services()
        pids = list(riot_logic.get_all_profiles().keys())
        for pid in pids: riot_logic.delete_profile(pid)
        self.log_status("[SYSTEM] DATA WIPED. RETURNED TO HOME.")
        self.show_home()

    # --- UTILS & LAUNCH LOGIC ---
    def start_pfp_pulse(self):
        def pulse():
            if not self._pulse_active: return
            current = self.pfp_border.cget("fg_color")
            self.pfp_border.configure(fg_color="#550088" if current == NEON_PURPLE else NEON_PURPLE)
            self.after(800, pulse)
        self.after(800, pulse)

    def bind_shard_hover(self, btns):
        for b in btns:
            def on_enter(e, btn=b):
                if btn.cget("state") != "disabled": btn.configure(border_color=HEXTECH_GOLD, fg_color=GLASS_HOVER if not btn.cget("image") else "transparent")
            def on_leave(e, btn=b):
                if btn.cget("state") != "disabled": btn.configure(border_color="#333344", fg_color=GLASS_PANE if not btn.cget("image") else "transparent")
            b.bind("<Enter>", on_enter)
            b.bind("<Leave>", on_leave)

    def trigger_kill_switch(self):
        self.log_status("[SYSTEM] PURGING ALL GAME SERVICES...")
        
        def kill_seq():
            riot_logic.force_kill_all_services()
            riot_logic.kill_all_third_party_apps()
            time.sleep(0.5)

        self.trigger_glitch(kill_seq, color="#FF0000")
        self.log_status("[SYSTEM] PURGE COMPLETE.")

    def switch_helper(self):
        """Immediately terminates all running helpers and launches the newly selected one."""
        selected_display = self.selected_helper.get()
        app_key = self.helper_options.get(selected_display)
        if app_key:
            self.log_status(f"[LOG] SWITCHING HELPER TO {selected_display.upper()}...")
            riot_logic.kill_all_third_party_apps()
            self.after(2000, lambda: self._relaunch_helper_finish(app_key, selected_display))

    def terminate_helpers(self):
        """Terminates all running helper applications."""
        self.log_status("[LOG] TERMINATING ALL HELPER APPS...")
        riot_logic.kill_all_third_party_apps()
        self.after(2000, lambda: self.log_status("[LOG] ALL HELPER APPS TERMINATED."))
        self.after(2000, lambda: self.log_status(f"[SYSTEM] {self.current_service.upper()} COMMAND CENTER ONLINE.")) # type: ignore
            
    def _relaunch_helper_finish(self, app_key, display_name):
        if riot_logic.launch_third_party_app(app_key):
            self.log_status(f"[LOG] {display_name.upper()} STARTED.")
            self.after(2000, lambda: self.log_status(f"[SYSTEM] {self.current_service.upper()} COMMAND CENTER ONLINE.")) # type: ignore
        else:
            self.log_status(f"[WARN] {display_name.upper()} NOT FOUND.")

    def switch_and_launch(self, pid, game):
        if self._switching: return
        self._switching = True
        for btn in getattr(self, 'shard_btns',[]): btn.configure(state="disabled", border_color="#222")

        self.log_status("[LOG] INITIATING GRACEFUL SHUTDOWN (4s FLUSH)...")
        riot_logic.request_graceful_shutdown(self.current_service)
        
        # Kill the old helpers immediately so they safely refresh on the new LoL profile swap!
        if game == "lol":
            riot_logic.kill_all_third_party_apps()
            
        self.after(4000, lambda: self._execute_swap(pid, game))

    def _execute_swap(self, pid, game):
        riot_logic.force_kill_all_services()
        self.log_status(f"[SYSTEM] INJECTING PROFILE ID: {pid}...")
        
        if not riot_logic.swap_account(pid, self.current_service):
            self._end_switch("[ERR] PROFILE DATA CORRUPTED.")
            return

        self.log_status(f"[LOG] LAUNCHING {game.upper()}...")
        riot_logic.launch_game(self.current_service, game)

        self.log_status("[LOG] WAITING FOR GAME TO INITIALIZE...")
        self.after(8000, lambda: self._launch_helper_and_finish(game))

    def _launch_helper_and_finish(self, game):
        # We ONLY restart/switch Helper Apps for League of Legends!
        if self.current_service != "bnet" and game == "lol":
            selected_display = self.selected_helper.get()
            app_key = self.helper_options.get(selected_display)
            if app_key and riot_logic.launch_third_party_app(app_key):
                self.log_status(f"[LOG] {selected_display.upper()} LAUNCHED.")
            else:
                self.log_status(f"[WARN] {selected_display.upper()} NOT FOUND.")

        self.log_status("[SYSTEM] LAUNCH SEQUENCE COMPLETE. SYSTEM IDLE.")
        self._end_switch()

    def _end_switch(self, message=None):
        self._switching = False
        for btn in getattr(self, 'shard_btns', []):
            btn.configure(state="normal")
        if message:
            self.log_status(message)

if __name__ == "__main__":
    app = RiotSwitcherApp()
    app.mainloop()