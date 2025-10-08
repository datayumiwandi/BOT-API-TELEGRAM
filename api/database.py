# api/database.py
from pymongo import MongoClient
from datetime import datetime
from . import settings

# Inisialisasi koneksi ke MongoDB
client = MongoClient(settings.MONGO_URI)
db = client[settings.DB_NAME]
users_collection = db.users

def get_user(user_id):
    """Mengambil data user dari database."""
    return users_collection.find_one({'user_id': str(user_id)})

def ensure_user(user_id, profile=None):
    """
    Memastikan user ada di database. Jika tidak ada, buat baru.
    Mengembalikan data user.
    """
    if profile is None:
        profile = {}

    user_data = get_user(user_id)
    if not user_data:
        user_data = {
            'user_id': str(user_id),
            'name': profile.get('first_name', 'User'),
            'xp': 0,
            'level': 1,
            'mood': 'neutral',
            'quests': [],
            'kota_shalat': settings.DEFAULT_KOTA_SHALAT,
            'created_at': datetime.now().isoformat(),
            'prayer_schedule': None,
            'schedule_date': None,
            **profile
        }
        users_collection.insert_one(user_data)
    return user_data

def update_user(user_id, data):
    """Memperbarui data user."""
    users_collection.update_one({'user_id': str(user_id)}, {'$set': data})

def get_all_users():
    """Mengambil semua user dari database."""
    return list(users_collection.find({}))

def is_user_allowed(user_id):
    """
    Mengecek apakah user diizinkan.
    (Untuk saat ini masih menggunakan list default, bisa dikembangkan
    untuk mengambil dari database settings).
    """
    return str(user_id) in settings.DEFAULT_ALLOWED_USERS