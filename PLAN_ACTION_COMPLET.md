# Plan d'Action Complet - Correction des Problèmes

## 🔍 Analyse des Problèmes

### Problème 1 : Prisma Client toujours avec SQLite

**Symptôme** : Les logs Vercel montrent toujours :
```
provider = "sqlite" // Dev: SQLite, Prod: PostgreSQL (Supabase)
error: Error validating datasource `db`: the URL must start with the protocol `file:`.
```

**Cause** : Le Prisma Client généré dans `node_modules/.prisma/client` contient encore l'ancien schema SQLite, même si `schema.prisma` est correct.

**Solution** :
1. Supprimer le Prisma Client généré
2. Régénérer avec le bon schema
3. S'assurer que Vercel utilise le bon schema lors du build

### Problème 2 : Page /startup essaie de se connecter à localhost

**Symptôme** : La page `/startup` essaie de se connecter à `http://localhost:8000` ce qui ne fonctionne pas en production Vercel.

**Cause** : La page est configurée pour un backend FastAPI local, pas pour Next.js API routes.

**Solution** : Adapter la page pour utiliser les API routes Next.js en production.

---

## ✅ Plan d'Action

### Étape 1 : Corriger le Prisma Client

1. **Supprimer le Prisma Client généré** :
   ```bash
   cd frontend
   rm -rf node_modules/.prisma
   ```

2. **Régénérer le Prisma Client** :
   ```bash
   npx prisma generate
   ```

3. **Vérifier que le schema généré est correct** :
   ```bash
   cat node_modules/.prisma/client/schema.prisma | grep provider
   ```

4. **Commiter les changements** :
   - Ajouter `node_modules/.prisma` au `.gitignore` si nécessaire
   - Commiter le `schema.prisma` correct

### Étape 2 : Corriger la page /startup

1. **Adapter la page pour la production** :
   - Détecter l'environnement (dev vs production)
   - En production : Utiliser les API routes Next.js (`/api/procedures`, `/api/auth/me`)
   - En dev : Utiliser `localhost:8000` si nécessaire

2. **Créer une API route pour le status** :
   - Créer `/api/startup/status` qui vérifie les services Next.js
   - Retourner l'état des services

### Étape 3 : Vérifier le Build Vercel

1. **S'assurer que le script build est correct** :
   - Vérifier que `"build": "prisma generate && next build"` est dans `package.json`
   - Vérifier que `postinstall: prisma generate` est présent

2. **Forcer un rebuild complet** :
   - Clear le cache de build Vercel
   - Redéployer

---

## 🚀 Actions Immédiates

1. ✅ Supprimer et régénérer le Prisma Client
2. ✅ Corriger la page `/startup` pour la production
3. ✅ Commiter et pousser les changements
4. ⏳ Vercel redéploiera automatiquement

---

## 📝 Fichiers à Modifier

1. `frontend/app/startup/page.tsx` - Adapter pour la production
2. `frontend/app/api/startup/status/route.ts` - Nouvelle route API (si nécessaire)
3. Vérifier `frontend/.gitignore` - S'assurer que `.prisma` n'est pas commité

---

## 🔍 Vérification Post-Déploiement

Après le redéploiement :
1. Tester `/api/auth/login` - Plus d'erreur 500
2. Tester `/startup` - Plus d'erreur CORS
3. Tester `/api/test-db` - Connexion DB fonctionnelle
