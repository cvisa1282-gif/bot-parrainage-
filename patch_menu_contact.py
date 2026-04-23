fichier = 'menu_buttons.py'

with open(fichier, 'r') as f:
    contenu = f.read()

ancien = "async def btn_signaler"
nouveau = """async def btn_contact(update, context):
    from signaler import menu_contact
    await menu_contact(update, context)

async def btn_signaler"""

contenu = contenu.replace(ancien, nouveau)

ancien2 = "elif txt == \"Signaler\":"
nouveau2 = """elif txt == "Contact":
        await btn_contact(update, context)
    elif txt == "Signaler":"""

contenu = contenu.replace(ancien2, nouveau2)

ancien3 = "pattern = r'^(Solde|Parrainage|Retrait|Signaler)$'"
nouveau3 = "pattern = r'^(Solde|Parrainage|Retrait|Signaler|Contact)$'"

contenu = contenu.replace(ancien3, nouveau3)

with open(fichier, 'w') as f:
    f.write(contenu)

print("OK")
