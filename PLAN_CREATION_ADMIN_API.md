# Plan Détaillé : Créer un Utilisateur Admin via Route API

## 📋 Vue d'ensemble

Ce plan vous guide étape par étape pour créer un utilisateur admin en utilisant la route API `/api/setup/create-admin` que nous avons créée.

**Durée estimée :** 5-10 minutes

---

## ✅ Étape 1 : Générer le Secret SETUP_SECRET

Avant d'ajouter la variable dans Vercel, générez un secret sécurisé.

### 1.1 Ouvrir le Terminal

Ouvrez votre terminal (Terminal.app sur Mac).

### 1.2 Générer le Secret

Exécutez cette commande :

```bash
openssl rand -base64 32
```

**Exemple de résultat :**
```
Kx9mP2vL8nQ5rT7wY3zA6bC1dE4fG8hI0jK2lM5nO8pQ1rS4tU7vW0xY3zA6bC=
```

**⚠️ IMPORTANT :** Copiez ce secret et gardez-le précieusement. Vous en aurez besoin à l'étape 4.

---

## ✅ Étape 2 : Ajouter SETUP_SECRET dans Vercel

### 2.1 Accéder à Vercel Dashboard

1. Allez sur [https://vercel.com](https://vercel.com)
2. Connectez-vous si nécessaire
3. Cliquez sur votre projet **"procedure1"** (ou le nom de votre projet)

### 2.2 Accéder aux Variables d'Environnement

1. Dans le menu en haut, cliquez sur **"Settings"**
2. Dans le menu de gauche, cliquez sur **"Environment Variables"**

### 2.3 Ajouter la Variable

1. Cliquez sur le bouton **"Add New"** (en haut à droite)
2. Remplissez le formulaire :
   - **Name** : `SETUP_SECRET`
   - **Value** : Collez le secret que vous avez généré à l'étape 1
   - **Environments** : Cochez les trois cases :
     - ✅ **Production**
     - ✅ **Preview**
     - ✅ **Development**
3. Cliquez sur **"Save"**

**Capture d'écran mentale :**
```
┌─────────────────────────────────────┐
│ Name: SETUP_SECRET                  │
│ Value: [Votre secret généré]        │
│ Environments:                       │
│   ☑ Production                      │
│   ☑ Preview                        │
│   ☑ Development                    │
│ [Save]                              │
└─────────────────────────────────────┘
```

### 2.4 Vérifier la Variable

Vérifiez que `SETUP_SECRET` apparaît bien dans la liste des variables d'environnement.

---

## ✅ Étape 3 : Redéployer l'Application

Pour que la nouvelle variable d'environnement soit disponible, vous devez redéployer l'application.

### Option A : Redéploiement Automatique (Recommandé)

1. Faites un petit changement dans votre code (par exemple, ajoutez un commentaire)
2. Commitez et poussez sur GitHub :
   ```bash
   git add .
   git commit -m "chore: add SETUP_SECRET for admin creation"
   git push
   ```
3. Vercel redéploiera automatiquement (attendez 2-3 minutes)

### Option B : Redéploiement Manuel

1. Allez dans Vercel Dashboard > votre projet > **"Deployments"**
2. Trouvez le dernier déploiement
3. Cliquez sur les **"..."** (trois points) à droite
4. Cliquez sur **"Redeploy"**
5. Attendez 2-3 minutes que le déploiement se termine

### 3.1 Vérifier le Déploiement

1. Allez dans **"Deployments"**
2. Vérifiez que le dernier déploiement est **"Ready"** (cercle vert)
3. Notez l'URL de votre application (ex: `https://procedure1-gz3mi2h0n-glenns-projects-7d11114a.vercel.app`)

---

## ✅ Étape 4 : Préparer la Commande curl

### 4.1 Récupérer les Informations Nécessaires

Vous aurez besoin de :
- **URL de votre application** : `https://votre-app.vercel.app`
- **SETUP_SECRET** : Le secret que vous avez généré à l'étape 1
- **Email** : L'email que vous voulez utiliser pour l'admin (ex: `admin@example.com`)
- **Mot de passe** : Un mot de passe sécurisé (minimum 8 caractères)

### 4.2 Préparer la Commande

Remplacez les valeurs dans cette commande :

```bash
curl -X POST https://VOTRE-URL-VERCEL/api/setup/create-admin \
  -H "Authorization: Bearer VOTRE_SETUP_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "VOTRE_EMAIL",
    "password": "VOTRE_MOT_DE_PASSE"
  }'
```

**Exemple avec des valeurs réelles :**
```bash
curl -X POST https://procedure1-gz3mi2h0n-glenns-projects-7d11114a.vercel.app/api/setup/create-admin \
  -H "Authorization: Bearer Kx9mP2vL8nQ5rT7wY3zA6bC1dE4fG8hI0jK2lM5nO8pQ1rS4tU7vW0xY3zA6bC=" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "MonMotDePasseSecurise123!"
  }'
```

---

## ✅ Étape 5 : Exécuter la Commande

### 5.1 Ouvrir le Terminal

Ouvrez votre terminal.

### 5.2 Exécuter la Commande

Collez et exécutez la commande que vous avez préparée à l'étape 4.

**Appuyez sur Entrée.**

### 5.3 Analyser la Réponse

#### ✅ Succès (Code 201)

Si tout fonctionne, vous verrez :

```json
{
  "success": true,
  "message": "Utilisateur admin créé avec succès",
  "user": {
    "id": 1,
    "email": "admin@example.com",
    "role": "admin",
    "createdAt": "2024-01-11T19:45:00.000Z"
  }
}
```

**✅ C'est bon !** Votre admin est créé.

#### ❌ Erreur "Non autorisé" (Code 401)

```json
{
  "error": "Non autorisé. Fournissez un token Bearer valide dans le header Authorization."
}
```

**Solutions :**
- Vérifiez que `SETUP_SECRET` est bien configuré dans Vercel
- Vérifiez que vous utilisez le bon secret dans la commande
- Vérifiez que l'application a été redéployée après avoir ajouté la variable

#### ❌ Erreur "Email déjà existant" (Code 400)

```json
{
  "error": "Un utilisateur avec cet email existe déjà"
}
```

**Solutions :**
- Utilisez un autre email
- Ou connectez-vous avec l'utilisateur existant
- Ou supprimez l'utilisateur existant via Supabase SQL Editor

#### ❌ Erreur "Format d'email invalide" (Code 400)

```json
{
  "error": "Format d'email invalide"
}
```

**Solution :** Utilisez un email valide (ex: `admin@example.com`)

#### ❌ Erreur "Mot de passe trop court" (Code 400)

```json
{
  "error": "Le mot de passe doit contenir au moins 8 caractères"
}
```

**Solution :** Utilisez un mot de passe d'au moins 8 caractères

#### ❌ Erreur Serveur (Code 500)

```json
{
  "error": "Erreur serveur lors de la création de l'utilisateur",
  "details": "..."
}
```

**Solutions :**
- Vérifiez les logs dans Vercel Dashboard > Deployments > Functions
- Vérifiez que `DATABASE_URL` est bien configuré
- Vérifiez que les migrations ont été appliquées

---

## ✅ Étape 6 : Vérifier la Création

### 6.1 Vérifier dans Supabase (Optionnel)

1. Allez sur [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Sélectionnez votre projet
3. Allez dans **"Table Editor"** > **"users"**
4. Vérifiez que votre utilisateur apparaît avec le rôle `admin`

### 6.2 Tester la Connexion

1. Allez sur `https://votre-app.vercel.app/login`
2. Entrez vos identifiants :
   - **Email** : L'email que vous avez utilisé
   - **Mot de passe** : Le mot de passe que vous avez défini
3. Cliquez sur **"Se connecter"**

**✅ Si vous arrivez sur le dashboard, c'est parfait !**

---

## ✅ Étape 7 : Supprimer la Route (SÉCURITÉ)

**⚠️ IMPORTANT :** Pour des raisons de sécurité, supprimez la route `/api/setup/*` après avoir créé votre admin.

### 7.1 Supprimer les Fichiers

Dans votre terminal, exécutez :

```bash
cd /Users/glenn/Desktop/procedures/frontend
rm -rf app/api/setup
```

### 7.2 Commiter et Pousser

```bash
git add app/api/setup
git commit -m "chore: remove setup routes after admin creation"
git push
```

### 7.3 Vérifier le Déploiement

Vercel redéploiera automatiquement. Vérifiez que le déploiement est réussi.

---

## 📝 Checklist Complète

Cochez chaque étape au fur et à mesure :

- [ ] **Étape 1** : Secret SETUP_SECRET généré
- [ ] **Étape 2** : SETUP_SECRET ajouté dans Vercel
- [ ] **Étape 3** : Application redéployée
- [ ] **Étape 4** : Commande curl préparée
- [ ] **Étape 5** : Commande exécutée avec succès
- [ ] **Étape 6** : Connexion testée et fonctionnelle
- [ ] **Étape 7** : Route supprimée (sécurité)

---

## 🔒 Conseils de Sécurité

1. **Mot de passe fort** : Utilisez un mot de passe d'au moins 12 caractères avec :
   - Majuscules
   - Minuscules
   - Chiffres
   - Symboles

2. **Secret unique** : Ne réutilisez jamais le même `SETUP_SECRET` pour d'autres projets

3. **Suppression rapide** : Supprimez la route `/api/setup/*` dès que possible après avoir créé l'admin

4. **Ne partagez jamais** : Ne partagez jamais votre `SETUP_SECRET` ou votre mot de passe admin

---

## 🆘 Résolution des Problèmes

### La commande curl ne fonctionne pas

**Vérifiez :**
- Que curl est installé : `curl --version`
- Que l'URL est correcte (sans espaces)
- Que les guillemets sont corrects dans le JSON

**Alternative :** Utilisez un outil comme Postman ou Insomnia

### Erreur "Failed to fetch" ou timeout

**Solutions :**
- Vérifiez que l'application est bien déployée
- Vérifiez que l'URL est correcte
- Attendez quelques minutes et réessayez

### Erreur de connexion après création

**Solutions :**
- Vérifiez que l'utilisateur existe dans Supabase
- Vérifiez que le mot de passe est correct
- Vérifiez que `JWT_SECRET` est bien configuré dans Vercel

---

## 📞 Commandes Rapides de Référence

### Générer le secret
```bash
openssl rand -base64 32
```

### Créer l'admin
```bash
curl -X POST https://VOTRE-URL/api/setup/create-admin \
  -H "Authorization: Bearer VOTRE_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "MotDePasse123!"}'
```

### Supprimer la route
```bash
cd frontend
rm -rf app/api/setup
git add app/api/setup
git commit -m "chore: remove setup routes"
git push
```

---

Une fois toutes ces étapes complétées, vous aurez un utilisateur admin fonctionnel et l'application sera sécurisée ! 🎉
