fichier = 'connecteur.py'

with open(fichier, 'r') as f:
    contenu = f.read()

a_remplacer = "app.add_handler(CommandHandler(\"suspects\", cmd_suspects))"
nouveau = "app.add_handler(CommandHandler(\"suspects\", cmd_suspects))\n    app.add_handler(CommandHandler(\"add\", cmd_add))\n    app.add_handler(CommandHandler(\"remove\", cmd_remove))\n    app.add_handler(CommandHandler(\"reset\", cmd_reset))"

contenu = contenu.replace(a_remplacer, nouveau)

import_remplacer = "from securite import cmd_ban, cmd_unban, cmd_logs, cmd_clearlogs, cmd_blacklist, cmd_suspects"
import_nouveau = "from securite import cmd_ban, cmd_unban, cmd_logs, cmd_clearlogs, cmd_blacklist, cmd_suspects, cmd_add, cmd_remove, cmd_reset"

contenu = contenu.replace(import_remplacer, import_nouveau)

with open(fichier, 'w') as f:
    f.write(contenu)

print("Patch connecteur OK")
