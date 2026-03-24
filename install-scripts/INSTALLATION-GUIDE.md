# OpenClaw Windows Installation Guide
## For Non-Technical Users

This guide walks you through installing OpenClaw on your Windows computer. By the end, you'll have your own AI assistant running locally.

---

## What You're Installing

| Component | What It Does | Size | Time |
|-----------|-------------|------|------|
| **WSL2** | Linux environment on Windows | ~500MB | 5 min |
| **Ubuntu** | Operating system for AI | ~1GB | 5 min |
| **Ollama** | AI model server | ~300MB | 2 min |
| **Kimi-K2.5** | Smart AI brain | ~4GB | 15-20 min |
| **OpenClaw** | Gateway to chat apps | ~50MB | 2 min |

**Total:** ~30 minutes initially, ~6GB disk space

---

## Prerequisites

- Windows 10 (version 2004+) or Windows 11
- Administrator access
- 8GB+ RAM recommended
- 10GB free disk space
- Internet connection

---

## Method 1: EASY - One-Click Installer (Recommended)

### Step 1: Download Files
1. Create a folder on your Desktop called `openclaw-install`
2. Download these 2 files into that folder:
   - `INSTALL-OPENCLAW.bat`
   - `openclaw-windows-installer.ps1`

### Step 2: Run Installer
1. Go to your `openclaw-install` folder
2. **Right-click** on `INSTALL-OPENCLAW.bat`
3. Select **"Run as administrator"**
4. Wait 20-30 minutes
5. Restart your computer when prompted
6. Done!

---

## Method 2: MANUAL - Step by Step

If the automatic installer doesn't work, follow these steps:

### Step 1: Install WSL2

Open PowerShell as Administrator (right-click Start → Windows PowerShell (Admin)):

```powershell
wsl --install
```

**Wait for:** "The requested operation completed successfully"

**Restart your computer**

### Step 2: Set Up Ubuntu

After restart, open PowerShell again:

```powershell
wsl --set-default-version 2
```

Then install Ubuntu:

```powershell
wsl --install -d Ubuntu-22.04
```

**Wait for:** Ubuntu to install and ask you to create a username

- Enter a username (e.g., "aiuser")
- Enter a password (remember this!)
- Confirm password

### Step 3: Install Dependencies

Inside the Ubuntu terminal (black window), run:

```bash
sudo apt update && sudo apt install -y curl git build-essential
```

### Step 4: Install Node.js

```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs
```

Verify:
```bash
node --version
```

Should show: `v22.x.x`

### Step 5: Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Wait for installation to complete.

### Step 6: Verify Ollama is Running

```bash
ollama --version
```

Should show a version number.

### Step 7: Download Kimi-K2.5 Model

```bash
ollama pull kimi-k2.5
```

**This takes 15-20 minutes!** The model is ~4GB.

You'll see a progress bar. Wait for it to complete.

### Step 8: Install OpenClaw

```bash
sudo npm install -g openclaw
```

### Step 9: Configure OpenClaw

Create a workspace:
```bash
mkdir -p ~/openclaw-workspace
cd ~/openclaw-workspace
```

Create config:
```bash
cat > config.json << 'EOF'
{
  "gateway": {
    "host": "localhost",
    "port": 3000
  },
  "models": {
    "default": "ollama/kimi-k2.5",
    "providers": {
      "ollama": {
        "baseUrl": "http://localhost:11434"
      }
    }
  }
}
EOF
```

### Step 10: Start OpenClaw

```bash
openclaw
```

**Open your browser and go to:** http://localhost:3000

You should see the OpenClaw interface!

---

## Daily Usage

### Starting OpenClaw Each Day

1. Open PowerShell or Terminal
2. Enter Linux: `wsl`
3. Start OpenClaw: `openclaw`
4. Open browser: http://localhost:3000

### Checking if Ollama is Running

```bash
ollama list
```

Should show `kimi-k2.5`

### Stopping OpenClaw

Press `Ctrl+C` in the terminal where it's running.

---

## Connecting Chat Apps (Optional)

### Telegram

1. Message @BotFather on Telegram
2. Create a new bot
3. Get your token
4. In OpenClaw:
   ```bash
   openclaw config telegram add
   ```
   - Enter your token
   - Enter your chat ID

### WhatsApp

```bash
openclaw config whatsapp add
```

Follow the QR code instructions.

### Discord

```bash
openclaw config discord add
```

Enter your bot token.

---

## Troubleshooting

### "WSL not found"
- Make sure you restarted after installing WSL2
- Run PowerShell as Administrator
- Try: `wsl --update`

### "Permission denied"  
- Use `sudo` before commands
- Or run: `sudo -i` to become root

### "Ollama not found"
```bash
sudo systemctl start ollama
```

### "Out of memory"
- Close other programs
- WSL2 uses RAM from Windows

### OpenClaw won't start
```bash
# Check config
openclaw config validate

# Reset config
rm ~/.config/openclaw/config.json
openclaw config init
```

---

## Quick Command Reference

| What You Want | Command |
|--------------|---------|
| Enter Linux | `wsl` |
| Exit Linux | `exit` |
| Start OpenClaw | `openclaw` |
| Check version | `openclaw --version` |
| List AI models | `ollama list` |
| Check Ollama | `curl http://localhost:11434` |
| View logs | `cat ~/.openclaw/logs/gateway.log` |

---

## Need Help?

1. Check logs in `~/.openclaw/logs/`
2. Run with verbose mode: `openclaw --verbose`
3. Visit: https://docs.openclaw.ai
4. Join Discord: https://discord.com/invite/clawd

---

## You're Done! 🎉

Your OpenClaw bot is running! You can now:
- Chat at http://localhost:3000
- Connect Telegram/WhatsApp/Discord
- Add skills and customize

Happy AI-ing! 🤖
