# 🎯 Instructions de Démarrage - Version Simplifiée

## ✅ Solution la Plus Simple

### Sur macOS :

**Option 1 : Double-cliquez sur `LAUNCH.command`**
- Le fichier est sur votre bureau dans le dossier `procedures`
- Double-cliquez dessus
- Votre navigateur s'ouvrira automatiquement (ou allez sur http://localhost:8080)
- Cliquez sur "Démarrer l'Application"

**Option 2 : Terminal simple**
```bash
cd /Users/glenn/Desktop/procedures
python3 startup_server.py
```
Puis ouvrez http://localhost:8080 dans votre navigateur

### Sur Windows/Linux :

```bash
cd procedures
python3 startup_server.py
```
Puis ouvrez http://localhost:8080 dans votre navigateur

## 🎨 Interface Web de Démarrage

Une fois sur http://localhost:8080, vous verrez :

1. **État des serveurs** en temps réel
   - Backend API (port 8000)
   - Frontend Web (port 3000)

2. **Bouton "Démarrer l'Application"**
   - Cliquez dessus
   - Le système fait TOUT automatiquement :
     - ✅ Crée les fichiers .env
     - ✅ Vérifie les dépendances
     - ✅ Démarre le backend
     - ✅ Démarre le frontend
     - ✅ Affiche les logs en temps réel

3. **Quand c'est prêt :**
   - Vous verrez "✅ Application prête !"
   - Des liens pour accéder à l'application
   - Un bouton "Arrêter" pour tout arrêter

## 📱 Accès à l'Application

Une fois démarré :
- **Application principale** : http://localhost:3000
- **Documentation API** : http://localhost:8000/docs
- **Panneau de contrôle** : http://localhost:8080 (reste ouvert)

## 🛑 Arrêter l'Application

- Depuis le panneau web : Cliquez sur "Arrêter"
- Depuis le terminal : `Ctrl+C` dans le terminal où tourne `startup_server.py`

## ⚠️ Première Installation

Si c'est la première fois :
1. Le système créera automatiquement les fichiers .env
2. Pour le backend, vous devrez peut-être installer les dépendances :
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Pour le frontend, vous devrez peut-être installer les dépendances :
   ```bash
   cd frontend
   npm install
   ```

Après la première installation, tout sera automatique ! 🎉
