# Informations Admin et NEXTAUTH_SECRET

**Date :** 2025-01-13

---

## ✅ Identifiants Admin

**Email :** `admin@procedures.local`  
**Mot de passe :** `AdminSecure123!`  
**Rôle :** `admin`

**⚠️ IMPORTANT :** Changez le mot de passe après la première connexion !

---

## 🔐 Hash Bcrypt du Mot de Passe

**Hash généré :**
```
$2a$10$bNMPCoMIcsoZr1WvEcIye.8h.giLEKDo5Ca01ekpVJVbRH9JVZmcy
```

---

## 📝 Créer l'Admin dans Supabase

### Option 1 : Via SQL Editor (Recommandé)

1. Aller sur : https://supabase.com/dashboard/project/mxxggubgvurldcneeter/sql/new

2. Exécuter cette requête SQL :

```sql
INSERT INTO users (email, password_hash, role, created_at, updated_at)
VALUES (
  'admin@procedures.local',
  '$2a$10$bNMPCoMIcsoZr1WvEcIye.8h.giLEKDo5Ca01ekpVJVbRH9JVZmcy',
  'admin',
  NOW(),
  NOW()
);
```

3. Vérifier que l'utilisateur a été créé :

```sql
SELECT id, email, role, created_at FROM users WHERE email = 'admin@procedures.local';
```

### Option 2 : Via Table Editor

1. Aller sur : https://supabase.com/dashboard/project/mxxggubgvurldcneeter/editor

2. Ouvrir la table `users`

3. Cliquer sur "Insert row"

4. Remplir les champs :
   - `email` : `admin@procedures.local`
   - `password_hash` : `$2a$10$bNMPCoMIcsoZr1WvEcIye.8h.giLEKDo5Ca01ekpVJVbRH9JVZmcy`
   - `role` : `admin`
   - `created_at` : (laisser vide, sera rempli automatiquement)
   - `updated_at` : (laisser vide, sera rempli automatiquement)

5. Cliquer sur "Save"

---

## 🔑 NEXTAUTH_SECRET

**Secret généré :**
```
6VFpR6uztJgLIs82VwhMWFR079z3WN1VNbhdTF9VUF0=
```

### Configuration dans Vercel

1. **Aller sur** : https://vercel.com/glenns-projects-7d11114a/procedure1/settings/environment-variables

2. **Trouver** la variable `NEXTAUTH_SECRET`

3. **Cliquer sur "Edit"**

4. **Remplacer** la valeur actuelle :
   - **Ancienne valeur** : `https://procedure1.vercel.app/`
   - **Nouvelle valeur** : `6VFpR6uztJgLIs82VwhMWFR079z3WN1VNbhdTF9VUF0=`

5. **Cliquer sur "Save"**

6. **Redéployer** l'application :
   - Aller dans "Deployments"
   - Cliquer sur "Redeploy" sur le dernier déploiement
   - Attendre 2-3 minutes

---

## ✅ Vérification

### Vérifier que l'Admin est Créé

1. Aller sur : https://supabase.com/dashboard/project/mxxggubgvurldcneeter/editor
2. Ouvrir la table `users`
3. Vérifier qu'un utilisateur avec `email = 'admin@procedures.local'` et `role = 'admin'` existe

### Tester la Connexion

1. Aller sur : https://procedure1.vercel.app/login
2. Se connecter avec :
   - Email : `admin@procedures.local`
   - Mot de passe : `AdminSecure123!`
3. Vérifier l'accès au dashboard et au panneau admin

---

## 📋 Résumé

- ✅ **Email admin** : `admin@procedures.local`
- ✅ **Mot de passe** : `AdminSecure123!`
- ✅ **Hash bcrypt** : `$2a$10$bNMPCoMIcsoZr1WvEcIye.8h.giLEKDo5Ca01ekpVJVbRH9JVZmcy`
- ✅ **NEXTAUTH_SECRET** : `6VFpR6uztJgLIs82VwhMWFR079z3WN1VNbhdTF9VUF0=`

**Actions requises :**
1. Créer l'admin dans Supabase (SQL ou Table Editor)
2. Configurer NEXTAUTH_SECRET dans Vercel
3. Redéployer l'application
4. Tester la connexion

---

**Toutes les informations sont prêtes pour finaliser la configuration !**
