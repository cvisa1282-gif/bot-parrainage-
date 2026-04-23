from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes



async def cmd_solde(update, context):
    user = update.effective_user
    import sqlite3
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE user_id = ?", (user.id,))
    data = c.fetchone()
    conn.close()
    if data:
        await update.message.reply_text(f"💰 Solde : *{data[0]} FCFA*", parse_mode='Markdown')
    else:
        await update.message.reply_text("Utilisez /start d'abord.")

async def cmd_parrainage(update, context):
    user = update.effective_user
    import sqlite3
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute("SELECT referral_code FROM users WHERE user_id = ?", (user.id,))
    data = c.fetchone()
    conn.close()
    if data:
        link = f"https://t.me/{context.bot.username}?start={data[0]}"
        await update.message.reply_text(f"🔗 Votre lien :\n`{link}`\n👥 +300 FCFA par filleul", parse_mode='Markdown')
    else:
        await update.message.reply_text("Utilisez /start d'abord.")

async def handle_menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "💰 Solde":
        from bot import solde
        await solde(update, context)
    elif text == "👥 Parrainage":
        from bot import parrainage
        await parrainage(update, context)
    elif text == "💳 Retrait":
        from bot import retrait_start
        await retrait_start(update, context)
    elif text == "🚨 Signaler":
        from signaler import menu_signaler
        await menu_signaler(update, context)


def enregistrer_handler_menu(app):
    pattern = r'^(💰 Solde|👥 Parrainage|💳 Retrait|🚨 Signaler|🎰 Loterie)$'
    app.add_handler(MessageHandler(filters.Regex(pattern), handle_menu_buttons))
