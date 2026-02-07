import motor.motor_asyncio
import base64
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from config import DB_URI, DB_NAME, BOT_CREATION_DATE
import asyncio

# MongoDB Client
client = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
db = client[DB_NAME]

# Collections
users_collection = db['users']
channels_collection = db['channels']
admins_collection = db['admins']
broadcasts_collection = db['broadcasts']
settings_collection = db['settings']
fsub_collection = db['force_sub']
links_collection = db['temporary_links']
backup_collection = db['backups']

# ========== USER MANAGEMENT ==========
async def add_user(user_id: int, username: str = None, first_name: str = None) -> bool:
    """Add user to database"""
    try:
        await users_collection.update_one(
            {'_id': user_id},
            {'$set': {
                'username': username,
                'first_name': first_name,
                'last_activity': datetime.utcnow(),
                'joined_at': datetime.utcnow()
            }},
            upsert=True
        )
        return True
    except Exception as e:
        print(f"Error adding user {user_id}: {e}")
        return False

async def get_user(user_id: int) -> Optional[Dict]:
    """Get user data"""
    try:
        return await users_collection.find_one({'_id': user_id})
    except:
        return None

async def get_all_users() -> List[int]:
    """Get all user IDs"""
    try:
        users = await users_collection.find({}).to_list(None)
        return [user['_id'] for user in users]
    except:
        return []

async def count_users() -> int:
    """Count total users"""
    try:
        return await users_collection.count_documents({})
    except:
        return 0

# ========== ADMIN MANAGEMENT ==========
async def add_admin(user_id: int, added_by: int = None) -> bool:
    """Add admin"""
    try:
        await admins_collection.update_one(
            {'_id': user_id},
            {'$set': {
                'added_by': added_by,
                'added_at': datetime.utcnow(),
                'permissions': ['all']
            }},
            upsert=True
        )
        return True
    except:
        return False

async def remove_admin(user_id: int) -> bool:
    """Remove admin"""
    try:
        result = await admins_collection.delete_one({'_id': user_id})
        return result.deleted_count > 0
    except:
        return False

async def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    try:
        admin = await admins_collection.find_one({'_id': user_id})
        return admin is not None
    except:
        return False

async def get_all_admins() -> List[Dict]:
    """Get all admins with details"""
    try:
        admins = await admins_collection.find({}).to_list(None)
        return admins
    except:
        return []

# ========== CHANNEL MANAGEMENT ==========
async def add_channel(channel_id: int, anime_name: str, added_by: int) -> Dict:
    """Add channel with all link types"""
    try:
        channel_data = {
            '_id': channel_id,
            'anime_name': anime_name,
            'added_by': added_by,
            'added_at': datetime.utcnow(),
            'primary_link': None,
            'request_token': None,
            'normal_token': None,
            'status': 'active',
            'last_updated': datetime.utcnow()
        }
        await channels_collection.update_one(
            {'_id': channel_id},
            {'$set': channel_data},
            upsert=True
        )
        return channel_data
    except Exception as e:
        print(f"Error adding channel: {e}")
        return {}

async def update_channel_links(channel_id: int, primary_link: str = None, 
                               request_token: str = None, normal_token: str = None) -> bool:
    """Update channel links"""
    try:
        update_data = {'last_updated': datetime.utcnow()}
        if primary_link:
            update_data['primary_link'] = primary_link
        if request_token:
            update_data['request_token'] = request_token
        if normal_token:
            update_data['normal_token'] = normal_token
            
        await channels_collection.update_one(
            {'_id': channel_id},
            {'$set': update_data}
        )
        return True
    except:
        return False

async def get_channel(channel_id: int) -> Optional[Dict]:
    """Get channel by ID"""
    try:
        return await channels_collection.find_one({'_id': channel_id})
    except:
        return None

async def get_channel_by_name(anime_name: str) -> List[Dict]:
    """Search channels by anime name"""
    try:
        channels = await channels_collection.find({
            'anime_name': {'$regex': anime_name, '$options': 'i'},
            'status': 'active'
        }).to_list(None)
        return channels
    except:
        return []

async def get_all_channels() -> List[Dict]:
    """Get all channels"""
    try:
        return await channels_collection.find({'status': 'active'}).to_list(None)
    except:
        return []

async def delete_channel(channel_id: int) -> bool:
    """Delete channel"""
    try:
        await channels_collection.update_one(
            {'_id': channel_id},
            {'$set': {'status': 'deleted', 'deleted_at': datetime.utcnow()}}
        )
        return True
    except:
        return False

async def count_channels() -> int:
    """Count total channels"""
    try:
        return await channels_collection.count_documents({'status': 'active'})
    except:
        return 0

# ========== TEMPORARY LINKS MANAGEMENT ==========
async def save_temporary_link(link_id: str, channel_id: int, link_type: str, 
                              invite_link: str, expires_at: datetime, 
                              message_ids: List[int] = None) -> bool:
    """Save temporary link for auto-revocation"""
    try:
        await links_collection.update_one(
            {'_id': link_id},
            {'$set': {
                'channel_id': channel_id,
                'link_type': link_type,
                'invite_link': invite_link,
                'expires_at': expires_at,
                'message_ids': message_ids or [],
                'created_at': datetime.utcnow(),
                'status': 'active'
            }},
            upsert=True
        )
        return True
    except:
        return False

async def get_expired_links() -> List[Dict]:
    """Get expired links for cleanup"""
    try:
        expired = await links_collection.find({
            'expires_at': {'$lt': datetime.utcnow()},
            'status': 'active'
        }).to_list(None)
        return expired
    except:
        return []

async def mark_link_revoked(link_id: str) -> bool:
    """Mark link as revoked"""
    try:
        await links_collection.update_one(
            {'_id': link_id},
            {'$set': {'status': 'revoked', 'revoked_at': datetime.utcnow()}}
        )
        return True
    except:
        return False

# ========== BROADCAST MANAGEMENT ==========
async def save_broadcast(broadcast_id: str, broadcast_type: str, content: Dict,
                         scheduled_for: datetime = None, delete_after: int = None) -> bool:
    """Save broadcast data"""
    try:
        await broadcasts_collection.update_one(
            {'_id': broadcast_id},
            {'$set': {
                'type': broadcast_type,
                'content': content,
                'scheduled_for': scheduled_for,
                'delete_after': delete_after,
                'sent_at': datetime.utcnow() if not scheduled_for else None,
                'status': 'pending' if scheduled_for else 'sent'
            }},
            upsert=True
        )
        return True
    except:
        return False

async def get_pending_broadcasts() -> List[Dict]:
    """Get pending broadcasts"""
    try:
        pending = await broadcasts_collection.find({
            'status': 'pending',
            'scheduled_for': {'$lte': datetime.utcnow()}
        }).to_list(None)
        return pending
    except:
        return []

# ========== SETTINGS MANAGEMENT ==========
async def save_setting(key: str, value: Any) -> bool:
    """Save bot setting"""
    try:
        await settings_collection.update_one(
            {'key': key},
            {'$set': {'value': value, 'updated_at': datetime.utcnow()}},
            upsert=True
        )
        return True
    except:
        return False

async def get_setting(key: str, default: Any = None) -> Any:
    """Get bot setting"""
    try:
        setting = await settings_collection.find_one({'key': key})
        return setting['value'] if setting else default
    except:
        return default

async def get_all_settings() -> Dict:
    """Get all settings"""
    try:
        settings = await settings_collection.find({}).to_list(None)
        return {s['key']: s['value'] for s in settings}
    except:
        return {}

# ========== FORCE SUB MANAGEMENT ==========
async def add_fsub_channel(channel_id: int, request_mode: bool = False) -> bool:
    """Add force sub channel"""
    try:
        await fsub_collection.update_one(
            {'_id': channel_id},
            {'$set': {
                'request_mode': request_mode,
                'added_at': datetime.utcnow(),
                'status': 'active'
            }},
            upsert=True
        )
        return True
    except:
        return False

async def remove_fsub_channel(channel_id: int) -> bool:
    """Remove force sub channel"""
    try:
        await fsub_collection.delete_one({'_id': channel_id})
        return True
    except:
        return False

async def get_fsub_channels() -> List[Dict]:
    """Get all force sub channels"""
    try:
        return await fsub_collection.find({'status': 'active'}).to_list(None)
    except:
        return []

async def is_fsub_enabled() -> bool:
    """Check if force sub is enabled"""
    try:
        setting = await settings_collection.find_one({'key': 'force_sub_enabled'})
        return setting['value'] if setting else False
    except:
        return False

# ========== BACKUP MANAGEMENT ==========
async def create_backup(backup_data: Dict) -> str:
    """Create backup"""
    try:
        backup_id = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        await backup_collection.insert_one({
            '_id': backup_id,
            'data': backup_data,
            'created_at': datetime.utcnow(),
            'size': len(json.dumps(backup_data))
        })
        return backup_id
    except:
        return ""

# ========== STATISTICS ==========
async def get_stats() -> Dict:
    """Get bot statistics"""
    try:
        return {
            'total_users': await count_users(),
            'total_channels': await count_channels(),
            'total_admins': await admins_collection.count_documents({}),
            'active_links': await links_collection.count_documents({'status': 'active'}),
            'bot_creation_date': BOT_CREATION_DATE,
            'bot_age_days': (datetime.utcnow() - BOT_CREATION_DATE).days
        }
    except:
        return {}

# ========== HELPER FUNCTIONS ==========
async def encode_string(text: str) -> str:
    """Base64 encode string"""
    return base64.urlsafe_b64encode(text.encode()).decode().strip('=')

async def decode_string(encoded: str) -> str:
    """Base64 decode string"""
    padding = 4 - (len(encoded) % 4)
    encoded += '=' * padding
    return base64.urlsafe_b64decode(encoded.encode()).decode()
