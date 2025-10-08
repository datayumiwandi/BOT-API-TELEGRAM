# api/bot.py
from datetime import datetime, timedelta
import pytz
from . import database as db
from . import utils
from . import settings

def get_user_prayer_schedule(user):
    """
    Mengambil jadwal shalat untuk user.
    Pertama, cek cache di data user. Jika tidak, ambil dari API.
    """
    tz = pytz.timezone(settings.DEFAULT_TIMEZONE)
    today_str = datetime.now(tz).strftime('%Y-%m-%d')

    if user.schedule_date == today_str and user._prayer_schedule:
        return user._prayer_schedule

    print(f"Mengambil jadwal shalat dari API untuk user {user.user_id}...")
    prayer_data = utils.get_prayer_time_from_api(user.kota_shalat)

    if prayer_data['success']:
        # Simpan jadwal dan reset pengingat lama
        update_data = {
            '_prayer_schedule': prayer_data['jadwal'],
            'schedule_date': today_str,
            '_reminder_status': {}  # Reset status pengingat
        }
        db.update_user(user.user_id, update_data)
        return prayer_data['jadwal']

    return None

def check_and_send_reminders():
    """
    Fungsi utama yang dipanggil oleh cron job untuk mengirim pengingat.
    """
    print("Scheduler running: Memeriksa pengingat shalat...")
    all_users = db.get_all_users()
    tz = pytz.timezone(settings.DEFAULT_TIMEZONE)
    now = datetime.now(tz)
    today_str = now.strftime('%Y-%m-%d')

    for user in all_users:
        # Dapatkan jadwal (dari cache atau API)
        schedule = get_user_prayer_schedule(user)
        if not schedule:
            continue

        for prayer_name, time_str in schedule.items():
            if prayer_name not in ['imsak', 'subuh', 'dzuhur', 'ashar', 'maghrib', 'isya']:
                continue

            try:
                hour, minute = map(int, time_str.split(':'))
                prayer_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            except (ValueError, AttributeError):
                continue

            time_diff_seconds = (prayer_time - now).total_seconds()
            
            is_reminder_time = 19 * 60 < time_diff_seconds <= 20 * 60
            
            # Cek status pengingat
            reminder_key = f"reminded_{prayer_name}"
            # Pastikan _reminder_status tidak None sebelum diakses
            reminder_status = user._reminder_status or {}
            already_reminded = reminder_status.get(reminder_key, False)

            if is_reminder_time and not already_reminded:
                print(f"Mengirim pengingat {prayer_name} ke user {user.user_id}")
                message = (
                    f"🔔 <b>Pengingat Shalat!</b>\n\n"
                    f"20 menit lagi akan masuk waktu <b>{prayer_name.capitalize()}</b> ({time_str})."
                )
                utils.send_telegram_message(user.user_id, message)

                # Tandai pengingat sudah dikirim
                reminder_status[reminder_key] = True
                db.update_user(user.user_id, {'_reminder_status': reminder_status})

    return "Scheduler finished."