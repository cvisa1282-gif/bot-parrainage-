fichier = 'securite.py'

with open(fichier, 'r') as f:
    contenu = f.read()

ajout = """
async def cmd_add(update, context):
    ADMIN_ID = 6610074482
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("Usage: /add [user_id] [montant]")
        return
    try:
        target = int(context.args[0])
        montant = int(context.args[1])
    except:
        await update.message.reply_text("ID et montant doivent etre des nombres.")
        return
    import sqlite3
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (montant, target))
    conn.commit()
    conn.close()
    log_action(target, "AJOUT_ADMIN", f"+{montant} FCFA", 0)
    await update.message.reply_text(f"OK. +{montant} FCFA pour {target}.")

async def cmd_remove(update, context):
    ADMIN_ID = 6610074482
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("Usage: /remove [user_id] [montant]")
        return
    try:
        target = int(context.args[0])
        montant = int(context.args[1])
    except:
        await update.message.reply_text("ID et montant doivent etre des nombres.")
        return
    import sqlite3
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (montant, target))
    conn.commit()
    conn.close()
    log_action(target, "RETRAIT_ADMIN", f"-{montant} FCFA", 1)
    await update.message.reply_text(f"OK. -{montant} FCFA pour {target}.")

async def cmd_reset(update, context):
    ADMIN_ID = 6610074482
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /reset [user_id]")
        return
    try:
        target = int(context.args[0])
    except:
        await update.message.reply_text("ID invalide.")
        return
    import sqlite3
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute("UPDATE users SET balance = 0 WHERE user_id = ?", (target,))
    conn.commit()
    conn.close()
    log_action(target, "RESET_SOLDE", "0 FCFA", 1)
    await update.message.reply_text(f"OK. Solde de {target} remis a zero.")
"""

contenu = contenu + ajout

with open(fichier, 'w') as f:
    f.write(contenu)

print("Patch admin balance OK")
