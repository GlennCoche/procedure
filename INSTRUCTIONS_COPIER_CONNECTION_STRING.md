# 📋 Instructions : Copier la Connection String Transaction Pooler

**Date :** 2026-01-13

---

## ✅ Comportement Normal

La modal "Connect to your project" est un **générateur de connection string**, pas une configuration persistante. Le choix "Transaction pooler" n'est **pas sauvegardé** - c'est normal !

**Vous devez copier la connection string affichée** et la mettre dans Vercel.

---

## 📋 Étapes à Suivre

### 1. Dans la Modal Supabase

1. **Sélectionner "Session pooler"** dans le dropdown "Method" (⚠️ **Session**, pas Transaction)
   - **Pourquoi Session pooler ?** Le Transaction pooler ne supporte pas les prepared statements que Prisma utilise
2. **La connection string s'affiche** dans la grande boîte grise :
   ```
   postgresql://postgres.mxxggubgvurldcneeter:[YOUR-PASSWORD]@aws-1-eu-central-1.pooler.supabase.com:5432/postgres
   ```

3. **⚠️ IMPORTANT :** 
   - Remplacez `[YOUR-PASSWORD]` par votre **vrai mot de passe** de base de données
   - **Ajoutez `?pgbouncer=true`** à la fin de la connection string :
   ```
   postgresql://postgres.mxxggubgvurldcneeter:[PASSWORD]@aws-1-eu-central-1.pooler.supabase.com:5432/postgres?pgbouncer=true
   ```
   - Si vous ne connaissez pas le mot de passe, cliquez sur "Reset your database password" en bas de la modal
   - OU allez dans Database Settings pour le réinitialiser

4. **Copier la connection string complète** (avec le mot de passe)

### 2. Mettre à Jour dans Vercel

1. **Aller sur** : https://vercel.com/glenns-projects-7d11114a/procedure1/settings/environment-variables

2. **Trouver la variable `DATABASE_URL`**

3. **Cliquer sur "Edit"** (ou "..." puis "Edit")

4. **Coller la connection string complète** que vous avez copiée :
   ```
   postgresql://postgres.mxxggubgvurldcneeter:[VOTRE-MOT-DE-PASSE]@aws-1-eu-central-1.pooler.supabase.com:6543/postgres
   ```

5. **⚠️ Vérifier** que la connection string contient :
   - ✅ Port `5432` (Session pooler)
   - ✅ Host avec `pooler.supabase.com`
   - ✅ User au format `postgres.mxxggubgvurldcneeter`
   - ✅ Votre mot de passe (pas `[YOUR-PASSWORD]`)
   - ✅ `?pgbouncer=true` à la fin

6. **Cliquer sur "Save"**

### 3. Redéployer

1. **Aller dans "Deployments"**
2. **Cliquer sur "Redeploy"** sur le dernier déploiement
3. **Attendre** 2-3 minutes

### 4. Tester

1. **Tester la connexion** : https://procedure1.vercel.app/api/test-db
   - Doit retourner `"connected": true`

2. **Tester le login** : https://procedure1.vercel.app/login
   - Email : `admin@procedures.local`
   - Mot de passe : `AdminSecure123!`

---

## 🔍 Comment Récupérer le Mot de Passe

Si vous ne connaissez pas le mot de passe de la base de données :

### Option 1 : Via la Modal

1. Dans la modal "Connect to your project"
2. Scroller jusqu'en bas
3. Cliquer sur "Reset your database password" → "Database Settings"
4. Dans Database Settings, cliquer sur "Reset database password"
5. Copier le nouveau mot de passe
6. Utiliser ce mot de passe dans la connection string

### Option 2 : Via Database Settings

1. **Aller sur** : https://supabase.com/dashboard/project/mxxggubgvurldcneeter/settings/database
2. **Section "Database password"**
3. **Cliquer sur "Reset database password"**
4. **Copier le nouveau mot de passe**
5. **Utiliser ce mot de passe dans la connection string**

---

## ✅ Format Final de la Connection String

La connection string complète devrait ressembler à :

```
postgresql://postgres.mxxggubgvurldcneeter:VotreMotDePasse123@aws-1-eu-central-1.pooler.supabase.com:5432/postgres?pgbouncer=true
```

**Sans** :
- ❌ `[YOUR-PASSWORD]` (remplacer par le vrai mot de passe)

**Avec** :
- ✅ Port `5432` (Session pooler - supporte les prepared statements Prisma)
- ✅ Host `pooler.supabase.com`
- ✅ Votre mot de passe réel
- ✅ `?pgbouncer=true` (obligatoire pour le pooler)

---

## ⚠️ Important

- La modal Supabase ne sauvegarde **pas** votre choix - c'est normal !
- Vous devez **copier** la connection string et la mettre dans Vercel
- Le choix "Transaction pooler" dans la modal est juste pour **générer** la bonne connection string
- Une fois copiée dans Vercel, elle sera utilisée pour tous les déploiements

---

## 🚀 Résumé Rapide

1. ✅ Sélectionner **"Session pooler"** dans la modal (⚠️ Session, pas Transaction)
2. ✅ Copier la connection string
3. ✅ **Ajouter `?pgbouncer=true`** à la fin
4. ✅ Remplacer `[YOUR-PASSWORD]` par le vrai mot de passe
5. ✅ Coller dans Vercel → Environment Variables → `DATABASE_URL`
6. ✅ Sauvegarder
7. ✅ Redéployer
8. ✅ Tester

**⚠️ Important :** Utilisez le **Session pooler** (port 5432) et non le Transaction pooler (port 6543) car Prisma a besoin des prepared statements que seul le Session pooler supporte.

**C'est tout ! Le choix dans la modal n'a pas besoin d'être sauvegardé - c'est juste un outil de génération.**
