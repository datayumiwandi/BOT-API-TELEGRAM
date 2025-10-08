import sys
import certifi  # <-- Pastikan import ini ada
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError
from datetime import datetime
from . import settings

# --- Inisialisasi Koneksi ke MongoDB ---
try:
    # Menggunakan sertifikat dari certifi untuk koneksi SSL yang stabil
    ca = certifi.where()
    client = MongoClient(settings.MONGO_URI, tlsCAFile=ca)

    # Perintah 'ping' akan melempar exception jika koneksi gagal
    client.admin.command('ping')
    print("✅ Koneksi ke MongoDB berhasil.")

except ConfigurationError as e:
    # Error ini terjadi jika MONGO_URI tidak valid
    print(f"❌ KESALAHAN KONFIGURASI MONGO_URI: {e}", file=sys.stderr)
    print("➡️ Pastikan MONGO_URI Anda diformat dengan benar.", file=sys.stderr)
    client = None
except ConnectionFailure as e:
    # Error ini terjadi jika server tidak bisa dijangkau (masalah Network Access/Firewall)
    print(f"❌ KESALAHAN KONEKSI MONGO: {e}", file=sys.stderr)
    print("➡️ Pastikan Anda sudah mengizinkan akses dari semua IP (0.0.0.0/0) di MongoDB Atlas.", file=sys.stderr)
    client = None
except Exception as e:
    # Menangkap error tak terduga lainnya
    print(f"❌ Terjadi error tak terduga saat menghubungkan ke MongoDB: {e}", file=sys.stderr)
    client = None

# Pastikan client tidak None sebelum membuat koneksi ke database dan collection
if client:
    db = client[settings.DB_NAME]
    users_collection = db.users
else:
    # Jika koneksi gagal, buat placeholder agar aplikasi tidak crash total
    print("🔴 Aplikasi berjalan tanpa koneksi database. Semua fungsi database akan gagal.", file=sys.stderr)
    db = None
    users_collection = None

# --- Fungsi-fungsi Database ---

def get_user(user_id):
    """Mengambil data user dari database."""
    if not users_collection: return None
    return users_collection.find_one({'user_id': str(user_id)})

def ensure_user(user_id, profile=None):
    """Memastikan user ada di database. Jika tidak ada, buat baru."""
    if not users_collection: return None
    if profile is None: profile = {}

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
    if not users_collection: return
    users_collection.update_one({'user_id': str(user_id)}, {'$set': data})

def get_all_users():
    """Mengambil semua user dari database."""
    if not users_collection: return []
    return list(users_collection.find({}))

def is_user_allowed(user_id):
    """Mengecek apakah user diizinkan."""
    return str(user_id) in settings.DEFAULT_ALLOWED_USERS