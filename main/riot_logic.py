import os
import shutil
import subprocess
import time
import asyncio
import json
import uuid
import ctypes
from ctypes import wintypes
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from third_party_apps import THIRD_PARTY_APPS

# =====================================================================
# 1. DIRECTORIES & GLOBALS
# =====================================================================
LOCAL_APP_DATA = os.getenv('LOCALAPPDATA', os.path.expanduser(r"~\AppData\Local"))
ROAMING_APP_DATA = os.getenv('APPDATA', os.path.expanduser(r"~\AppData\Roaming"))
PROGRAM_DATA = os.getenv('PROGRAMDATA', r"C:\ProgramData")

RIOVERT_DIR = os.path.join(LOCAL_APP_DATA, "Riovert")
PROFILES_FILE = os.path.join(RIOVERT_DIR, "profiles.json")
ENCRYPTION_KEY_FILE = os.path.join(RIOVERT_DIR, "encryption.key")

RIOT_GAMES_DIR = os.path.join(LOCAL_APP_DATA, "Riot Games")
RIOT_CLIENT_DIR = os.path.join(RIOT_GAMES_DIR, "Riot Client")
BNET_ROAMING_DIR = os.path.join(ROAMING_APP_DATA, "Battle.net")

_APP_PATH_CACHE = {}
_ENCRYPTION_KEY_CACHE = None

# =====================================================================
# 2. CRYPTOGRAPHY & SECURITY
# =====================================================================
class DATA_BLOB(ctypes.Structure):
    _fields_ =[("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_byte))]

def _dpapi_encrypt(data: bytes) -> bytes:
    CryptProtectData = ctypes.windll.crypt32.CryptProtectData
    data_in = DATA_BLOB(len(data), ctypes.cast(data, ctypes.POINTER(ctypes.c_byte))) # type: ignore
    data_out = DATA_BLOB()
    if CryptProtectData(ctypes.byref(data_in), None, None, None, None, 0, ctypes.byref(data_out)):
        result = ctypes.string_at(data_out.pbData, data_out.cbData)
        ctypes.windll.kernel32.LocalFree(data_out.pbData)
        return result
    return b""

def _dpapi_decrypt(data: bytes) -> bytes:
    CryptUnprotectData = ctypes.windll.crypt32.CryptUnprotectData
    data_in = DATA_BLOB(len(data), ctypes.cast(data, ctypes.POINTER(ctypes.c_byte))) # type: ignore
    data_out = DATA_BLOB()
    if CryptUnprotectData(ctypes.byref(data_in), None, None, None, None, 0, ctypes.byref(data_out)):
        result = ctypes.string_at(data_out.pbData, data_out.cbData)
        ctypes.windll.kernel32.LocalFree(data_out.pbData)
        return result
    return b""

def _get_encryption_key():
    global _ENCRYPTION_KEY_CACHE
    if _ENCRYPTION_KEY_CACHE: return _ENCRYPTION_KEY_CACHE
    os.makedirs(RIOVERT_DIR, exist_ok=True)
    if os.path.exists(ENCRYPTION_KEY_FILE):
        try:
            with open(ENCRYPTION_KEY_FILE, "rb") as f:
                decrypted_key = _dpapi_decrypt(f.read())
                if decrypted_key:
                    _ENCRYPTION_KEY_CACHE = decrypted_key
                    return decrypted_key
        except: pass 

    new_key = Fernet.generate_key()
    with open(ENCRYPTION_KEY_FILE, "wb") as f:
        f.write(_dpapi_encrypt(new_key))
    _ENCRYPTION_KEY_CACHE = new_key
    return new_key

def _process_folder_encryption(folder_path, encrypt=True):
    """Encrypts or decrypts all sensitive files in a directory."""
    fernet = Fernet(_get_encryption_key())
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file != "active_profile.txt" and file.endswith(('.yaml', '.yml', '.json', '.config')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "rb") as f: data = f.read()
                    processed_data = fernet.encrypt(data) if encrypt else fernet.decrypt(data)
                    with open(file_path, "wb") as f: f.write(processed_data)
                except: pass

def setup_profiles_folder():
    os.makedirs(RIOVERT_DIR, exist_ok=True)
    if not os.path.exists(PROFILES_FILE):
        with open(PROFILES_FILE, "w") as f: json.dump({}, f)

# =====================================================================
# 3. PROCESS MANAGEMENT (KILLERS)
# =====================================================================
def _bulk_taskkill(process_names, force=True):
    if not process_names: return
    args = ["taskkill"] + (["/F"] if force else [])
    for p in process_names: args.extend(["/IM", p])
    subprocess.run(args, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)

async def force_kill_all_services():
    """Aggressively force-kills everything related to Riot or Bnet."""
    _bulk_taskkill([
        "RiotClientServices.exe", "RiotClientCrashHandler.exe", "RiotClientUx.exe", 
        "RiotClientUxRender.exe", "LeagueClient.exe", "LeagueClientUx.exe", "VALORANT.exe",
        "Battle.net.exe", "Agent.exe", "Overwatch.exe"
    ], force=True)
    await asyncio.sleep(1.0) 

async def request_graceful_shutdown(service):
    """Sends a soft-close signal so SQLite DBs save tokens before hard-killing."""
    targets =[]
    if service == "riot": targets =["RiotClientServices.exe", "LeagueClient.exe", "RiotClientUx.exe", "VALORANT.exe"]
    elif service == "bnet": targets =["Battle.net.exe"]
    _bulk_taskkill(targets, force=False)
    await asyncio.sleep(2.0)

async def kill_helpers(app_key=None):
    """Kills a specific helper, or ALL helpers if left blank."""
    exes_to_kill = set()
    if app_key:
        config = THIRD_PARTY_APPS.get(app_key.lower())
        if config: exes_to_kill.update(config.get("exe_names",[]))
    else:
        for config in THIRD_PARTY_APPS.values():
            exes_to_kill.update(config.get("exe_names",[]))
            
    _bulk_taskkill(list(exes_to_kill), force=True)
    await asyncio.sleep(1.0)

# =====================================================================
# 4. REGISTRY MANAGEMENT & VALIDATION
# =====================================================================
def get_all_profiles():
    try:
        with open(PROFILES_FILE, "r") as f: return json.load(f)
    except: return {}

def get_profiles_by_service(service):
    return {k: v for k, v in get_all_profiles().items() if v.get("service") == service}

def delete_profile(pid):
    profiles = get_all_profiles()
    if pid not in profiles: return

    service = profiles[pid]["service"]
    target = os.path.join(RIOT_GAMES_DIR, f"Riot Client_{pid}") if service == "riot" else os.path.join(ROAMING_APP_DATA, f"Battle.net_{pid}")
        
    if os.path.exists(target): shutil.rmtree(target, ignore_errors=True)
    del profiles[pid]
    with open(PROFILES_FILE, "w") as f: json.dump(profiles, f, indent=4)

def validate_saved_profile(pid):
    """Diagnostics tool to verify if a stored backup is healthy."""
    profiles = get_all_profiles()
    if pid not in profiles: return False
    service = profiles[pid]["service"]
    
    if service == "riot":
        yaml = os.path.join(RIOT_GAMES_DIR, f"Riot Client_{pid}", "Data", "RiotGamesPrivateSettings.yaml")
        return os.path.exists(yaml) and os.path.getsize(yaml) >= 1500
    else:
        config = os.path.join(ROAMING_APP_DATA, f"Battle.net_{pid}", "Battle.net.config")
        return os.path.exists(config) and os.path.getsize(config) >= 500

def validate_active_auth(service):
    """Checks if the currently active profile/auth is valid."""
    active_dir = RIOT_CLIENT_DIR if service == "riot" else BNET_ROAMING_DIR
    
    if service == "riot":
        yaml = os.path.join(active_dir, "Data", "RiotGamesPrivateSettings.yaml")
        return os.path.exists(yaml) and os.path.getsize(yaml) >= 1500
    else:
        config = os.path.join(active_dir, "Battle.net.config")
        return os.path.exists(config) and os.path.getsize(config) >= 500

def launch_third_party_app(app_key):
    """Locates and launches a third-party app."""
    app_key = app_key.lower()
    if app_key in _APP_PATH_CACHE and os.path.exists(_APP_PATH_CACHE[app_key]):
        os.startfile(_APP_PATH_CACHE[app_key])
        return True

    app_config = THIRD_PARTY_APPS.get(app_key)
    if not app_config: return False

    for path in app_config.get("exact_paths",[]):
        if os.path.exists(path):
            _APP_PATH_CACHE[app_key] = path
            os.startfile(path)
            return True

    search_roots =[os.getenv('ProgramFiles'), os.getenv('ProgramFiles(x86)'), LOCAL_APP_DATA]
    for root in filter(None, search_roots):
        try:
            for r, _, files in os.walk(root):
                for f in files:
                    if f.lower().endswith('.exe') and any(t in f.lower() for t in app_config.get("search_terms",[])):
                        path = os.path.join(r, f)
                        _APP_PATH_CACHE[app_key] = path
                        os.startfile(path)
                        return True
        except: continue
    return False

def save_profile(pid, name, service, game, rank, region=""):
    profiles = get_all_profiles()
    profiles[pid] = {
        "name": name,
        "service": service,
        "game": game,
        "rank": rank,
        "region": region
    }
    with open(PROFILES_FILE, "w") as f:
        json.dump(profiles, f, indent=4)

# =====================================================================
# 5. SETUP WIZARD (ADDING PROFILES)
# =====================================================================
def _get_client_path(service):
    if service == "riot":
        path = r"C:\Riot Games\Riot Client\RiotClientServices.exe"
        install_file = os.path.join(PROGRAM_DATA, "Riot Games", "RiotClientInstalls.json")
        if os.path.exists(install_file):
            try: path = json.load(open(install_file)).get("rc_default", path)
            except: pass
        return path
    else:
        for p in[r"C:\Program Files (x86)\Battle.net\Battle.net.exe", r"C:\Program Files\Battle.net\Battle.net.exe"]:
            if os.path.exists(p): return p
        return ""

async def prepare_fresh_client(service):
    """Safely stashes active session and opens a fresh login screen."""
    await force_kill_all_services()
    
    active_dir = RIOT_CLIENT_DIR if service == "riot" else BNET_ROAMING_DIR
    parent_dir = RIOT_GAMES_DIR if service == "riot" else ROAMING_APP_DATA
    prefix = "Riot Client" if service == "riot" else "Battle.net"

    if os.path.exists(active_dir):
        tracker = os.path.join(active_dir, "active_profile.txt")
        current_id = open(tracker, "r").read().strip() if os.path.exists(tracker) else f"unknown_{int(time.time())}"
        
        _process_folder_encryption(active_dir, encrypt=True)
        os.rename(active_dir, os.path.join(parent_dir, f"{prefix}_{current_id}"))

    subprocess.Popen([_get_client_path(service)])

async def validate_and_capture_profile(name, service, game, rank, region=""):
    """Validates the login token. If successful, encrypts and saves it. Returns new PID on success."""
    await force_kill_all_services()
    
    active_dir = RIOT_CLIENT_DIR if service == "riot" else BNET_ROAMING_DIR
    parent_dir = RIOT_GAMES_DIR if service == "riot" else ROAMING_APP_DATA
    prefix = "Riot Client" if service == "riot" else "Battle.net"

    is_valid = False
    if service == "riot":
        yaml = os.path.join(active_dir, "Data", "RiotGamesPrivateSettings.yaml")
        is_valid = os.path.exists(yaml) and os.path.getsize(yaml) >= 1500
    else:
        config = os.path.join(active_dir, "Battle.net.config")
        is_valid = os.path.exists(config) and os.path.getsize(config) >= 500

    if not is_valid: return None 

    pid = str(uuid.uuid4())[:8]
    target_backup = os.path.join(parent_dir, f"{prefix}_{pid}")
    
    _process_folder_encryption(active_dir, encrypt=True)
    os.rename(active_dir, target_backup)
    with open(os.path.join(target_backup, "active_profile.txt"), "w") as f: f.write(pid)

    profiles = get_all_profiles()
    profiles[pid] = {"name": name, "service": service, "game": game, "rank": rank, "region": region}
    with open(PROFILES_FILE, "w") as f: json.dump(profiles, f, indent=4)
    return pid

# =====================================================================
# 6. DYNAMIC PLAY ENGINE
# =====================================================================
async def _execute_folder_swap(pid, service):
    active_dir = RIOT_CLIENT_DIR if service == "riot" else BNET_ROAMING_DIR
    parent_dir = RIOT_GAMES_DIR if service == "riot" else ROAMING_APP_DATA
    prefix = "Riot Client" if service == "riot" else "Battle.net"
    target_backup = os.path.join(parent_dir, f"{prefix}_{pid}")

    if os.path.exists(active_dir):
        tracker = os.path.join(active_dir, "active_profile.txt")
        current_id = open(tracker, "r").read().strip() if os.path.exists(tracker) else f"unknown_{int(time.time())}"
        _process_folder_encryption(active_dir, encrypt=True)
        os.rename(active_dir, os.path.join(parent_dir, f"{prefix}_{current_id}"))

    if os.path.exists(target_backup):
        os.rename(target_backup, active_dir)
        _process_folder_encryption(active_dir, encrypt=False)
        await asyncio.sleep(0.5) 
    else:
        os.makedirs(active_dir, exist_ok=True)
        
    with open(os.path.join(active_dir, "active_profile.txt"), "w") as f: f.write(pid)
    return True

async def play_profile(pid, helper_app_key=None, status_callback=None):
    """THE MASTER ENGINE."""
    def log(msg):
        if status_callback: status_callback(msg)

    profiles = get_all_profiles()
    if pid not in profiles:
        log("[ERR] PROFILE NOT FOUND IN REGISTRY.")
        return False
        
    profile = profiles[pid]
    service = profile["service"]
    game = profile["game"]
    name = profile["name"]

    log(f"[LOG] FLUSHING {name.upper()} TO DISK (4s)...")
    await request_graceful_shutdown(service)
    
    if game == "lol": 
        await kill_helpers() 
        
    await asyncio.sleep(4.0)

    await force_kill_all_services()
    
    log(f"[SYSTEM] INJECTING: {name.upper()}...")
    await _execute_folder_swap(pid, service)

    log(f"[LOG] LAUNCHING {game.upper()}...")
    client_path = _get_client_path(service)
    args = []
    if game == "valorant": args =["--launch-product=valorant", "--launch-patchline=live"]
    elif game == "lol": args =["--launch-product=league_of_legends", "--launch-patchline=live"]
    elif game == "overwatch": args = ["--exec=launch Pro"]
    
    subprocess.Popen([client_path] + args, cwd=os.path.dirname(client_path))

    if game == "lol" and helper_app_key:
        log("[LOG] WAITING FOR GAME INITIALIZATION (8s)...")
        await asyncio.sleep(8.0)
        
        app_config = THIRD_PARTY_APPS.get(helper_app_key.lower())
        display_name = app_config.get("display", helper_app_key) if app_config else helper_app_key
        
        if launch_third_party_app(helper_app_key):
            log(f"[LOG] {display_name.upper()} LAUNCHED.")
        else:
            log(f"[WARN] {display_name.upper()} EXECUTABLE NOT FOUND.")

    log("[SYSTEM] SEQUENCE COMPLETE. SYSTEM IDLE.")
    return True
