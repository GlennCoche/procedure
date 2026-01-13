#!/bin/bash
# Launcher macOS - Double-cliquez simplement sur ce fichier !

cd "$(dirname "$0")"

# Vérifier si un serveur est déjà en cours d'exécution
if curl -s http://localhost:8080/api/status > /dev/null 2>&1; then
    echo "✅ Un serveur de démarrage est déjà en cours d'exécution !"
    echo "📱 Ouverture du navigateur sur http://localhost:8080"
    open http://localhost:8080
    exit 0
fi

# Lancer le serveur
echo "🚀 Démarrage du serveur de démarrage..."
python3 startup_server.py
