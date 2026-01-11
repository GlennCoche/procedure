# ✅ Test de Démarrage

## Vérification Rapide

Le serveur de démarrage devrait maintenant :
1. ✅ Détecter si un serveur est déjà en cours d'exécution
2. ✅ Utiliser un port alternatif si 8080 est occupé
3. ✅ Ouvrir automatiquement le navigateur sur macOS
4. ✅ Gérer les erreurs gracieusement

## Test

1. **Double-cliquez sur `LAUNCH.command`**
   - Si un serveur tourne déjà → Le navigateur s'ouvre automatiquement
   - Sinon → Le serveur démarre et ouvre le navigateur

2. **Ou depuis le terminal :**
   ```bash
   cd /Users/glenn/Desktop/procedures
   python3 startup_server.py
   ```

3. **Ouvrez http://localhost:8080** dans votre navigateur

4. **Cliquez sur "Démarrer l'Application"**

## Résolution de Problèmes

### Port déjà utilisé
Le script détecte automatiquement et utilise un port alternatif, ou vous informe si un serveur tourne déjà.

### Serveur déjà en cours
Si vous voyez "Address already in use", c'est qu'un serveur tourne déjà. Ouvrez simplement http://localhost:8080 dans votre navigateur.

### Arrêter un serveur existant
```bash
lsof -ti:8080 | xargs kill
```
