# Python WhatsApp Terminal Bot 🤖

A lightweight, hybrid Python + Node.js WhatsApp bot that allows you to send automated text messages to a Person or a Group directly from your terminal. 

It generates a native ASCII QR code in your terminal to easily link your WhatsApp account without needing to open a visible browser.

## How it Works ⚙️
Because WhatsApp makes it very difficult for purely Python-based scripts to generate and read auth QR codes natively in the terminal without popping up visible browsers, this project uses a powerful **hybrid approach**:
1. **Node.js Bridge (`wa_bridge.js`)**: Runs headlessly in the background using `whatsapp-web.js`. It generates the QR code safely and natively maintains the session.
2. **Python Orchestrator (`bot.py`)**: A clean Python interface that you run and interact with. It launches the Node bridge behind the scenes, asks you for the target numbers/groups, and serves as the scheduler.

## Prerequisites 📋
To run this project, you will need the following installed on your machine:
- **Node.js** (v18 or newer recommended)
- **Python 3.x**
- **NPM** (Node Package Manager)

## Installation 🚀

1. **Clone the repository:**
   ```bash
   git clone https://github.com/anda-glitch/auto_text_bot.git
   cd auto_text_bot
   ```

2. **Install the Node.js dependencies:**
   This will install `whatsapp-web.js` (and Chromium) along with `qrcode-terminal` to render the QR inside the terminal.
   ```bash
   npm install
   ```

## Usage 💻
Run the Python bot script:
```bash
python3 bot.py
```

1. **Select Target**: After the bot connects and displays `✅ WHATSAPP IS CONNECTED!`, you will see a menu:
    - **1: Person (Number)**: Enter the number with country code (e.g., `614...`).
    - **2: Name of group**: Enter the *exact* name of the group.
    - **3: Group ID**: Use a permanent ID (e.g., `120363...@g.us`).
    - **4: List all Groups**: This will fetch and print a table of all your groups and their IDs so you can copy-paste them.
2. **Scan the QR Code**: If it's your first time, an ASCII QR code will be generated in your terminal. Scan it via WhatsApp **Linked Devices**.
3. **Enjoy!** Once authenticated and target is selected, it will start sending the automated payload on its 1-minute schedule.

*Note: You only need to scan the QR code the very first time. Your session will be saved locally in a hidden `.wwebjs_auth` directory so you won't have to scan it again.*

## Dependencies 📦
* **Python**: `subprocess`, `threading`, `json`, `time`, `sys`, `os` (All Standard Library — no `pip install` required!)
* **Node.js**:
  - [`whatsapp-web.js`](https://github.com/pedroslopez/whatsapp-web.js/) - Heavy lifting for WhatsApp web automation.
  - [`qrcode-terminal`](https://github.com/gtanner/qrcode-terminal) - Displays an ASCII QR code in the terminal.

## Disclaimer ⚠️
This project relies on unofficial automation of WhatsApp Web. It is intended for educational purposes only. Do not use this for spamming or flooding, as WhatsApp actively monitors for unusual bot-like behavior and may flag or ban your number.
