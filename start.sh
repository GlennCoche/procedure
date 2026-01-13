#!/bin/bash

# Script de démarrage pour le projet

echo "🚀 Démarrage du système de procédures..."

# Vérifier que les répertoires existent
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Erreur: Les répertoires backend et frontend doivent exister"
    exit 1
fi

# Créer les fichiers .env s'ils n'existent pas
if [ ! -f "backend/.env" ]; then
    echo "📝 Création de backend/.env..."
    cat > backend/.env << 'EOF'
OPENAI_API_KEY=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
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=change-me-in-production-please-use-secure-random-key-12345
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:3001
EOF
fi

if [ ! -f "frontend/.env.local" ]; then
    echo "📝 Création de frontend/.env.local..."
    cat > frontend/.env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=change-me-in-production-please-use-secure-random-key-12345
EOF
fi

# Démarrer le backend
echo "📦 Démarrage du backend..."
cd backend
if [ ! -d "venv" ]; then
    echo "Création de l'environnement virtuel..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt

# Vérifier que la base de données existe
if [ ! -f "app.db" ]; then
    echo "Initialisation de la base de données..."
    python scripts/init_db.py
fi

echo "✅ Backend prêt sur http://localhost:8000"
uvicorn app.main:app --reload &
BACKEND_PID=$!

# Attendre que le backend démarre
sleep 3

# Démarrer le frontend
echo "🎨 Démarrage du frontend..."
cd ../frontend

if [ ! -d "node_modules" ]; then
    echo "Installation des dépendances..."
    npm install
fi

echo "✅ Frontend prêt sur http://localhost:3000"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✨ Application démarrée!"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:3000"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter"

# Attendre les processus
wait $BACKEND_PID $FRONTEND_PID
