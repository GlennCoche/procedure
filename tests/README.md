# Système de Tests Automatisés

Système complet de tests automatisés pour valider toutes les fonctionnalités de l'application.

## 🚀 Démarrage Rapide

### Lancer tous les tests
```bash
npm run test
```

### Lancer les tests en production
```bash
npm run test:prod
```

### Lancer une suite spécifique
```bash
npm run test:auth
npm run test:procedures
npm run test:executions
```

## 📋 Structure

```
tests/
├── e2e/              # Tests End-to-End (Playwright)
├── api/              # Tests API (Vitest)
├── utils/            # Utilitaires de test
├── fixtures/         # Données de test
├── reports/          # Rapports générés
├── test-runner.ts    # Orchestrateur principal
└── cli.ts            # Interface en ligne de commande
```

## 🧪 Types de Tests

### Tests API
Tests rapides des routes API avec Vitest.

### Tests E2E
Tests complets de l'interface utilisateur avec Playwright.

### Tests d'Intégration
Scénarios complets testant plusieurs fonctionnalités ensemble.

### Tests de Performance
Validation des temps de réponse.

### Tests de Sécurité
Validation des permissions et protection contre les vulnérabilités.

## 🔧 Correction Automatique

Le système peut détecter et corriger automatiquement certains bugs :

- Erreurs de cookies (déjà corrigé)
- Problèmes de type isActive (déjà corrigé)
- Autres corrections selon l'analyse

## 📊 Rapports

Les rapports sont générés dans `tests/reports/` :

- **JSON** : `test-report-{timestamp}.json`
- **HTML** : `test-report-{timestamp}.html`

## 🔍 Options CLI

```bash
npm run test -- --help              # Aide
npm run test -- --env production    # Environnement
npm run test -- --suite auth        # Suite spécifique
npm run test -- --no-fix            # Désactiver auto-fix
npm run test -- --verbose           # Mode verbeux
```

## 📝 Ajouter de Nouveaux Tests

### Test API
Créer un fichier dans `tests/api/` :
```typescript
import { describe, it, expect } from 'vitest'

describe('My Feature', () => {
  it('should work correctly', async () => {
    // Test code
  })
})
```

### Test E2E
Créer un fichier dans `tests/e2e/` :
```typescript
import { test, expect } from '@playwright/test'

test('should work in browser', async ({ page }) => {
  // Test code
})
```

## 🐛 Détection de Bugs

Les bugs sont automatiquement détectés et analysés. Le système :
1. Détecte les erreurs
2. Analyse la cause racine
3. Propose une correction
4. Tente la correction automatique si possible
5. Re-teste pour valider

## 📚 Documentation Complète

Voir :
- `tests/ARCHITECTURE.md` : Architecture technique
- `tests/BUGS.md` : Historique des bugs
