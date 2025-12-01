# ranks.py (Python 3.13 moslangan)
import subprocess
import logging
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ConversationHandler, MessageHandler, ContextTypes, filters
)

# ===== CONFIG =====
TELEGRAM_TOKEN = "8552735296:AAF0tzjDyR9H8ZW7mWMwwonteI5YU_irBYc"
SERVER_HOST = "minexis.aternos.me"
SERVER_PORT = "25565"
ASK_NICK = 1
ALLOWED_RANKS = {"legend", "vip", "imperator", "mod"}
# ==================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Minxis botiga xush kelibsiz /ranks bilan o'zingizga 4 olishigiz mumkin boshlang.")

async def ranks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("legend", callback_data="rank_legend"),
         InlineKeyboardButton("vip", callback_data="rank_vip")],
        [InlineKeyboardButton("imperator", callback_data="rank_imperator"),
         InlineKeyboardButton("mod", callback_data="rank_mod")],
    ]
    await update.message.reply_text("Qaysi rankni berishni xohlaysiz?", reply_markup=InlineKeyboardMarkup(keyboard))

async def rank_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    _, rank_key = data.split("_", 1)
    if rank_key not in ALLOWED_RANKS:
        await query.edit_message_text("Noto'g'ri rank tanlandi.")
        return ConversationHandler.END
    context.user_data["pending_rank"] = rank_key
    await query.edit_message_text(f"Siz `{rank_key}` tanladingiz. Iltimos serverdagi nikini yuboring.")
    return ASK_NICK

async def run_node_command(node_cmd: str) -> str:
    """Async subprocess run Python 3.13 bilan mos"""
    def blocking():
        result = subprocess.run(node_cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result
    return await asyncio.to_thread(blocking)

async def receive_nick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nick = update.message.text.strip()
    rank = context.user_data.get("pending_rank")
    if not rank:
        await update.message.reply_text("Rank topilmadi. /ranks bilan qayta boshlang.")
        return ConversationHandler.END

    node_cmd = f'node ranksbot.js {SERVER_HOST} {SERVER_PORT} {nick} {rank}'
    await update.message.reply_text(f"Bot serverga kirib `{nick}` ga `{rank}` rankini berishi uchun ishga tushyapti...")

    try:
        proc = await run_node_command(node_cmd)
        out = proc.stdout.strip()
        err = proc.stderr.strip()
        if proc.returncode == 0:
            reply = f"✅ Muvaffaqiyat! Bot buyruq yubordi.\n\nServer javobi:\n{out if out else '(no stdout)'}"
        else:
            reply = f"❌ Xatolik: node jarayoni kodi {proc.returncode} bilan tugadi.\n\nSTDOUT:\n{out}\n\nSTDERR:\n{err}"
        await update.message.reply_text(reply)
    except Exception as e:
        logger.exception("Node chaqirishda xato")
        await update.message.reply_text(f"❌ Jarayon chaqirishda xatolik: {e}")

    context.user_data.pop("pending_rank", None)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("pending_rank", None)
    await update.message.reply_text("Bekor qilindi.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(rank_button_handler, pattern=r"^rank_")],
        states={ASK_NICK: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_nick)]},
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ranks", ranks_command))
    app.add_handler(conv)

    logger.info("Telegram bot ishga tushmoqda...")
    app.run_polling()  # Python 3.13 da async bilan mos

if __name__ == "__main__":
    main()
