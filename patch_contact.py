fichier = 'signaler.py'

with open(fichier, 'r') as f:
    contenu = f.read()

code = """

async def menu_contact(update, context):
    user = update.effective_user
    context.user_data['waiting_contact'] = True
    await update.message.reply_text("Ecrivez votre message pour l'admin. Il sera transmis directement.")

async def capturer_contact(update, context):
    if not context.user_data.get('waiting_contact'):
        return False
    user = update.effective_user
    msg = update.message.text
    context.user_data['waiting_contact'] = False
    
    texte_admin = f"Message de {user.first_name}\\nID: {user.id}\\n@{user.username or 'N/A'}\\n\\n{msg}\\n\\n/reply {user.id} votre reponse"
    await context.bot.send_message(6610074482, texte_admin)
    await update.message.reply_text("Message envoye a l'admin. Reponse sous 24h.")
    return True
"""

contenu = contenu + code

with open(fichier, 'w') as f:
    f.write(contenu)

print("OK")
