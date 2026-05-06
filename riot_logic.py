import os
import shutil
import subprocess
import time
import json
import uuid
import ctypes
from ctypes import wintypes
from third_party_apps import THIRD_PARTY_APPS
from cryptography.fernet import Fernet, InvalidToken

# --- PATHS & DIRECTORIES ---
LOCAL_APP_DATA = os.getenv('LOCALAPPDATA', os.path.expanduser(r"~\AppData\Local"))
ROAMING_APP_DATA = os.getenv('APPDATA', os.path.expanduser(r"~\AppData\Roaming"))
PROGRAM_DATA = os.getenv('PROGRAMDATA', r"C:\ProgramData")

RIOVERT_DIR = os.path.join(LOCAL_APP_DATA, "Riovert")
PROFILES_FILE = os.path.join(RIOVERT_DIR, "profiles.json")
ENCRYPTION_KEY_FILE = os.path.join(RIOVERT_DIR, "encryption.key")

RIOT_GAMES_DIR = os.path.join(LOCAL_APP_DATA, "Riot Games")
RIOT_CLIENT_DIR = os.path.join(RIOT_GAMES_DIR, "Riot Client")
BNET_ROAMING_DIR = os.path.join(ROAMING_APP_DATA, "Battle.net")

# --- PERFORMANCE CACHES ---
_APP_PATH_CACHE = {}
_RIOT_PATH_CACHE = None
_BNET_PATH_CACHE = None
_ENCRYPTION_KEY_CACHE = None

# --- WINDOWS DPAPI (DATA PROTECTION API) ---
class DATA_BLOB(ctypes.Structure):
    _fields_ =[("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_byte))]

def dpapi_encrypt(data: bytes) -> bytes:
    """Encrypts data using the current Windows User Account credentials."""
    CryptProtectData = ctypes.windll.crypt32.CryptProtectData
    data_in = DATA_BLOB(len(data), ctypes.cast(data, ctypes.POINTER(ctypes.c_byte))) # type: ignore
    data_out = DATA_BLOB()
    if CryptProtectData(ctypes.byref(data_in), None, None, None, None, 0, ctypes.byref(data_out)):
        result = ctypes.string_at(data_out.pbData, data_out.cbData)
        ctypes.windll.kernel32.LocalFree(data_out.pbData)
        return result
    return b""

def dpapi_decrypt(data: bytes) -> bytes:
    """Decrypts data. Fails if attempted by a different Windows user or on a different PC."""
    CryptUnprotectData = ctypes.windll.crypt32.CryptUnprotectData
    data_in = DATA_BLOB(len(data), ctypes.cast(data, ctypes.POINTER(ctypes.c_byte))) # type: ignore
    data_out = DATA_BLOB()
    if CryptUnprotectData(ctypes.byref(data_in), None, None, None, None, 0, ctypes.byref(data_out)):
        result = ctypes.string_at(data_out.pbData, data_out.cbData)
        ctypes.windll.kernel32.LocalFree(data_out.pbData)
        return result
    return b""

# --- ENCRYPTION FUNCTIONS ---
def get_encryption_key():
    """Generates a secure random key and protects it with Windows DPAPI."""
    global _ENCRYPTION_KEY_CACHE
    if _ENCRYPTION_KEY_CACHE:
        return _ENCRYPTION_KEY_CACHE

    os.makedirs(RIOVERT_DIR, exist_ok=True)

    # 1. Try to load and decrypt an existing key
    if os.path.exists(ENCRYPTION_KEY_FILE):
        try:
            with open(ENCRYPTION_KEY_FILE, "rb") as f:
                encrypted_key = f.read()
                decrypted_key = dpapi_decrypt(encrypted_key)
                if decrypted_key:
                    _ENCRYPTION_KEY_CACHE = decrypted_key
                    return decrypted_key
        except:
            pass # If decryption fails (e.g. moved to a new PC), we generate a new one

    new_key = Fernet.generate_key()
    encrypted_new_key = dpapi_encrypt(new_key)
    with open(ENCRYPTION_KEY_FILE, "wb") as f:
        f.write(encrypted_new_key)

    _ENCRYPTION_KEY_CACHE = new_key
    return new_key

def encrypt_file(file_path):
    try:
        fernet = Fernet(get_encryption_key())
        with open(file_path, "rb") as f:
            data = f.read()
        encrypted_data = fernet.encrypt(data)
        with open(file_path, "wb") as f:
            f.write(encrypted_data)
        return True
    except:
        return False

def decrypt_file(file_path):
    try:
        fernet = Fernet(get_encryption_key())
        with open(file_path, "rb") as f:
            encrypted_data = f.read()
        decrypted_data = fernet.decrypt(encrypted_data)
        with open(file_path, "wb") as f:
            f.write(decrypted_data)
        return True
    except InvalidToken:
        # File wasn't encrypted, ignore it
        return False
    except Exception:
        return False

def encrypt_sensitive_files(folder_path):
    """Encrypts ALL files in the backup to ensure SQLite Cookies are protected."""
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # We must leave the tracker file readable so the UI knows who it belongs to
            if file != "active_profile.txt":
                file_path = os.path.join(root, file)
                encrypt_file(file_path)

def decrypt_sensitive_files(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file != "active_profile.txt":
                file_path = os.path.join(root, file)
                decrypt_file(file_path)

def setup_profiles_folder():
    os.makedirs(RIOVERT_DIR, exist_ok=True)
    if not os.path.exists(PROFILES_FILE):
        with open(PROFILES_FILE, "w") as f:
            json.dump({}, f)

# --- PROFILE REGISTRY MANAGEMENT ---
def get_all_profiles():
    if not os.path.exists(PROFILES_FILE): return {}
    try:
        with open(PROFILES_FILE, "r") as f: return json.load(f)
    except: return {}

def get_profiles_by_service(service):
    profiles = get_all_profiles()
    return {k: v for k, v in profiles.items() if v.get("service") == service}

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

def delete_profile(pid):
    profiles = get_all_profiles()
    if pid in profiles:
        service = profiles[pid].get("service")
        if service == "riot":
            target = os.path.join(RIOT_GAMES_DIR, f"Riot Client_{pid}")
            if os.path.exists(target): shutil.rmtree(target, ignore_errors=True)
        elif service == "bnet":
            target = os.path.join(ROAMING_APP_DATA, f"Battle.net_{pid}")
            if os.path.exists(target): shutil.rmtree(target, ignore_errors=True)
            
        del profiles[pid]
        with open(PROFILES_FILE, "w") as f:
            json.dump(profiles, f, indent=4)

# --- PROCESS MANAGEMENT ---
def _bulk_taskkill(process_names, force=True):
    if not process_names: return
    args = ["taskkill"]
    if force: args.append("/F")
    for p in process_names:
        args.extend(["/IM", p])
    subprocess.run(args, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)

def force_kill_all_services():
    _bulk_taskkill([
        "RiotClientServices.exe", "RiotClientCrashHandler.exe", "RiotClientUx.exe", 
        "RiotClientUxRender.exe", "RiotClientUxHelper.exe", "LeagueClient.exe", 
        "LeagueClientUx.exe", "VALORANT.exe",
        "Battle.net.exe", "Agent.exe", "Overwatch.exe"
    ], force=True)
    time.sleep(1.0)

def request_graceful_shutdown(service=None):
    targets =[]
    if service in [None, "riot"]:
        targets.extend(["RiotClientServices.exe", "LeagueClient.exe", "RiotClientUx.exe", "VALORANT.exe"])
    if service in [None, "bnet"]:
        targets.extend(["Battle.net.exe"])
    _bulk_taskkill(targets, force=False)

# --- LAUNCH PATH LOCATORS ---
def get_riot_client_path():
    global _RIOT_PATH_CACHE
    if _RIOT_PATH_CACHE and os.path.exists(_RIOT_PATH_CACHE): return _RIOT_PATH_CACHE
    installs_file = os.path.join(PROGRAM_DATA, "Riot Games", "RiotClientInstalls.json")
    default_path = r"C:\Riot Games\Riot Client\RiotClientServices.exe"
    if os.path.exists(installs_file):
        try:
            with open(installs_file, "r") as f:
                _RIOT_PATH_CACHE = json.load(f).get("rc_default", default_path)
                return _RIOT_PATH_CACHE
        except: pass
    return default_path

def get_bnet_client_path():
    global _BNET_PATH_CACHE
    if _BNET_PATH_CACHE and os.path.exists(_BNET_PATH_CACHE): return _BNET_PATH_CACHE
    common_paths =[
        r"C:\Program Files (x86)\Battle.net\Battle.net.exe",
        r"C:\Program Files\Battle.net\Battle.net.exe"
    ]
    for p in common_paths:
        if os.path.exists(p):
            _BNET_PATH_CACHE = p
            return p
    return common_paths[0] 

def safe_rename(src, dst, retries=3):
    for _ in range(retries):
        try:
            if os.path.exists(dst):
                shutil.rmtree(dst, ignore_errors=True)
                time.sleep(0.1)
            os.rename(src, dst)
            return True
        except PermissionError:
            time.sleep(0.2) 
    return False

# --- FOLDER SWAPPING LOGIC ---
def _stash_active_folder(active_dir, backup_prefix, parent_dir):
    if os.path.exists(active_dir):
        tracker = os.path.join(active_dir, "active_profile.txt")
        if os.path.exists(tracker):
            with open(tracker, "r") as f:
                current_profile = f.read().strip()
            backup = os.path.join(parent_dir, f"{backup_prefix}_{current_profile}")
        else:
            backup = os.path.join(parent_dir, f"{backup_prefix}_unknown_{int(time.time())}")

        encrypt_sensitive_files(active_dir)
        safe_rename(active_dir, backup)

def swap_account(pid, service):
    if service == "riot":
        target_backup = os.path.join(RIOT_GAMES_DIR, f"Riot Client_{pid}")
        _stash_active_folder(RIOT_CLIENT_DIR, "Riot Client", RIOT_GAMES_DIR)

        if os.path.exists(target_backup):
            safe_rename(target_backup, RIOT_CLIENT_DIR)
            decrypt_sensitive_files(RIOT_CLIENT_DIR)
            time.sleep(0.5)  # <--- Added: Lets Windows flush file locks to disk!
        else:
            os.makedirs(RIOT_CLIENT_DIR, exist_ok=True)

        with open(os.path.join(RIOT_CLIENT_DIR, "active_profile.txt"), "w") as f: f.write(pid)
        return True

    elif service == "bnet":
        target_backup = os.path.join(ROAMING_APP_DATA, f"Battle.net_{pid}")
        _stash_active_folder(BNET_ROAMING_DIR, "Battle.net", ROAMING_APP_DATA)

        if os.path.exists(target_backup):
            safe_rename(target_backup, BNET_ROAMING_DIR)
            decrypt_sensitive_files(BNET_ROAMING_DIR)
            time.sleep(0.5)  # <--- Added: Lets Windows flush file locks to disk!
        else:
            os.makedirs(BNET_ROAMING_DIR, exist_ok=True)

        with open(os.path.join(BNET_ROAMING_DIR, "active_profile.txt"), "w") as f: f.write(pid)
        return True
    return False

def launch_game(service, game):
    if service == "riot":
        riot_path = get_riot_client_path()
        args =["--launch-product=valorant", "--launch-patchline=live"] if game == "valorant" else["--launch-product=league_of_legends", "--launch-patchline=live"]
        subprocess.Popen([riot_path] + args, cwd=os.path.dirname(riot_path))
    elif service == "bnet":
        bnet_path = get_bnet_client_path()
        args =["--exec=launch Pro"] if game == "overwatch" else[]
        subprocess.Popen([bnet_path] + args, cwd=os.path.dirname(bnet_path))

# --- SETUP & CAPTURE LOGIC ---
def prepare_setup(service):
    force_kill_all_services()
    if service == "riot":
        _stash_active_folder(RIOT_CLIENT_DIR, "Riot Client", RIOT_GAMES_DIR)
        subprocess.Popen([get_riot_client_path()])
    elif service == "bnet":
        _stash_active_folder(BNET_ROAMING_DIR, "Battle.net", ROAMING_APP_DATA)
        subprocess.Popen([get_bnet_client_path()])

def capture_target_profile(pid, service):
    force_kill_all_services()
    if service == "riot":
        target_backup = os.path.join(RIOT_GAMES_DIR, f"Riot Client_{pid}")
        if os.path.exists(target_backup): shutil.rmtree(target_backup, ignore_errors=True)
        if os.path.exists(RIOT_CLIENT_DIR):
            safe_rename(RIOT_CLIENT_DIR, target_backup)
            encrypt_sensitive_files(target_backup)
            os.makedirs(target_backup, exist_ok=True)
            with open(os.path.join(target_backup, "active_profile.txt"), "w") as f: f.write(pid)
    elif service == "bnet":
        target_backup = os.path.join(ROAMING_APP_DATA, f"Battle.net_{pid}")
        if os.path.exists(target_backup): shutil.rmtree(target_backup, ignore_errors=True)
        if os.path.exists(BNET_ROAMING_DIR):
            safe_rename(BNET_ROAMING_DIR, target_backup)
            encrypt_sensitive_files(target_backup)
            os.makedirs(target_backup, exist_ok=True)
            with open(os.path.join(target_backup, "active_profile.txt"), "w") as f: f.write(pid)

def validate_active_auth(service):
    if service == "riot":
        yaml_path = os.path.join(RIOT_CLIENT_DIR, "Data", "RiotGamesPrivateSettings.yaml")
        return os.path.exists(yaml_path) and os.path.getsize(yaml_path) >= 1500
    elif service == "bnet":
        config_path = os.path.join(BNET_ROAMING_DIR, "Battle.net.config")
        return os.path.exists(config_path) and os.path.getsize(config_path) >= 500
    return False

def validate_saved_auth(pid, service):
    # If the files are encrypted, checking their size is still valid because
    # Fernet encryption slightly increases file size, maintaining the size constraint logic!
    if service == "riot":
        yaml_path = os.path.join(RIOT_GAMES_DIR, f"Riot Client_{pid}", "Data", "RiotGamesPrivateSettings.yaml")
        return os.path.exists(yaml_path) and os.path.getsize(yaml_path) >= 1500
    elif service == "bnet":
        config_path = os.path.join(ROAMING_APP_DATA, f"Battle.net_{pid}", "Battle.net.config")
        return os.path.exists(config_path) and os.path.getsize(config_path) >= 500
    return False

# --- THIRD PARTY APP SUPPORT ---
def get_third_party_app_path(app_key):
    app_key = app_key.lower()
    if app_key in _APP_PATH_CACHE and os.path.exists(_APP_PATH_CACHE[app_key]): return _APP_PATH_CACHE[app_key]
    app_config = THIRD_PARTY_APPS.get(app_key)
    if not app_config: return None
    for path in app_config.get("exact_paths",[]):
        if path and os.path.exists(path):
            _APP_PATH_CACHE[app_key] = path
            return path
    search_roots =[os.getenv('ProgramFiles', r"C:\Program Files"), os.getenv('ProgramFiles(x86)', r"C:\Program Files (x86)"), os.path.expanduser(r"~\AppData\Local")]
    for root in filter(None, search_roots):
        try:
            for path_root, _, files in os.walk(root):
                for file in files:
                    lf = file.lower()
                    if lf.endswith('.exe') and any(term in lf for term in app_config.get("search_terms",[])):
                        candidate = os.path.join(path_root, file)
                        _APP_PATH_CACHE[app_key] = candidate
                        return candidate
        except Exception: continue
    return None

def kill_all_third_party_apps():
    """Bulk terminates all known helper apps dynamically by reading the config file."""
    all_exes = set()
    for app_config in THIRD_PARTY_APPS.values():
        all_exes.update(app_config.get("exe_names",[]))
        
    _bulk_taskkill(list(all_exes), force=True)
    time.sleep(1.0)

def kill_third_party_app(app_key):
    """Kills a specific app. If it's an Overwolf app, this cleanly wipes Overwolf too."""
    app_config = THIRD_PARTY_APPS.get(app_key.lower())
    if app_config:
        _bulk_taskkill(app_config.get("exe_names",[]), force=True)
        time.sleep(1.0)

def launch_third_party_app(app_key):
    app_path = get_third_party_app_path(app_key)
    if not app_path: return False
    try: os.startfile(app_path); return True
    except: return False