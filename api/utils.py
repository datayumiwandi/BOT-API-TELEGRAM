# api/utils.py
import requests
import pytz
from datetime import datetime
from . import settings

# --- Telegram Communication ---
def send_telegram_message(chat_id, text, **kwargs):
    """Mengirim pesan ke Telegram."""
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML', **kwargs}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Telegram message: {e}")
        return None

def edit_telegram_message(chat_id, message_id, text, **kwargs):
    """Mengedit pesan di Telegram."""
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/editMessageText"
    payload = {'chat_id': chat_id, 'message_id': message_id, 'text': text, 'parse_mode': 'HTML', **kwargs}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to edit Telegram message: {e}")
        return None

# --- Date & Time ---
def get_today_date(full=False):
    """Mendapatkan tanggal hari ini sesuai timezone."""
    tz = pytz.timezone(settings.DEFAULT_TIMEZONE)
    now = datetime.now(tz)
    if full:
        return now.strftime('%A, %d %B %Y')
    return {'tahun': now.year, 'bulan': f"{now.month:02}", 'tanggal': f"{now.day:02}"}

# --- External API Calls ---
def get_prayer_time_from_api(kota_id):
    """Mengambil data jadwal shalat dari API MyQuran."""
    try:
        date_info = get_today_date()
        url = f"{settings.SHALAT_BASE}/{kota_id}/{date_info['tahun']}/{date_info['bulan']}/{date_info['tanggal']}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get('status') and data.get('data'):
            return {'success': True, 'jadwal': data['data']['jadwal'], 'kota': data['data']['lokasi']}
        return {'success': False, 'error': 'Invalid API response'}
    except Exception as e:
        print(f"Error getting prayer time from API: {e}")
        return {'success': False, 'error': str(e)}