# 🔧 Solution : Erreur Prisma "prepared statement already exists"

**Date :** 2026-01-13

---

## ❌ Problème Identifié

Erreur lors du build Vercel :
```
ConnectorError(ConnectorError { user_facing_error: None, kind: QueryError(PostgresError { code: "42P05", message: "prepared statement \"s1\" already exists", severity: "ERROR" })
```

**Cause :** Le **Transaction pooler** (port 6543) ne supporte **pas** les prepared statements, mais Prisma en utilise pour optimiser les requêtes.

---

## ✅ Solution : Utiliser Session Pooler avec pgbouncer=true

Le **Session pooler** (port 5432 avec `pgbouncer=true`) supporte les prepared statements et est compatible avec Prisma.

### Étapes à Suivre

1. **Aller sur Supabase** : https://supabase.com/dashboard/project/mxxggubgvurldcneeter/settings/database
2. **Ouvrir la modal "Connect to your project"**
3. **Sélectionner** :
   - **Type** : URI
   - **Source** : Primary Database
   - **Method** : **Session pooler** (pas Transaction pooler)
4. **Copier la connection string** qui devrait ressembler à :
   ```
   postgresql://postgres.mxxggubgvurldcneeter:[PASSWORD]@aws-1-eu-central-1.pooler.supabase.com:5432/postgres
   ```
5. **Ajouter `?pgbouncer=true`** à la fin :
   ```
   postgresql://postgres.mxxggubgvurldcneeter:[PASSWORD]@aws-1-eu-central-1.pooler.supabase.com:5432/postgres?pgbouncer=true
   ```
6. **Mettre à jour dans Vercel** :
   - Aller sur : https://vercel.com/glenns-projects-7d11114a/procedure1/settings/environment-variables
   - Trouver `DATABASE_URL`
   - Cliquer sur "Edit"
   - Coller la nouvelle connection string (Session pooler avec `pgbouncer=true`)
   - Sauvegarder
7. **Redéployer** l'application

---

## 🔍 Différence entre Transaction et Session Pooler

### Transaction Pooler (Port 6543)
- ❌ **Ne supporte PAS** les prepared statements
- ✅ Optimisé pour les transactions courtes
- ❌ **Incompatible avec Prisma** (qui utilise des prepared statements)

### Session Pooler (Port 5432 avec pgbouncer=true)
- ✅ **Supporte** les prepared statements
- ✅ Compatible avec Prisma
- ✅ Fonctionne bien pour les applications serverless

---

## 📋 Format Final de la Connection String

**Session pooler avec pgbouncer** :
```
postgresql://postgres.mxxggubgvurldcneeter:[PASSWORD]@aws-1-eu-central-1.pooler.supabase.com:5432/postgres?pgbouncer=true
```

**Paramètres importants** :
- ✅ Port `5432` (Session pooler)
- ✅ Host avec `pooler.supabase.com`
- ✅ `?pgbouncer=true` (obligatoire pour le pooler)
- ✅ User au format `postgres.mxxggubgvurldcneeter`

---

## 🚀 Test

Après avoir mis à jour la `DATABASE_URL` et redéployé :

1. **Vérifier les logs de build Vercel** :
   - Plus d'erreur "prepared statement already exists"
   - Le build devrait réussir

2. **Tester l'application** :
   - https://procedure1.vercel.app/api/test-db
   - https://procedure1.vercel.app/login
   - https://procedure1.vercel.app/dashboard

---

## ⚠️ Note

**Pourquoi cette erreur ?**

Prisma utilise des prepared statements pour optimiser les requêtes répétées. Le Transaction pooler ne les supporte pas car il est conçu pour des transactions très courtes et isolées. Le Session pooler, en revanche, maintient une session complète et supporte les prepared statements.

---

**Une fois la connection string mise à jour avec le Session pooler, le problème devrait être résolu ! 🎉**
