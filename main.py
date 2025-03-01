import logging
import os
import threading
import asyncio
from flask import Flask, request, send_from_directory
from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
from database import Database

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = '7899507312:AAE6UtB-ARAu7cKvPfpksQdSFjhXEchZ7EY'
APP_URL = 'https://trumpipampi.onrender.com/app'
WEBHOOK_URL = 'https://trumpipampi.onrender.com/webhook'

flask_app = Flask(__name__, static_folder='app')
db = Database()

@flask_app.route('/app')
def serve_app():
    chat_id = request.args.get('chat_id', '')
    logger.info(f"Serving app for chat_id: {chat_id}")
    app_dir = os.path.join(flask_app.root_path, 'app')
    logger.info(f"App directory: {app_dir}, files: {os.listdir(app_dir)}")
    return send_from_directory(app_dir, 'index.html')

@flask_app.route('/api/sync', methods=['POST'])
def sync():
    try:
        data = request.get_json()
        chat_id = data.get('chat_id')
        if not chat_id:
            return {"error": "chat_id is required"}, 400
        db.sync_user(chat_id, data['balance'], data['energy'], data['max_energy'], data['level'], data['multitap'])
        logger.info(f"Sync successful for chat_id: {chat_id}")
        return {"status": "synced"}, 200
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        return {"error": str(e)}, 500

@flask_app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        chat_id = request.args.get('chat_id')
        if not chat_id:
            return {"error": "chat_id is required"}, 400
        stats = db.get_stats(int(chat_id))
        logger.info(f"Stats returned for chat_id: {chat_id}: {stats}")
        return stats, 200
    except Exception as e:
        logger.error(f"Stats fetch failed: {e}")
        return {"error": str(e)}, 500

@flask_app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = Update.de_json(request.get_json(), bot)
        if update:
            app.process_update(update)
        return '', 200
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        return '', 500

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

def run_flask():
    logger.info("Starting Flask server on 0.0.0.0:5000...")
    flask_app.run(host='0.0.0.0', port=5000)

async def setup_webhook():
    global bot
    bot = Bot(TOKEN)
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook set to {WEBHOOK_URL}")

def main():
    logger.info("Initializing TrumpiPumpi bot...")
    global app
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    # Асинхронно устанавливаем вебхук
    asyncio.run(setup_webhook())

    # Запускаем Flask в отдельном потоке
    threading.Thread(target=run_flask, daemon=True).start()

    # Держим основной поток живым
    while True:
        time.sleep(60)

if __name__ == '__main__':
    logger.info("Starting TrumpiPumpi bot...")
    main()
