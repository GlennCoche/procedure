# 🚀 Démarrage Rapide - Seed des Données de Test

## Méthode la plus simple (Recommandée)

```bash
# 1. Assurez-vous que le backend est démarré
cd backend
source venv/bin/activate  # ou votre environnement virtuel
uvicorn app.main:app --reload

# 2. Dans un autre terminal, exécutez le seed
cd scripts
python3 seed_test_data.py
```

C'est tout ! Vous aurez maintenant :
- ✅ 6 procédures de maintenance (alarmes Huawei)
- ✅ 4 tips généraux
- ✅ 6 tips de référence

## Vérification

1. Allez sur http://localhost:3000/dashboard/procedures
2. Vous devriez voir 6 procédures listées
3. Allez sur http://localhost:3000/dashboard/tips
4. Vous devriez voir 10 tips

## Import depuis PDF (Optionnel)

Si vous avez des documents PDF à importer :

```bash
# 1. Installer les dépendances
pip install PyPDF2 pdfplumber

# 2. Importer un PDF
python3 import_test_data.py --pdf chemin/vers/document.pdf --brand "NomMarque"
```

## Besoin d'aide ?

Voir le guide complet : `scripts/README_IMPORT_DATA.md`
