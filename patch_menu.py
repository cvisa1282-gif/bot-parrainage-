# PATCH : Correction des boutons Solde et Parrainage
# Ce script modifie menu_buttons.py pour corriger les imports

fichier = 'menu_buttons.py'

with open(fichier, 'r') as f:
    contenu = f.read()

# Correction 1 : Remplacer les imports bot par des fonctions locales
old_import = """    if text == "💰 Solde":
        from bot import solde
        await solde(update, context)
    
    elif text == "👥 Parrainage":
        from bot import parrainage
        await parrainage(update, context)"""

new_import = """    if text == "💰 Solde":
        await cmd_solde(update, context)
    
    elif text == "👥 Parrainage":
        await cmd_parrainage(update, context)"""

contenu = contenu.replace(old_import, new_import)

# Ajouter les fonctions manquantes si nécessaire
if "async def cmd_solde" not in contenu:
    fonctions = """
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
        await update.message.reply_text(f"🔗 Votre lien :\\n`{link}`\\n👥 +300 FCFA par filleul", parse_mode='Markdown')
    else:
        await update.message.reply_text("Utilisez /start d'abord.")
"""
    # Insérer avant la fonction handle_menu_buttons
    contenu = contenu.replace(
        "async def handle_menu_buttons",
        fonctions + "\nasync def handle_menu_buttons"
    )

with open(fichier, 'w') as f:
    f.write(contenu)

print("✅ Patch appliqué : Solde et Parrainage corrigés")
