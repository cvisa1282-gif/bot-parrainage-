from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes


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
