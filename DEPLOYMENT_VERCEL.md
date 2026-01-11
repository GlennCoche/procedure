# Guide de Déploiement Vercel

Ce guide vous explique comment déployer votre application Next.js Full-Stack sur Vercel.

## Prérequis

- Un compte GitHub avec votre code
- Un compte Vercel (gratuit)
- Un projet Supabase configuré (voir `DEPLOYMENT_SUPABASE.md`)

## Étape 1 : Préparer le projet

### 1.1 Structure du projet et GitHub

**IMPORTANT : Ce qui doit être dans GitHub :**

✅ **À COMMITER dans GitHub :**
- Tout le dossier `frontend/` (sauf les fichiers ignorés par `.gitignore`)
- Les fichiers de documentation à la racine (`.md`)
- Le fichier `.gitignore` à la racine
- **PAS** le dossier `backend/` (si vous n'utilisez que Supabase)
- **PAS** les fichiers `.env.local` (déjà dans `.gitignore`)

**Structure recommandée dans GitHub :**
```
procedures/                    # Repository GitHub
├── .gitignore                 # ✅ À commiter
├── README.md                   # ✅ À commiter
├── DEPLOYMENT_SUPABASE.md      # ✅ À commiter
├── DEPLOYMENT_VERCEL.md        # ✅ À commiter
├── frontend/                   # ✅ TOUT le dossier frontend
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── prisma/
│   ├── package.json
│   ├── vercel.json
│   ├── next.config.js
│   └── ... (tout sauf node_modules, .next, .env.local)
└── backend/                    # ❌ PAS nécessaire si vous utilisez Supabase
```

**Ce qui NE DOIT PAS être dans GitHub :**
- ❌ `frontend/.env.local` (contient vos secrets)
- ❌ `frontend/node_modules/` (dépendances)
- ❌ `frontend/.next/` (build)
- ❌ `backend/` (si vous n'utilisez que Supabase)
- ❌ Tous les fichiers listés dans `.gitignore`

### 1.2 Vérifier que .env.local n'est pas commité

Vérifiez que votre `.gitignore` contient bien :
```gitignore
.env
.env.local
.env*.local
```

Puis vérifiez que `.env.local` n'est pas suivi par Git :
```bash
cd /Users/glenn/Desktop/procedures
git status
```

Si `.env.local` apparaît, il ne doit PAS être commité. Il est déjà dans `.gitignore`, donc normalement Git l'ignore automatiquement.

### 1.3 Vérifier le build

Testez le build localement :
```bash
cd frontend
npm run build
```

Si le build échoue, corrigez les erreurs avant de continuer.

## Étape 2 : Créer un compte Vercel

1. Allez sur [https://vercel.com](https://vercel.com)
2. Cliquez sur "Sign Up"
3. Connectez-vous avec GitHub (recommandé)

## Étape 3 : Importer le projet dans Vercel

### 3.1 Créer le projet Vercel

1. Dans le dashboard Vercel, cliquez sur **"Add New..."** > **"Project"**
2. Si c'est la première fois, connectez votre compte GitHub :
   - Cliquez sur **"Import Git Repository"**
   - Autorisez Vercel à accéder à votre GitHub
   - Sélectionnez votre repository `procedures` (ou le nom que vous avez donné)

### 3.2 Configuration du projet (ÉTAPES DÉTAILLÉES)

Une fois votre repository sélectionné, vous verrez la page de configuration. **Configurez EXACTEMENT comme suit :**

#### A. Framework Preset
- **Framework Preset** : `Next.js`
- Vercel devrait détecter automatiquement Next.js, mais vérifiez que c'est bien sélectionné

#### B. Root Directory (CRUCIAL !)
- **Root Directory** : Cliquez sur **"Edit"** à côté de "Root Directory"
- Entrez : `frontend`
- ⚠️ **IMPORTANT** : C'est la partie la plus importante ! Vercel doit savoir que votre application Next.js est dans le sous-dossier `frontend/`, pas à la racine du repository.

#### C. Build & Development Settings
Cliquez sur **"Show Advanced Options"** ou **"Override"** pour personnaliser :

**Build Command :**
```
npm run build
```
(ou laissez par défaut si c'est déjà `npm run build`)

**Output Directory :**
```
.next
```
(ou laissez par défaut)

**Install Command :**
```
npm install
```
(ou laissez par défaut - Vercel exécutera automatiquement `prisma generate` grâce au script `postinstall` dans `package.json`)

#### D. Environment Variables (à configurer APRÈS)
- **Ne configurez PAS les variables d'environnement maintenant**
- Vous les ajouterez à l'Étape 4
- Cliquez simplement sur **"Deploy"** pour l'instant (le premier déploiement échouera probablement, c'est normal)

### 3.3 Résumé de la configuration

Votre configuration devrait ressembler à ceci :

```
Framework Preset: Next.js
Root Directory: frontend
Build Command: npm run build
Output Directory: .next
Install Command: npm install
```

**Capture d'écran mentale :**
```
┌─────────────────────────────────────┐
│ Framework Preset: [Next.js ▼]      │
│ Root Directory: [frontend]  [Edit] │ ← IMPORTANT !
│ Build Command: [npm run build]     │
│ Output Directory: [.next]           │
│ Install Command: [npm install]      │
└─────────────────────────────────────┘
```

## Étape 4 : Configurer les variables d'environnement

### 4.1 Accéder aux variables d'environnement

1. Après le premier déploiement (même s'il échoue), allez dans votre projet Vercel
2. Cliquez sur l'onglet **"Settings"** (en haut de la page)
3. Dans le menu de gauche, cliquez sur **"Environment Variables"**

### 4.2 Variables requises

Ajoutez **UNE PAR UNE** les variables suivantes. Pour chaque variable :

1. Cliquez sur **"Add New"**
2. Entrez le **Name** (nom de la variable)
3. Entrez la **Value** (valeur)
4. Cochez les environnements : ✅ **Production**, ✅ **Preview**, ✅ **Development**
5. Cliquez sur **"Save"**

| Variable | Valeur | Description |
|----------|--------|-------------|
| `DATABASE_URL` | `postgresql://postgres:Xj75c29u-Xpyqh6r@db.mxxggubgvurldcneeter.supabase.co:5432/postgres` | Connection string Supabase (remplacez par la vôtre) |
| `JWT_SECRET` | `votre-secret-jwt` | Secret pour signer les JWT (générez avec `openssl rand -base64 32`) |
| `OPENAI_API_KEY` | `sk-...` | Clé API OpenAI (optionnel, seulement si vous utilisez le chat IA) |
| `NEXTAUTH_URL` | `https://votre-app.vercel.app` | URL de production (Vercel vous donnera l'URL après le premier déploiement) |
| `NEXTAUTH_SECRET` | `votre-secret-nextauth` | Secret NextAuth (générez avec `openssl rand -base64 32`) |

### 4.3 Exemple de configuration

**Variable 1 : DATABASE_URL**
```
Name: DATABASE_URL
Value: postgresql://postgres:Xj75c29u-Xpyqh6r@db.mxxggubgvurldcneeter.supabase.co:5432/postgres
Environments: ✅ Production ✅ Preview ✅ Development
```

**Variable 2 : JWT_SECRET**
```
Name: JWT_SECRET
Value: [Générez avec: openssl rand -base64 32]
Environments: ✅ Production ✅ Preview ✅ Development
```

**Variable 3 : NEXTAUTH_URL**
```
Name: NEXTAUTH_URL
Value: https://votre-app.vercel.app
(Remplacez par l'URL que Vercel vous donne après le premier déploiement)
Environments: ✅ Production ✅ Preview ✅ Development
```

**Variable 4 : NEXTAUTH_SECRET**
```
Name: NEXTAUTH_SECRET
Value: [Générez avec: openssl rand -base64 32]
Environments: ✅ Production ✅ Preview ✅ Development
```

**Variable 5 : OPENAI_API_KEY** (optionnel)
```
Name: OPENAI_API_KEY
Value: sk-... (votre clé OpenAI)
Environments: ✅ Production ✅ Preview ✅ Development
```

### 4.2 Générer les secrets

Générez des secrets sécurisés :

```bash
# JWT_SECRET
openssl rand -base64 32

# NEXTAUTH_SECRET
openssl rand -base64 32
```

### 4.3 Configurer pour tous les environnements

Pour chaque variable, sélectionnez :
- ✅ Production
- ✅ Preview
- ✅ Development

## Étape 5 : Configurer Prisma pour Vercel

### 5.1 Script postinstall

Vérifiez que `package.json` contient :
```json
{
  "scripts": {
    "postinstall": "prisma generate",
    "db:migrate": "prisma migrate deploy"
  }
}
```

### 5.2 Vérification du script postinstall

Le script `postinstall` dans `package.json` s'exécutera automatiquement après `npm install` sur Vercel. Vérifiez que votre `frontend/package.json` contient :

```json
{
  "scripts": {
    "postinstall": "prisma generate"
  }
}
```

**Note** : Si vous avez déjà ajouté `postinstall` dans `package.json`, vous n'avez rien à faire. Vercel exécutera automatiquement `prisma generate` après l'installation des dépendances.

### 5.3 Build Command personnalisé (optionnel)

Si vous voulez personnaliser davantage, allez dans **Settings** > **General** > **Build & Development Settings** :

**Build Command** :
```bash
npm run build
```

**Install Command** (déjà géré par postinstall) :
```bash
npm install
```
(Le `prisma generate` sera exécuté automatiquement via `postinstall`)

## Étape 6 : Déployer

1. Cliquez sur "Deploy"
2. Vercel va :
   - Installer les dépendances
   - Générer le client Prisma
   - Builder l'application
   - Déployer sur leur CDN

3. Attendez 2-5 minutes

## Étape 7 : Appliquer les migrations

Après le premier déploiement, appliquez les migrations Prisma :

### Option 1 : Via Vercel CLI

```bash
npm i -g vercel
vercel login
cd frontend
vercel env pull .env.local
npx prisma migrate deploy
```

### Option 2 : Via Vercel Functions

Créez une route API temporaire pour appliquer les migrations :

```typescript
// app/api/migrate/route.ts (À SUPPRIMER APRÈS)
import { NextResponse } from 'next/server'
import { exec } from 'child_process'
import { promisify } from 'util'

const execAsync = promisify(exec)

export async function POST(request: Request) {
  // Sécurité : vérifier un secret
  const authHeader = request.headers.get('authorization')
  if (authHeader !== `Bearer ${process.env.MIGRATE_SECRET}`) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  try {
    const { stdout, stderr } = await execAsync('npx prisma migrate deploy')
    return NextResponse.json({ stdout, stderr })
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}
```

**Important** : Supprimez cette route après avoir appliqué les migrations !

## Étape 8 : Vérifier le déploiement

1. Vérifiez l'URL de production (ex: `https://votre-app.vercel.app`)
2. Testez les fonctionnalités :
   - ✅ Login/Register
   - ✅ Liste des procédures
   - ✅ Chat IA
   - ✅ Vision IA
   - ✅ Tips

## Étape 9 : Configurer un domaine personnalisé (optionnel)

1. Dans **Settings** > **Domains**
2. Ajoutez votre domaine
3. Suivez les instructions pour configurer les DNS

## Étape 10 : Monitoring et Logs

### 10.1 Voir les logs

1. Allez dans **Deployments**
2. Cliquez sur un déploiement
3. Cliquez sur "Functions" pour voir les logs des API routes

### 10.2 Analytics

Vercel Analytics est disponible dans le plan gratuit (limité).

## Configuration avancée

### Headers de sécurité

Le fichier `vercel.json` contient déjà des headers de sécurité. Vous pouvez ajouter :

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    }
  ]
}
```

### Redirects

Pour rediriger `/` vers `/login` :

```json
{
  "redirects": [
    {
      "source": "/",
      "destination": "/login",
      "permanent": false
    }
  ]
}
```

## Rollback en cas de problème

1. Allez dans **Deployments**
2. Trouvez le dernier déploiement qui fonctionnait
3. Cliquez sur les "..." > "Promote to Production"

## Limites du plan gratuit

- **100 GB** de bande passante par mois
- **100 heures** de build time par mois
- **100 fonctions serverless** simultanées
- **10 secondes** de timeout pour les fonctions

## Optimisations

### 1. Optimiser les images

Utilisez `next/image` pour toutes les images.

### 2. Cache les réponses API

Ajoutez des headers de cache dans vos routes API :

```typescript
return NextResponse.json(data, {
  headers: {
    'Cache-Control': 'public, s-maxage=60, stale-while-revalidate=300',
  },
})
```

### 3. Réduire la taille du bundle

- Utilisez `next/dynamic` pour le code splitting
- Analysez le bundle avec `@next/bundle-analyzer`

## Troubleshooting

### Erreur "Module not found"

- Vérifiez que toutes les dépendances sont dans `package.json`
- Vérifiez que `node_modules` n'est pas dans `.gitignore` (il ne devrait pas l'être)

### Erreur Prisma

- Vérifiez que `prisma generate` est dans `postinstall`
- Vérifiez que `DATABASE_URL` est correctement configuré

### Erreur de build

- Vérifiez les logs dans Vercel
- Testez le build localement : `npm run build`

### Timeout des fonctions

- Les fonctions ont un timeout de 10s sur le plan gratuit
- Optimisez les requêtes longues (chat IA, vision)
- Utilisez le streaming pour les réponses longues

### Erreur CORS

- Vérifiez que les headers CORS sont correctement configurés dans `vercel.json`
- Vérifiez que `NEXTAUTH_URL` correspond à votre domaine

## Support

- Documentation Vercel : [https://vercel.com/docs](https://vercel.com/docs)
- Discord Vercel : [https://vercel.com/discord](https://vercel.com/discord)
