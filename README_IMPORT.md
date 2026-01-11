# Dossier à importer dans GitHub

Ce dossier contient **uniquement** les fichiers qui doivent être commités dans votre repository GitHub.

## Contenu

### ✅ Fichiers à la racine
- `.gitignore` - Configuration Git pour ignorer les fichiers sensibles
- Tous les fichiers `.md` (documentation)

### ✅ Dossier `frontend/`
- Tout le code source de l'application Next.js
- Configuration Prisma
- Composants React
- Routes API
- **EXCLUS** : `node_modules/`, `.next/`, `.env.local` (déjà dans `.gitignore`)

## Ce qui N'EST PAS inclus (et c'est normal)

- ❌ `backend/` - Pas nécessaire si vous utilisez Supabase
- ❌ `frontend/.env.local` - Fichier de secrets (ne doit JAMAIS être commité)
- ❌ `frontend/node_modules/` - Dépendances (seront installées via `npm install`)
- ❌ `frontend/.next/` - Build Next.js (sera généré lors du build)
- ❌ Tous les fichiers listés dans `.gitignore`

## Instructions pour importer dans GitHub

1. **Créer un nouveau repository GitHub** (ou utiliser un existant)

2. **Initialiser Git dans ce dossier** :
   ```bash
   cd /Users/glenn/Desktop/procedures/importergithub
   git init
   git add .
   git commit -m "Initial commit: Application Next.js avec Supabase"
   ```

3. **Connecter au repository GitHub** :
   ```bash
   git remote add origin https://github.com/VOTRE-USERNAME/VOTRE-REPO.git
   git branch -M main
   git push -u origin main
   ```

4. **Vérifier que `.env.local` n'est PAS commité** :
   ```bash
   git ls-files | grep .env
   ```
   (Ne doit rien retourner)

## Structure finale dans GitHub

```
procedures/
├── .gitignore
├── README.md
├── DEPLOYMENT_SUPABASE.md
├── DEPLOYMENT_VERCEL.md
├── [autres fichiers .md]
└── frontend/
    ├── app/
    ├── components/
    ├── lib/
    ├── prisma/
    ├── package.json
    ├── vercel.json
    └── ...
```

## Important

⚠️ **NE COMMITEZ JAMAIS** :
- Les fichiers `.env.local` ou `.env`
- Les secrets (mots de passe, clés API)
- Les dossiers `node_modules/` ou `.next/`

Ces fichiers sont déjà dans `.gitignore` et seront automatiquement ignorés par Git.
