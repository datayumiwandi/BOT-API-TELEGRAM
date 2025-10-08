# api/database.py
from sqlalchemy import create_engine, Column, String, Integer, JSON, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import json
from . import settings

# --- Konfigurasi SQLAlchemy ---
try:
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    print("✅ Koneksi database SQLAlchemy siap.")
except Exception as e:
    print(f"❌ Gagal mengkonfigurasi SQLAlchemy: {e}")
    engine = None
    SessionLocal = None
    Base = None

# --- Model/Tabel untuk User ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    kota_shalat = Column(String, default=settings.DEFAULT_KOTA_SHALAT)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Kita gunakan JSON untuk menyimpan data yang fleksibel
    _profile_data = Column('profile_data', JSON, default={})
    _prayer_schedule = Column('prayer_schedule', JSON, default={})
    _reminder_status = Column('reminder_status', JSON, default={})
    schedule_date = Column(String, default="")

# Buat tabel di database jika belum ada
if engine:
    Base.metadata.create_all(bind=engine)

# --- Fungsi-fungsi untuk berinteraksi dengan Database ---

def get_db_session():
    """Membuka sesi database dan menutupnya setelah selesai."""
    if not SessionLocal:
        return None
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user(user_id_str):
    """Mengambil data user dari database."""
    db_gen = get_db_session()
    db = next(db_gen, None)
    if db:
        return db.query(User).filter(User.user_id == user_id_str).first()
    return None

def ensure_user(user_id, profile_dict=None):
    """Memastikan user ada di database. Jika tidak, buat baru."""
    user_id_str = str(user_id)
    db_gen = get_db_session()
    db = next(db_gen, None)
    if not db:
        return None
        
    user = db.query(User).filter(User.user_id == user_id_str).first()
    if not user:
        new_user = User(
            user_id=user_id_str,
            name=profile_dict.get('first_name', 'User'),
            _profile_data=profile_dict
        )
        db.add(new_user)
        try:
            db.commit()
            db.refresh(new_user)
            print(f"User baru dibuat: {user_id_str}")
            return new_user
        except SQLAlchemyError as e:
            print(f"Error saat membuat user baru: {e}")
            db.rollback()
            return None
    return user

def update_user(user_id, data_dict):
    """Memperbarui data user."""
    user_id_str = str(user_id)
    db_gen = get_db_session()
    db = next(db_gen, None)
    if not db:
        return

    user = db.query(User).filter(User.user_id == user_id_str).first()
    if user:
        for key, value in data_dict.items():
            if hasattr(user, key):
                setattr(user, key, value)
        try:
            db.commit()
        except SQLAlchemyError as e:
            print(f"Error saat update user: {e}")
            db.rollback()

def get_all_users():
    """Mengambil semua user dari database."""
    db_gen = get_db_session()
    db = next(db_gen, None)
    if db:
        return db.query(User).all()
    return []

def is_user_allowed(user_id):
    """Mengecek apakah user diizinkan."""
    return str(user_id) in settings.DEFAULT_ALLOWED_USERS