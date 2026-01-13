# Quick Start - Système de Tests

## 🚀 Démarrage en 3 Étapes

### 1. Installer les Dépendances (Déjà fait ✅)
```bash
cd frontend
npm install
```

### 2. Configurer les Variables d'Environnement

Créer `frontend/.env.local` :
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/test_db
JWT_SECRET=test-secret-key
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=test-secret
OPENAI_API_KEY=sk-... (optionnel pour tests IA)
```

### 3. Lancer les Tests
```bash
npm run test
```

---

## 📋 Commandes Essentielles

```bash
# Tous les tests
npm run test

# Tests en production
npm run test:prod

# Une suite spécifique
npm run test:auth

# Avec options
npm run test -- --verbose --suite procedures
```

---

## 📊 Consulter les Rapports

Après l'exécution, les rapports sont dans `tests/reports/` :

```bash
# Ouvrir le rapport HTML
open tests/reports/test-report-*.html

# Voir le rapport JSON
cat tests/reports/test-report-*.json
```

---

## 🐛 Correction Automatique

Le système corrige automatiquement les bugs détectés. Pour désactiver :

```bash
npm run test -- --no-fix
```

---

## ✅ Vérification Rapide

```bash
# Tester uniquement l'authentification
npm run test:auth

# Si tout passe, tester le reste
npm run test
```

---

**C'est tout ! Le système est prêt à être utilisé.**
