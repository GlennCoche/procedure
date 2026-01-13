# 🔍 Diagnostic - Erreur Login 500

**Date :** 2026-01-13  
**URL testée :** https://procedure1.vercel.app/login

---

## ❌ Problème Identifié

L'endpoint `/api/test-db` retourne :
```json
{
  "database": {
    "connected": false,
    "error": "Can't reach database server at `db.mxxggubgvurldcneeter.supabase.co:5432`"
  }
}
```

**Cause :** Vercel essaie de se connecter directement au port 5432 au lieu d'utiliser le **Connection Pooler** (port 6543).

**Analyse des logs Supabase :** La base de données est **active et accessible**. Des connexions depuis Vercel sont détectées, mais elles utilisent probablement le pooler. Le problème est que la `DATABASE_URL` dans Vercel pointe vers la connexion directe au lieu du pooler.

---

## 🔍 Causes Possibles

### 1. **Base de données Supabase en pause** ⚠️
- Les projets Supabase gratuits se mettent en pause après 7 jours d'inactivité
- **Solution :** Réactiver le projet dans le dashboard Supabase

### 2. **DATABASE_URL incorrecte ou expirée** ⚠️
- La connection string peut avoir expiré ou être incorrecte
- **Solution :** Vérifier et mettre à jour la `DATABASE_URL` dans Vercel

### 3. **Problème de réseau/firewall** ⚠️
- Les IP de Vercel peuvent être bloquées
- **Solution :** Vérifier les paramètres de sécurité Supabase

---

## ✅ Solutions à Appliquer

### Solution 1 : Vérifier l'état du projet Supabase

1. **Aller sur** : https://supabase.com/dashboard/project/mxxggubgvurldcneeter
2. **Vérifier** si le projet est actif ou en pause
3. **Si en pause** : Cliquer sur "Resume" pour réactiver

### Solution 2 : Utiliser le Connection Pooler (OBLIGATOIRE)

**⚠️ IMPORTANT :** Pour Vercel (serverless), vous **DEVEZ** utiliser le Connection Pooler, pas la connexion directe.

1. **Aller sur** : https://supabase.com/dashboard/project/mxxggubgvurldcneeter/settings/database
2. **Section "Connection string"**
3. **Sélectionner** : **"Connection pooling"** (pas "Direct connection")
4. **Copier** la connection string (elle doit contenir `pooler.supabase.com` et le port `6543`)
5. **Format attendu** :
   ```
   postgresql://postgres.mxxggubgvurldcneeter:[PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres?pgbouncer=true&connection_limit=1
   ```
6. **Mettre à jour dans Vercel** :
   - Aller sur : https://vercel.com/glenns-projects-7d11114a/procedure1/settings/environment-variables
   - Trouver `DATABASE_URL`
   - Cliquer sur "Edit"
   - Remplacer par la connection string avec pooler
   - Sauvegarder
7. **Redéployer** l'application

### Solution 3 : Vérifier les paramètres de sécurité Supabase

1. **Aller sur** : https://supabase.com/dashboard/project/mxxggubgvurldcneeter/settings/database
2. **Vérifier** :
   - "Connection pooling" est activé
   - "SSL mode" est configuré correctement
   - Aucune restriction IP qui bloque Vercel

### Solution 4 : Tester la connexion locale

Pour vérifier si le problème vient de Supabase ou de Vercel :

```bash
# Tester la connexion avec la DATABASE_URL de Vercel
cd frontend
npx prisma db pull
```

---

## 📋 Checklist de Vérification

- [ ] Projet Supabase est actif (pas en pause)
- [ ] `DATABASE_URL` dans Vercel est correcte et à jour
- [ ] Connection pooling est activé dans Supabase
- [ ] SSL mode est configuré correctement
- [ ] Aucune restriction IP qui bloque Vercel
- [ ] Redéploiement effectué après modification de `DATABASE_URL`

---

## 🚀 Actions Immédiates

1. **Vérifier l'état du projet Supabase** (Solution 1)
2. **Vérifier la DATABASE_URL dans Vercel** (Solution 2)
3. **Redéployer l'application** si nécessaire
4. **Tester à nouveau** : https://procedure1.vercel.app/api/test-db
5. **Tester le login** : https://procedure1.vercel.app/login

---

## 📝 Notes

- Le problème n'est **pas** lié au code TypeScript (corrigé)
- Le problème n'est **pas** lié au Prisma Client (généré correctement)
- Le problème est **uniquement** lié à la connexion à la base de données Supabase

Une fois la connexion rétablie, le login devrait fonctionner correctement.
