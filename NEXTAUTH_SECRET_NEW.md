# Nouveau NEXTAUTH_SECRET à Configurer dans Vercel

**Date :** 2025-01-13  
**Action requise :** Mettre à jour la variable d'environnement dans Vercel

---

## Secret Généré

Exécutez cette commande pour générer le secret :

```bash
openssl rand -base64 32
```

**OU** utilisez le script :
```bash
./scripts/generate-secret.sh
```

---

## Configuration dans Vercel

1. **Aller sur** : https://vercel.com/glenns-projects-7d11114a/procedure1/settings/environment-variables

2. **Trouver** la variable `NEXTAUTH_SECRET`

3. **Cliquer sur "Edit"**

4. **Remplacer** la valeur actuelle (`https://procedure1.vercel.app/`) par le nouveau secret généré

5. **Cliquer sur "Save"**

6. **Redéployer** l'application :
   - Aller dans "Deployments"
   - Cliquer sur "Redeploy" sur le dernier déploiement
   - Attendre 2-3 minutes

---

## Vérification

Après le redéploiement, tester la connexion :
- Aller sur https://procedure1.vercel.app/login
- Se connecter avec les identifiants admin
- Vérifier que l'authentification fonctionne

---

**⚠️ IMPORTANT :** Supprimez ce fichier après avoir configuré le secret dans Vercel.
