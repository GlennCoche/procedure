# Guide - Serveur Next.js Persistant

Ce guide explique comment maintenir le serveur Next.js actif automatiquement.

## 🎯 Solutions Disponibles

### Solution 1 : Script de Gestion Simple (Recommandé pour début)

Le script `scripts/start-server.sh` permet de démarrer, arrêter et gérer le serveur facilement.

#### Utilisation

```bash
# Démarrer le serveur
./scripts/start-server.sh start
# ou depuis frontend/
npm run server:start

# Vérifier le statut
./scripts/start-server.sh status
# ou
npm run server:status

# Arrêter le serveur
./scripts/start-server.sh stop
# ou
npm run server:stop

# Redémarrer le serveur
./scripts/start-server.sh restart
# ou
npm run server:restart
```

#### Avantages
- ✅ Simple à utiliser
- ✅ Pas de dépendances supplémentaires
- ✅ Logs dans `.next-server.log`
- ✅ Gestion du PID automatique

#### Inconvénients
- ⚠️  Ne redémarre pas automatiquement en cas de crash
- ⚠️  Ne démarre pas automatiquement au boot du système

---

### Solution 2 : PM2 (Recommandé pour production)

PM2 est un gestionnaire de processus qui redémarre automatiquement le serveur en cas de crash.

#### Installation et Configuration

```bash
# Installer PM2 globalement
npm install -g pm2

# Configurer PM2 pour ce projet
./scripts/setup-pm2.sh
```

#### Utilisation

```bash
# Démarrer le serveur
pm2 start ecosystem.config.js

# Voir le statut
pm2 status

# Voir les logs
pm2 logs procedures-nextjs

# Redémarrer
pm2 restart procedures-nextjs

# Arrêter
pm2 stop procedures-nextjs

# Sauvegarder la configuration
pm2 save

# Démarrer automatiquement au boot du système
pm2 startup
pm2 save
```

#### Avantages
- ✅ Redémarrage automatique en cas de crash
- ✅ Démarrage automatique au boot (avec `pm2 startup`)
- ✅ Gestion des logs
- ✅ Monitoring intégré
- ✅ Idéal pour la production

#### Inconvénients
- ⚠️  Nécessite l'installation de PM2
- ⚠️  Configuration initiale requise

---

### Solution 3 : Launchd (macOS uniquement)

Pour démarrer automatiquement le serveur au démarrage de macOS.

#### Création du fichier LaunchAgent

```bash
# Créer le répertoire si nécessaire
mkdir -p ~/Library/LaunchAgents

# Créer le fichier de configuration
cat > ~/Library/LaunchAgents/com.procedures.nextjs.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.procedures.nextjs</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/npm</string>
        <string>run</string>
        <string>dev</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/glenn/Desktop/procedures/frontend</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/glenn/Desktop/procedures/.next-server.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/glenn/Desktop/procedures/.next-server-error.log</string>
</dict>
</plist>
EOF

# Charger le service
launchctl load ~/Library/LaunchAgents/com.procedures.nextjs.plist

# Démarrer immédiatement
launchctl start com.procedures.nextjs
```

#### Commandes Launchd

```bash
# Démarrer
launchctl start com.procedures.nextjs

# Arrêter
launchctl stop com.procedures.nextjs

# Vérifier le statut
launchctl list | grep procedures

# Désactiver le démarrage automatique
launchctl unload ~/Library/LaunchAgents/com.procedures.nextjs.plist
```

#### Avantages
- ✅ Démarrage automatique au boot
- ✅ Redémarrage automatique en cas de crash
- ✅ Intégré à macOS
- ✅ Pas de dépendances externes

#### Inconvénients
- ⚠️  macOS uniquement
- ⚠️  Configuration plus complexe

---

## 🚀 Recommandation

### Pour le Développement Local

**Utiliser le script simple** (`scripts/start-server.sh`) :
- Facile à utiliser
- Pas de configuration complexe
- Suffisant pour le développement

```bash
# Au début de votre session de travail
npm run server:start

# Vérifier que tout fonctionne
npm run server:status
```

### Pour la Production ou Usage Intensif

**Utiliser PM2** :
- Redémarrage automatique
- Monitoring
- Gestion des logs
- Démarrage au boot

```bash
# Configuration initiale (une seule fois)
./scripts/setup-pm2.sh
pm2 start ecosystem.config.js
pm2 startup
pm2 save
```

---

## 📝 Scripts NPM Disponibles

Après configuration, vous pouvez utiliser :

```bash
# Depuis le dossier frontend/
npm run server:start    # Démarrer le serveur
npm run server:stop     # Arrêter le serveur
npm run server:restart  # Redémarrer le serveur
npm run server:status  # Vérifier le statut
```

---

## 🔍 Vérification

Pour vérifier que le serveur est actif :

```bash
# Vérifier le processus
ps aux | grep "next dev"

# Tester l'API
curl http://localhost:3000/api/auth/me
# ou
curl http://localhost:3001/api/auth/me
```

---

## 🐛 Dépannage

### Le serveur ne démarre pas

1. Vérifier les logs : `tail -f .next-server.log`
2. Vérifier le port : `lsof -i :3000` ou `lsof -i :3001`
3. Vérifier les variables d'environnement : `cat frontend/.env.local`

### Le serveur s'arrête tout seul

1. Vérifier la mémoire : `free -h` ou `vm_stat`
2. Vérifier les erreurs dans les logs
3. Utiliser PM2 pour redémarrage automatique

### Port déjà utilisé

```bash
# Trouver le processus utilisant le port
lsof -i :3000

# Arrêter le processus
kill -9 <PID>
```

---

## ✅ Checklist de Démarrage

- [ ] Serveur démarré : `npm run server:start`
- [ ] Statut vérifié : `npm run server:status`
- [ ] API accessible : `curl http://localhost:3000/api/auth/me`
- [ ] Tests fonctionnent : `npm run test:all`

---

**Le serveur restera actif jusqu'à ce que vous l'arrêtiez manuellement ou que vous redémarriez votre machine (sauf si vous utilisez PM2 avec `startup`).**
