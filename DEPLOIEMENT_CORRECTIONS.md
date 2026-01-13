# Déploiement des Corrections - Bug Login

**Date :** 2025-01-13

---

## ⚠️ Situation

Le répertoire n'est pas un dépôt Git initialisé. Les changements doivent être déployés via une autre méthode.

---

## 🚀 Options de Déploiement

### Option 1 : Via Vercel CLI (Recommandé)

Si Vercel CLI est installé et configuré :

```bash
cd /Users/glenn/Desktop/procedures/frontend

# Vérifier la connexion Vercel
vercel whoami

# Si non connecté, se connecter
vercel login

# Lier le projet (si pas déjà fait)
vercel link

# Déployer
vercel --prod
```

### Option 2 : Via GitHub (Si le projet est connecté)

Si le projet est connecté à GitHub via Vercel :

1. **Initialiser Git (si nécessaire) :**
   ```bash
   cd /Users/glenn/Desktop/procedures
   git init
   git remote add origin <URL_DU_REPO_GITHUB>
   ```

2. **Commiter et pousser :**
   ```bash
   git add frontend/app/api/auth/
   git commit -m "fix: correct cookie handling in Next.js 15 API routes"
   git push origin main
   ```

3. **Vercel déploiera automatiquement**

### Option 3 : Via Interface Vercel (Upload manuel)

1. Aller sur : https://vercel.com/glenns-projects-7d11114a/procedure1/deployments
2. Cliquer sur "Deploy" ou "Redeploy"
3. Vercel utilisera le code du dernier déploiement

**Note :** Cette option ne fonctionnera que si les fichiers sont déjà dans le dépôt connecté.

### Option 4 : Créer un Dépôt Git et Connecter

1. **Initialiser Git :**
   ```bash
   cd /Users/glenn/Desktop/procedures
   git init
   ```

2. **Créer un fichier .gitignore :**
   ```bash
   cat > .gitignore << EOF
   node_modules/
   .next/
   .env.local
   .env*.local
   *.log
   venv/
   __pycache__/
   *.pyc
   .DS_Store
   EOF
   ```

3. **Premier commit :**
   ```bash
   git add .
   git commit -m "Initial commit with login bug fix"
   ```

4. **Créer un repo sur GitHub** et connecter :
   ```bash
   git remote add origin <URL_DU_REPO>
   git branch -M main
   git push -u origin main
   ```

5. **Connecter Vercel au repo GitHub** via le dashboard Vercel

---

## 📋 Fichiers Modifiés à Déployer

Les fichiers suivants ont été corrigés :

1. ✅ `frontend/app/api/auth/login/route.ts`
2. ✅ `frontend/app/api/auth/register/route.ts`
3. ✅ `frontend/app/api/auth/logout/route.ts`

---

## ✅ Vérification Après Déploiement

Une fois déployé, tester :

1. **Aller sur** : https://procedure1.vercel.app/login
2. **Se connecter avec** :
   - Email : `admin@procedures.local`
   - Mot de passe : `AdminSecure123!`
3. **Vérifier** :
   - ✅ Pas d'erreur 500
   - ✅ Connexion réussie
   - ✅ Redirection vers le dashboard
   - ✅ Cookie `auth-token` défini

---

## 🔍 Vérifier les Logs Vercel

Si des erreurs persistent :

1. Aller sur : https://vercel.com/glenns-projects-7d11114a/procedure1/logs
2. Vérifier les logs récents
3. Chercher les erreurs liées à `/api/auth/login`

---

## 📝 Résumé des Corrections

- ✅ Utilisation de `Response.cookies.set()` au lieu de `cookies().set()`
- ✅ Normalisation de l'email en minuscules
- ✅ Amélioration de la gestion d'erreurs

**Les fichiers sont prêts à être déployés !**

---

**Choisissez l'option de déploiement qui correspond à votre configuration actuelle.**
