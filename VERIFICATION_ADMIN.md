# Vérification de l'Admin

**Date :** 2025-01-13

---

## ✅ Statut Actuel

L'erreur **"duplicate key value violates unique constraint"** signifie que **l'admin existe déjà** dans la base de données !

C'est une bonne nouvelle - l'utilisateur a été créé avec succès lors d'une tentative précédente.

---

## 🔍 Vérifier que l'Admin Existe

### Requête SQL pour Vérifier

Exécutez cette requête dans le SQL Editor de Supabase :

```sql
SELECT 
  id,
  email,
  role,
  created_at,
  updated_at
FROM users 
WHERE email = 'admin@procedures.local';
```

**URL :** https://supabase.com/dashboard/project/mxxggubgvurldcneeter/sql/new

### Résultat Attendu

Si l'admin existe, vous devriez voir :
- `id` : Un nombre (ex: 1, 2, etc.)
- `email` : `admin@procedures.local`
- `role` : `admin`
- `created_at` : Date de création
- `updated_at` : Date de mise à jour

---

## 🔐 Identifiants de Connexion

**Email :** `admin@procedures.local`  
**Mot de passe :** `AdminSecure123!`

---

## ✅ Tester la Connexion

1. **Aller sur** : https://procedure1.vercel.app/login

2. **Se connecter avec** :
   - Email : `admin@procedures.local`
   - Mot de passe : `AdminSecure123!`

3. **Vérifier** :
   - ✅ Accès au dashboard
   - ✅ Accès au panneau admin (`/admin/procedures`)
   - ✅ Toutes les fonctionnalités disponibles

---

## 🔧 Si la Connexion Ne Fonctionne Pas

### Option 1 : Vérifier le Hash du Mot de Passe

Si le mot de passe ne fonctionne pas, il est possible que le hash dans la base de données soit différent.

**Vérifier le hash actuel :**
```sql
SELECT email, password_hash, role 
FROM users 
WHERE email = 'admin@procedures.local';
```

**Si nécessaire, mettre à jour le hash :**
```sql
UPDATE users 
SET password_hash = '$2a$10$bNMPCoMIcsoZr1WvEcIye.8h.giLEKDo5Ca01ekpVJVbRH9JVZmcy',
    updated_at = NOW()
WHERE email = 'admin@procedures.local';
```

### Option 2 : Supprimer et Recréer l'Admin

Si vous voulez recréer l'admin proprement :

```sql
-- Supprimer l'admin existant
DELETE FROM users WHERE email = 'admin@procedures.local';

-- Recréer l'admin
INSERT INTO users (email, password_hash, role, created_at, updated_at)
VALUES (
  'admin@procedures.local',
  '$2a$10$bNMPCoMIcsoZr1WvEcIye.8h.giLEKDo5Ca01ekpVJVbRH9JVZmcy',
  'admin',
  NOW(),
  NOW()
);
```

---

## 📋 Checklist de Vérification

- [ ] Admin existe dans Supabase (requête SQL)
- [ ] NEXTAUTH_SECRET configuré dans Vercel : `6VFpR6uztJgLIs82VwhMWFR079z3WN1VNbhdTF9VUF0=`
- [ ] Application redéployée sur Vercel
- [ ] Connexion fonctionne avec les identifiants
- [ ] Accès au dashboard confirmé
- [ ] Accès au panneau admin confirmé

---

## 🎉 Résumé

**Statut :** ✅ Admin créé avec succès !

L'erreur "duplicate key" confirme que l'utilisateur existe déjà. Vous pouvez maintenant vous connecter avec :
- Email : `admin@procedures.local`
- Mot de passe : `AdminSecure123!`

**Prochaine étape :** Tester la connexion sur https://procedure1.vercel.app/login

---

**Tout est prêt pour la connexion !**
