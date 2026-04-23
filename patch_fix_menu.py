# PATCH : Correction définitive des boutons Solde et Parrainage

fichier = 'menu_buttons.py'

with open(fichier, 'r') as f:
    contenu = f.read()

# Code de remplacement complet pour handle_menu_buttons
nouveau_code = """import sqlite3

async def cmd_solde(update, context):
    user = update.effective_user
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE user_id = ?", (user.id,))
    data = c.fetchone()
    conn.close()
    if data:
        await update.message.reply_text(f"💰 Votre solde : *{data[0]} FCFA*", parse_mode='Markdown')
    else:
        await update.message.reply_text("⚠️ Utilisez /start d'abord.")

async def cmd_parrainage(update, context):
    user = update.effective_user
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute("SELECT referral_code FROM users WHERE user_id = ?", (user.id,))
    data = c.fetchone()
    conn.close()
    if data:
        link = f"https://t.me/{context.bot.username}?start={data[0]}"
        await update.message.reply_text(f"🔗 Votre lien de parrainage :\\n`{link}`\\n\\n👥 Parrain : +300 FCFA\\n🎁 Filleul : +150 FCFA", parse_mode='Markdown')
    else:
        await update.message.reply_text("⚠️ Utilisez /start d'abord.")

async def handle_menu_buttons(update, context):
    text = update.message.text
    
    if text == "💰 Solde":
        await cmd_solde(update, context)
    
    elif text == "👥 Parrainage":
        await cmd_parrainage(update, context)
    
    elif text == "💳 Retrait":
        from bot import retrait_start
        await retrait_start(update, context)
    
    elif text == "🚨 Signaler":
        from signaler import menu_signaler
        await menu_signaler(update, context)


def enregistrer_handler_menu(app):
    from telegram.ext import MessageHandler, filters
    pattern = r'^(💰 Solde|👥 Parrainage|💳 Retrait|🚨 Signaler)$'
    app.add_handler(MessageHandler(filters.Regex(pattern), handle_menu_buttons))
"""

# Remplacer tout le contenu
# On garde juste ce qui est après la fonction enregistrer_handler_menu
contenu = nouveau_code

with open(fichier, 'w') as f:
    f.write(contenu)

print("✅ Patch appliqué : menu_buttons.py remplacé")
