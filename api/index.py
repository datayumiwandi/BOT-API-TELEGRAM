# api/index.py

from flask import Flask, request, jsonify
import sys
from . import settings, bot
from .handlers import COMMAND_HANDLERS
from .database import is_user_allowed

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook_handler():
    """Menerima update dari Telegram."""
    try:
        data = request.json
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            user = message['from']
            text = message.get('text', '')

            if not is_user_allowed(user['id']):
                print(f"Akses ditolak untuk user: {user['id']}")
                return 'ok', 200

            handler = COMMAND_HANDLERS.get(text)
            if handler:
                handler(chat_id, user)
                
    except Exception as e:
        # Jika terjadi error apapun, cetak ke log Vercel
        print(f"🔥🔥🔥 ERROR DI WEBHOOK: {e}", file=sys.stderr)
        # Import traceback untuk mencetak detail error
        import traceback
        traceback.print_exc(file=sys.stderr)

    return 'ok', 200

# ... (sisa kode Anda dari /cron/reminders sampai akhir tetap sama) ...
@app.route('/cron/reminders', methods=['POST'])
def cron_handler():
    """Endpoint untuk Cron Job pengingat shalat."""
    auth_secret = request.headers.get('X-Cron-Secret')
    if auth_secret != settings.CRON_SECRET:
        return 'Unauthorized', 401

    result = bot.check_and_send_reminders()
    return result, 200

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint untuk cek status aplikasi."""
    return jsonify({'status': 'healthy', 'version': 'v2.0-modular-debug'})

@app.route('/')
def index():
    """Halaman utama."""
    return 'YUI Assistant Worker (Python Version - Modular) 🌟'