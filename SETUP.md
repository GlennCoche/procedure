# Guide de Configuration

## Configuration Initiale

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Créer `backend/.env`:
```env
OPENAI_API_KEY=sk-votre-clé-api-openai
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=change-me-to-secure-key-in-production
```

Initialiser la base de données:
```bash
python scripts/init_db.py
python scripts/create_admin.py
```

Lancer le serveur:
```bash
uvicorn app.main:app --reload
```

### 2. Frontend

```bash
cd frontend
npm install
```

Créer `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=change-me-to-secure-key-in-production
```

Lancer le serveur:
```bash
npm run dev
```

## Utilisation

1. Accéder à http://localhost:3000
2. Se connecter avec le compte admin créé
3. Créer des procédures via `/admin/procedures`
4. Les techniciens peuvent exécuter les procédures via `/dashboard/procedures`

## Notes

- Le modèle OpenAI utilisé est GPT-4o-mini pour réduire les coûts
- La Vision API utilise GPT-4o pour la reconnaissance d'images
- Un système de cache est implémenté pour réduire les appels API
- Les fichiers uploadés sont stockés dans `backend/uploads/`
