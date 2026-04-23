# ==================== GESTIONNAIRE DE MENUS ====================
# Ce fichier centralise tous les boutons du clavier persistant.
# bot.py n'a plus besoin d'être modifié pour ajouter des menus.

from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes


async def handle_menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Route les clics sur les boutons du clavier vers les modules correspondants.
    Chaque module doit exposer une fonction 'menu_nommodule(update, context)'.
    """
    text = update.message.text
    user = update.effective_user
    
    if text == "💰 Solde":
        # Importer et appeler la fonction solde
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
    
    elif text == "🎰 Loterie":
        from loterie import menu_loterie
        await menu_loterie(update, context)
    
    # ========== AJOUTER LES NOUVEAUX BOUTONS ICI ==========
    # elif text == "🆕 Nouveau Bouton":
    #     from nouveau_module import menu_nouveau
    #     await menu_nouveau(update, context)


def enregistrer_handler_menu(app):
    """Enregistre le handler des boutons du clavier dans l'application"""
    pattern = r'^(💰 Solde|👥 Parrainage|💳 Retrait|🚨 Signaler|🎰 Loterie)$'
    app.add_handler(MessageHandler(filters.Regex(pattern), handle_menu_buttons))
    print("✅ Handler menu centralisé enregistré")


print("✅ Module menu_buttons chargé")
