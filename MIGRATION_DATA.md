# Guide de Migration des Données

Ce guide vous explique comment migrer les données de votre base SQLite locale vers Supabase PostgreSQL.

## Prérequis

- Base de données SQLite existante (`backend/app.db`)
- Projet Supabase configuré (voir `DEPLOYMENT_SUPABASE.md`)
- Python 3.11+ installé
- Node.js 18+ installé

## Méthode 1 : Script Python (Recommandé)

### Étape 1 : Créer le script de migration

Créez `scripts/migrate_to_supabase.py` :

```python
#!/usr/bin/env python3
"""
Script de migration des données SQLite vers Supabase PostgreSQL
"""

import sqlite3
import psycopg2
import json
from psycopg2.extras import execute_values
from datetime import datetime

# Configuration
SQLITE_DB = "backend/app.db"
SUPABASE_URL = "postgresql://postgres:password@db.xxx.supabase.co:5432/postgres"

def migrate_users(sqlite_conn, pg_conn):
    """Migrer les utilisateurs"""
    cursor_sqlite = sqlite_conn.cursor()
    cursor_pg = pg_conn.cursor()
    
    users = cursor_sqlite.execute("SELECT id, email, password_hash, role, created_at, updated_at FROM users").fetchall()
    
    for user in users:
        try:
            cursor_pg.execute(
                """
                INSERT INTO users (id, email, password_hash, role, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                user
            )
        except Exception as e:
            print(f"Erreur migration user {user[1]}: {e}")
    
    pg_conn.commit()
    print(f"✅ {len(users)} utilisateurs migrés")

def migrate_procedures(sqlite_conn, pg_conn):
    """Migrer les procédures"""
    cursor_sqlite = sqlite_conn.cursor()
    cursor_pg = pg_conn.cursor()
    
    procedures = cursor_sqlite.execute("""
        SELECT id, title, description, category, tags, created_by, version, 
               flowchart_data, is_active, created_at, updated_at
        FROM procedures
    """).fetchall()
    
    for proc in procedures:
        try:
            # Convertir tags et flowchart_data en JSON string si nécessaire
            tags = proc[4] if isinstance(proc[4], str) else json.dumps(proc[4]) if proc[4] else None
            flowchart = proc[7] if isinstance(proc[7], str) else json.dumps(proc[7]) if proc[7] else None
            is_active = bool(proc[8]) if isinstance(proc[8], int) else proc[8]
            
            cursor_pg.execute(
                """
                INSERT INTO procedures (id, title, description, category, tags, created_by, 
                                      version, flowchart_data, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (proc[0], proc[1], proc[2], proc[3], tags, proc[5], proc[6], 
                 flowchart, is_active, proc[9], proc[10])
            )
        except Exception as e:
            print(f"Erreur migration procédure {proc[0]}: {e}")
    
    pg_conn.commit()
    print(f"✅ {len(procedures)} procédures migrées")

def migrate_steps(sqlite_conn, pg_conn):
    """Migrer les étapes"""
    cursor_sqlite = sqlite_conn.cursor()
    cursor_pg = pg_conn.cursor()
    
    steps = cursor_sqlite.execute("""
        SELECT id, procedure_id, order, title, description, instructions,
               photos, files, validation_type, created_at
        FROM steps
    """).fetchall()
    
    for step in steps:
        try:
            photos = step[6] if isinstance(step[6], str) else json.dumps(step[6]) if step[6] else None
            files = step[7] if isinstance(step[7], str) else json.dumps(step[7]) if step[7] else None
            
            cursor_pg.execute(
                """
                INSERT INTO steps (id, procedure_id, "order", title, description, instructions,
                                 photos, files, validation_type, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (step[0], step[1], step[2], step[3], step[4], step[5], 
                 photos, files, step[8], step[9])
            )
        except Exception as e:
            print(f"Erreur migration step {step[0]}: {e}")
    
    pg_conn.commit()
    print(f"✅ {len(steps)} étapes migrées")

def migrate_executions(sqlite_conn, pg_conn):
    """Migrer les exécutions"""
    cursor_sqlite = sqlite_conn.cursor()
    cursor_pg = pg_conn.cursor()
    
    executions = cursor_sqlite.execute("""
        SELECT id, user_id, procedure_id, status, current_step, started_at, completed_at
        FROM executions
    """).fetchall()
    
    for exec in executions:
        try:
            cursor_pg.execute(
                """
                INSERT INTO executions (id, user_id, procedure_id, status, current_step, 
                                      started_at, completed_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                exec
            )
        except Exception as e:
            print(f"Erreur migration execution {exec[0]}: {e}")
    
    pg_conn.commit()
    print(f"✅ {len(executions)} exécutions migrées")

def migrate_step_executions(sqlite_conn, pg_conn):
    """Migrer les exécutions d'étapes"""
    cursor_sqlite = sqlite_conn.cursor()
    cursor_pg = pg_conn.cursor()
    
    step_execs = cursor_sqlite.execute("""
        SELECT id, execution_id, step_id, status, photos, comments, completed_at
        FROM step_executions
    """).fetchall()
    
    for se in step_execs:
        try:
            photos = se[4] if isinstance(se[4], str) else json.dumps(se[4]) if se[4] else "[]"
            
            cursor_pg.execute(
                """
                INSERT INTO step_executions (id, execution_id, step_id, status, photos, 
                                           comments, completed_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (se[0], se[1], se[2], se[3], photos, se[5], se[6])
            )
        except Exception as e:
            print(f"Erreur migration step_execution {se[0]}: {e}")
    
    pg_conn.commit()
    print(f"✅ {len(step_execs)} exécutions d'étapes migrées")

def migrate_tips(sqlite_conn, pg_conn):
    """Migrer les tips"""
    cursor_sqlite = sqlite_conn.cursor()
    cursor_pg = pg_conn.cursor()
    
    tips = cursor_sqlite.execute("""
        SELECT id, title, content, category, tags, created_by, created_at, updated_at
        FROM tips
    """).fetchall()
    
    for tip in tips:
        try:
            tags = tip[4] if isinstance(tip[4], str) else json.dumps(tip[4]) if tip[4] else None
            
            cursor_pg.execute(
                """
                INSERT INTO tips (id, title, content, category, tags, created_by, 
                                created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (tip[0], tip[1], tip[2], tip[3], tags, tip[5], tip[6], tip[7])
            )
        except Exception as e:
            print(f"Erreur migration tip {tip[0]}: {e}")
    
    pg_conn.commit()
    print(f"✅ {len(tips)} tips migrés")

def migrate_chat_messages(sqlite_conn, pg_conn):
    """Migrer les messages de chat"""
    cursor_sqlite = sqlite_conn.cursor()
    cursor_pg = pg_conn.cursor()
    
    messages = cursor_sqlite.execute("""
        SELECT id, user_id, message, response, context, created_at
        FROM chat_messages
    """).fetchall()
    
    for msg in messages:
        try:
            context = msg[4] if isinstance(msg[4], str) else json.dumps(msg[4]) if msg[4] else None
            
            cursor_pg.execute(
                """
                INSERT INTO chat_messages (id, user_id, message, response, context, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (msg[0], msg[1], msg[2], msg[3], context, msg[5])
            )
        except Exception as e:
            print(f"Erreur migration message {msg[0]}: {e}")
    
    pg_conn.commit()
    print(f"✅ {len(messages)} messages migrés")

def main():
    print("🚀 Début de la migration...")
    
    # Connexions
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    pg_conn = psycopg2.connect(SUPABASE_URL)
    
    try:
        # Désactiver temporairement les contraintes
        cursor_pg = pg_conn.cursor()
        cursor_pg.execute("SET session_replication_role = 'replica';")
        pg_conn.commit()
        
        # Migrer dans l'ordre des dépendances
        migrate_users(sqlite_conn, pg_conn)
        migrate_procedures(sqlite_conn, pg_conn)
        migrate_steps(sqlite_conn, pg_conn)
        migrate_executions(sqlite_conn, pg_conn)
        migrate_step_executions(sqlite_conn, pg_conn)
        migrate_tips(sqlite_conn, pg_conn)
        migrate_chat_messages(sqlite_conn, pg_conn)
        
        # Réactiver les contraintes
        cursor_pg.execute("SET session_replication_role = 'origin';")
        pg_conn.commit()
        
        print("✅ Migration terminée avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        pg_conn.rollback()
    finally:
        sqlite_conn.close()
        pg_conn.close()

if __name__ == "__main__":
    main()
```

### Étape 2 : Installer les dépendances

```bash
pip install psycopg2-binary
```

### Étape 3 : Configurer la connection string

Modifiez `SUPABASE_URL` dans le script avec votre connection string Supabase.

### Étape 4 : Exécuter le script

```bash
python3 scripts/migrate_to_supabase.py
```

## Méthode 2 : Via Prisma (Alternative)

### Étape 1 : Exporter SQLite en JSON

Créez un script Node.js pour exporter :

```typescript
// scripts/export-sqlite.ts
import Database from 'better-sqlite3'
import fs from 'fs'

const db = new Database('backend/app.db')

const data = {
  users: db.prepare('SELECT * FROM users').all(),
  procedures: db.prepare('SELECT * FROM procedures').all(),
  steps: db.prepare('SELECT * FROM steps').all(),
  executions: db.prepare('SELECT * FROM executions').all(),
  stepExecutions: db.prepare('SELECT * FROM step_executions').all(),
  tips: db.prepare('SELECT * FROM tips').all(),
  chatMessages: db.prepare('SELECT * FROM chat_messages').all(),
}

fs.writeFileSync('exported-data.json', JSON.stringify(data, null, 2))
console.log('✅ Données exportées dans exported-data.json')
```

### Étape 2 : Importer dans Supabase

Créez un script pour importer :

```typescript
// scripts/import-supabase.ts
import { PrismaClient } from '@prisma/client'
import fs from 'fs'

const db = new PrismaClient()
const data = JSON.parse(fs.readFileSync('exported-data.json', 'utf-8'))

async function importData() {
  // Importer dans l'ordre des dépendances
  await db.user.createMany({ data: data.users, skipDuplicates: true })
  await db.procedure.createMany({ data: data.procedures, skipDuplicates: true })
  await db.step.createMany({ data: data.steps, skipDuplicates: true })
  await db.execution.createMany({ data: data.executions, skipDuplicates: true })
  await db.stepExecution.createMany({ data: data.stepExecutions, skipDuplicates: true })
  await db.tip.createMany({ data: data.tips, skipDuplicates: true })
  await db.chatMessage.createMany({ data: data.chatMessages, skipDuplicates: true })
  
  console.log('✅ Données importées avec succès')
}

importData()
  .catch(console.error)
  .finally(() => db.$disconnect())
```

## Vérification

Après la migration, vérifiez les données :

1. **Via Supabase Dashboard** :
   - Allez dans **Table Editor**
   - Vérifiez que toutes les tables contiennent des données

2. **Via Prisma Studio** :
   ```bash
   cd frontend
   npx prisma studio
   ```

3. **Via SQL** :
   ```sql
   SELECT COUNT(*) FROM users;
   SELECT COUNT(*) FROM procedures;
   SELECT COUNT(*) FROM executions;
   ```

## Gestion des erreurs

### Erreur de foreign key

Si vous avez des erreurs de foreign key, migrez dans cet ordre :
1. Users
2. Procedures
3. Steps
4. Executions
5. StepExecutions
6. Tips
7. ChatMessages

### Erreur de type de données

- Vérifiez que les types JSON sont correctement convertis
- Vérifiez que les booléens SQLite (0/1) sont convertis en boolean PostgreSQL

### Erreur de séquence

Réinitialisez les séquences après la migration :

```sql
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));
SELECT setval('procedures_id_seq', (SELECT MAX(id) FROM procedures));
-- Répétez pour toutes les tables avec auto-increment
```

## Backup

Avant de migrer, faites un backup :

```bash
# Backup SQLite
cp backend/app.db backend/app.db.backup

# Backup Supabase (via pg_dump)
pg_dump $DATABASE_URL > supabase-backup.sql
```

## Rollback

Si quelque chose ne va pas, vous pouvez restaurer :

```bash
# Restaurer Supabase
psql $DATABASE_URL < supabase-backup.sql
```
