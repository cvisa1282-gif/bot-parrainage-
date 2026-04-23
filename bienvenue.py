from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CommandHandler


async def start_bienvenue(update: Update, context):
    user = update.effective_user
    
    text = f"""
✅ *Bienvenue {user.first_name} !*

💰 *Solde* — Consultez votre argent
👥 *Parrainage* — Gagnez +300 FCFA par filleul
💳 *Retrait* — Retirez dès 5000 FCFA
🚨 *Signaler* — Signalez un problème

🛡️ *Sécurité active 24/7*

Bonne chance ! 🍀
"""

    menu_keyboard = [
        ["💰 Solde", "👥 Parrainage"],
        ["💳 Retrait", "🚨 Signaler"],
        ["🎰 Loterie"]
    ]
    reply_markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)
    
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')


def enregistrer(app):
    app.add_handler(CommandHandler("start", start_bienvenue))
