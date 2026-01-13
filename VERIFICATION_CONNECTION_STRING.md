# ✅ Vérification de la Connection String

**Date :** 2026-01-13

---

## 🔍 Analyse de Votre Connection String

D'après la capture d'écran, vous avez sélectionné :
- **Type** : URI
- **Source** : Primary Database
- **Method** : **Session pooler** ⚠️

**Connection string affichée** :
```
postgresql://postgres.mxxggubgvurldcneeter:[PASSWORD]@aws-1-eu-central-1.pooler.supabase.com:5432/postgres
```

**Paramètres visibles** :
- Host: `aws-1-eu-central-1.pooler.supabase.com` ✅ (pooler, correct)
- Port: `5432` ⚠️
- Database: `postgres` ✅
- User: `postgres.mxxggubgvurldcneeter` ✅ (format correct)
- pool_mode: `session` ⚠️

---

## ⚠️ Problème Identifié

Pour **Vercel (serverless)**, le **Session pooler** avec port `5432` peut fonctionner, mais il est **recommandé d'utiliser le Transaction pooler** (port `6543`) qui est optimisé pour les applications serverless.

---

## ✅ Solution : Utiliser Transaction Pooler

### Option 1 : Transaction Pooler (Recommandé pour Vercel)

1. **Dans la modal "Connect to your project"**
2. **Changer le "Method"** de **"Session pooler"** à **"Transaction pooler"**
3. **Copier la nouvelle connection string** qui devrait avoir :
   - Port: `6543` (au lieu de `5432`)
   - pool_mode: `transaction` (au lieu de `session`)
   - Host: `aws-1-eu-central-1.pooler.supabase.com` (reste le même)

**Format attendu** :
```
postgresql://postgres.mxxggubgvurldcneeter:[PASSWORD]@aws-1-eu-central-1.pooler.supabase.com:6543/postgres?pgbouncer=true&connection_limit=1
```

### Option 2 : Session Pooler avec pgbouncer=true (Alternative)

Si vous gardez le Session pooler, vous devez **ajouter manuellement** les paramètres `pgbouncer=true` et `connection_limit=1` à la connection string :

**Format à utiliser** :
```
postgresql://postgres.mxxggubgvurldcneeter:[PASSWORD]@aws-1-eu-central-1.pooler.supabase.com:5432/postgres?pgbouncer=true&connection_limit=1
```

---

## 🎯 Recommandation

**Utilisez le Transaction pooler** (Option 1) car :
- ✅ Optimisé pour les applications serverless (Vercel)
- ✅ Port 6543 dédié au pooler
- ✅ Meilleure gestion des connexions pour les fonctions serverless
- ✅ Pas besoin d'ajouter manuellement des paramètres

---

## 📋 Étapes à Suivre

1. **Dans la modal Supabase** :
   - Changer "Method" de "Session pooler" à **"Transaction pooler"**
   - **⚠️ IMPORTANT :** La modal ne sauvegarde pas le choix - c'est normal ! C'est juste un générateur.
   - **Copier la connection string affichée**
   - **Remplacer `[YOUR-PASSWORD]`** par votre vrai mot de passe de base de données
   - Si vous ne connaissez pas le mot de passe : cliquer sur "Reset your database password" en bas de la modal

2. **Vérifier que la connection string contient** :
   - ✅ Port `6543`
   - ✅ Host avec `pooler.supabase.com`
   - ✅ User au format `postgres.mxxggubgvurldcneeter`
   - ✅ Votre mot de passe réel (pas `[YOUR-PASSWORD]`)

3. **Aller sur Vercel** :
   - https://vercel.com/glenns-projects-7d11114a/procedure1/settings/environment-variables
   - Trouver `DATABASE_URL`
   - Cliquer sur "Edit"
   - **Coller la connection string complète** (avec le mot de passe)
   - Sauvegarder

4. **Redéployer** l'application

5. **Tester** :
   - https://procedure1.vercel.app/api/test-db (doit retourner `"connected": true`)
   - https://procedure1.vercel.app/login

---

## ⚠️ Note sur l'Avertissement IPv4

L'avertissement orange indique que le Session pooler est "IPv4 proxied". Pour Vercel, cela devrait fonctionner, mais le **Transaction pooler** est généralement plus fiable pour les applications serverless.

---

**Conclusion :** Changez le "Method" à **"Transaction pooler"** et utilisez cette connection string pour Vercel.
