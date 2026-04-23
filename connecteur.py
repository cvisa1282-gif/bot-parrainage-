# ==================== CONNECTEUR UNIVERSEL ====================
def connecter_tout(app):
    from telegram.ext import CommandHandler
    
    # Le message de bienvenue DOIT remplacer l'ancien /start
    from bienvenue import start_bienvenue as nouveau_start
    app.add_handler(CommandHandler("start", nouveau_start))
    
    from securite import cmd_ban, cmd_unban, cmd_logs, cmd_clearlogs, cmd_blacklist, cmd_suspects
    app.add_handler(CommandHandler("ban", cmd_ban))
    app.add_handler(CommandHandler("unban", cmd_unban))
    app.add_handler(CommandHandler("logs", cmd_logs))
    app.add_handler(CommandHandler("clearlogs", cmd_clearlogs))
    app.add_handler(CommandHandler("blacklist", cmd_blacklist))
    app.add_handler(CommandHandler("suspects", cmd_suspects))
    
    from signaler import cmd_reply
    app.add_handler(CommandHandler("reply", cmd_reply))
    
    from loterie_fix import enregistrer as enregistrer_loterie
    enregistrer_loterie(app)
    
    from menu_buttons import enregistrer_handler_menu
    enregistrer_handler_menu(app)
    
    print("✅ Tous les modules connectés")
