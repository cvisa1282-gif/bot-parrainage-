# ==================== MODULE SIGNALER (COMPLET) ====================
# Fichier unique : menu + transfert admin + reply

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes

ADMIN_ID = 6610074482


# ==================== FONCTION MENU ====================

async def menu_signaler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Appelée quand l'utilisateur clique sur '🚨 Signaler'"""
    user = update.effective_user
    
    await update.message.reply_text(
        "📢 *Signalement de problème*\n\n"
        "Décrivez votre problème en un message.\n"
        "L'administration le recevra immédiatement.\n\n"
        "✍️ Tapez votre message :",
        parse_mode='Markdown'
    )
    
    context.user_data['waiting_signal'] = True


# ==================== FONCTION CAPTURE ====================

async def capturer_signalement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Capture le message et l'envoie à l'admin"""
    if not context.user_data.get('waiting_signal'):
        return False
    
    user = update.effective_user
    message = update.message.text
    context.user_data['waiting_signal'] = False
    
    admin_msg = (
        f"📢 *SIGNALEMENT*\n\n"
        f"👤 {user.first_name}\n"
        f"🆔 `{user.id}`\n"
        f"📛 @{user.username or 'N/A'}\n\n"
        f"📝 *Message :*\n{message}\n\n"
        f"───\n"
        f"/reply {user.id} Votre réponse"
    )
    
    await context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg, parse_mode='Markdown')
    
    await update.message.reply_text(
        "✅ *Signalement envoyé !*\nL'administration vous répondra bientôt.",
        parse_mode='Markdown'
    )
    
    return True


# ==================== COMMANDE REPLY ====================

async def cmd_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin : /reply [id] [message]"""
    if update.effective_user.id != ADMIN_ID:
        return
    
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("Usage : `/reply 123456 Votre message`", parse_mode='Markdown')
        return
    
    target_id = context.args[0]
    if not target_id.isdigit():
        await update.message.reply_text("❌ ID invalide.")
        return
    
    target_id = int(target_id)
    reply_text = " ".join(context.args[1:])
    
    try:
        await context.bot.send_message(
            chat_id=target_id,
            text=f"📬 *Réponse admin :*\n\n{reply_text}",
            parse_mode='Markdown'
        )
        await update.message.reply_text(f"✅ Réponse envoyée à `{target_id}`.", parse_mode='Markdown')
    except:
        await update.message.reply_text("❌ Échec de l'envoi.")


print("✅ Module signalement prêt")
