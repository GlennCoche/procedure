# Instructions - Clear Cache Vercel

## 🚨 Action Manuelle Requise

Le problème Prisma persiste car **Vercel utilise un cache de build** qui contient l'ancien Prisma Client généré avec SQLite.

### Étapes pour Clear le Cache

1. **Aller sur Vercel Dashboard** :
   - https://vercel.com/dashboard
   - Sélectionner le projet `procedure1`

2. **Aller dans Settings** :
   - Cliquer sur "Settings" dans le menu de gauche
   - Section "General"

3. **Clear Build Cache** :
   - Scroller jusqu'à la section "Build & Development Settings"
   - Cliquer sur "Clear Build Cache" ou "Purge Build Cache"
   - Confirmer l'action

4. **Redéployer** :
   - Aller dans "Deployments"
   - Cliquer sur "Redeploy" sur le dernier déploiement
   - Ou faire un nouveau commit pour déclencher un redéploiement automatique

---

## ✅ Corrections Appliquées

1. ✅ **Script prebuild ajouté** : Nettoie le Prisma Client avant le build
2. ✅ **schema.postgresql.prisma supprimé** : Évite la confusion
3. ✅ **Script build** : `prisma generate && next build`

---

## 🔍 Vérification

Après le clear du cache et le redéploiement :

1. **Vérifier les logs de build Vercel** :
   - Vérifier que `prebuild` s'exécute
   - Vérifier que `prisma generate` s'exécute
   - Vérifier qu'il n'y a pas d'erreur

2. **Tester l'application** :
   - `/api/auth/login` - Plus d'erreur 500
   - `/api/test-db` - Connexion DB fonctionnelle
   - `/startup` - Plus d'erreur CORS

---

**Le clear du cache Vercel est la solution définitive au problème.**
