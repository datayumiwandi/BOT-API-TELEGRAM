# api/bot.py
from datetime import datetime, timedelta
import pytz
from . import database as db
from . import utils
from . import settings

def get_user_prayer_schedule(user_data):
    """
    Mengambil jadwal shalat untuk user.
    Pertama, cek cache di data user. Jika tidak ada atau sudah usang, ambil dari API.
    """
    tz = pytz.timezone(settings.DEFAULT_TIMEZONE)
    today_str = datetime.now(tz).strftime('%Y-%m-%d')

    if user_data.get('schedule_date') == today_str and user_data.get('prayer_schedule'):
        return user_data['prayer_schedule']

    print(f"Mengambil jadwal shalat dari API untuk user {user_data['user_id']}...")
    prayer_data = utils.get_prayer_time_from_api(user_data.get('kota_shalat', settings.DEFAULT_KOTA_SHALAT))

    if prayer_data['success']:
        # Simpan jadwal dan tanggalnya sebagai cache
        update_data = {
            'prayer_schedule': prayer_data['jadwal'],
            'schedule_date': today_str
        }
        # Hapus status pengingat dari hari kemarin
        keys_to_unset = {k: "" for k in user_data if k.startswith('reminded_')}
        if keys_to_unset:
            db.users_collection.update_one(
                {'user_id': user_data['user_id']},
                {'$set': update_data, '$unset': keys_to_unset}
            )
        else:
            db.update_user(user_data['user_id'], update_data)

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
        user_id = user['user_id']
        chat_id = user_id

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
            
            # Kirim pengingat jika waktu shalat antara 19 dan 20 menit dari sekarang
            is_reminder_time = 19 * 60 < time_diff_seconds <= 20 * 60
            reminder_key = f"reminded_{prayer_name}_{today_str}"
            already_reminded = user.get(reminder_key, False)

            if is_reminder_time and not already_reminded:
                print(f"Mengirim pengingat {prayer_name} ke user {user_id}")
                message = (
                    f"🔔 <b>Pengingat Shalat!</b>\n\n"
                    f"20 menit lagi akan masuk waktu <b>{prayer_name.capitalize()}</b> ({time_str})."
                )
                utils.send_telegram_message(chat_id, message)

                # Tandai pengingat sudah dikirim
                db.update_user(user_id, {reminder_key: True})

    return "Scheduler finished."