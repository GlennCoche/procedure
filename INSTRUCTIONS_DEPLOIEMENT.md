# Instructions de Déploiement - Corrections Login

**Date :** 2025-01-13

---

## 📋 Situation Actuelle

- ✅ **Corrections effectuées** : Les fichiers ont été corrigés localement
- ⚠️ **Dépôt Git** : Non initialisé dans ce répertoire
- ✅ **Vercel CLI** : Installé et configuré
- ⚠️ **Configuration Vercel** : Problème de chemin détecté

---

## 🚀 Solutions pour Déployer

### Option 1 : Déployer via Vercel Dashboard (Le Plus Simple)

Si votre projet est connecté à GitHub, Vercel déploie automatiquement à chaque push.

**Si vous avez accès au repo GitHub :**

1. **Initialiser Git dans ce répertoire :**
   ```bash
   cd /Users/glenn/Desktop/procedures
   git init
   git remote add origin <URL_DU_REPO_GITHUB>
   git add frontend/app/api/auth/
   git commit -m "fix: correct cookie handling in Next.js 15 API routes"
   git push origin main
   ```

2. **Vercel déploiera automatiquement** (2-3 minutes)

### Option 2 : Corriger la Configuration Vercel

1. **Aller sur** : https://vercel.com/glenns-projects-7d11114a/procedure1/settings

2. **Vérifier "Root Directory"** :
   - Doit être : `frontend`
   - Si c'est `frontend/frontend`, corriger en `frontend`

3. **Sauvegarder** et redéployer

### Option 3 : Upload Manuel via Vercel CLI (Si GitHub non disponible)

Si le projet n'est pas connecté à GitHub, vous pouvez créer un déploiement temporaire :

```bash
cd /Users/glenn/Desktop/procedures/frontend

# Créer un déploiement
vercel --prod
```

**Note :** Cela créera un nouveau déploiement mais ne mettra pas à jour le déploiement principal si le projet est connecté à GitHub.

### Option 4 : Utiliser Vercel Git Integration

1. **Aller sur** : https://vercel.com/glenns-projects-7d11114a/procedure1/settings/git

2. **Vérifier le repo connecté**

3. **Si aucun repo n'est connecté**, connecter votre repo GitHub

4. **Une fois connecté**, pousser les changements vers GitHub et Vercel déploiera automatiquement

---

## 📝 Fichiers Modifiés

Les fichiers suivants ont été corrigés et doivent être déployés :

1. ✅ `frontend/app/api/auth/login/route.ts`
2. ✅ `frontend/app/api/auth/register/route.ts`
3. ✅ `frontend/app/api/auth/logout/route.ts`

---

## ✅ Vérification Après Déploiement

Une fois déployé :

1. **Aller sur** : https://procedure1.vercel.app/login
2. **Se connecter avec** :
   - Email : `admin@procedures.local`
   - Mot de passe : `AdminSecure123!`
3. **Vérifier** :
   - ✅ Pas d'erreur 500
   - ✅ Connexion réussie
   - ✅ Redirection vers le dashboard

---

## 🔍 Si le Déploiement Échoue

### Vérifier les Logs Vercel

1. Aller sur : https://vercel.com/glenns-projects-7d11114a/procedure1/logs
2. Vérifier les erreurs de build ou runtime

### Vérifier la Configuration

1. Aller sur : https://vercel.com/glenns-projects-7d11114a/procedure1/settings
2. Vérifier :
   - **Root Directory** : `frontend`
   - **Build Command** : `npm run build`
   - **Output Directory** : `.next`
   - **Install Command** : `npm install`

---

## 💡 Recommandation

**La meilleure solution** est de connecter le projet à GitHub (si ce n'est pas déjà fait) et de pousser les changements. Cela permet :
- ✅ Déploiements automatiques
- ✅ Historique des changements
- ✅ Rollback facile si nécessaire

---

## 📋 Checklist

- [ ] Déterminer si le projet est connecté à GitHub
- [ ] Si oui, pousser les changements vers GitHub
- [ ] Si non, utiliser une des options ci-dessus
- [ ] Vérifier le déploiement sur Vercel
- [ ] Tester la connexion

---

**Les fichiers sont corrigés et prêts à être déployés !**
