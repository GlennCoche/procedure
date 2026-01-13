# NEXTAUTH_SECRET - Valeur à Configurer

**⚠️ TEMPORAIRE - À SUPPRIMER APRÈS UTILISATION**

---

## Secret Généré

Exécutez cette commande pour générer votre secret :

```bash
openssl rand -base64 32
```

**OU** utilisez Node.js :

```bash
node -e "const crypto = require('crypto'); console.log(crypto.randomBytes(32).toString('base64'))"
```

**OU** utilisez Python :

```bash
python3 -c "import secrets, base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"
```

---

## Configuration dans Vercel

1. **Générez le secret** avec une des commandes ci-dessus

2. **Copiez le secret généré**

3. **Allez sur** : https://vercel.com/glenns-projects-7d11114a/procedure1/settings/environment-variables

4. **Trouvez** la variable `NEXTAUTH_SECRET`

5. **Cliquez sur "Edit"**

6. **Remplacez** la valeur actuelle :
   - **Ancienne valeur** : `https://procedure1.vercel.app/`
   - **Nouvelle valeur** : [Collez le secret généré]

7. **Cliquez sur "Save"**

8. **Redéployez** :
   - Allez dans "Deployments"
   - Cliquez sur "Redeploy" sur le dernier déploiement
   - Attendez 2-3 minutes

---

## Exemple de Secret

Un secret généré ressemble à ceci (64 caractères) :
```
Kx9mP2vL8nQ5rT7wY3zA6bC1dE4fG8hI0jK2lM5nO8pQ1rS4tU7vW0xY3zA6bC=
```

**⚠️ NE COMMITEZ PAS CE FICHIER AVEC UN SECRET RÉEL DEDANS !**

---

**Supprimez ce fichier après avoir configuré le secret dans Vercel.**
