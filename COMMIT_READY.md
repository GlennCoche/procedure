# Commandes Git Prêtes à Exécuter

**Date :** 2025-01-13

---

## Changements à Commiter

### Fichiers Supprimés
- `frontend/app/api/setup/create-admin/route.ts`
- `frontend/app/api/setup/migrate/route.ts`
- Dossier `frontend/app/api/setup/` (supprimé)

### Nouveaux Fichiers
- `scripts/create-admin.sh` - Script de création admin
- `scripts/create-admin-node.js` - Script Node.js pour création admin
- `scripts/test-api.sh` - Script de tests API
- `scripts/generate-secret.sh` - Script de génération de secret
- `FINALISATION_COMPLETE.md` - Résumé de finalisation
- `ACTIONS_IMMEDIATES.md` - Guide d'actions immédiates
- `NEXTAUTH_SECRET_VALUE.md` - Instructions pour NEXTAUTH_SECRET
- `NEXTAUTH_SECRET_NEW.md` - Documentation NEXTAUTH_SECRET

### Fichiers Modifiés
- `PLAN_FINALISATION_IMMEDIATE.md` - Checklist mise à jour

---

## Commandes Git

```bash
cd /Users/glenn/Desktop/procedures

# Vérifier les changements
git status

# Ajouter tous les changements
git add frontend/app/api/setup
git add scripts/
git add *.md

# Vérifier ce qui sera commité
git status

# Commiter
git commit -m "chore: remove setup routes and add helper scripts

- Remove temporary setup routes (/api/setup/*) for security
- Add create-admin.sh script for admin creation
- Add create-admin-node.js alternative script
- Add test-api.sh script for API testing
- Add generate-secret.sh script for secret generation
- Add documentation files for finalization process
- Update PLAN_FINALISATION_IMMEDIATE.md with progress"

# Pousser vers GitHub
git push
```

---

## Après le Push

1. Vercel déploiera automatiquement les changements
2. Attendre 2-3 minutes pour le déploiement
3. Vérifier que les routes setup retournent 404 :
   ```bash
   curl -X POST https://procedure1.vercel.app/api/setup/create-admin \
     -H "Authorization: Bearer ejZ+z34wqydLsZwnXxfvIBR76CMFbrqHH1NATD6Ip5c="
   ```

---

**Exécutez ces commandes pour finaliser les changements.**
