# ==================== MODULE BIENVENUE - AUTONOME ====================
# Ce fichier gère le message de /start.
# Modifiez-le à tout moment sans toucher à bot.py.

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CommandHandler


async def start_bienvenue(update: Update, context):
    """Nouveau message de bienvenue complet"""
    user = update.effective_user
    
    text = f"""
✅ *Bienvenue {user.first_name} !*

📋 *Ce que vous pouvez faire :*

💰 *Solde* — Consultez votre argent
👥 *Parrainage* — Gagnez +300 FCFA par filleul (+150 pour le filleul)
💳 *Retrait* — Retirez dès 5000 FCFA (Moov Money / Miss by YAS)
🚨 *Signaler* — Signalez un problème à l'admin
🎰 *Loterie* — Tentez de gagner 2000 FCFA ou un lien boosté

🛡️ *Système de sécurité actif :*
• Anti-flood (3 secondes entre actions)
• Anti-bot (usernames suspects détectés)
• Limite de parrainages (5/heure)
• Liste noire des utilisateurs malveillants
• Logs de toutes les activités
• Alertes admin en temps réel

⚠️ Toute activité suspecte est signalée à l'administration.

📌 *Commandes disponibles :*
/help — Aide complète
/solde — Voir votre solde
/parrainage — Votre lien de parrainage
/retrait — Faire un retrait

Bonne chance à tous ! 🍀
"""

    menu_keyboard = [
        ["💰 Solde", "👥 Parrainage"],
        ["💳 Retrait", "🚨 Signaler"],
        ["🎰 Loterie"]
    ]
    reply_markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)
    
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')


# ==================== FONCTION D'ENREGISTREMENT ====================

def enregistrer(app):
    """Enregistre le handler /start dans l'application"""
    app.add_handler(CommandHandler("start", start_bienvenue))
    print("✅ Module bienvenue enregistré")


print("✅ Module bienvenue prêt")
