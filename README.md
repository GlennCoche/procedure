# Système de Procédures de Maintenance Photovoltaïque

Application web complète pour la gestion et l'exécution de procédures de maintenance sur les centrales photovoltaïques.

## 🚀 Fonctionnalités

- **Authentification sécurisée** avec rôles (Admin, Technicien)
- **Reconnaissance d'équipements** via IA (OpenAI Vision)
- **Exécution de procédures** étape par étape avec suivi de progression
- **Création de procédures** avec éditeur visuel et logigrammes
- **Chat IA** (texte et vocal) pour assistance technique
- **Base de connaissances** Tips/Astuces avec recherche
- **Interface moderne** style Apple, responsive et accessible

## 🏗️ Architecture

### Next.js Full-Stack

L'application utilise une architecture **Next.js Full-Stack** :

- **Frontend** : Next.js 14+ (App Router) avec React et TypeScript
- **Backend** : API Routes Next.js (`/app/api/*`)
- **Base de données** : PostgreSQL (Supabase) via Prisma ORM
- **Déploiement** : Vercel (frontend + API) + Supabase (base de données)

```
Next.js Application
├── Frontend (React/Next.js Pages)
├── API Routes (/app/api/*)
├── Prisma ORM
└── Supabase PostgreSQL
```

## 📋 Prérequis

- Node.js 18+
- npm ou yarn
- Clé API OpenAI
- Compte Supabase (gratuit)
- Compte Vercel (gratuit)

## 🚀 Installation et Démarrage

### 1. Cloner le projet

```bash
git clone <votre-repo>
cd procedures
```

### 2. Installer les dépendances

```bash
cd frontend
npm install
```

### 3. Configurer les variables d'environnement

Créez `frontend/.env.local` :

```env
# Base de données
# Pour développement local avec SQLite (temporaire)
DATABASE_URL="file:./dev.db"
# Pour production avec Supabase PostgreSQL
# DATABASE_URL="postgresql://user:password@host:port/database?schema=public"

# JWT Authentication
JWT_SECRET="générez-un-secret-sécurisé-avec-openssl-rand-base64-32"

# OpenAI API
OPENAI_API_KEY="sk-votre-clé-api-openai"

# NextAuth
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="générez-un-secret-sécurisé-avec-openssl-rand-base64-32"
```

### 4. Générer le client Prisma

```bash
cd frontend
npx prisma generate
```

### 5. Créer la base de données (développement local)

```bash
cd frontend
npx prisma db push
```

### 6. Démarrer l'application

```bash
cd frontend
npm run dev
```

L'application sera accessible sur `http://localhost:3000`

## 📚 Documentation

### Guides de déploiement

- **`DEPLOYMENT_SUPABASE.md`** : Guide complet pour configurer Supabase
- **`DEPLOYMENT_VERCEL.md`** : Guide complet pour déployer sur Vercel
- **`MIGRATION_DATA.md`** : Guide pour migrer les données SQLite vers Supabase

### Architecture et migration

- **`MIGRATION_NEXTJS_FULLSTACK.md`** : Guide détaillé de la migration vers Next.js Full-Stack
- **`EXEMPLES_MIGRATION.md`** : Exemples de code concrets pour la migration
- **`ARCHITECTURE_ET_ALTERNATIVES.md`** : Explication des alternatives et solutions cloud

## 🛠️ Stack Technique

### Frontend
- Next.js 14+ (App Router)
- TypeScript
- Tailwind CSS + shadcn/ui
- Zustand + React Query
- Prisma Client

### Backend (API Routes)
- Next.js API Routes
- Prisma ORM
- OpenAI API (GPT-4o-mini, Vision API)
- JWT Authentication

### Base de données
- PostgreSQL (Supabase)
- Prisma ORM

## 📁 Structure du Projet

```
procedures/
├── frontend/              # Application Next.js Full-Stack
│   ├── app/
│   │   ├── (auth)/       # Pages d'authentification
│   │   ├── (dashboard)/  # Pages dashboard
│   │   ├── admin/        # Pages admin
│   │   └── api/          # API Routes (Backend)
│   ├── components/       # Composants React
│   ├── lib/              # Utilitaires (api.ts, auth.ts, db.ts)
│   ├── prisma/           # Schéma Prisma
│   └── ...
├── backend/              # ⚠️ Déprécié (gardé pour référence)
└── docs/                 # Documentation
```

## 🔐 Authentification

L'authentification utilise des **cookies HTTP-only** pour la sécurité :

- **Login** : `POST /api/auth/login`
- **Register** : `POST /api/auth/register`
- **Me** : `GET /api/auth/me`
- **Logout** : `POST /api/auth/logout`

Les cookies sont automatiquement inclus dans les requêtes `fetch()` sur la même origine.

## 🗄️ Base de Données

### Schéma Prisma

Le schéma Prisma est défini dans `frontend/prisma/schema.prisma` :

- `User` : Utilisateurs
- `Procedure` : Procédures de maintenance
- `Step` : Étapes des procédures
- `Execution` : Exécutions de procédures
- `StepExecution` : Exécutions d'étapes
- `Tip` : Tips et astuces
- `ChatMessage` : Messages de chat IA

### Commandes Prisma

```bash
# Générer le client Prisma
npx prisma generate

# Créer/mettre à jour la base de données
npx prisma db push

# Ouvrir Prisma Studio (interface graphique)
npx prisma studio

# Créer une migration
npx prisma migrate dev --name nom_migration

# Appliquer les migrations (production)
npx prisma migrate deploy
```

## 🌐 Déploiement

### Développement local

```bash
cd frontend
npm run dev
```

### Production (Vercel + Supabase)

1. **Configurer Supabase** : Voir `DEPLOYMENT_SUPABASE.md`
2. **Déployer sur Vercel** : Voir `DEPLOYMENT_VERCEL.md`

## 🔧 Scripts Disponibles

```bash
# Développement
npm run dev

# Build de production
npm run build

# Démarrer en production
npm run start

# Linter
npm run lint

# Prisma
npm run db:migrate    # Appliquer les migrations
npm run db:studio     # Ouvrir Prisma Studio
```

## 📝 Variables d'Environnement

| Variable | Description | Exemple |
|----------|-------------|---------|
| `DATABASE_URL` | Connection string PostgreSQL | `postgresql://...` |
| `JWT_SECRET` | Secret pour signer les JWT | `généré avec openssl` |
| `OPENAI_API_KEY` | Clé API OpenAI | `sk-...` |
| `NEXTAUTH_URL` | URL de l'application | `http://localhost:3000` |
| `NEXTAUTH_SECRET` | Secret NextAuth | `généré avec openssl` |

## 🐛 Troubleshooting

### Erreur Prisma

```bash
# Régénérer le client Prisma
npx prisma generate
```

### Erreur de connexion à la base de données

- Vérifiez que `DATABASE_URL` est correct
- Vérifiez que Supabase est accessible
- Vérifiez les politiques RLS sur Supabase

### Erreur d'authentification

- Vérifiez que les cookies sont bien définis
- Vérifiez que `JWT_SECRET` est configuré
- Vérifiez les logs dans la console du navigateur

## 📖 Ressources

- [Documentation Next.js](https://nextjs.org/docs)
- [Documentation Prisma](https://www.prisma.io/docs)
- [Documentation Supabase](https://supabase.com/docs)
- [Documentation Vercel](https://vercel.com/docs)

## 📄 Licence

Ce projet est privé.
