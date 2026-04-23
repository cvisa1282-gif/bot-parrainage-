# ==================== MODULE LOTERIE - COMPLET & AUTONOME ====================

import random
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler

ADMIN_ID = 6610074482
TICKET_PRICE = 500

conn = sqlite3.connect('bot_data.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS boosted_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id INTEGER,
    code TEXT UNIQUE,
    bonus_amount INTEGER,
    used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()


def effectuer_tirage():
    tirage = random.randint(1, 100)
    if tirage <= 5:
        return "jackpot", 2000
    elif tirage <= 15:
        return "boost", 500
    elif tirage <= 30:
        return "boost", 500
    else:
        return "perdu", 0


def generer_code_boost():
    return "BOOST" + ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=8))


async def menu_loterie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user.id,))
    data = cursor.fetchone()
    if not data:
        await update.message.reply_text("Utilisez /start d'abord.")
        return
    balance = data[0]
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🎫 Acheter un ticket ({TICKET_PRICE} FCFA)", callback_data="loto_buy")],
        [InlineKeyboardButton("📊 Mes gains", callback_data="loto_wins")],
        [InlineKeyboardButton("ℹ️ Règles", callback_data="loto_rules")]
    ])
    
    await update.message.reply_text(
        f"🎰 *LOTERIE*\n\n"
        f"💰 Solde : *{balance} FCFA*\n"
        f"🎫 Ticket : *{TICKET_PRICE} FCFA*\n\n"
        f"🥇 Jackpot 2000 FCFA (5%)\n"
        f"🥈 Lien boosté 500/F (10%)\n"
        f"🥉 Lien boosté 500/F (15%)\n"
        f"❌ Perdu (70%)",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )


async def handle_loto_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    data = query.data
    
    if data == "loto_rules":
        await query.edit_message_text(
            f"📋 *RÈGLES*\n\n"
            f"🎫 Ticket : {TICKET_PRICE} FCFA\n"
            f"🥇 Jackpot : +2000 FCFA (5%)\n"
            f"🥈 Boost : 500 FCFA/filleul (10%)\n"
            f"🥉 Boost : 500 FCFA/filleul (15%)\n"
            f"❌ Perdu (70%)",
            parse_mode='Markdown'
        )
        return
    
    if data == "loto_wins":
        cursor.execute("SELECT * FROM boosted_links WHERE owner_id = ? ORDER BY created_at DESC LIMIT 5", (user.id,))
        links = cursor.fetchall()
        if not links:
            await query.edit_message_text("📊 Aucun gain.", parse_mode='Markdown')
            return
        text = "📊 *VOS GAINS :*\n\n"
        for l in links:
            s = "✅ Actif" if l[4] < 10 else "❌ Usé"
            text += f"🔗 `{l[2]}` | +{l[3]} FCFA | {s}\n"
        await query.edit_message_text(text, parse_mode='Markdown')
        return
    
    if data == "loto_buy":
        cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user.id,))
        bal = cursor.fetchone()
        if not bal or bal[0] < TICKET_PRICE:
            await query.edit_message_text("❌ Solde insuffisant.", parse_mode='Markdown')
            return
        
        cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (TICKET_PRICE, user.id))
        conn.commit()
        
        resultat, valeur = effectuer_tirage()
        
        if resultat == "jackpot":
            cursor.execute("UPDATE users SET balance = balance + 2000 WHERE user_id = ?", (user.id,))
            conn.commit()
            new_bal = bal[0] - TICKET_PRICE + 2000
            await query.edit_message_text(
                f"🎉 *JACKPOT !*\n+2000 FCFA\n💰 Nouveau solde : *{new_bal} FCFA*",
                parse_mode='Markdown'
            )
            await context.bot.send_message(ADMIN_ID, f"🎉 Jackpot gagné par {user.first_name} (ID:`{user.id}`)", parse_mode='Markdown')
        
        elif resultat == "boost":
            code = generer_code_boost()
            cursor.execute("INSERT INTO boosted_links (owner_id, code, bonus_amount) VALUES (?,?,?)", (user.id, code, 500))
            conn.commit()
            lien = f"https://t.me/{context.bot.username}?start={code}"
            await query.edit_message_text(
                f"🎉 *LIEN BOOSTÉ !*\n🔗 `{lien}`\n💰 +500 FCFA/filleul\n👥 10 utilisations max",
                parse_mode='Markdown'
            )
            await context.bot.send_message(ADMIN_ID, f"🎉 Lien boost gagné par {user.first_name} (ID:`{user.id}`)", parse_mode='Markdown')
        
        else:
            new_bal = bal[0] - TICKET_PRICE
            await query.edit_message_text(
                f"😞 *PERDU !*\n💰 Solde : *{new_bal} FCFA*\nRetentez votre chance !",
                parse_mode='Markdown'
            )


# ==================== HANDLER POUR LE BOUTON MENU ====================

async def handle_loto_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🎰 Loterie":
        await menu_loterie(update, context)


# ==================== FONCTION D'ENREGISTREMENT ====================

def enregistrer_handlers(app: Application):
    """Appelée depuis bot.py pour ajouter les handlers de la loterie"""
    app.add_handler(CallbackQueryHandler(handle_loto_callback, pattern="^loto_"))
    app.add_handler(MessageHandler(filters.Regex(r'^🎰 Loterie$'), handle_loto_button))
    print("✅ Handlers loterie enregistrés")


print("✅ Module loterie chargé")
