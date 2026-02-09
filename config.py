import os
from os import environ
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# ========== BOT CONFIGURATION ==========
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")
APP_ID = int(os.environ.get("APP_ID", "22768311"))
API_HASH = os.environ.get("API_HASH", "702d8884f48b42e865425391432b3794")
OWNER_ID = int(os.environ.get("OWNER_ID", "6040503076"))
PORT = int(os.environ.get("PORT", "8080"))

# ========== DATABASE CONFIG ==========
DB_URI = os.environ.get("DATABASE_URL", "")
DB_NAME = os.environ.get("DATABASE_NAME", "crunchyroll_bot")

# ========== BOT SETTINGS ==========
TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "50"))
BOT_CREATION_DATE = datetime(2026, 1, 26)  # Fixed creation date

# ========== MEDIA FILES ==========
START_PIC = os.environ.get("START_PIC", "https://telegra.ph/file/f3d3aff9ec422158feb05-d2180e3665e0ac4d32.jpg")
DEFAULT_IMAGE = os.environ.get("DEFAULT_IMAGE", "https://telegra.ph/file/f3d3aff9ec422158feb05-d2180e3665e0ac4d32.jpg")

# ========== MESSAGES ==========
START_MSG = """<b>Konnichiwa! 🤗</b>

<b>Mera Naam <a href='https://telegra.ph/Crunchy-Roll-Vault-04-08'>Crunchyroll Link Provider</a> hai.</b>  

<b>Main aapko <i>anime channels</i> ki links provide karta hu, Iss Anime Ke Channel Se.</b>

<blockquote>
🔹 Agar aapko kisi anime ki link chahiye,<br>
🔹 Ya channel ki link nahi mil rahi hai,<br>
🔹 Ya link expired ho gayi hai
</blockquote>

<b>Toh aap <a href='https://t.me/CrunchyRollChannel'>@CrunchyRollChannel</a> se New aur working links le sakte hain.</b>  

<b>Shukriya! ❤️</b>"""

HELP_MSG = """<blockquote expandable>
<b>🆘 Help & Support</b>  
Agar aapko kisi bhi help ki zaroorat hai, toh humse yahan sampark karein:  
<b><a href='https://t.me/CrunchyRollHelper'>@CrunchyRollHelper</a></b>
</blockquote>

<b>🎬 More Anime</b>  
Agar aap aur anime dekna chahte hain, toh yahan se dekh sakte hain:  
<b><a href='https://t.me/CrunchyRollChannel'>@CrunchyRollChannel</a></b>

<blockquote expandable>
<b>🤖 Bot Info</b>  
Bot ki jaankari ke liye /about ya /info ka istemal karein.
</blockquote>"""

ABOUT_MSG = """<b>About The Bot</b>

<b>🤖 My Name:</b> <a href='https://telegra.ph/Crunchy-Roll-Vault-04-08'>Crunchyroll Link Provider</a>
<b>📅 Bot Age:</b> {bot_age}
<b>🎬 Anime Channel:</b> <a href='https://t.me/Crunchyrollchannel'>Crunchy Roll Channel</a>
<b>💻 Language:</b> <a href='https://www.python.org/'>Python</a>
<b>👨‍💻 Developer:</b> <a href='https://t.me/World_Fastest_Bots'>World Fastest Bots</a>

<b><i>This Is Private/Paid Bot Provided By @World_Fastest_Bots</i></b>"""

# ========== DEFAULT SETTINGS ==========
DEFAULT_REVOKE_TIME = 1800  # 30 minutes in seconds
DEFAULT_DELETE_TIME = 1800  # 30 minutes in seconds
DEFAULT_BUTTON_TEXT = "⛩️ 𝗖𝗟𝗜𝗖𝗞 𝗛𝗘𝗥𝗘 𝗧𝗢 𝗝𝗈𝗜𝗡 ⛩️"
DEFAULT_FSUB_MESSAGE = """<b>ʀᴏᴋᴏ {first}!</b>

<b>ᴛᴜᴍɴᴇ ᴀʙʜɪ ᴛᴀᴋ ʜᴀᴍᴀʀᴀ ᴀɴɪᴍᴇ ᴄʜᴀɴɴᴇʟ ᴊᴏɪɴ ɴᴀʜɪɴ ᴋɪʏᴀ ʜᴀɪ!</b>

<blockquote><b>ᴀɴɪᴍᴇ ᴋᴇ ᴇᴘɪꜱᴏᴅᴇꜱ ᴀᴜʀ ᴘᴜʀᴇ ᴀɴɪᴍᴇꜱ ʜɪɴᴅɪ ᴍᴇɪɴ ᴅᴇᴋʜɴᴇ ᴋᴇ ʟɪʏᴇ, ᴘᴇʜʟᴇ ʜᴀᴍᴀʀᴇ ᴄʜᴀɴɴᴇʟꜱ ᴊᴏɪɴ ᴋᴀʀɴᴀ ʜᴏɢᴀ।</b></blockquote>

<b>ꜱᴀʙ ᴄʜᴀɴɴᴇʟꜱ ᴊᴏɪɴ ᴋᴀʀɴᴇ ᴋᴇ ʙᴀᴀᴅ /start ʟɪᴋʜᴏ ᴀᴜʀ ᴍᴀᴢᴀ ʟᴜᴛᴏ!</b>"""

# ========== SYSTEM CONFIG ==========
try:
    ADMINS = []
    for x in (os.environ.get("ADMINS", "").split()):
        try:
            ADMINS.append(int(x))
        except ValueError:
            continue
except:
    ADMINS = []

# Add owner as admin
if OWNER_ID not in ADMINS:
    ADMINS.append(OWNER_ID)

# Add default admin
ADMINS.append(6040503076)

# ========== LOGGING ==========
LOG_FILE_NAME = "crunchyroll_bot.log"
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            LOG_FILE_NAME,
            maxBytes=10000000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)

# Bot uptime tracker
import time
class Uptime:
    def __init__(self):
        self.start_time = time.time()
    
    def get_uptime(self):
        uptime = time.time() - self.start_time
        days = int(uptime // 86400)
        hours = int((uptime % 86400) // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)
        return f"{days}d {hours}h {minutes}m {seconds}s"

UPTIME = Uptime()
