# Étapes Restantes pour Rendre l'Application 100% Fonctionnelle

## Problème Actuel

La page `/startup` essaie de se connecter à un backend FastAPI local (`http://localhost:8000`) qui n'existe pas en production. En production sur Vercel, l'application Next.js utilise ses propres routes API intégrées.

## ✅ Étape 1 : Configurer les Variables d'Environnement sur Vercel

### 1.1 Accéder aux Variables d'Environnement

1. Allez sur [https://vercel.com](https://vercel.com)
2. Sélectionnez votre projet `procedure`
3. Cliquez sur **"Settings"** (en haut)
4. Dans le menu de gauche, cliquez sur **"Environment Variables"**

### 1.2 Ajouter les Variables Requises

Ajoutez **UNE PAR UNE** les variables suivantes. Pour chaque variable :

1. Cliquez sur **"Add New"**
2. Entrez le **Name** (nom de la variable)
3. Entrez la **Value** (valeur)
4. Cochez les environnements : ✅ **Production**, ✅ **Preview**, ✅ **Development**
5. Cliquez sur **"Save"**

#### Variable 1 : DATABASE_URL

**Si vous avez déjà Supabase configuré :**
- Récupérez votre connection string depuis Supabase Dashboard
- Format : `postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres`

**Si vous n'avez pas encore Supabase :**
- Suivez le guide `DEPLOYMENT_SUPABASE.md` pour créer un projet Supabase
- Récupérez la connection string

```
Name: DATABASE_URL
Value: postgresql://postgres:[VOTRE-MOT-DE-PASSE]@db.[PROJECT-REF].supabase.co:5432/postgres
Environments: ✅ Production ✅ Preview ✅ Development
```

#### Variable 2 : JWT_SECRET

Générez un secret sécurisé :

```bash
openssl rand -base64 32
```

Puis ajoutez-le :

```
Name: JWT_SECRET
Value: [Le secret généré]
Environments: ✅ Production ✅ Preview ✅ Development
```

#### Variable 3 : NEXTAUTH_URL

Utilisez l'URL de votre déploiement Vercel :

```
Name: NEXTAUTH_URL
Value: https://procedure1-gz3mi2h0n-glenns-projects-7d11114a.vercel.app
(Remplacez par votre URL Vercel réelle)
Environments: ✅ Production ✅ Preview ✅ Development
```

#### Variable 4 : NEXTAUTH_SECRET

Générez un autre secret :

```bash
openssl rand -base64 32
```

```
Name: NEXTAUTH_SECRET
Value: [Le secret généré]
Environments: ✅ Production ✅ Preview ✅ Development
```

#### Variable 5 : OPENAI_API_KEY (Optionnel)

Seulement si vous utilisez le chat IA ou la vision IA :

```
Name: OPENAI_API_KEY
Value: sk-... (votre clé OpenAI)
Environments: ✅ Production ✅ Preview ✅ Development
```

## ✅ Étape 2 : Appliquer les Migrations Prisma

Après avoir configuré `DATABASE_URL`, vous devez créer les tables dans Supabase.

### Option A : Via Vercel CLI (Recommandé)

```bash
# Installer Vercel CLI globalement
npm i -g vercel

# Se connecter à Vercel
vercel login

# Aller dans le dossier frontend
cd frontend

# Télécharger les variables d'environnement depuis Vercel
vercel env pull .env.local

# Appliquer les migrations
npx prisma migrate deploy
```

### Option B : Via une Route API Temporaire

Créez temporairement une route pour appliquer les migrations :

1. Créez le fichier `frontend/app/api/migrate/route.ts` :

```typescript
import { NextResponse } from 'next/server'
import { exec } from 'child_process'
import { promisify } from 'util'

const execAsync = promisify(exec)

export async function POST(request: Request) {
  // Sécurité : vérifier un secret
  const authHeader = request.headers.get('authorization')
  const secret = process.env.MIGRATE_SECRET || 'temporary-secret-change-me'
  
  if (authHeader !== `Bearer ${secret}`) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  try {
    const { stdout, stderr } = await execAsync('npx prisma migrate deploy')
    return NextResponse.json({ 
      success: true,
      stdout,
      stderr 
    })
  } catch (error: any) {
    return NextResponse.json({ 
      error: error.message,
      stderr: error.stderr 
    }, { status: 500 })
  }
}
```

2. Ajoutez `MIGRATE_SECRET` dans les variables d'environnement Vercel
3. Appelez l'endpoint après le déploiement :

```bash
curl -X POST https://votre-app.vercel.app/api/migrate \
  -H "Authorization: Bearer temporary-secret-change-me"
```

4. **IMPORTANT** : Supprimez cette route après avoir appliqué les migrations !

### Option C : Via Supabase SQL Editor

1. Allez dans Supabase Dashboard > **SQL Editor**
2. Exécutez le schéma Prisma manuellement (voir `frontend/prisma/schema.prisma`)

## ✅ Étape 3 : Créer un Utilisateur Admin

Après les migrations, créez un utilisateur admin pour vous connecter.

### Option A : Via une Route API Temporaire

Créez `frontend/app/api/setup/create-admin/route.ts` :

```typescript
import { NextResponse } from 'next/server'
import { db } from '@/lib/db'
import { hashPassword } from '@/lib/auth'

export async function POST(request: Request) {
  // Sécurité : vérifier un secret
  const authHeader = request.headers.get('authorization')
  const secret = process.env.SETUP_SECRET || 'temporary-secret-change-me'
  
  if (authHeader !== `Bearer ${secret}`) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  try {
    const body = await request.json()
    const { email, password } = body

    if (!email || !password) {
      return NextResponse.json({ error: 'Email et mot de passe requis' }, { status: 400 })
    }

    // Vérifier si l'utilisateur existe déjà
    const existing = await db.user.findUnique({
      where: { email }
    })

    if (existing) {
      return NextResponse.json({ error: 'Utilisateur déjà existant' }, { status: 400 })
    }

    // Créer l'utilisateur admin
    const passwordHash = await hashPassword(password)
    const user = await db.user.create({
      data: {
        email,
        passwordHash,
        role: 'admin'
      }
    })

    return NextResponse.json({ 
      success: true,
      message: 'Admin créé avec succès',
      userId: user.id
    })
  } catch (error: any) {
    return NextResponse.json({ 
      error: error.message 
    }, { status: 500 })
  }
}
```

2. Ajoutez `SETUP_SECRET` dans les variables d'environnement Vercel
3. Appelez l'endpoint :

```bash
curl -X POST https://votre-app.vercel.app/api/setup/create-admin \
  -H "Authorization: Bearer temporary-secret-change-me" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "votre-mot-de-passe-securise"}'
```

4. **IMPORTANT** : Supprimez cette route après avoir créé l'admin !

### Option B : Via Supabase Dashboard

1. Allez dans Supabase Dashboard > **Table Editor** > **users**
2. Ajoutez manuellement un utilisateur avec :
   - `email` : votre email
   - `password_hash` : hash bcrypt de votre mot de passe
   - `role` : `admin`

## ✅ Étape 4 : Adapter la Page /startup pour la Production

La page `/startup` est conçue pour le développement local. En production, elle ne devrait pas essayer de se connecter à un backend local.

### Option A : Désactiver la Page en Production

Modifiez `frontend/app/startup/page.tsx` pour détecter l'environnement :

```typescript
"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

export default function StartupPage() {
  const router = useRouter()

  useEffect(() => {
    // En production, rediriger vers le dashboard
    if (process.env.NODE_ENV === 'production') {
      router.push('/dashboard')
    }
  }, [router])

  // En production, ne rien afficher (redirection en cours)
  if (process.env.NODE_ENV === 'production') {
    return null
  }

  // Code existant pour le développement...
  // ...
}
```

### Option B : Adapter pour Vérifier les Routes API Next.js

Modifiez la page pour vérifier les routes API Next.js au lieu du backend FastAPI :

```typescript
const checkStatus = async () => {
  try {
    // Vérifier les routes API Next.js
    const [backendResponse, frontendResponse] = await Promise.all([
      fetch("/api/procedures").catch(() => null),
      fetch("/api/auth/me").catch(() => null)
    ])
    
    setStatus({
      backend: {
        running: backendResponse?.ok ?? false,
        url: window.location.origin
      },
      frontend: {
        running: frontendResponse?.ok ?? false,
        url: window.location.origin
      }
    })
  } catch (error) {
    console.error("Erreur lors de la vérification:", error)
  }
}
```

## ✅ Étape 5 : Redéployer sur Vercel

Après avoir configuré toutes les variables d'environnement :

1. Allez dans Vercel Dashboard > votre projet
2. Cliquez sur **"Deployments"**
3. Cliquez sur **"Redeploy"** sur le dernier déploiement
4. Ou faites un nouveau commit sur GitHub (Vercel redéploiera automatiquement)

## ✅ Étape 6 : Vérifier le Fonctionnement

1. **Testez la connexion** :
   - Allez sur `https://votre-app.vercel.app/login`
   - Connectez-vous avec l'utilisateur admin créé

2. **Testez les fonctionnalités** :
   - ✅ Login/Register
   - ✅ Liste des procédures (`/procedures`)
   - ✅ Dashboard (`/dashboard`)
   - ✅ Chat IA (`/chat`) - si OPENAI_API_KEY est configuré
   - ✅ Vision IA (`/camera`) - si OPENAI_API_KEY est configuré
   - ✅ Tips (`/tips`)

3. **Vérifiez les logs** :
   - Allez dans Vercel Dashboard > **Deployments** > votre déploiement
   - Cliquez sur **"Functions"** pour voir les logs des routes API

## ✅ Étape 7 : Configurer un Domaine Personnalisé (Optionnel)

1. Dans Vercel Dashboard > **Settings** > **Domains**
2. Ajoutez votre domaine
3. Suivez les instructions pour configurer les DNS
4. Mettez à jour `NEXTAUTH_URL` avec votre nouveau domaine

## 🔧 Résolution des Problèmes Courants

### Erreur "Failed to fetch" sur /startup

**Cause** : La page essaie de se connecter à `localhost:8000` qui n'existe pas en production.

**Solution** : Suivez l'Étape 4 pour adapter ou désactiver la page `/startup`.

### Erreur "Database connection failed"

**Cause** : `DATABASE_URL` n'est pas configuré ou incorrect.

**Solution** :
1. Vérifiez que `DATABASE_URL` est bien dans les variables d'environnement Vercel
2. Vérifiez que la connection string est correcte
3. Vérifiez que les migrations ont été appliquées

### Erreur "Non authentifié"

**Cause** : `JWT_SECRET` n'est pas configuré ou différent entre les environnements.

**Solution** :
1. Vérifiez que `JWT_SECRET` est configuré dans Vercel
2. Assurez-vous d'utiliser le même secret partout

### Erreur Prisma "Table does not exist"

**Cause** : Les migrations n'ont pas été appliquées.

**Solution** : Suivez l'Étape 2 pour appliquer les migrations.

## 📋 Checklist Finale

- [ ] Variables d'environnement configurées sur Vercel
  - [ ] `DATABASE_URL`
  - [ ] `JWT_SECRET`
  - [ ] `NEXTAUTH_URL`
  - [ ] `NEXTAUTH_SECRET`
  - [ ] `OPENAI_API_KEY` (optionnel)
- [ ] Migrations Prisma appliquées
- [ ] Utilisateur admin créé
- [ ] Page `/startup` adaptée pour la production
- [ ] Application redéployée sur Vercel
- [ ] Connexion testée
- [ ] Fonctionnalités testées

Une fois toutes ces étapes complétées, votre application sera 100% fonctionnelle en production ! 🎉
