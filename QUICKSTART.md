# Guide de Démarrage Rapide

## 🚀 Installation Express

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
SECRET_KEY=change-me-in-production-12345
```

Initialiser:
```bash
python scripts/init_db.py
python scripts/create_admin.py
```

Lancer:
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
NEXTAUTH_SECRET=change-me-in-production-12345
```

Lancer:
```bash
npm run dev
```

## ✅ Vérification

1. Backend: http://localhost:8000/docs
2. Frontend: http://localhost:3000
3. Se connecter avec le compte admin créé
4. Créer une procédure via `/admin/procedures`

## 🔧 Problèmes Courants

### Erreur "Module not found"
- Vérifier que toutes les dépendances sont installées
- Relancer `pip install -r requirements.txt` ou `npm install`

### Erreur de connexion API
- Vérifier que le backend tourne sur le port 8000
- Vérifier les variables d'environnement

### Erreur de base de données
- Exécuter `python scripts/init_db.py`
- Vérifier que le fichier `app.db` existe
