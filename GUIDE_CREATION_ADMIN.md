# Guide : Appliquer les Migrations et Créer un Admin

## 📋 Étape 1 : Appliquer les Migrations Prisma

Les migrations créent toutes les tables nécessaires dans votre base de données Supabase.

### Option A : Via Vercel CLI (Recommandé)

Cette méthode nécessite d'avoir Vercel CLI installé localement.

#### 1.1 Installer Vercel CLI

```bash
npm install -g vercel
```

#### 1.2 Se connecter à Vercel

```bash
vercel login
```

Cela ouvrira votre navigateur pour vous authentifier.

#### 1.3 Aller dans le dossier frontend

```bash
cd frontend
```

#### 1.4 Télécharger les variables d'environnement depuis Vercel

```bash
vercel env pull .env.local
```

Cette commande va :
- Créer ou mettre à jour le fichier `.env.local`
- Télécharger toutes les variables d'environnement configurées sur Vercel
- Inclure notamment `DATABASE_URL` qui est nécessaire pour les migrations

#### 1.5 Appliquer les migrations

```bash
npx prisma migrate deploy
```

Cette commande va :
- Se connecter à votre base de données Supabase via `DATABASE_URL`
- Créer toutes les tables définies dans `prisma/schema.prisma`
- Créer les index et contraintes nécessaires

**Résultat attendu :**
```
Environment variables loaded from .env.local
Prisma schema loaded from prisma/schema.prisma
Datasource "db": PostgreSQL database "postgres", schema "public" at "db.xxx.supabase.co:5432"

Applying migration `001_initial`
The following migration(s) have been applied:

migrations/
  └─ 001_initial/
    └─ migration.sql

✔ All migrations have been successfully applied.
```

### Option B : Via une Route API Temporaire

Si vous ne pouvez pas utiliser Vercel CLI, vous pouvez créer une route API temporaire.

**⚠️ ATTENTION : Supprimez cette route après utilisation pour des raisons de sécurité !**

#### 1. Créer la route de migration

Le fichier existe déjà : `frontend/app/api/migrate/route.ts` (voir le guide `ETAPES_RESTANTES_DEPLOIEMENT.md`)

#### 2. Ajouter le secret dans Vercel

Dans Vercel Dashboard > Settings > Environment Variables, ajoutez :

```
Name: MIGRATE_SECRET
Value: [Générez avec: openssl rand -base64 32]
Environments: ✅ Production ✅ Preview ✅ Development
```

#### 3. Appeler l'endpoint

```bash
curl -X POST https://votre-app.vercel.app/api/migrate \
  -H "Authorization: Bearer VOTRE_MIGRATE_SECRET"
```

#### 4. Supprimer la route après utilisation

```bash
rm frontend/app/api/migrate/route.ts
```

---

## 👤 Étape 2 : Créer un Utilisateur Admin

Après avoir appliqué les migrations, vous devez créer un utilisateur admin pour vous connecter à l'application.

### Méthode 1 : Via la Route API (Recommandé)

#### 2.1 Ajouter le secret SETUP_SECRET dans Vercel

1. Allez dans **Vercel Dashboard** > votre projet > **Settings** > **Environment Variables**
2. Cliquez sur **"Add New"**
3. Ajoutez :

```
Name: SETUP_SECRET
Value: [Générez avec: openssl rand -base64 32]
Environments: ✅ Production ✅ Preview ✅ Development
```

**Générer le secret :**
```bash
openssl rand -base64 32
```

4. Cliquez sur **"Save"**

#### 2.2 Redéployer l'application

Après avoir ajouté la variable, redéployez l'application :
- Soit faites un nouveau commit sur GitHub (déploiement automatique)
- Soit allez dans Vercel Dashboard > Deployments > "Redeploy"

#### 2.3 Appeler l'endpoint pour créer l'admin

**Via curl (Terminal) :**

```bash
curl -X POST https://votre-app.vercel.app/api/setup/create-admin \
  -H "Authorization: Bearer VOTRE_SETUP_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "VotreMotDePasseSecurise123!"
  }'
```

**Remplacez :**
- `VOTRE_SETUP_SECRET` : Le secret que vous avez configuré dans Vercel
- `admin@example.com` : Votre email
- `VotreMotDePasseSecurise123!` : Votre mot de passe (minimum 8 caractères)

**Résultat attendu (succès) :**
```json
{
  "success": true,
  "message": "Utilisateur admin créé avec succès",
  "user": {
    "id": 1,
    "email": "admin@example.com",
    "role": "admin",
    "createdAt": "2024-01-11T10:00:00.000Z"
  }
}
```

**Résultat en cas d'erreur :**
```json
{
  "error": "Un utilisateur avec cet email existe déjà"
}
```

#### 2.4 Tester la connexion

1. Allez sur `https://votre-app.vercel.app/login`
2. Connectez-vous avec :
   - **Email** : L'email que vous avez utilisé
   - **Mot de passe** : Le mot de passe que vous avez défini

#### 2.5 Supprimer la route après utilisation (IMPORTANT)

Pour des raisons de sécurité, supprimez la route après avoir créé votre admin :

```bash
rm -rf frontend/app/api/setup
```

Puis commitez et poussez sur GitHub :

```bash
git add frontend/app/api/setup
git commit -m "chore: remove setup route after admin creation"
git push
```

### Méthode 2 : Via Supabase Dashboard (Alternative)

Si vous préférez créer l'utilisateur directement dans Supabase :

#### 2.1 Accéder à Supabase SQL Editor

1. Allez sur [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Sélectionnez votre projet
3. Cliquez sur **"SQL Editor"** dans le menu de gauche

#### 2.2 Générer le hash du mot de passe

Vous devez générer un hash bcrypt du mot de passe. Utilisez Node.js :

```bash
cd frontend
node -e "const bcrypt = require('bcryptjs'); bcrypt.hash('VotreMotDePasse123!', 10).then(hash => console.log(hash))"
```

Cela affichera un hash comme : `$2a$10$xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

#### 2.3 Exécuter la requête SQL

Dans Supabase SQL Editor, exécutez :

```sql
INSERT INTO users (email, password_hash, role, created_at, updated_at)
VALUES (
  'admin@example.com',
  '$2a$10$VOTRE_HASH_BCRYPT_ICI',
  'admin',
  NOW(),
  NOW()
);
```

**Remplacez :**
- `admin@example.com` : Votre email
- `$2a$10$VOTRE_HASH_BCRYPT_ICI` : Le hash généré à l'étape précédente

#### 2.4 Vérifier la création

Exécutez cette requête pour vérifier :

```sql
SELECT id, email, role, created_at FROM users WHERE email = 'admin@example.com';
```

---

## ✅ Vérification Finale

Après avoir créé votre admin, vérifiez que tout fonctionne :

1. **Connexion** : `https://votre-app.vercel.app/login`
   - Connectez-vous avec vos identifiants admin

2. **Dashboard** : `https://votre-app.vercel.app/dashboard`
   - Vous devriez voir le dashboard

3. **Admin Panel** : `https://votre-app.vercel.app/admin/procedures`
   - Vous devriez pouvoir accéder au panneau admin

---

## 🔒 Sécurité

**IMPORTANT :**

1. ✅ **Supprimez la route `/api/setup/create-admin` après utilisation**
2. ✅ **Ne partagez jamais votre `SETUP_SECRET`**
3. ✅ **Utilisez un mot de passe fort (minimum 12 caractères, avec majuscules, minuscules, chiffres et symboles)**
4. ✅ **Changez le `SETUP_SECRET` après avoir créé votre admin**

---

## 🆘 Résolution des Problèmes

### Erreur "Non autorisé" lors de la création de l'admin

**Cause** : Le secret dans le header ne correspond pas à `SETUP_SECRET` dans Vercel.

**Solution** :
1. Vérifiez que `SETUP_SECRET` est bien configuré dans Vercel
2. Vérifiez que vous utilisez le bon secret dans le header `Authorization: Bearer ...`
3. Redéployez l'application après avoir ajouté la variable

### Erreur "Table does not exist"

**Cause** : Les migrations n'ont pas été appliquées.

**Solution** : Suivez l'Étape 1 pour appliquer les migrations.

### Erreur "Un utilisateur avec cet email existe déjà"

**Cause** : Un utilisateur avec cet email existe déjà dans la base de données.

**Solution** :
- Utilisez un autre email
- Ou connectez-vous avec l'utilisateur existant
- Ou supprimez l'utilisateur existant via Supabase SQL Editor

### Erreur de connexion après création

**Cause** : Le mot de passe n'a pas été correctement hashé ou la base de données n'est pas synchronisée.

**Solution** :
1. Vérifiez que les migrations ont été appliquées
2. Vérifiez que l'utilisateur existe dans Supabase
3. Recréez l'utilisateur si nécessaire

---

## 📝 Résumé des Commandes

```bash
# 1. Installer Vercel CLI (une seule fois)
npm install -g vercel

# 2. Se connecter à Vercel
vercel login

# 3. Aller dans le dossier frontend
cd frontend

# 4. Télécharger les variables d'environnement
vercel env pull .env.local

# 5. Appliquer les migrations
npx prisma migrate deploy

# 6. Créer un admin (remplacez les valeurs)
curl -X POST https://votre-app.vercel.app/api/setup/create-admin \
  -H "Authorization: Bearer VOTRE_SETUP_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "VotreMotDePasse123!"}'

# 7. Supprimer la route setup (après utilisation)
rm -rf app/api/setup
```

---

Une fois ces étapes complétées, vous pourrez vous connecter à l'application avec votre compte admin ! 🎉
