import os

# --- ENVIRONMENT PATH BUILDERS ---
# Automatically resolves paths regardless of the user's Windows drive letter or username
PF = os.getenv('ProgramFiles', r"C:\Program Files")
PF86 = os.getenv('ProgramFiles(x86)', r"C:\Program Files (x86)")
LOCAL_APPDATA = os.getenv('LOCALAPPDATA', os.path.expanduser(r"~\AppData\Local"))
ROAMING_APPDATA = os.getenv('APPDATA', os.path.expanduser(r"~\AppData\Roaming"))
DESKTOP = os.path.expanduser(r"~\Desktop")
START_MENU = os.path.join(ROAMING_APPDATA, r"Microsoft\Windows\Start Menu\Programs")

# Overwolf Core Processes (Killed alongside any app that depends on Overwolf)
OVERWOLF_EXES =[
    "Overwolf.exe", 
    "OverwolfBrowser.exe", 
    "OverwolfHelper.exe", 
    "OverwolfUpdater.exe",
    "OWExplorer.exe"
]

THIRD_PARTY_APPS = {
    # --- POROFESSOR ---
    "porofessor_standalone": {
        "display": "Porofessor (Standalone)",
        "search_terms": ["porofessor standalone"],
        "exe_names": ["Porofessor Standalone.exe", "Porofessor.exe"],
        "exact_paths":[
            os.path.join(LOCAL_APPDATA, "Porofessor", "Porofessor.exe"),
            os.path.join(PF, "Porofessor Standalone", "Porofessor Standalone.exe"),
            os.path.join(PF86, "Porofessor Standalone", "Porofessor Standalone.exe"),
        ],
    },
    "porofessor_overwolf": {
        "display": "Porofessor (Overwolf)",
        "search_terms":["porofessor", "porofessor for overwolf"],
        "exe_names": ["Porofessor for Overwolf.exe"] + OVERWOLF_EXES,
        "exact_paths":[
            # Overwolf apps are typically launched securely via their shortcuts
            os.path.join(DESKTOP, "Porofessor.lnk"),
            os.path.join(DESKTOP, "Porofessor for Overwolf.lnk"),
            os.path.join(START_MENU, "Porofessor.lnk"),
            os.path.join(START_MENU, "Porofessor for Overwolf.lnk"),
        ],
    },

    # --- MOBALYTICS ---
    "mobalytics_standalone": {
        "display": "Mobalytics (Standalone)",
        "search_terms": ["mobalytics desktop"],
        "exe_names":["Mobalytics.exe", "Mobalytics Desktop.exe"],
        "exact_paths":[
            os.path.join(LOCAL_APPDATA, "Mobalytics", "Mobalytics.exe"),
            os.path.join(PF, "Mobalytics", "Mobalytics.exe"),
            os.path.join(PF86, "Mobalytics", "Mobalytics.exe"),
        ],
    },
    "mobalytics_overwolf": {
        "display": "Mobalytics (Overwolf)",
        "search_terms": ["mobalytics"],
        "exe_names": ["Mobalytics.exe"] + OVERWOLF_EXES,
        "exact_paths":[
            os.path.join(DESKTOP, "Mobalytics.lnk"),
            os.path.join(START_MENU, "Overwolf", "Mobalytics.lnk"),
        ],
    },

    # --- OP.GG ---
    "opgg": {
        "display": "OP.GG Desktop",
        "search_terms": ["op.gg", "opgg"],
        "exe_names": ["OP.GG.exe"],
        "exact_paths":[
            os.path.join(LOCAL_APPDATA, "Programs", "OP.GG", "OP.GG.exe"),
            os.path.join(PF, "OP.GG", "OP.GG.exe"),
            os.path.join(PF86, "OP.GG", "OP.GG.exe"),
        ],
    },

    # --- BLITZ ---
    "blitz": {
        "display": "Blitz.gg",
        "search_terms": ["blitz"],
        "exe_names":["Blitz.exe"],
        "exact_paths":[
            os.path.join(LOCAL_APPDATA, "Programs", "Blitz", "Blitz.exe"),
            os.path.join(PF, "Blitz", "Blitz.exe"),
            os.path.join(PF86, "Blitz", "Blitz.exe"),
        ],
    },

    # --- U.GG ---
    "ugg_standalone": {
        "display": "U.GG (Standalone)",
        "search_terms":["u.gg", "ugg"],
        "exe_names": ["u.gg.exe", "UGG.exe"],
        "exact_paths":[
            os.path.join(LOCAL_APPDATA, "Programs", "u.gg", "u.gg.exe"),
            os.path.join(PF, "u.gg", "u.gg.exe"),
            os.path.join(PF86, "u.gg", "u.gg.exe"),
        ],
    },
    "ugg_overwolf": {
        "display": "U.GG (Overwolf)",
        "search_terms": ["u.gg", "ugg"],
        "exe_names": ["u.gg.exe"] + OVERWOLF_EXES,
        "exact_paths":[
            os.path.join(DESKTOP, "U.GG.lnk"),
            os.path.join(START_MENU, "Overwolf", "U.GG.lnk"),
        ],
    },

    # --- LEAGUE OF GRAPHS ---
    "leagueofgraphs": {
        "display": "League of Graphs",
        "search_terms":["league of graphs", "leagueofgraphs"],
        "exe_names": ["League of Graphs.exe"],
        "exact_paths":[
            os.path.join(LOCAL_APPDATA, "Programs", "League of Graphs", "League of Graphs.exe"),
        ],
    },

    # --- VALORANT TRACKER (OVERWOLF) ---
    "valorant_tracker_overwolf": {
        "display": "Valorant Tracker (Overwolf)",
        "search_terms": ["valorant tracker", "tracker.gg"],
        "exe_names": ["Valorant Tracker.exe", "Tracker.gg.exe"] + OVERWOLF_EXES,
        "exact_paths":[
            os.path.join(DESKTOP, "Valorant Tracker.lnk"),
            os.path.join(START_MENU, "Overwolf", "Valorant Tracker.lnk"),
            os.path.join(DESKTOP, "Tracker.gg.lnk"),
        ],
    }
}