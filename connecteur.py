# ==================== CONNECTEUR UNIVERSEL ====================
# Ce fichier branche TOUS les modules au bot.
# Ajoutez les nouveaux modules ici.


def connecter_tout(app):
    """Ajoute tous les handlers des modules à l'application"""
    
    # Module bienvenue
    from bienvenue import enregistrer as enregistrer_bienvenue
    enregistrer_bienvenue(app)
    
    # Module sécurité (ban, unban, logs, etc.)
    from securite import cmd_ban, cmd_unban, cmd_logs, cmd_clearlogs, cmd_blacklist, cmd_suspects
    from telegram.ext import CommandHandler
    app.add_handler(CommandHandler("ban", cmd_ban))
    app.add_handler(CommandHandler("unban", cmd_unban))
    app.add_handler(CommandHandler("logs", cmd_logs))
    app.add_handler(CommandHandler("clearlogs", cmd_clearlogs))
    app.add_handler(CommandHandler("blacklist", cmd_blacklist))
    app.add_handler(CommandHandler("suspects", cmd_suspects))
    
    # Module signaler (reply)
    from signaler import cmd_reply
    app.add_handler(CommandHandler("reply", cmd_reply))
    
    # Module loterie
    from loterie_fix import enregistrer as enregistrer_loterie
enregistrer_loterie(app)
    
    # Module menu centralisé
    from menu_buttons import enregistrer_handler_menu
    enregistrer_handler_menu(app)
    
    # ========== AJOUTER LES NOUVEAUX MODULES ICI ==========
    # from nouveau_module import enregistrer
    # enregistrer(app)
    
    print("✅ Tous les modules connectés")


print("✅ Connecteur prêt")
