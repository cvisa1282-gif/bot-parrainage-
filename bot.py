#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sqlite3
import random
import string
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# ==================== CONFIGURATION ====================
TOKEN = "8698644284:AAHIC3AqioREc_y3ywc7gCuCH-rtbNXE2HM"
ADMIN_ID = 6610074482
CHANNEL_USERNAME = "@samuel00388"
CHANNEL_LINK = "https://t.me/samuel00388"

# ==================== BASE DE DONNÉES SQLITE ====================
conn = sqlite3.connect('bot_data.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    balance INTEGER DEFAULT 0,
    parrain_id INTEGER,
    referral_code TEXT UNIQUE,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS withdrawals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount INTEGER,
    method TEXT,
    phone TEXT,
    country TEXT,
    status TEXT DEFAULT 'pending',
    admin_note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()

# ==================== ÉTATS CONVERSATION RETRAIT ====================
CHOIX_METHODE, SAISIE_NUMERO, SAISIE_PAYS, SAISIE_MONTANT = range(4)

# ==================== FONCTIONS UTILITAIRES ====================
def generate_referral_code(user_id):
    return f"REF{user_id}{''.join(random.choices(string.digits, k=4))}"

async def check_channel_member(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        chat_member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except:
        return False

def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone()

def create_user(user_id, username, first_name, parrain_id=None):
    if not get_user(user_id):
        ref_code = generate_referral_code(user_id)
        cursor.execute(
            "INSERT INTO users (user_id, username, first_name, parrain_id, referral_code, balance) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, username, first_name, parrain_id, ref_code, 150)
        )
        if parrain_id:
            cursor.execute("UPDATE users SET balance = balance + 300 WHERE user_id = ?", (parrain_id,))
        conn.commit()
    return get_user(user_id)

# ==================== COMMANDES ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args
    
    parrain_id = None
    if args and args[0].startswith("REF"):
        cursor.execute("SELECT user_id FROM users WHERE referral_code = ?", (args[0],))
        res = cursor.fetchone()
        if res:
            parrain_id = res[0]
    
    is_member = await check_channel_member(user.id, context)
    if not is_member:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Rejoindre le canal", url=CHANNEL_LINK)],
            [InlineKeyboardButton("✅ J'ai rejoint", callback_data="check_join")]
        ])
        await update.message.reply_text(
            f"🚫 *Accès restreint*\n\n"
            f"Pour utiliser ce bot, vous devez d'abord rejoindre notre canal officiel :\n{CHANNEL_LINK}\n\n"
            f"Cliquez sur 'J'ai rejoint' après l'avoir fait.",
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        return
    
    user_data = create_user(user.id, user.username, user.first_name, parrain_id)
    
    menu_keyboard = [
        ["💰 Solde", "👥 Parrainage"],
        ["💳 Retrait"]
    ]
    reply_markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)
    
    welcome_text = f"✅ *Bienvenue {user.first_name} !*\n\n"
    welcome_text += f"💰 Votre solde : *{user_data[3]} FCFA*\n"
    welcome_text += f"🔗 Votre lien de parrainage :\n`https://t.me/{context.bot.username}?start={user_data[5]}`"
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def check_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    
    if await check_channel_member(user.id, context):
        await query.edit_message_text("✅ Vérification réussie ! Utilisez /start pour commencer.")
    else:
        await query.answer("❌ Vous n'avez pas encore rejoint le canal !", show_alert=True)

async def solde(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = get_user(user.id)
    if user_data:
        await update.message.reply_text(f"💰 Votre solde actuel : *{user_data[3]} FCFA*", parse_mode='Markdown')
    else:
        await update.message.reply_text("Utilisez /start d'abord.")

async def parrainage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = get_user(user.id)
    if user_data:
        link = f"https://t.me/{context.bot.username}?start={user_data[5]}"
        await update.message.reply_text(
            f"🔗 *Votre lien de parrainage :*\n`{link}`\n\n"
            f"👥 Parrain : *+300 FCFA*\n🎁 Filleul : *+150 FCFA*",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("Utilisez /start d'abord.")

async def handle_menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "💰 Solde":
        await solde(update, context)
    elif text == "👥 Parrainage":
        await parrainage(update, context)
    elif text == "💳 Retrait":
        await retrait_start(update, context)

# ==================== RETRAIT ====================
async def retrait_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if not await check_channel_member(user.id, context):
        await update.message.reply_text(f"🚫 Rejoignez d'abord {CHANNEL_LINK}")
        return ConversationHandler.END
    
    user_data = get_user(user.id)
    if not user_data or user_data[3] < 5000:
        await update.message.reply_text("❌ Solde insuffisant. Minimum : *5000 FCFA*", parse_mode='Markdown')
        return ConversationHandler.END
    
    keyboard = [
        [InlineKeyboardButton("Moov Money Flooz", callback_data="method_moov")],
        [InlineKeyboardButton("Miss by YAS", callback_data="method_miss")],
        [InlineKeyboardButton("❌ Annuler", callback_data="cancel_retrait")]
    ]
    await update.message.reply_text(
        "💳 *Choisissez votre moyen de retrait :*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return CHOIX_METHODE

async def choix_methode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "cancel_retrait":
        await query.edit_message_text("❌ Demande annulée.")
        return ConversationHandler.END
    
    context.user_data['retrait_method'] = "Moov Money" if "moov" in query.data else "Miss by YAS"
    await query.edit_message_text("📱 *Entrez le numéro de téléphone pour le dépôt :*", parse_mode='Markdown')
    return SAISIE_NUMERO

async def saisie_numero(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['retrait_phone'] = update.message.text
    await update.message.reply_text("🌍 *Entrez votre pays :*", parse_mode='Markdown')
    return SAISIE_PAYS

async def saisie_pays(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['retrait_country'] = update.message.text
    await update.message.reply_text("💵 *Entrez le montant à retirer (FCFA) :*", parse_mode='Markdown')
    return SAISIE_MONTANT

async def saisie_montant(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    try:
        amount = int(update.message.text)
    except:
        await update.message.reply_text("❌ Montant invalide. Annulé.")
        return ConversationHandler.END
    
    user_data = get_user(user.id)
    if not user_data or user_data[3] < amount or amount < 5000:
        await update.message.reply_text("❌ Montant invalide ou inférieur à 5000 FCFA.")
        return ConversationHandler.END
    
    cursor.execute(
        "INSERT INTO withdrawals (user_id, amount, method, phone, country) VALUES (?, ?, ?, ?, ?)",
        (user.id, amount, context.user_data['retrait_method'], context.user_data['retrait_phone'], context.user_data['retrait_country'])
    )
    cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, user.id))
    conn.commit()
    
    withdrawal_id = cursor.lastrowid
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Valider", callback_data=f"val_{withdrawal_id}_{user.id}_{amount}"),
            InlineKeyboardButton("❌ Refuser", callback_data=f"ref_{withdrawal_id}_{user.id}_{amount}")
        ]
    ])
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🔔 *NOUVELLE DEMANDE DE RETRAIT*\n\n"
             f"🆔 ID Retrait : `{withdrawal_id}`\n"
             f"👤 Utilisateur : {user.first_name} (ID: `{user.id}`)\n"
             f"💳 Méthode : {context.user_data['retrait_method']}\n"
             f"📱 Numéro : {context.user_data['retrait_phone']}\n"
             f"🌍 Pays : {context.user_data['retrait_country']}\n"
             f"💰 Montant : *{amount} FCFA*",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )
    
    await update.message.reply_text("✅ Votre demande a été envoyée à l'administration.")
    return ConversationHandler.END

async def cancel_retrait(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Demande annulée.")
    return ConversationHandler.END

# ==================== ADMIN ====================
async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    
    if user.id != ADMIN_ID:
        await query.answer("⛔ Accès refusé.")
        return
    
    await query.answer()
    data = query.data
    
    if data.startswith("val_"):
        parts = data.split("_")
        withdrawal_id = int(parts[1])
        target_user = int(parts[2])
        amount = int(parts[3])
        
        cursor.execute("UPDATE withdrawals SET status = 'validated' WHERE id = ?", (withdrawal_id,))
        conn.commit()
        
        await query.edit_message_text(query.message.text + "\n\n✅ *VALIDÉ*", parse_mode='Markdown')
        await context.bot.send_message(target_user, f"✅ Votre retrait de *{amount} FCFA* a été validé !", parse_mode='Markdown')
        
    elif data.startswith("ref_"):
        parts = data.split("_")
        withdrawal_id = int(parts[1])
        target_user = int(parts[2])
        amount = int(parts[3])
        
        context.user_data['awaiting_refuse'] = True
        context.user_data['refuse_w_id'] = withdrawal_id
        context.user_data['refuse_user'] = target_user
        context.user_data['refuse_amount'] = amount
        
        await query.edit_message_text(query.message.text + "\n\n📝 *Entrez la raison du refus :*", parse_mode='Markdown')

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(balance) FROM users")
    total_balance = cursor.fetchone()[0] or 0
    cursor.execute("SELECT COUNT(*) FROM withdrawals WHERE status = 'pending'")
    pending = cursor.fetchone()[0]
    
    await update.message.reply_text(
        f"📊 *STATISTIQUES*\n\n"
        f"👥 Utilisateurs : {total_users}\n"
        f"💰 Solde total : {total_balance} FCFA\n"
        f"⏳ Retraits en attente : {pending}",
        parse_mode='Markdown'
    )

async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /broadcast Votre message")
        return
    
    message = " ".join(context.args)
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    count = 0
    for u in users:
        try:
            await context.bot.send_message(u[0], f"📢 *Message de l'administration :*\n\n{message}", parse_mode='Markdown')
            count += 1
            await asyncio.sleep(0.05)
        except:
            pass
    await update.message.reply_text(f"✅ Message envoyé à {count} utilisateurs.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('awaiting_refuse') and update.effective_user.id == ADMIN_ID:
        reason = update.message.text
        w_id = context.user_data['refuse_w_id']
        target_user = context.user_data['refuse_user']
        amount = context.user_data['refuse_amount']
        
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, target_user))
        cursor.execute("UPDATE withdrawals SET status = 'refused', admin_note = ? WHERE id = ?", (reason, w_id))
        conn.commit()
        
        await context.bot.send_message(target_user, f"❌ Votre retrait de *{amount} FCFA* a été refusé.\n📝 Raison : {reason}", parse_mode='Markdown')
        await update.message.reply_text("✅ Refus enregistré et utilisateur remboursé.")
        context.user_data['awaiting_refuse'] = False

# ==================== MAIN ====================
def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("solde", solde))
    app.add_handler(CommandHandler("parrainage", parrainage))
    app.add_handler(CommandHandler("stats", admin_stats))
    app.add_handler(CommandHandler("broadcast", admin_broadcast))
    
    app.add_handler(CallbackQueryHandler(check_join_callback, pattern="^check_join$"))
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^(val_|ref_)"))
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("retrait", retrait_start)],
        states={
            CHOIX_METHODE: [CallbackQueryHandler(choix_methode, pattern=None)],
            SAISIE_NUMERO: [MessageHandler(filters.TEXT & ~filters.COMMAND, saisie_numero)],
            SAISIE_PAYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, saisie_pays)],
            SAISIE_MONTANT: [MessageHandler(filters.TEXT & ~filters.COMMAND, saisie_montant)],
        },
        fallbacks=[CommandHandler("cancel", cancel_retrait)]
    )
    app.add_handler(conv_handler)
    
    app.add_handler(MessageHandler(filters.Regex(r'^(💰 Solde|👥 Parrainage|💳 Retrait)$'), handle_menu_buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot démarré...")
    app.run_polling()

if __name__ == '__main__':
    main()
