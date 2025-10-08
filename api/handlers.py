# api/handlers.py
from . import database as db
from . import utils

def handle_start(chat_id, user_profile):
    """Menangani perintah /start."""
    db.ensure_user(user_profile['id'], user_profile)
    welcome_message = (
        f"Hai <b>{user_profile['first_name']}</b>! 👋\n"
        "Aku YUI, asisten virtual untuk membantumu tetap produktif."
    )
    utils.send_telegram_message(chat_id, welcome_message)

def handle_shalat(chat_id, user_profile):
    """Menangani perintah /shalat."""
    user_data = db.ensure_user(user_profile['id'], user_profile)
    kota_id = user_data.get('kota_shalat', '2106')

    prayer_data = utils.get_prayer_time_from_api(kota_id)

    if not prayer_data['success']:
        utils.send_telegram_message(chat_id, "❌ Gagal mengambil jadwal shalat. Coba lagi nanti.")
        return

    today_str = utils.get_today_date(full=True)
    jadwal = prayer_data['jadwal']
    text = (
        f"<b>══ 🕋 JADWAL SHALAT ══</b>\n"
        f"<i>{today_str}</i>\n\n"
        f"<b>Lokasi:</b> {prayer_data['kota']}\n\n"
        f"<b>• Imsak:</b> {jadwal.get('imsak', '-')}\n"
        f"<b>• Subuh:</b> {jadwal.get('subuh', '-')}\n"
        f"<b>• Terbit:</b> {jadwal.get('terbit', '-')}\n"
        f"<b>• Dhuha:</b> {jadwal.get('dhuha', '-')}\n"
        f"<b>• Dzuhur:</b> {jadwal.get('dzuhur', '-')}\n"
        f"<b>• Ashar:</b> {jadwal.get('ashar', '-')}\n"
        f"<b>• Maghrib:</b> {jadwal.get('maghrib', '-')}\n"
        f"<b>• Isya:</b> {jadwal.get('isya', '-')}\n"
    )
    utils.send_telegram_message(chat_id, text)

# Mapping dari teks perintah ke fungsi handler-nya
COMMAND_HANDLERS = {
    '/start': handle_start,
    '/shalat': handle_shalat
}