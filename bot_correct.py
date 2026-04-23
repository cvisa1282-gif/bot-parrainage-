#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sqlite3
import random
import string
import asyncio
from datetime import datetime
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# ==================== CONFIGURATION ====================
TOKEN = "8698644284:AAHIC3AqioREc_y3ywc7gCuCH-rtbNXE2HM"
ADMIN_ID = 6610074482
CHANNEL_USERNAME = "@samuel00388"
CHANNEL_LINK = "https://t.me/samuel00388"

# ==================== BASE DE DONNÉES ====================
conn = sqlite3.connect('bot_data.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, balance INTEGER DEFAULT 0, parrain_id INTEGER, referral_code TEXT UNIQUE, joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS withdrawals (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, amount INTEGER, method TEXT, phone TEXT, country TEXT, status TEXT DEFAULT 'pending', admin_note TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
conn.commit()

CHOIX_METHODE, SAISIE_NUMERO, SAISIE_PAYS, SAISIE_MONTANT = range(4)

# ==================== FONCTIONS UTILITAIRES ====================
def generate_referral_code(user_id):
    return f"REF{user_id}{''.join(random.choices(string.digits, k=4))}"

async def check_channel_member(user_id, context):
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
        cursor.execute("INSERT INTO users (user_id, username, first_name, parrain_id, referral_code, balance) VALUES (?, ?, ?, ?, ?, ?)", (user_id, username, first_name, parrain_id, ref_code, 150))
        if parrain_id:
            cursor.execute("UPDATE users SET balance = balance + 300 WHERE user_id = ?", (parrain_id,))
        conn.commit()
    return get_user(user_id)

# ==================== COMMANDES DE BASE ====================
async def solde(update, context):
    user = update.effective_user
    user_data = get_user(user.id)
    if user_data:
        await update.message.reply_text(f"💰 Solde : *{user_data[3]} FCFA*", parse_mode='Markdown')

async def parrainage(update, context):
    user = update.effective_user
    user_data = get_user(user.id)
    if user_data:
        link = f"https://t.me/{context.bot.username}?start={user_data[5]}"
        await update.message.reply_text(f"🔗 Lien : `{link}`\n👥 Parrain : +300 FCFA\n🎁 Filleul : +150 FCFA", parse_mode='Markdown')

# ==================== RETRAIT ====================
async def retrait_start(update, context):
    user = update.effective_user
    user_data = get_user(user.id)
    if not user_data or user_data[3] < 5000:
        await update.message.reply_text("❌ Solde insuffisant. Minimum 5000 FCFA.")
        return ConversationHandler.END
    keyboard = [[InlineKeyboardButton("Moov Money", callback_data="method_moov")], [InlineKeyboardButton("Miss by YAS", callback_data="method_miss")], [InlineKeyboardButton("❌ Annuler", callback_data="cancel_retrait")]]
    await update.message.reply_text("💳 Choisissez :", reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOIX_METHODE

async def choix_methode(update, context):
    query = update.callback_query
    await query.answer()
    if query.data == "cancel_retrait":
        await query.edit_message_text("❌ Annulé.")
        return ConversationHandler.END
    context.user_data['retrait_method'] = "Moov Money" if "moov" in query.data else "Miss by YAS"
    await query.edit_message_text("📱 Numéro :")
    return SAISIE_NUMERO

async def saisie_numero(update, context):
    context.user_data['retrait_phone'] = update.message.text
    await update.message.reply_text("🌍 Pays :")
    return SAISIE_PAYS

async def saisie_pays(update, context):
    context.user_data['retrait_country'] = update.message.text
    await update.message.reply_text("💵 Montant (FCFA) :")
    return SAISIE_MONTANT

async def saisie_montant(update, context):
    user = update.effective_user
    try:
        amount = int(update.message.text)
    except:
        await update.message.reply_text("❌ Invalide.")
        return ConversationHandler.END
    user_data = get_user(user.id)
    if not user_data or user_data[3] < amount or amount < 5000:
        await update.message.reply_text("❌ Montant invalide.")
        return ConversationHandler.END
    cursor.execute("INSERT INTO withdrawals (user_id, amount, method, phone, country) VALUES (?,?,?,?,?)", (user.id, amount, context.user_data['retrait_method'], context.user_data['retrait_phone'], context.user_data['retrait_country']))
    cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, user.id))
    conn.commit()
    wid = cursor.lastrowid
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Valider", callback_data=f"val_{wid}_{user.id}_{amount}"), InlineKeyboardButton("❌ Refuser", callback_data=f"ref_{wid}_{user.id}_{amount}")]])
    await context.bot.send_message(ADMIN_ID, f"🔔 Retrait\n🆔 {wid}\n👤 {user.first_name} (`{user.id}`)\n💳 {context.user_data['retrait_method']}\n📱 {context.user_data['retrait_phone']}\n🌍 {context.user_data['retrait_country']}\n💰 {amount} FCFA", reply_markup=keyboard, parse_mode='Markdown')
    await update.message.reply_text("✅ Demande envoyée.")
    return ConversationHandler.END

async def cancel_retrait(update, context):
    await update.message.reply_text("❌ Annulé.")
    return ConversationHandler.END

# ==================== ADMIN ====================
async def admin_callback(update, context):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("⛔ Accès refusé.")
        return
    await query.answer()
    data = query.data
    if data.startswith("val_"):
        _, wid, target, amount = data.split("_")
        cursor.execute("UPDATE withdrawals SET status='validated' WHERE id=?", (int(wid),))
        conn.commit()
        await query.edit_message_text(query.message.text + "\n\n✅ VALIDÉ", parse_mode='Markdown')
        await context.bot.send_message(int(target), f"✅ Retrait de {amount} FCFA validé !")
    elif data.startswith("ref_"):
        _, wid, target, amount = data.split("_")
        context.user_data.update({'awaiting_refuse': True, 'refuse_w_id': int(wid), 'refuse_user': int(target), 'refuse_amount': int(amount)})
        await query.edit_message_text(query.message.text + "\n\n📝 Raison du refus :", parse_mode='Markdown')

async def admin_stats(update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    cursor.execute("SELECT COUNT(*), SUM(balance) FROM users")
    total, total_bal = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) FROM withdrawals WHERE status='pending'")
    pending = cursor.fetchone()[0]
    await update.message.reply_text(f"📊 Stats\n👥 {total} users\n💰 {total_bal or 0} FCFA\n⏳ {pending} retraits")

async def admin_broadcast(update, context):
    if update.effective_user.id != ADMIN_ID or not context.args:
        return
    msg = " ".join(context.args)
    cursor.execute("SELECT user_id FROM users")
    count = 0
    for u in cursor.fetchall():
        try:
            await context.bot.send_message(u[0], f"📢 {msg}")
            count += 1
            await asyncio.sleep(0.05)
        except:
            pass
    await update.message.reply_text(f"✅ Envoyé à {count} users.")

async def handle_message(update, context):
    if context.user_data.get('awaiting_refuse') and update.effective_user.id == ADMIN_ID:
        reason = update.message.text
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (context.user_data['refuse_amount'], context.user_data['refuse_user']))
        cursor.execute("UPDATE withdrawals SET status='refused', admin_note=? WHERE id=?", (reason, context.user_data['refuse_w_id']))
        conn.commit()
        await context.bot.send_message(context.user_data['refuse_user'], f"❌ Retrait refusé.\n📝 {reason}")
        await update.message.reply_text("✅ Refus enregistré.")
        context.user_data['awaiting_refuse'] = False

# ==================== FAUX SERVEUR WEB ====================
class FakeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot running")
    def log_message(self, format, *args):
        pass

def run_web():
    HTTPServer(('0.0.0.0', 10000), FakeHandler).serve_forever()

# ==================== MAIN ====================
def main():
    Thread(target=run_web, daemon=True).start()
    
    app = Application.builder().token(TOKEN).build()
    
    # Handlers de base
    app.add_handler(CommandHandler("solde", solde))
    app.add_handler(CommandHandler("parrainage", parrainage))
    app.add_handler(CommandHandler("stats", admin_stats))
    app.add_handler(CommandHandler("broadcast", admin_broadcast))
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^(val_|ref_)"))
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("retrait", retrait_start)],
        states={
            CHOIX_METHODE: [CallbackQueryHandler(choix_methode)],
            SAISIE_NUMERO: [MessageHandler(filters.TEXT & ~filters.COMMAND, saisie_numero)],
            SAISIE_PAYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, saisie_pays)],
            SAISIE_MONTANT: [MessageHandler(filters.TEXT & ~filters.COMMAND, saisie_montant)],
        },
        fallbacks=[CommandHandler("cancel", cancel_retrait)]
    )
    app.add_handler(conv_handler)
    
    # ========== CONNECTEUR : BRANCHE TOUS LES MODULES ==========
    from connecteur import connecter_tout
    connecter_tout(app)
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Bot opérationnel !")
    app.run_polling()

if __name__ == '__main__':
    main()
