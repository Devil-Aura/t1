import base64
import re
import asyncio
import psutil
import time
from datetime import datetime, timedelta
from typing import Tuple, List, Dict, Optional
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.errors import UserNotParticipant, FloodWait
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import ADMINS, OWNER_ID
from database import is_admin

# ========== FILTERS ==========
class IsAdmin(filters.Filter):
    async def __call__(self, client, message):
        return await is_admin(message.from_user.id)

is_admin_filter = IsAdmin()

class IsOwnerOrAdmin(filters.Filter):
    async def __call__(self, client, message):
        user_id = message.from_user.id
        return user_id == OWNER_ID or await is_admin(user_id)

is_owner_or_admin = IsOwnerOrAdmin()

# ========== ENCODING/DECODING ==========
def encode_string(string: str) -> str:
    """Base64 encode string for URLs"""
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    return (base64_bytes.decode("ascii")).strip("=")

def decode_string(base64_string: str) -> str:
    """Base64 decode string from URL"""
    base64_string = base64_string.strip("=")
    padding = 4 - (len(base64_string) % 4)
    base64_string += "=" * padding
    base64_bytes = base64_string.encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes)
    return string_bytes.decode("ascii")

# ========== TIME FUNCTIONS ==========
def get_readable_time(seconds: int) -> str:
    """Convert seconds to readable time"""
    periods = [
        ('year', 365*24*60*60),
        ('month', 30*24*60*60),
        ('day', 24*60*60),
        ('hour', 60*60),
        ('minute', 60),
        ('second', 1)
    ]
    
    result = []
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result.append(f"{period_value} {period_name}{'s' if period_value > 1 else ''}")
    
    return ", ".join(result) if result else "0 seconds"

def parse_time_string(time_str: str) -> int:
    """Parse time string like 1D 2H 30M to seconds"""
    time_units = {
        'D': 86400, 'd': 86400,  # Days
        'H': 3600, 'h': 3600,    # Hours
        'M': 60, 'm': 60,        # Minutes
        'S': 1, 's': 1           # Seconds
    }
    
    total_seconds = 0
    pattern = r'(\d+)([DdHhMmSs])'
    matches = re.findall(pattern, time_str)
    
    for value, unit in matches:
        total_seconds += int(value) * time_units[unit]
    
    return total_seconds if total_seconds > 0 else 1800  # Default 30 minutes

def format_timedelta(td: timedelta) -> str:
    """Format timedelta to readable string"""
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0:
        parts.append(f"{seconds}s")
    
    return " ".join(parts) if parts else "0s"

# ========== SYSTEM STATUS ==========
def get_system_status() -> Dict:
    """Get system status (CPU, RAM, etc.)"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu': round(cpu_percent, 1),
            'ram': round(memory.percent, 1),
            'ram_used': round(memory.used / (1024**3), 1),  # GB
            'ram_total': round(memory.total / (1024**3), 1),  # GB
            'disk_used': round(disk.used / (1024**3), 1),  # GB
            'disk_total': round(disk.total / (1024**3), 1),  # GB
            'disk_percent': round(disk.percent, 1)
        }
    except:
        return {'cpu': 0, 'ram': 0, 'ram_used': 0, 'ram_total': 0, 
                'disk_used': 0, 'disk_total': 0, 'disk_percent': 0}

# ========== TEXT FORMATTING ==========
def escape_markdown(text: str) -> str:
    """Escape markdown characters"""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

# ========== BUTTON GENERATORS ==========
def create_nav_buttons(current_page: int, total_pages: int, 
                       prefix: str = "page") -> List[List[InlineKeyboardButton]]:
    """Create navigation buttons"""
    buttons = []
    
    if total_pages > 1:
        row = []
        if current_page > 0:
            row.append(InlineKeyboardButton("◀️ Previous", callback_data=f"{prefix}_{current_page-1}"))
        
        row.append(InlineKeyboardButton(f"{current_page+1}/{total_pages}", callback_data="noop"))
        
        if current_page < total_pages - 1:
            row.append(InlineKeyboardButton("Next ▶️", callback_data=f"{prefix}_{current_page+1}"))
        
        buttons.append(row)
    
    return buttons

def create_close_button() -> List[List[InlineKeyboardButton]]:
    """Create close button"""
    return [[InlineKeyboardButton("❌ Close", callback_data="close")]]

def create_back_button(back_to: str) -> List[List[InlineKeyboardButton]]:
    """Create back button"""
    return [[InlineKeyboardButton("🔙 Back", callback_data=f"back_{back_to}")]]

# ========== VALIDATION FUNCTIONS ==========
def is_valid_channel_id(channel_id: str) -> bool:
    """Check if string is valid channel ID"""
    try:
        cid = int(channel_id)
        return cid < 0  # Channel IDs are negative
    except:
        return False

def is_valid_url(url: str) -> bool:
    """Check if string is valid URL"""
    url_pattern = re.compile(
        r'^(https?://)?'  # http:// or https://
        r'(([A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(url_pattern.match(url))

# ========== MESSAGE UTILITIES ==========
async def delete_message_after(message: Message, seconds: int) -> None:
    """Delete message after specified seconds"""
    await asyncio.sleep(seconds)
    try:
        await message.delete()
    except:
        pass

async def edit_or_reply(message: Message, text: str, **kwargs) -> Message:
    """Edit message or reply if can't edit"""
    try:
        return await message.edit_text(text, **kwargs)
    except:
        return await message.reply_text(text, **kwargs)

# ========== CHAT PERMISSION CHECK ==========
async def check_bot_permissions(client, chat_id: int) -> Tuple[bool, str]:
    """Check if bot has necessary permissions in chat"""
    try:
        chat = await client.get_chat(chat_id)
        
        # Check if bot is admin
        try:
            bot_member = await client.get_chat_member(chat_id, (await client.get_me()).id)
            if bot_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return False, "Bot is not admin in the channel"
        except:
            return False, "Bot is not a member of the channel"
        
        # Check invite link permission
        if bot_member.privileges and not bot_member.privileges.can_invite_users:
            return False, "Bot doesn't have invite link permission"
        
        return True, "All permissions OK"
    
    except Exception as e:
        return False, f"Error checking permissions: {str(e)}"

async def create_invite_link(client, chat_id: int, creates_join_request: bool = False, 
                            expire_date: datetime = None) -> Optional[str]:
    """Create invite link with error handling"""
    try:
        invite = await client.create_chat_invite_link(
            chat_id=chat_id,
            expire_date=expire_date,
            creates_join_request=creates_join_request,
            member_limit=1
        )
        return invite.invite_link
    except Exception as e:
        print(f"Error creating invite link: {e}")
        return None

# ========== PAGINATION ==========
def paginate_list(items: List, page: int, per_page: int = 10) -> Tuple[List, int]:
    """Paginate list of items"""
    total_items = len(items)
    total_pages = (total_items + per_page - 1) // per_page
    
    if page < 0:
        page = 0
    if page >= total_pages:
        page = total_pages - 1
    
    start_idx = page * per_page
    end_idx = min(start_idx + per_page, total_items)
    
    return items[start_idx:end_idx], total_pages

# ========== FORMATTING TEMPLATES ==========
def format_user_info(user) -> str:
    """Format user info for display"""
    name = user.first_name or ""
    if user.last_name:
        name += f" {user.last_name}"
    
    username = f"@{user.username}" if user.username else "No username"
    
    return f"👤 {name}\n🆔 {user.id}\n📱 {username}"

def format_channel_info(channel) -> str:
    """Format channel info for display"""
    title = escape_markdown(channel.title)
    members = getattr(channel, 'members_count', 'N/A')
    
    return f"📢 {title}\n👥 Members: {members}\n🆔 {channel.id}"
