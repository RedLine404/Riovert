# Riovert

### High-Performance Riot Games & Battle.net Profile Orchestrator

Riovert is a sophisticated profile management utility built with Python, featuring a custom **Hextech-Cyber** aesthetic and **Glassmorphism** UI. It automates the complex process of switching accounts for Riot Games and Battle.net by managing authentication tokens and system-level processes.

---

## 💎 Technical Showcases
* **Stateful UI Transitions:** Custom "Glitch" overlay transitions during frame swaps for a premium, immersive feel.
* **Orchestration Logic:** Handles graceful shutdowns (4s flush) and forced purges of game services to prevent account data corruption.
* **Asset Bundling:** Implements `sys._MEIPASS` resource routing to ensure a portable, single-file `.exe` experience.
* **Secure Wizard Workflow:** A multi-step setup wizard that validates account authentication state before saving to disk.

---

## 🚀 Key Features
* **Secure Profile Switching:** Uses robust cryptographic methods to manage and switch between Riot Games & Battle.net accounts securely.
* **Modern UI/UX:** A bespoke interface built with `customtkinter`, utilizing transparency and modern design patterns for a high-end user experience.
* **Process Orchestration:** Instantly manages background game processes (e.g., "Terminate All" logic) to ensure a clean state for profile transitions.
* **Image Processing:** Efficient handling of assets and UI elements via `Pillow`.
* **Whitelisting Logic:** Granular control over which processes remain active during system optimization.

---

## 🛠️ Technical Stack
* **Language:** Python
* **UI Framework:** customtkinter (Glassmorphism & Hextech-Cyber theme)
* **Security:** cryptography (Secure credential and state management)
* **Imaging:** Pillow (PIL)
* **Packaging:** PyInstaller

---

## 📖 How to use
1. Open Riovert
2. Select the type of account(s) you want to set up (Riot Games and/or Battle.net)
3. Select how many accounts for each client service (Riot Games - Battle.net)
4. The specified client will open automatically.
5. CRITICAL: Check 'Stay Signed In' box, and sign-in to each of your accounts respecivly as prompted in Riovert.
6. Close the client manually (press the "X" button), and close it from the system tray & Task Manager.
7. Fill info as prompted in Riovert & Click "Complete".
8. Riovert will handle everthing from there.
9. Repeat this process until you have all of your specified accounts set up (if more than one account).

---

## 📦 Installation for Developers
1. Clone the repository:
   ```bash
   git clone [https://github.com/](https://github.com/)[Your-GitHub-Username]/riovert.git
   ```
2. Move to Riovert's directory
   ```bash
   cd riovert
   ```
3. Install requirements
   ```bash
   pip install -r requirements.txt
   ```

---

## 📥 For Users (Standalone)
If you just want to use the application without setting up a Python environment, download the latest version from the Releases section. The executable is standalone and contains all necessary components.

---

**Note:** This project is intended for educational and personal use. Ensure compliance with all Third-Party Terms of Service.

---

# Riovert: The "Glass-Hex" Update (v1.2.1)

Riovert has officially evolved from a single-service background utility into a premium, AAA-grade multi-platform profile manager. We completely stripped out the old blocking architecture and grey-box interfaces, replacing them with a fully asynchronous engine and a stunning, custom-built UI.

## 🚀 What's New in v1.2.1

### 🌍 Multi-Platform Expansion
* **Battle.net (Overwatch) Support:** Riovert is no longer just for Riot Games. We have engineered a brand new file-swapping pipeline for Blizzard's Battle.net, allowing seamless switching between Overwatch accounts alongside your Valorant and League of Legends profiles.
* **Smart Helper App Integration:** The app now dynamically detects and manages third-party helpers (Porofessor, OP.GG, Mobalytics, U.GG, Blitz). It will automatically launch, restart, or cleanly terminate both standalone and Overwolf-based helpers depending on the active game, preventing cross-account API contamination.

### 🎨 The "Glass-Hex" UI Overhaul
We completely migrated the frontend to **Flet (Flutter)** to deliver a true AAA game launcher experience.
* **Glassmorphism & Depth:** Replaced flat backgrounds with true Z-axis stacking. UI cards now use mathematically blurred, frosted-acrylic panes (`ft.Blur`) that dynamically distort the cyberpunk wallpaper behind them.
* **Micro-Animations:** Added buttery-smooth, implicit hover animations. Cards scale up with an ease-out-back bounce and emit a Hextech Gold / Neon Purple drop-shadow glow when hovered.
* **Frameless Immersion:** Stripped away the default Windows OS title bar in favor of a custom, draggable glass header, making the app feel like a native gaming client.
* **The "Terminal Ticker":** A persistent status bar at the bottom of the screen that logs real-time system events (e.g., `> [SYSTEM] FLUSHING LEAGUE EUW TO DISK (4s)...`) without breaking immersion.

### ⚙️ Asynchronous Backend Engine
* **Zero UI Freezing:** The backend was entirely rewritten using Python's `asyncio`. Complex folder swaps, SQLite database flushing, and process terminations no longer block the main thread. The UI remains completely fluid, and loading states render perfectly while the backend does the heavy lifting.
* **The "Soft-Flush" Pipeline:** Fixed an issue where force-killing Riot/Battle.net caused session corruption. Riovert now sends a graceful shutdown signal, asynchronously waits 4 seconds for the SQLite databases to safely commit your cookies to the disk, and *then* drops a hard `taskkill` to unlock the folders.

### 🛡️ Military-Grade DPAPI Security
Session tokens bypass Two-Factor Authentication (2FA), so we completely upgraded how Riovert protects them.
* **Machine-Tied Encryption:** Instead of storing plaintext keys, Riovert now generates a secure AES-256 (Fernet) key and passes it directly to the Windows OS using **Data Protection API (DPAPI)** via `ctypes`.
* **The Result:** The encryption key is mathematically locked to your specific Windows Login Credentials. Even if a bad actor steals your Riovert `AppData` directory and moves it to another PC, the session tokens are impossible to decrypt. 

### 🛠️ Quality of Life
* **The Setup Wizard:** A completely automated, UI-driven loop that guides you through adding new accounts. Just log in normally, and Riovert captures, encrypts, and vaults the session in the background.
* **Diagnostics Dashboard:** Added a new Settings page to instantly validate encrypted tokens, wipe corrupted files, or cleanly factory-reset the entire Riovert ecosystem.
* **Single .exe Compilation:** The app is now fully bundled via `flet pack`, embedding all assets natively so it can run flawlessly on any Windows machine as a single, portable executable.