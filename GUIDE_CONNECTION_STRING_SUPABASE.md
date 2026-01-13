# 📋 Guide : Copier la Connection String avec Pooler

**Date :** 2026-01-13

---

## 🎯 Objectif

Récupérer la **Connection String avec Connection Pooler** pour Vercel.

---

## 📍 Où Trouver la Connection String

La connection string se trouve dans la page **"Project Settings"** (pas "Database Settings").

### Méthode 1 : Via Project Settings (Recommandé)

1. **Aller sur** : https://supabase.com/dashboard/project/mxxggubgvurldcneeter/settings/general
   - OU cliquer sur **"Project Settings"** dans le menu latéral gauche
   - OU aller sur : https://supabase.com/dashboard/project/mxxggubgvurldcneeter/settings

2. **Scroller jusqu'à la section "Database"** ou "Connection string"

3. **Trouver la section "Connection string"** qui contient :
   - Un onglet ou sélecteur : **"Connection pooling"** vs **"Direct connection"**
   - OU deux sections distinctes : "Connection pooling" et "Direct connection"

4. **Sélectionner "Connection pooling"** (pas "Direct connection")

5. **Copier la connection string** qui ressemble à :
   ```
   postgresql://postgres.mxxggubgvurldcneeter:[PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres?pgbouncer=true&connection_limit=1
   ```

### Méthode 2 : Via Database Settings (Alternative)

1. **Aller sur** : https://supabase.com/dashboard/project/mxxggubgvurldcneeter/settings/database

2. **Chercher une section "Connection info"** ou **"Connection string"**

3. **Sélectionner "Connection pooling"** dans les options

4. **Copier la connection string**

---

## ✅ Comment Identifier la Bonne Connection String

La connection string avec **pooler** doit contenir :

### ✅ Caractéristiques de la Connection String avec Pooler

1. **Host** : `pooler.supabase.com` (pas `db.mxxggubgvurldcneeter.supabase.co`)
   - Exemple : `aws-0-eu-central-1.pooler.supabase.com`

2. **Port** : `6543` OU `5432` avec `pgbouncer=true`
   - Port `6543` : Pooler dédié
   - Port `5432` avec `pgbouncer=true` : Pooler partagé

3. **User** : `postgres.mxxggubgvurldcneeter` (format avec le projet ID)

4. **Paramètres** :
   - `pgbouncer=true` (obligatoire)
   - `connection_limit=1` (recommandé pour Vercel)

### ❌ Connection String Directe (À ÉVITER pour Vercel)

```
postgresql://postgres:[PASSWORD]@db.mxxggubgvurldcneeter.supabase.co:5432/postgres
```

**Caractéristiques** :
- Host : `db.mxxggubgvurldcneeter.supabase.co`
- Port : `5432` (sans pooler)
- User : `postgres` (sans projet ID)

---

## 📝 Exemples de Formats Corrects

### Format 1 : Pooler Dédié (Port 6543)
```
postgresql://postgres.mxxggubgvurldcneeter:[PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres?pgbouncer=true&connection_limit=1
```

### Format 2 : Pooler Partagé (Port 5432 avec pgbouncer)
```
postgresql://postgres.mxxggubgvurldcneeter:[PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:5432/postgres?pgbouncer=true&connection_limit=1
```

---

## 🔍 Si Vous Ne Trouvez Pas la Section

Si la section "Connection string" n'est pas visible :

1. **Vérifier que vous êtes dans "Project Settings"** (pas "Database Settings")
2. **Chercher un onglet "API"** ou **"Connection info"** dans le menu
3. **Utiliser la documentation Supabase** :
   - https://supabase.com/docs/guides/database/connecting-to-postgres#connection-pooler

---

## 🚀 Après Avoir Copié la Connection String

1. **Aller sur Vercel** : https://vercel.com/glenns-projects-7d11114a/procedure1/settings/environment-variables

2. **Trouver `DATABASE_URL`**

3. **Cliquer sur "Edit"**

4. **Coller la nouvelle connection string** (avec pooler)

5. **Sauvegarder**

6. **Redéployer** l'application

---

## ✅ Vérification

Après avoir mis à jour la `DATABASE_URL` :

1. **Tester la connexion** : https://procedure1.vercel.app/api/test-db
   - Doit retourner `"connected": true`

2. **Tester le login** : https://procedure1.vercel.app/login
   - Email : `admin@procedures.local`
   - Mot de passe : `AdminSecure123!`

---

## 📸 Capture d'Écran Attendue

Dans la page "Project Settings", vous devriez voir quelque chose comme :

```
Database
├── Connection string
│   ├── [Onglet] Connection pooling  ← SÉLECTIONNER CELUI-CI
│   ├── [Onglet] Direct connection
│   └── [Bouton "Copy"] ou [Champ avec valeur]
```

OU

```
Connection info
├── Connection pooling
│   └── postgresql://postgres.mxxggubgvurldcneeter:...@pooler.supabase.com:6543/...
└── Direct connection
    └── postgresql://postgres:...@db.mxxggubgvurldcneeter.supabase.co:5432/...
```

---

**Important :** Assurez-vous de sélectionner **"Connection pooling"** et non **"Direct connection"** !
