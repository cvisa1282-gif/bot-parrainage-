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

    text = ("\n".join([
        "Bienvenue " + str(user.first_name) + " !",
        "",
        "Solde - Consultez votre argent",
        "Parrainage - Gagnez +300 FCFA par filleul",
        "Retrait - Retirez des 5000 FCFA",
        "Signaler - Signalez un probleme",
        "",
        "Securite active 24/7",
        "",
        "Bonne chance !"
    ]))

    menu_keyboard = [
        ["Solde", "Parrainage"],
        ["Retrait", "Signaler"]
    ]
    reply_markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)

    await update.message.reply_text(text, reply_markup=reply_markup)


def enregistrer(app):
    app.add_handler(CommandHandler("start", start_bienvenue))


print("Module bienvenue pret")
