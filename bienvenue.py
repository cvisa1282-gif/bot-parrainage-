import sqlite3
import random
import string
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CommandHandler


async def start_bienvenue(update: Update, context):
    user = update.effective_user
    args = context.args

    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user.id,))
    existe = c.fetchone()

    if not existe:
        ref_code = "REF" + str(user.id) + ''.join(random.choices(string.digits, k=4))
        parrain_id = None
        if args and args[0].startswith("REF"):
            c.execute("SELECT user_id FROM users WHERE referral_code = ?", (args[0],))
            res = c.fetchone()
            if res:
                parrain_id = res[0]
        c.execute("INSERT INTO users (user_id, username, first_name, parrain_id, referral_code, balance) VALUES (?, ?, ?, ?, ?, ?)",
                  (user.id, user.username, user.first_name, parrain_id, ref_code, 150))
        if parrain_id:
            c.execute("UPDATE users SET balance = balance + 300 WHERE user_id = ?", (parrain_id,))
        conn.commit()
    conn.close()

    text = (
        "BIENVENUE SUR SAMS-JOB !\n\n"
        "Gagnez de l'argent en invitant vos amis.\n\n"
        "FONCTIONNEMENT :\n"
        "1. Partagez votre lien de parrainage\n"
        "2. Vos amis rejoignent le bot via votre lien\n"
        "3. Vous gagnez 300 FCFA par filleul\n"
        "4. Vos filleuls recoivent 150 FCFA\n"
        "5. Retrait possible des 5000 FCFA\n\n"
        "METHODES DE RETRAIT :\n"
        "- Moov Money Flooz\n"
        "- Miss by YAS\n\n"
        "SECURITE :\n"
        "- Anti-triche actif 24/7\n"
        "- Comptes suspects automatiquement bloques\n"
        "- Limite de 5 parrainages par heure\n\n"
        "Utilisez les boutons ci-dessous pour naviguer."
    )

    menu_keyboard = [
        ["Solde", "Parrainage"],
        ["Retrait", "Signaler"],
        ["Contact"]
    ]
    reply_markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)

    await update.message.reply_text(text, reply_markup=reply_markup)


def enregistrer(app):
    app.add_handler(CommandHandler("start", start_bienvenue))
