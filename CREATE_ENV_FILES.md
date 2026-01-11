# ⚠️ IMPORTANT : Créer les fichiers .env

Le script `start.sh` nécessite les fichiers de configuration suivants :

## 1. Backend - Créer `backend/.env`

```bash
cd backend
cat > .env << 'EOF'
OPENAI_API_KEY=sk-votre-clé-api-openai
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=change-me-in-production-please-use-secure-random-key-12345
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:3001
EOF
```

## 2. Frontend - Créer `frontend/.env.local`

```bash
cd frontend
cat > .env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=change-me-in-production-please-use-secure-random-key-12345
EOF
```

## 3. Ensuite, relancer le script

```bash
./start.sh
```

## Ou créer manuellement

**Backend** (`backend/.env`):
```
OPENAI_API_KEY=votre-clé-api-openai
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=votre-clé-secrète-aléatoire
```

**Frontend** (`frontend/.env.local`):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=votre-clé-secrète-aléatoire
```
