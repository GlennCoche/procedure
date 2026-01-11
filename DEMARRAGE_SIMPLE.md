# 🚀 Démarrage Ultra-Simple

## Méthode 1 : Serveur de Démarrage Web (RECOMMANDÉ)

### Étape 1 : Lancer le serveur de démarrage

```bash
cd /Users/glenn/Desktop/procedures
python3 startup_server.py
```

### Étape 2 : Ouvrir votre navigateur

Allez sur : **http://localhost:8080**

### Étape 3 : Cliquer sur "Démarrer l'Application"

C'est tout ! Le système va :
- ✅ Vérifier et créer les fichiers .env automatiquement
- ✅ Démarrer le backend
- ✅ Démarrer le frontend
- ✅ Afficher l'état en temps réel
- ✅ Vous donner les liens pour accéder à l'application

## Méthode 2 : Script Shell (Alternative)

```bash
./start.sh
```

## Accès à l'Application

Une fois démarré :
- **Application Web** : http://localhost:3000
- **API Documentation** : http://localhost:8000/docs
- **Panneau de Contrôle** : http://localhost:8080

## Arrêter l'Application

Depuis le panneau de contrôle (http://localhost:8080), cliquez sur "Arrêter"

Ou depuis le terminal : `Ctrl+C`
