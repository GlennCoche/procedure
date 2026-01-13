# Résultat de la Création Admin

**Date :** 2025-01-13

---

## ⚠️ Problème Rencontré

La route `/api/setup/create-admin` retourne une erreur **405 (Method Not Allowed)**.

**Causes possibles :**
1. La route a été supprimée lors d'un déploiement précédent
2. Le déploiement n'a pas encore été effectué avec les routes setup
3. La route n'est pas accessible en production

---

## ✅ Secret NEXTAUTH_SECRET Généré

**Secret généré :**
```
6VFpR6uztJgLIs82VwhMWFR079z3WN1VNbhdTF9VUF0=
```

**Action requise :**
1. Aller sur : https://vercel.com/glenns-projects-7d11114a/procedure1/settings/environment-variables
2. Trouver la variable `NEXTAUTH_SECRET`
3. Cliquer sur "Edit"
4. Remplacer la valeur actuelle (`https://procedure1.vercel.app/`) par :
   ```
   6VFpR6uztJgLIs82VwhMWFR079z3WN1VNbhdTF9VUF0=
   ```
5. Cliquer sur "Save"
6. Redéployer l'application

---

## 🔧 Solutions pour Créer l'Admin

### Option 1 : Créer l'Admin Directement dans Supabase

1. Aller sur : https://supabase.com/dashboard/project/mxxggubgvurldcneeter/editor
2. Ouvrir la table `users`
3. Cliquer sur "Insert" ou utiliser SQL Editor :
   ```sql
   INSERT INTO users (email, password_hash, role, created_at, updated_at)
   VALUES (
     'admin@procedures.local',
     -- Vous devez générer le hash avec bcrypt
     -- Utilisez cette commande Node.js pour générer le hash :
     -- node -e "const bcrypt = require('bcryptjs'); bcrypt.hash('AdminSecure123!', 10).then(h => console.log(h))"
     '$2a$10$...', -- Hash bcrypt du mot de passe
     'admin',
     NOW(),
     NOW()
   );
   ```

### Option 2 : Utiliser Prisma Studio (Local)

Si vous avez accès localement :
```bash
cd /Users/glenn/Desktop/procedures/frontend
npx prisma studio
```
Puis créer l'utilisateur via l'interface.

### Option 3 : Créer un Script SQL Direct

Créer un script SQL avec le hash bcrypt du mot de passe et l'exécuter dans Supabase SQL Editor.

---

## 📋 Identifiants Proposés

**Email :** `admin@procedures.local`  
**Password :** `AdminSecure123!`  
**Role :** `admin`

**⚠️ IMPORTANT :** Changez le mot de passe après la première connexion !

---

## 🔐 NEXTAUTH_SECRET

**Valeur à configurer dans Vercel :**
```
6VFpR6uztJgLIs82VwhMWFR079z3WN1VNbhdTF9VUF0=
```

**URL de configuration :**
https://vercel.com/glenns-projects-7d11114a/procedure1/settings/environment-variables

---

**Prochaine étape :** Créer l'admin via Supabase directement ou attendre que les routes setup soient redéployées.
