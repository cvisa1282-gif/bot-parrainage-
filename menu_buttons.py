import sqlite3
from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes

async def btn_solde(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE user_id=?", (uid,))
    row = c.fetchone()
    conn.close()
    if row:
        await update.message.reply_text(f"Solde : {row[0]} FCFA")
    else:
        await update.message.reply_text("Utilisez /start d'abord.")

async def btn_parrainage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute("SELECT referral_code FROM users WHERE user_id=?", (uid,))
    row = c.fetchone()
    conn.close()
    if row:
        lien = f"https://t.me/{context.bot.username}?start={row[0]}"
        await update.message.reply_text(f"Lien : {lien}\n\nParrain : +300 FCFA\nFilleul : +150 FCFA")
    else:
        await update.message.reply_text("Utilisez /start d'abord.")

async def btn_retrait(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from bot import retrait_start
    await retrait_start(update, context)

async def btn_signaler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from signaler import menu_signaler
    await menu_signaler(update, context)

async def routeur(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text
    if txt == "Solde":
        await btn_solde(update, context)
    elif txt == "Parrainage":
        await btn_parrainage(update, context)
    elif txt == "Retrait":
        await btn_retrait(update, context)
    elif txt == "Signaler":
        await btn_signaler(update, context)

def enregistrer_handler_menu(app):
    pattern = r'^(Solde|Parrainage|Retrait|Signaler)$'
    app.add_handler(MessageHandler(filters.Regex(pattern), routeur))
    print("Menu enregistre")
