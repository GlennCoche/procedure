#!/bin/bash

# Script pour configurer PM2 pour gérer le serveur Next.js
# PM2 est un gestionnaire de processus qui redémarre automatiquement le serveur

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo "🔧 Configuration de PM2 pour Next.js..."

# Vérifier si PM2 est installé
if ! command -v pm2 &> /dev/null; then
    echo "📦 Installation de PM2..."
    npm install -g pm2
fi

cd "$FRONTEND_DIR"

# Créer le fichier de configuration PM2
cat > "$PROJECT_DIR/ecosystem.config.js" << 'EOF'
module.exports = {
  apps: [{
    name: 'procedures-nextjs',
    script: 'npm',
    args: 'run dev',
    cwd: './frontend',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'development',
      PORT: 3000
    },
    error_file: './logs/pm2-error.log',
    out_file: './logs/pm2-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true
  }]
}
EOF

echo "✅ Configuration PM2 créée: ecosystem.config.js"
echo ""
echo "📋 Commandes PM2 disponibles:"
echo "   pm2 start ecosystem.config.js    # Démarrer le serveur"
echo "   pm2 stop procedures-nextjs       # Arrêter le serveur"
echo "   pm2 restart procedures-nextjs    # Redémarrer le serveur"
echo "   pm2 status                       # Voir le statut"
echo "   pm2 logs procedures-nextjs       # Voir les logs"
echo "   pm2 save                         # Sauvegarder la configuration"
echo "   pm2 startup                      # Démarrer au boot du système"
echo ""
echo "💡 Pour démarrer automatiquement au boot:"
echo "   pm2 startup"
echo "   pm2 save"
