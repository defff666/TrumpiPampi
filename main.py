import telegram
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from flask import Flask, request, send_from_directory
import threading
import logging
import time
from database import Database

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = '7899507312:AAE6UtB-ARAu7cKvPfpksQdSFjhXEchZ7EY'
APP_URL = 'https://trumpipampi.onrender.com/app'

flask_app = Flask(__name__)
db = Database()

@flask_app.route('/app')
def serve_app():
    chat_id = request.args.get('chat_id')
    logger.info(f"Serving app for chat_id: {chat_id}")
    return send_from_directory('app', 'index.html')

@flask_app.route('/api/tap', methods=['POST'])
def tap():
    chat_id = int(request.json['chat_id'])
    logger.info(f"Received tap request for chat_id: {chat_id}")
    balance, energy = db.tap(chat_id)
    logger.info(f"Tap processed for {chat_id}: balance={balance}, energy={energy}")
    return {'balance': balance, 'energy': energy}

@flask_app.route('/api/stats', methods=['GET'])
def get_stats():
    chat_id = int(request.args.get('chat_id'))
    logger.info(f"Received stats request for chat_id: {chat_id}")
    balance, energy, max_energy = db.get_stats(chat_id)
    logger.info(f"Stats returned for {chat_id}: balance={balance}, energy={energy}, max_energy={max_energy}")
    return {'balance': balance, 'energy': energy, 'max_energy': max_energy}

def run_flask():
    logger.info("Starting Flask server on 0.0.0.0:5000...")
    flask_app.run(host='0.0.0.0', port=5000)

async def start(update: Update, context: ContextTypes):
    chat_id = update.message.chat_id
    ref_id = context.args[0].split('_')[1] if context.args and '_' in context.args[0] else None
    db.register_user(chat_id, ref_id)
    logger.info(f"User {chat_id} started bot with ref_id: {ref_id}")
    await update.message.reply_text(
        "Welcome to Trumpi Pumpi! Tap Trump to earn TRUMP coins! 💰",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Start Pumping!", web_app=WebAppInfo(url=f"{APP_URL}?chat_id={chat_id}"))]
        ])
    )

def main():
    logger.info("Initializing TrumpiPumpi bot...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    threading.Thread(target=run_flask, daemon=True).start()
    while True:
        try:
            logger.info("Bot is polling...")
            app.run_polling()
        except telegram.error.NetworkError as e:
            logger.warning(f"Network error: {e}. Retrying in 5 sec...")
            time.sleep(5)
        except telegram.error.Conflict as e:
            logger.error(f"Conflict error: {e}. Another instance is running. Retrying in 5 sec...")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Bot crashed: {e}")
            raise

if __name__ == '__main__':
    logger.info("Starting TrumpiPumpi bot...")
    main()
