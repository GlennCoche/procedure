# 🔧 Solution : Erreur 401 - Cookie Non Envoyé

**Date :** 2026-01-13

---

## ❌ Problème Identifié

Le dashboard reste blanc avec l'erreur :
```
GET https://procedure1.vercel.app/api/auth/me 401 (Unauthorized)
```

**Cause :** Les cookies ne sont pas envoyés avec les requêtes `fetch()` car `credentials: 'include'` n'était pas spécifié.

---

## ✅ Solution Appliquée

Ajout de `credentials: 'include'` à toutes les requêtes `fetch()` qui doivent envoyer les cookies :

### 1. Layout du Dashboard (`app/(dashboard)/layout.tsx`)

**Avant** :
```typescript
const response = await fetch("/api/auth/me")
```

**Après** :
```typescript
const response = await fetch("/api/auth/me", {
  credentials: "include",
})
```

### 2. Page Dashboard (`app/(dashboard)/dashboard/page.tsx`)

**Avant** :
```typescript
const response = await fetch("/api/auth/me")
```

**Après** :
```typescript
const response = await fetch("/api/auth/me", {
  credentials: "include",
})
```

### 3. Header (`components/layout/header.tsx`)

**Avant** :
```typescript
await fetch("/api/auth/logout", { method: "POST" })
const response = await fetch("/api/auth/me")
```

**Après** :
```typescript
await fetch("/api/auth/logout", { 
  method: "POST",
  credentials: "include",
})
const response = await fetch("/api/auth/me", {
  credentials: "include",
})
```

---

## 🔍 Vérification du Cookie

Le cookie `auth-token` est créé dans `/api/auth/login` avec :
```typescript
response.cookies.set('auth-token', token, {
  httpOnly: true,
  secure: process.env.NODE_ENV === 'production',
  sameSite: 'lax',
  maxAge: 60 * 60 * 24 * 7, // 7 jours
  path: '/',
})
```

**Configuration correcte** :
- ✅ `httpOnly: true` - Sécurisé
- ✅ `secure: true` en production - HTTPS uniquement
- ✅ `sameSite: 'lax'` - Protection CSRF
- ✅ `path: '/'` - Accessible sur tout le site

---

## 📋 Fichiers Modifiés

1. `frontend/app/(dashboard)/layout.tsx`
2. `frontend/app/(dashboard)/dashboard/page.tsx`
3. `frontend/components/layout/header.tsx`

---

## 🚀 Test

Après le redéploiement :

1. **Se connecter** : https://procedure1.vercel.app/login
2. **Vérifier le dashboard** : https://procedure1.vercel.app/dashboard
   - Le dashboard devrait s'afficher correctement
   - Plus d'erreur 401 dans la console
   - L'email de l'utilisateur devrait être visible

---

## ⚠️ Note Importante

**Pourquoi `credentials: 'include'` est nécessaire ?**

Par défaut, les requêtes `fetch()` ne transmettent **pas** les cookies HTTP-only. Il faut explicitement spécifier `credentials: 'include'` pour que les cookies soient envoyés avec la requête.

**Alternatives** :
- `credentials: 'same-origin'` - Envoie les cookies uniquement pour les requêtes vers la même origine (recommandé)
- `credentials: 'include'` - Envoie les cookies pour toutes les requêtes (y compris cross-origin)

Pour notre cas (même origine), `credentials: 'include'` fonctionne parfaitement.

---

**Le dashboard devrait maintenant fonctionner correctement ! 🎉**
