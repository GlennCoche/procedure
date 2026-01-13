# Guide d'Import de Données de Test

Ce guide explique comment remplir la base de données avec des données de test à partir de documents techniques (PDF, manuels, etc.).

## 📋 Vue d'ensemble

Deux scripts sont disponibles pour créer des données de test :

1. **`seed_test_data.py`** : Script rapide avec des données d'exemple pré-définies (basées sur le document Huawei EMMA)
2. **`import_test_data.py`** : Script avancé pour parser des documents PDF et créer automatiquement des procédures

## 🚀 Méthode 1 : Seed rapide (Recommandé pour commencer)

Cette méthode utilise des données pré-définies basées sur le document Huawei EMMA.

### Prérequis

- Le backend doit être démarré sur `http://localhost:8000`
- Un utilisateur admin doit exister (par défaut: `admin@procedures.local` / `admin123`)

### Utilisation

```bash
# Depuis la racine du projet
cd scripts
python3 seed_test_data.py
```

### Options

```bash
# Spécifier l'URL de l'API
python3 seed_test_data.py --api-url http://localhost:8000

# Spécifier les identifiants admin
python3 seed_test_data.py --email admin@procedures.local --password admin123
```

### Données créées

- **6 procédures** basées sur les alarmes Huawei EMMA :
  - 4000: Inverter Communication Error
  - 4001: App Communication Certificate Expired
  - 4003: Auxiliary Power Fault
  - 4004: Abnormal DI Instruction
  - 4006: Charger Communication Error
  - 4013: BackupBox Overload

- **4 tips généraux** de maintenance et diagnostic
- **6 tips de référence** (un par alarme) avec les détails complets

## 📄 Méthode 2 : Import depuis PDF

Cette méthode permet d'importer des données depuis des documents PDF techniques.

### Installation des dépendances

```bash
# Installer les bibliothèques de parsing PDF
pip install PyPDF2 pdfplumber

# Ou ajouter à requirements.txt et installer
pip install -r backend/requirements.txt
```

### Utilisation

```bash
# Parser un PDF et créer les procédures
python3 import_test_data.py --pdf chemin/vers/document.pdf --brand Huawei

# Mode test (sans insertion en base)
python3 import_test_data.py --pdf document.pdf --brand Huawei --dry-run
```

### Options

```bash
python3 import_test_data.py \
  --pdf Alarm_Reference_EMMA_V02_2024-01-19_EN.pdf \
  --api-url http://localhost:8000 \
  --email admin@procedures.local \
  --password admin123 \
  --brand Huawei
```

### Format de document supporté

Le script parse les documents au format **Huawei EMMA Alarm Reference** :
- Détecte les alarmes par leur ID (format: "2 4000 Alarm Name")
- Extrait la sévérité (Critical, Major, Minor, Warning)
- Extrait les causes possibles
- Extrait les suggestions de résolution

## 🔧 Structure des données créées

### Procédures

Chaque alarme est convertie en une procédure avec :

- **Titre** : "Résolution alarme [ID]: [Nom] ([Marque])"
- **Description** : Description complète avec sévérité
- **Catégorie** : "Alarmes [Marque]"
- **Tags** : [Marque, Alarme-ID, Sévérité, maintenance]
- **Étapes** :
  1. Identifier l'alarme
  2. Une étape par cause possible
  3. Une étape par suggestion

### Tips

Deux types de tips sont créés :

1. **Tips généraux** : Conseils de maintenance et diagnostic
2. **Tips de référence** : Référence complète pour chaque alarme avec causes et suggestions

## 📊 Exemple de données créées

### Procédure exemple

```json
{
  "title": "Résolution alarme 4000: Inverter Communication Error (Huawei)",
  "description": "Procédure de résolution pour l'alarme 4000...",
  "category": "Alarmes Huawei",
  "tags": ["Huawei", "Alarme-4000", "major", "maintenance"],
  "steps": [
    {
      "title": "Identifier l'alarme 4000",
      "order": 1,
      "instructions": "Accéder au menu de monitoring..."
    },
    {
      "title": "Vérifier la cause 1",
      "order": 2,
      "instructions": "Vérifier: The cable connection..."
    }
  ]
}
```

## 🎯 Cas d'usage

### Ajouter des documents pour d'autres marques

1. Placez vos documents PDF dans un dossier `docs/`
2. Exécutez le script pour chaque document :

```bash
# Pour SMA
python3 import_test_data.py --pdf docs/SMA_Alarm_Reference.pdf --brand SMA

# Pour Fronius
python3 import_test_data.py --pdf docs/Fronius_Manual.pdf --brand Fronius
```

### Enrichir le contexte du Chat IA

Les tips créés servent de contexte pour le Chat IA. Plus vous ajoutez de documents, plus le Chat IA aura de connaissances.

### Tester toutes les fonctionnalités

Avec les données de seed, vous pouvez tester :
- ✅ Liste des procédures
- ✅ Détails d'une procédure
- ✅ Exécution d'une procédure étape par étape
- ✅ Recherche de tips
- ✅ Chat IA avec contexte
- ✅ Reconnaissance d'équipement

## 🐛 Dépannage

### Erreur de connexion

Vérifiez que :
- Le backend est démarré (`http://localhost:8000`)
- Les identifiants admin sont corrects
- L'utilisateur a le rôle "admin"

### Erreur de parsing PDF

- Vérifiez que le PDF n'est pas protégé par mot de passe
- Le format doit être similaire au document Huawei EMMA
- Utilisez `--dry-run` pour voir ce qui serait extrait

### Procédures dupliquées

Si vous réexécutez le script, les procédures seront créées à nouveau. Pour éviter les doublons :
- Supprimez les procédures existantes via l'interface admin
- Ou modifiez le script pour vérifier l'existence avant création

## 📝 Prochaines étapes

1. **Ajouter plus de documents** : Placez vos documents PDF dans `docs/` et importez-les
2. **Personnaliser les procédures** : Modifiez les procédures créées via l'interface admin
3. **Enrichir les tips** : Ajoutez vos propres tips via l'interface ou le script
4. **Tester le Chat IA** : Posez des questions sur les alarmes et procédures

## 🔗 Ressources

- Document Huawei EMMA : `Alarm_Reference_EMMA_V02_2024-01-19_EN.pdf`
- API Documentation : `http://localhost:8000/docs`
- Interface Admin : `http://localhost:3000/admin`
