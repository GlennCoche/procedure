# Historique des Bugs Détectés et Corrigés

Ce document liste tous les bugs détectés par le système de tests, leurs causes, et les solutions appliquées.

## Format

Chaque bug est documenté avec :
- **ID** : Identifiant unique
- **Sévérité** : critical, major, minor
- **Test** : Nom du test qui a échoué
- **Cause racine** : Analyse de la cause
- **Solution** : Correction appliquée
- **Statut** : detected, fixed, failed

---

## Bugs Corrigés

### BUG-001 : Erreur 500 sur Login
- **Sévérité** : critical
- **Test** : login with valid credentials
- **Cause racine** : Utilisation incorrecte de `cookies().set()` dans Next.js 15
- **Solution** : Remplacé par `Response.cookies.set()`
- **Statut** : fixed
- **Fichiers** : `frontend/app/api/auth/login/route.ts`, `frontend/app/api/auth/register/route.ts`, `frontend/app/api/auth/logout/route.ts`

### BUG-002 : isActive Type Error
- **Sévérité** : critical
- **Test** : get procedures list
- **Cause racine** : Utilisation de `isActive: 1` au lieu de `isActive: true` pour PostgreSQL
- **Solution** : Remplacé `isActive: 1` par `isActive: true`
- **Statut** : fixed
- **Fichiers** : `frontend/app/api/procedures/route.ts`

---

## Bugs en Cours d'Analyse

(Aucun pour le moment)

---

## Prévention

Pour éviter les bugs similaires :

1. **Cookies** : Toujours utiliser `Response.cookies.set()` dans Next.js 15
2. **Types** : Vérifier les types Prisma (Boolean vs Int)
3. **Tests** : Exécuter les tests avant chaque commit
4. **Validation** : Valider toutes les entrées utilisateur

---

**Dernière mise à jour** : 2025-01-13
