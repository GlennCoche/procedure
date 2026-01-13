# Architecture du Système de Tests

## Vue d'Ensemble

Le système de tests utilise une architecture modulaire avec séparation claire entre :
- Tests API (Vitest) - Rapides, unitaires
- Tests E2E (Playwright) - Complets, interface utilisateur
- Système de correction automatique
- Génération de rapports

## Composants Principaux

### 1. Test Runner (`test-runner.ts`)

Orchestrateur principal qui :
- Exécute les tests par suite
- Gère l'ordre d'exécution
- Coordonne la détection et correction des bugs
- Génère les rapports

### 2. Utilitaires

#### `test-helpers.ts`
- Helpers pour authentification
- Helpers pour requêtes API
- Credentials de test

#### `test-db.ts`
- Connexion à la base de données de test
- Nettoyage des données
- Seed de données de test

#### `test-reports.ts`
- Génération de rapports JSON
- Génération de rapports HTML
- Formatage des bugs

#### `auto-fix.ts`
- Détection automatique de bugs
- Analyse de la cause racine
- Correction automatique
- Re-test après correction

## Flux d'Exécution

```
1. CLI lance TestRunner
   ↓
2. TestRunner exécute chaque suite
   ↓
3. Pour chaque suite:
   - Exécute tests API (Vitest)
   - Exécute tests E2E (Playwright)
   - Collecte les résultats
   ↓
4. Détection de bugs
   ↓
5. Analyse automatique
   ↓
6. Correction automatique (si activé)
   ↓
7. Re-test (si correction appliquée)
   ↓
8. Génération de rapports
```

## Environnements

### Local
- URL : `http://localhost:3000`
- Base de données : PostgreSQL local ou Supabase
- Utilise le serveur de développement Next.js

### Production
- URL : `https://procedure1.vercel.app`
- Base de données : Supabase production
- Tests sur l'application déployée

## Configuration

### Variables d'Environnement

- `TEST_URL` : URL de base pour les tests
- `TEST_DATABASE_URL` : URL de la base de données de test
- `TEST_JWT_SECRET` : Secret JWT pour les tests
- `OPENAI_API_KEY` : Clé API OpenAI (pour tests IA)

## Extension

Pour ajouter de nouveaux types de tests :

1. Créer le fichier de test dans `api/` ou `e2e/`
2. Le test sera automatiquement détecté par le runner
3. Les bugs seront automatiquement analysés

## Performance

- Tests API : ~1-2 secondes par suite
- Tests E2E : ~5-10 secondes par suite
- Total : ~2-5 minutes pour tous les tests
