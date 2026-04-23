fichier = 'bienvenue.py'

with open(fichier, 'r') as f:
    contenu = f.read()

ancien = '["Retrait", "Signaler"]'
nouveau = '["Retrait", "Signaler"],\n        ["Contact"]'

contenu = contenu.replace(ancien, nouveau)

with open(fichier, 'w') as f:
    f.write(contenu)

print("OK")
