# Actions Immédiates - Création Admin et Configuration

**Date :** 2025-01-13

---

## 1. Créer l'Utilisateur Admin

### Option A : Via Script Shell
```bash
cd /Users/glenn/Desktop/procedures
./scripts/create-admin.sh admin@procedures.local AdminSecure123!
```

### Option B : Via Script Node.js
```bash
cd /Users/glenn/Desktop/procedures
node scripts/create-admin-node.js admin@procedures.local AdminSecure123!
```

### Option C : Via curl Direct
```bash
curl -X POST https://procedure1.vercel.app/api/setup/create-admin \
  -H "Authorization: Bearer ejZ+z34wqydLsZwnXxfvIBR76CMFbrqHH1NATD6Ip5c=" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@procedures.local", "password": "AdminSecure123!"}'
```

**Identifiants proposés :**
- Email : `admin@procedures.local`
- Password : `AdminSecure123!`

**⚠️ IMPORTANT :** Changez le mot de passe après la première connexion !

---

## 2. Générer et Configurer NEXTAUTH_SECRET

### Générer le Secret

**Option A : Avec openssl**
```bash
openssl rand -base64 32
```

**Option B : Avec Node.js**
```bash
node -e "const crypto = require('crypto'); console.log(crypto.randomBytes(32).toString('base64'))"
```

**Option C : Avec Python**
```bash
python3 -c "import secrets, base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"
```

**Option D : Utiliser le script**
```bash
./scripts/generate-secret.sh
```

### Configurer dans Vercel

1. **Aller sur** : https://vercel.com/glenns-projects-7d11114a/procedure1/settings/environment-variables

2. **Trouver** la variable `NEXTAUTH_SECRET`

3. **Cliquer sur "Edit"**

4. **Remplacer** la valeur actuelle :
   - **Ancienne valeur** : `https://procedure1.vercel.app/`
   - **Nouvelle valeur** : [Le secret généré ci-dessus]

5. **Cliquer sur "Save"**

6. **Redéployer** :
   - Aller dans "Deployments"
   - Cliquer sur "Redeploy" sur le dernier déploiement
   - Attendre 2-3 minutes

---

## 3. Commiter les Changements

```bash
cd /Users/glenn/Desktop/procedures

# Vérifier les changements
git status

# Ajouter les fichiers
git add frontend/app/api/setup
git add scripts/
git add FINALISATION_COMPLETE.md
git add PLAN_FINALISATION_IMMEDIATE.md

# Commiter
git commit -m "chore: remove setup routes and add helper scripts

- Remove temporary setup routes (/api/setup/*)
- Add create-admin.sh script for admin creation
- Add test-api.sh script for API testing
- Add generate-secret.sh script for secret generation
- Update documentation"

# Pousser
git push
```

---

## Vérification

### Vérifier que l'admin est créé
1. Aller sur : https://supabase.com/dashboard/project/mxxggubgvurldcneeter/editor
2. Ouvrir la table `users`
3. Vérifier qu'un utilisateur avec `role = 'admin'` existe

### Vérifier que les routes setup sont supprimées
```bash
curl -X POST https://procedure1.vercel.app/api/setup/create-admin \
  -H "Authorization: Bearer ejZ+z34wqydLsZwnXxfvIBR76CMFbrqHH1NATD6Ip5c="
```
**Résultat attendu :** 404 Not Found

### Tester la connexion
1. Aller sur : https://procedure1.vercel.app/login
2. Se connecter avec les identifiants admin
3. Vérifier l'accès au dashboard

---

**Fin des Actions Immédiates**
