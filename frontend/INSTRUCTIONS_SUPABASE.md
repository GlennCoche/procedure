# Instructions pour Basculer vers Supabase

Quand vous êtes prêt à déployer sur Supabase, suivez ces étapes :

## 1. Changer le schéma Prisma

```bash
cd frontend
cp prisma/schema.postgresql.prisma prisma/schema.prisma
```

## 2. Mettre à jour DATABASE_URL

Dans `frontend/.env.local`, remplacez :
```env
DATABASE_URL="file:./dev.db"
```

Par votre connection string Supabase :
```env
DATABASE_URL="postgresql://postgres:password@db.xxx.supabase.co:5432/postgres"
```

## 3. Régénérer le client Prisma

```bash
npx prisma generate
```

## 4. Appliquer les migrations

```bash
npx prisma migrate deploy
```

## 5. Mettre à jour les routes API

Les routes API utilisent `isActive: 1` pour SQLite. Pour PostgreSQL, Prisma convertira automatiquement `1` en `true`, donc pas besoin de changer le code.

Si vous voulez être explicite, vous pouvez utiliser :
```typescript
const isActiveValue = process.env.DATABASE_URL?.includes('postgresql') ? true : 1
```

Mais ce n'est pas nécessaire, Prisma gère la conversion automatiquement.
