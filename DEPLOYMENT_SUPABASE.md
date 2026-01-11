# Guide de Déploiement Supabase

Ce guide vous explique comment configurer Supabase pour votre application Next.js Full-Stack.

## Étape 1 : Créer un compte Supabase

1. Allez sur [https://supabase.com](https://supabase.com)
2. Cliquez sur "Start your project"
3. Connectez-vous avec GitHub, Google, ou créez un compte

## Étape 2 : Créer un nouveau projet

1. Cliquez sur "New Project"
2. Remplissez les informations :
   - **Organization** : Créez ou sélectionnez une organisation
   - **Name** : `procedures-maintenance` (ou le nom de votre choix)
   - **Database Password** : Générez un mot de passe fort et **SAVEZ-LE** (vous en aurez besoin)
   - **Region** : Choisissez la région la plus proche (ex: `West Europe (Paris)`)
   - **Pricing Plan** : Sélectionnez "Free" pour commencer

3. Cliquez sur "Create new project"
4. Attendez 2-3 minutes que le projet soit créé

## Étape 3 : Récupérer la connection string

### Navigation détaillée :

1. **Accéder à Settings** :
   - Dans votre projet Supabase, regardez la **sidebar gauche**
   - Cliquez sur **"Settings"** (icône d'engrenage ⚙️) en bas de la sidebar
   - Vous verrez plusieurs sections : **PROJECT SETTINGS**, **CONFIGURATION**, **BILLING**

2. **Accéder à Database** :
   - Dans la section **CONFIGURATION**, vous verrez **"Database"** avec une flèche →
   - Cliquez sur **"Database"** (ou utilisez le lien direct dans PROJECT SETTINGS si disponible)

3. **Trouver la Connection string** :
   - Une fois dans la page Database, faites défiler vers le bas
   - Cherchez la section **"Connection string"** ou **"Connection pooling"**
   - Si vous ne voyez pas cette section, cherchez **"Connection info"** ou **"Database connection"**
   - La section peut être sous un onglet ou dans une sous-section

4. **Sélectionner le format URI** :
   - Vous verrez un **dropdown** ou des **onglets** avec différents formats :
     - **URI** (format complet avec mot de passe)
     - **JDBC** (pour Java)
     - **Connection pooling** (pour les connexions multiples)
   - Sélectionnez **"URI"** dans le dropdown

5. **Copier la connection string** :
   - La connection string ressemble à :
     ```
     postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
     ```
   - Cliquez sur le bouton **"Copy"** à côté de la connection string
   - **Important** : Remplacez `[YOUR-PASSWORD]` par le mot de passe que vous avez créé à l'étape 2

### Alternative : Si vous ne trouvez toujours pas la section

Si la section "Connection string" n'apparaît pas dans Database, essayez :

1. **Via l'URL directe** :
   - Allez sur : `https://supabase.com/dashboard/project/[VOTRE-PROJECT-REF]/settings/database`
   - Remplacez `[VOTRE-PROJECT-REF]` par la référence de votre projet (visible dans l'URL de votre projet)

2. **Via l'API Settings** :
   - Allez dans **Settings** > **API** (ou **Data API**)
   - Cherchez la section **"Project URL"** ou **"Database URL"**
   - La connection string peut être affichée là-bas

3. **Construire manuellement** :
   - Votre URL de projet ressemble à : `https://[PROJECT-REF].supabase.co`
   - La connection string sera : `postgresql://postgres:[VOTRE-MOT-DE-PASSE]@db.[PROJECT-REF].supabase.co:5432/postgres`
   - Remplacez `[PROJECT-REF]` par la référence de votre projet (sans le préfixe `https://` et sans `.supabase.co`)

## Étape 4 : Configurer les variables d'environnement

### Localement (`.env.local`)

**Créez le fichier `frontend/.env.local`** (s'il n'existe pas déjà) :

```bash
cd frontend
touch .env.local
```

Puis ajoutez la connection string dans `frontend/.env.local` :

```env
# Connection string Supabase
DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres"

# JWT Secret (générez avec: openssl rand -base64 32)
JWT_SECRET="change-me-in-production"

# NextAuth Configuration
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="change-me-in-production"

# OpenAI API Key (optionnel pour le chat IA)
OPENAI_API_KEY=""
```

**Important** : 
- Remplacez `[YOUR-PASSWORD]` par votre mot de passe Supabase
- Remplacez `[PROJECT-REF]` par la référence de votre projet (ex: `mxxggubgvurldcneeter`)
- Le fichier `.env.local` est déjà dans `.gitignore`, donc il ne sera PAS commité dans GitHub

### Sur Vercel

1. Allez dans votre projet Vercel
2. **Settings** > **Environment Variables**
3. Ajoutez `DATABASE_URL` avec la connection string Supabase

## Étape 5 : Appliquer les migrations Prisma

1. Assurez-vous que votre schéma Prisma est à jour (`frontend/prisma/schema.prisma`)
2. Générez le client Prisma :
   ```bash
   cd frontend
   npx prisma generate
   ```
3. Créez la migration initiale :
   ```bash
   npx prisma migrate dev --name init
   ```
4. Appliquez les migrations sur Supabase :
   ```bash
   npx prisma migrate deploy
   ```

## Étape 6 : Vérifier les tables créées

1. Dans Supabase, allez dans **Table Editor**
2. Vous devriez voir toutes les tables :
   - `users`
   - `procedures`
   - `steps`
   - `executions`
   - `step_executions`
   - `tips`
   - `chat_messages`

## Étape 7 : Configurer Row Level Security (RLS)

### Activer RLS sur toutes les tables

Exécutez ces commandes SQL dans **SQL Editor** de Supabase :

```sql
-- Activer RLS sur toutes les tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE procedures ENABLE ROW LEVEL SECURITY;
ALTER TABLE steps ENABLE ROW LEVEL SECURITY;
ALTER TABLE executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE step_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE tips ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
```

### Politiques RLS pour Users

```sql
-- Les utilisateurs peuvent lire leur propre profil
CREATE POLICY "Users can read own profile"
ON users FOR SELECT
USING (auth.uid()::text = id::text);

-- Les utilisateurs peuvent mettre à jour leur propre profil
CREATE POLICY "Users can update own profile"
ON users FOR UPDATE
USING (auth.uid()::text = id::text);
```

### Politiques RLS pour Procedures

```sql
-- Lecture publique des procédures actives
CREATE POLICY "Procedures are viewable by everyone"
ON procedures FOR SELECT
USING (is_active = true);

-- Seuls les admins peuvent créer/modifier/supprimer
CREATE POLICY "Admins can manage procedures"
ON procedures FOR ALL
USING (
  EXISTS (
    SELECT 1 FROM users
    WHERE users.id = procedures.created_by
    AND users.role = 'admin'
  )
);
```

### Politiques RLS pour Executions

```sql
-- Les utilisateurs peuvent lire leurs propres exécutions
CREATE POLICY "Users can read own executions"
ON executions FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM users
    WHERE users.id = executions.user_id
    AND auth.uid()::text = users.id::text
  )
);

-- Les utilisateurs peuvent créer leurs propres exécutions
CREATE POLICY "Users can create own executions"
ON executions FOR INSERT
WITH CHECK (
  EXISTS (
    SELECT 1 FROM users
    WHERE users.id = executions.user_id
    AND auth.uid()::text = users.id::text
  )
);

-- Les utilisateurs peuvent mettre à jour leurs propres exécutions
CREATE POLICY "Users can update own executions"
ON executions FOR UPDATE
USING (
  EXISTS (
    SELECT 1 FROM users
    WHERE users.id = executions.user_id
    AND auth.uid()::text = users.id::text
  )
);
```

### Politiques RLS pour Tips

```sql
-- Lecture publique des tips
CREATE POLICY "Tips are viewable by everyone"
ON tips FOR SELECT
USING (true);

-- Seuls les admins peuvent créer/modifier/supprimer
CREATE POLICY "Admins can manage tips"
ON tips FOR ALL
USING (
  EXISTS (
    SELECT 1 FROM users
    WHERE users.id = tips.created_by
    AND users.role = 'admin'
  )
);
```

### Politiques RLS pour ChatMessages

```sql
-- Les utilisateurs peuvent lire leurs propres messages
CREATE POLICY "Users can read own messages"
ON chat_messages FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM users
    WHERE users.id = chat_messages.user_id
    AND auth.uid()::text = users.id::text
  )
);

-- Les utilisateurs peuvent créer leurs propres messages
CREATE POLICY "Users can create own messages"
ON chat_messages FOR INSERT
WITH CHECK (
  EXISTS (
    SELECT 1 FROM users
    WHERE users.id = chat_messages.user_id
    AND auth.uid()::text = users.id::text
  )
);
```

**Note** : Ces politiques utilisent `auth.uid()` qui nécessite l'authentification Supabase. Pour une application avec JWT personnalisé, vous pouvez désactiver RLS ou utiliser des fonctions personnalisées.

## Étape 8 : Configuration du stockage (optionnel)

Si vous voulez stocker les photos et fichiers sur Supabase Storage :

1. Allez dans **Storage** dans Supabase
2. Créez un nouveau bucket nommé `uploads`
3. Configurez les politiques d'accès :
   - **Public** : Pour les fichiers accessibles publiquement
   - **Private** : Pour les fichiers nécessitant une authentification

## Étape 9 : Créer un utilisateur admin initial

Vous pouvez créer un utilisateur admin via Prisma Studio ou directement en SQL :

```sql
-- Hasher le mot de passe avec bcrypt (remplacez 'your-password' par un mot de passe)
-- Utilisez un outil en ligne ou votre application pour générer le hash
INSERT INTO users (email, password_hash, role)
VALUES ('admin@example.com', '$2a$10$...', 'admin');
```

Ou utilisez Prisma Studio :
```bash
cd frontend
npx prisma studio
```

## Limites du plan gratuit

- **500 MB** de base de données
- **1 GB** de stockage de fichiers
- **2 GB** de bande passante
- **50 000** requêtes par mois

## Migration des données existantes

Voir `MIGRATION_DATA.md` pour migrer les données de SQLite vers Supabase.

## Troubleshooting

### Erreur de connexion

- Vérifiez que le mot de passe dans la connection string est correct
- Vérifiez que votre IP n'est pas bloquée (Settings > Database > Connection Pooling)

### Erreur de migration

- Vérifiez que le schéma Prisma est correct
- Vérifiez que vous avez les permissions nécessaires
- Essayez de supprimer et recréer les migrations

### RLS bloque les requêtes

- Vérifiez que les politiques RLS sont correctement configurées
- Pour le développement, vous pouvez temporairement désactiver RLS :
  ```sql
  ALTER TABLE table_name DISABLE ROW LEVEL SECURITY;
  ```

## Support

- Documentation Supabase : [https://supabase.com/docs](https://supabase.com/docs)
- Discord Supabase : [https://discord.supabase.com](https://discord.supabase.com)
