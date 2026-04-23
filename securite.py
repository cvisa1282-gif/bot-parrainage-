# ==================== MODULE DE SÉCURITÉ - SYSTÈME POLICE ====================
# Importe ce code dans bot.py ou utilise directement les commandes admin

import time
import re
from collections import defaultdict
import sqlite3

# Connexion à la même base de données que bot.py
conn = sqlite3.connect('bot_data.db', check_same_thread=False)
cursor = conn.cursor()

# ==================== TABLES DE SÉCURITÉ ====================
cursor.execute('''
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT,
    details TEXT,
    is_suspicious INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS blacklist (
    user_id INTEGER PRIMARY KEY,
    reason TEXT,
    banned_by INTEGER,
    banned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()

# ==================== VARIABLES ANTI-FLOOD ====================
user_last_action = defaultdict(float)
FLOOD_DELAY = 3  # secondes minimum entre 2 actions

user_daily_parrainages = defaultdict(int)
user_daily_reset = defaultdict(float)
MAX_PARRAINAGES_PER_HOUR = 5
PARRAINAGE_COOLDOWN = 3600  # 1 heure en secondes

# ==================== FONCTIONS DE BASE ====================

def log_action(user_id, action, details="", is_suspicious=0):
    """Enregistre une action dans les logs"""
    cursor.execute(
        "INSERT INTO logs (user_id, action, details, is_suspicious) VALUES (?, ?, ?, ?)",
        (user_id, action, details, is_suspicious)
    )
    conn.commit()


async def alert_admin(context, message):
    """Envoie une alerte à l'admin (ID 6610074482)"""
    ADMIN_ID = 6610074482
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🚨 *ALERTE POLICE*\n\n{message}",
            parse_mode='Markdown'
        )
    except:
        pass


def check_flood(user_id):
    """Retourne False si l'utilisateur fait du flood"""
    now = time.time()
    if now - user_last_action.get(user_id, 0) < FLOOD_DELAY:
        return False
    user_last_action[user_id] = now
    return True


def check_parrainage_limit(user_id):
    """Retourne False si trop de parrainages en 1 heure"""
    now = time.time()
    if now - user_daily_reset.get(user_id, 0) > PARRAINAGE_COOLDOWN:
        user_daily_parrainages[user_id] = 0
        user_daily_reset[user_id] = now
    if user_daily_parrainages.get(user_id, 0) >= MAX_PARRAINAGES_PER_HOUR:
        return False
    user_daily_parrainages[user_id] = user_daily_parrainages.get(user_id, 0) + 1
    return True


def is_suspicious_username(username):
    """Détecte les noms d'utilisateur suspects (patterns de bots)"""
    if not username:
        return False
    patterns = [
        r'bot\d+', r'spam\d+', r'test\d+', r'^[a-z]{10,}\d{5,}',
        r'filleul\d+', r'cheat\d+', r'hack\d+', r'script\d+', r'fake\d+'
    ]
    for pattern in patterns:
        if re.search(pattern, username.lower()):
            return True
    return False


def is_banned(user_id):
    """Vérifie si l'utilisateur est banni"""
    cursor.execute("SELECT * FROM blacklist WHERE user_id = ?", (user_id,))
    return cursor.fetchone() is not None


# ==================== FONCTIONS À APPELER DEPUIS BOT.PY ====================

async def securite_start(user, context):
    """
    Vérifications de sécurité au démarrage.
    Retourne (True, None) si OK, (False, message_erreur) si bloqué.
    À appeler dans start() de bot.py :
        ok, msg = await securite_start(user, context)
        if not ok: await update.message.reply_text(msg)
    """
    # 1. Vérifier bannissement
    if is_banned(user.id):
        log_action(user.id, "TENTATIVE_BANNI", "", 1)
        await alert_admin(context, f"⚠️ Utilisateur banni tente d'accéder : {user.first_name} (ID: `{user.id}`)")
        return False, "🚫 *Vous êtes banni de ce bot.*"
    
    # 2. Vérifier flood
    if not check_flood(user.id):
        log_action(user.id, "FLOOD", "", 1)
        await alert_admin(context, f"⚠️ Flood : {user.first_name} (ID: `{user.id}`)")
        return False, "⚠️ *Trop rapide !* Attends quelques secondes."
    
    # 3. Vérifier username suspect
    if is_suspicious_username(user.username or ""):
        log_action(user.id, "USERNAME_SUSPECT", f"@{user.username}", 1)
        await alert_admin(context, f"🚨 Username suspect : @{user.username} (ID: `{user.id}`)")
    
    # 4. Loguer l'accès
    log_action(user.id, "ACCES_AUTORISE", "", 0)
    
    return True, None


async def securite_parrainage(parrain_id, context):
    """Vérifie la limite de parrainage. Retourne True si OK, False si bloqué."""
    if parrain_id and not check_parrainage_limit(parrain_id):
        log_action(parrain_id, "LIMITE_PARRAINAGE", f"{MAX_PARRAINAGES_PER_HOUR}/heure", 1)
        await alert_admin(context, f"⚠️ Limite parrainage atteinte : ID `{parrain_id}`")
        return False
    return True


# ==================== COMMANDES ADMIN ====================

async def cmd_ban(update, context):
    """Commande /ban [user_id] [raison]"""
    ADMIN_ID = 6610074482
    if update.effective_user.id != ADMIN_ID:
        return
    
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("📋 Usage : `/ban [user_id] [raison]`", parse_mode='Markdown')
        return
    
    target_id = int(context.args[0])
    reason = " ".join(context.args[1:]) if len(context.args) > 1 else "Aucune raison"
    
    cursor.execute(
        "INSERT OR REPLACE INTO blacklist (user_id, reason, banned_by) VALUES (?, ?, ?)",
        (target_id, reason, ADMIN_ID)
    )
    conn.commit()
    log_action(target_id, "BAN", reason, 1)
    
    await update.message.reply_text(
        f"🚫 *Utilisateur banni*\n\n"
        f"🆔 ID : `{target_id}`\n"
        f"📝 Raison : {reason}",
        parse_mode='Markdown'
    )


async def cmd_unban(update, context):
    """Commande /unban [user_id]"""
    ADMIN_ID = 6610074482
    if update.effective_user.id != ADMIN_ID:
        return
    
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("📋 Usage : `/unban [user_id]`", parse_mode='Markdown')
        return
    
    target_id = int(context.args[0])
    cursor.execute("DELETE FROM blacklist WHERE user_id = ?", (target_id,))
    conn.commit()
    log_action(target_id, "UNBAN", "", 0)
    
    await update.message.reply_text(f"✅ Utilisateur `{target_id}` débanni.", parse_mode='Markdown')


async def cmd_blacklist(update, context):
    """Commande /blacklist : afficher tous les bannis"""
    ADMIN_ID = 6610074482
    if update.effective_user.id != ADMIN_ID:
        return
    
    cursor.execute("SELECT * FROM blacklist ORDER BY banned_at DESC LIMIT 20")
    rows = cursor.fetchall()
    
    if not rows:
        await update.message.reply_text("✅ Aucun utilisateur banni.")
        return
    
    text = "🚫 *LISTE DES BANNIS :*\n\n"
    for r in rows:
        text += f"• `{r[0]}` | {r[1][:30]} | {r[3][:10]}\n"
    
    await update.message.reply_text(text, parse_mode='Markdown')


async def cmd_logs(update, context):
    """Commande /logs [n] : afficher les derniers logs"""
    ADMIN_ID = 6610074482
    if update.effective_user.id != ADMIN_ID:
        return
    
    limit = 20
    if context.args and context.args[0].isdigit():
        limit = int(context.args[0])
    
    cursor.execute("SELECT * FROM logs ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    
    if not rows:
        await update.message.reply_text("📭 Aucun log.")
        return
    
    text = f"📋 *DERNIERS LOGS ({limit}) :*\n\n"
    for r in rows:
        emoji = "🚨" if r[4] == 1 else "📝"
        text += f"{emoji} `{r[2]}` | User:`{r[1]}` | {r[3][:40]}\n"
    
    await update.message.reply_text(text, parse_mode='Markdown')


async def cmd_clearlogs(update, context):
    """Commande /clearlogs : effacer tous les logs"""
    ADMIN_ID = 6610074482
    if update.effective_user.id != ADMIN_ID:
        return
    
    cursor.execute("DELETE FROM logs")
    conn.commit()
    await update.message.reply_text("✅ Tous les logs ont été effacés.")


async def cmd_suspects(update, context):
    """Commande /suspects : afficher uniquement les logs suspects"""
    ADMIN_ID = 6610074482
    if update.effective_user.id != ADMIN_ID:
        return
    
    cursor.execute("SELECT * FROM logs WHERE is_suspicious = 1 ORDER BY created_at DESC LIMIT 15")
    rows = cursor.fetchall()
    
    if not rows:
        await update.message.reply_text("✅ Aucune activité suspecte détectée.")
        return
    
    text = "🚨 *ACTIVITÉS SUSPECTES :*\n\n"
    for r in rows:
        text += f"• `{r[2]}` | User:`{r[1]}` | {r[3][:50]}\n"
    
    await update.message.reply_text(text, parse_mode='Markdown')


print("✅ Module sécurité chargé : anti-flood, anti-bot, logs, blacklist")
