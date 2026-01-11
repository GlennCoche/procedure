# 📊 Système de Logs Détaillé

## Logs Disponibles

### 1. Logs du Serveur de Démarrage
**Fichier :** `logs/startup_YYYYMMDD.log`

Contient :
- Toutes les requêtes HTTP (GET/POST)
- Démarrage des processus backend/frontend
- Erreurs et exceptions avec stack traces
- État des serveurs
- Données détaillées de chaque opération

**Format :**
```
[2026-01-11 14:35:12.345] [INFO] Fonction start_backend() appelée | Data: {"path": "/path/to/backend"}
[2026-01-11 14:35:12.456] [ERROR] Erreur démarrage backend | Data: {"error": "message"}
```

### 2. Logs Frontend (Console Navigateur)
**Accès :** Console du navigateur (F12)

Fonctions disponibles :
- `getDebugLogs()` - Voir tous les logs en mémoire
- `exportDebugLogs()` - Exporter les logs en JSON

**Format :**
```javascript
{
  "timestamp": "2026-01-11T14:35:12.345Z",
  "level": "error",
  "message": "Erreur dans startServers",
  "data": {...},
  "stack": "..."
}
```

### 3. Logs Backend (Application)
**Fichier :** `backend/logs/app_YYYYMMDD.log`

Contient :
- Logs de l'application FastAPI
- Requêtes API
- Erreurs serveur
- Opérations base de données

## Utilisation

### Voir les logs en temps réel

**Terminal :**
```bash
tail -f logs/startup_*.log
```

**Navigateur :**
1. Ouvrir la console (F12)
2. Taper `getDebugLogs()` pour voir tous les logs
3. Taper `exportDebugLogs()` pour télécharger un fichier JSON

### Analyser les erreurs

1. **Erreurs JavaScript :**
   - Ouvrir la console du navigateur
   - Voir les logs avec `getDebugLogs()`
   - Filtrer par niveau : `getDebugLogs().filter(l => l.level === 'error')`

2. **Erreurs Serveur :**
   - Voir le fichier `logs/startup_*.log`
   - Chercher les lignes `[ERROR]` ou `[CRITICAL]`

3. **Erreurs Backend/Frontend :**
   - Voir les fichiers dans `backend/logs/`
   - Vérifier les processus avec `ps aux | grep uvicorn` ou `ps aux | grep node`

## Niveaux de Logs

- **DEBUG** : Informations très détaillées pour le débogage
- **INFO** : Informations générales sur le fonctionnement
- **WARN** : Avertissements (non bloquants)
- **ERROR** : Erreurs qui empêchent certaines fonctionnalités
- **CRITICAL** : Erreurs critiques qui arrêtent l'application

## Exemples de Logs

### Démarrage réussi
```
[INFO] Fonction start_backend() appelée
[INFO] Backend directory | Data: {"path": "/path/to/backend"}
[INFO] Processus backend créé | Data: {"pid": 12345}
[INFO] Backend démarré avec succès
```

### Erreur
```
[ERROR] Exception dans start_backend | Data: {"error": "...", "traceback": "..."}
```

## Debugging

Pour déboguer un problème :

1. **Vérifier les logs du serveur de démarrage :**
   ```bash
   cat logs/startup_*.log | grep ERROR
   ```

2. **Vérifier la console du navigateur :**
   - Ouvrir F12
   - Voir les erreurs en rouge
   - Utiliser `getDebugLogs()` pour plus de détails

3. **Vérifier les processus :**
   ```bash
   ps aux | grep -E "uvicorn|node.*dev"
   ```

4. **Tester les endpoints :**
   ```bash
   curl http://localhost:8080/api/status
   curl -X POST http://localhost:8080/api/start
   ```
