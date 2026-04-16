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
   cd riovert
   pip install -r requirements.txt
   ```

## 📥 For Users (Standalone)
If you just want to use the application without setting up a Python environment, download the latest version from the Releases section. The executable is standalone and contains all necessary components.

---

**Note:** This project is intended for educational and personal use. Ensure compliance with all Third-Party Terms of Service.
