# ==================== MODULE LOTERIE CORRIGÉ ====================
import random
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, MessageHandler, filters, ContextTypes

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


# ==================== MENU LOTERIE ====================

async def menu_loterie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Vérifier si l'utilisateur existe dans la base
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user.id,))
    data = cursor.fetchone()
    
    if not data:
        await update.message.reply_text("⚠️ Utilisez /start d'abord pour vous inscrire.")
        return
    
    balance = data[0]
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🎫 Acheter un ticket ({TICKET_PRICE} FCFA)", callback_data="loto_buy")],
        [InlineKeyboardButton("📊 Mes gains", callback_data="loto_wins")],
        [InlineKeyboardButton("ℹ️ Règles", callback_data="loto_rules")]
    ])
    
    await update.message.reply_text(
        f"🎰 *LOTERIE*\n\n"
        f"💰 Votre solde : *{balance} FCFA*\n"
        f"🎫 Prix du ticket : *{TICKET_PRICE} FCFA*\n\n"
        f"🥇 *Jackpot* : 2000 FCFA (5%)\n"
        f"🥈 *Lien boosté* : 500 FCFA/filleul (10%)\n"
        f"🥉 *Lien boosté* : 500 FCFA/filleul (15%)\n"
        f"❌ *Perdu* (70%)\n\n"
        f"Tentez votre chance !",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )


# ==================== CALLBACKS ====================

async def handle_loto_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    data = query.data
    
    if data == "loto_rules":
        await query.edit_message_text(
            f"📋 *RÈGLES*\n\n"
            f"🎫 Ticket : {TICKET_PRICE} FCFA\n\n"
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
            await query.edit_message_text("📊 Aucun gain pour le moment.", parse_mode='Markdown')
            return
        text = "📊 *VOS GAINS :*\n\n"
        for link in links:
            status = "✅ Actif" if link[4] < 10 else "❌ Épuisé"
            text += f"🔗 `{link[2]}` | +{link[3]} FCFA | {status}\n"
        await query.edit_message_text(text, parse_mode='Markdown')
        return
    
    if data == "loto_buy":
        cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user.id,))
        bal = cursor.fetchone()
        
        if not bal or bal[0] < TICKET_PRICE:
            await query.edit_message_text("❌ Solde insuffisant pour acheter un ticket.", parse_mode='Markdown')
            return
        
        # Débiter
        cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (TICKET_PRICE, user.id))
        conn.commit()
        
        # Tirage
        resultat, valeur = effectuer_tirage()
        
        if resultat == "jackpot":
            cursor.execute("UPDATE users SET balance = balance + 2000 WHERE user_id = ?", (user.id,))
            conn.commit()
            await query.edit_message_text(
                f"🎉 *JACKPOT !*\n\n+2000 FCFA ajoutés à votre compte !",
                parse_mode='Markdown'
            )
            # Notifier admin
            try:
                await context.bot.send_message(
                    ADMIN_ID,
                    f"🎉 Jackpot gagné par {user.first_name} (ID: `{user.id}`)",
                    parse_mode='Markdown'
                )
            except:
                pass
        
        elif resultat == "boost":
            code = generer_code_boost()
            cursor.execute("INSERT INTO boosted_links (owner_id, code, bonus_amount) VALUES (?, ?, ?)", (user.id, code, 500))
            conn.commit()
            lien = f"https://t.me/{context.bot.username}?start={code}"
            await query.edit_message_text(
                f"🎉 *LIEN BOOSTÉ GAGNÉ !*\n\n"
                f"🔗 `{lien}`\n"
                f"💰 +500 FCFA par filleul\n"
                f"👥 Utilisable 10 fois",
                parse_mode='Markdown'
            )
            try:
                await context.bot.send_message(
                    ADMIN_ID,
                    f"🎉 Lien boosté gagné par {user.first_name} (ID: `{user.id}`)",
                    parse_mode='Markdown'
                )
            except:
                pass
        
        else:
            await query.edit_message_text(
                f"😞 *PERDU !*\n\nRetentez votre chance !",
                parse_mode='Markdown'
            )


# ==================== HANDLER BOUTON MENU ====================

async def handle_loto_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🎰 Loterie":
        await menu_loterie(update, context)


# ==================== ENREGISTREMENT ====================

def enregistrer(app):
    app.add_handler(CallbackQueryHandler(handle_loto_callback, pattern="^loto_"))
    app.add_handler(MessageHandler(filters.Regex(r'^🎰 Loterie$'), handle_loto_button))
    print("✅ Loterie corrigée enregistrée")


print("✅ Module loterie_fix prêt")
