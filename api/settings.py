# api/settings.py
import os

# Telegram & Cron
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "GANTI_DENGAN_TOKEN_BOT_ANDA")
CRON_SECRET = os.getenv("CRON_SECRET", "RAHASIA-ANDA-UNTUK-CRON")

# Database (menggunakan PostgreSQL dengan SQLAlchemy)
DATABASE_URL = os.getenv("DATABASE_URL", "postgres://user:password@host:port/dbname")

# Default values
DEFAULT_ALLOWED_USERS = ["7549219256", "6606294583"]
DEFAULT_TIMEZONE = 'Asia/Makassar'
DEFAULT_KOTA_SHALAT = '2106'

# API URLs
CUACA_URL = "https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4=63.08.05.2016"
GEMPA_URL = "https://data.bmkg.go.id/DataMKG/TEWS/autogempa.json"
SHALAT_BASE = "https://api.myquran.com/v2/sholat/jadwal"