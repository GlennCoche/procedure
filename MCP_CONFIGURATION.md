# Configuration MCP pour Cursor IDE

Ce document décrit la configuration des serveurs MCP installés pour le projet d'import intelligent de documentation photovoltaïque.

## MCPs Installés

### Priorité 1 - Essentiels

1. **pdf-tools-mcp** (danielkennedy1)
   - **Chemin** : `/Users/glenn/Desktop/procedures/mcp-servers/pdf-tools-mcp`
   - **Type** : Python
   - **Installation** : `pip install -e .`
   - **Usage** : Extraction PDF améliorée avec images
   - **Tâches** : `enhance_extraction`

2. **mcp-sqlite** (jparkerweb)
   - **Chemin** : `/Users/glenn/Desktop/procedures/mcp-servers/mcp-sqlite`
   - **Type** : Node.js
   - **Installation** : `npm install`
   - **Usage** : Gestion base SQLite locale
   - **Tâches** : `create_local_db`, `create_migration_script`

3. **content-core** (lfnovo)
   - **Chemin** : `/Users/glenn/Desktop/procedures/mcp-servers/content-core`
   - **Type** : Python
   - **Installation** : `pip install -e .`
   - **Usage** : Extraction d'informations essentielles
   - **Tâches** : `create_ai_analyzer`, `create_intelligent_structurer`

### Priorité 2 - Recommandés

4. **mcp-summarizer** (0xshellming)
   - **Chemin** : `/Users/glenn/Desktop/procedures/mcp-servers/mcp-summarizer`
   - **Type** : Node.js/TypeScript
   - **Installation** : `npm install && npm run build`
   - **Usage** : Synthèse automatique de contenu
   - **Tâches** : `create_ai_analyzer`, `create_ai_enricher`

5. **local_faiss_mcp** (nonatofabio)
   - **Type** : Python (PyPI)
   - **Installation** : `pip install local-faiss-mcp`
   - **Usage** : Stockage vectoriel local pour embeddings
   - **Tâches** : `import_validated_data` (génération embeddings)

## Configuration Cursor

Pour configurer ces MCPs dans Cursor, ajoutez la configuration suivante dans les paramètres MCP de Cursor.

### Option 1 : Configuration via Settings UI

1. Ouvrir Cursor Settings (Cmd+,)
2. Rechercher "MCP" ou "Model Context Protocol"
3. Ajouter chaque serveur MCP avec les paramètres ci-dessous

### Option 2 : Configuration via fichier JSON

Le fichier de configuration se trouve généralement à :
- `~/.cursor/mcp.json` (configuration globale)
- `~/Library/Application Support/Cursor/User/settings.json` (paramètres utilisateur)

### Configuration Recommandée

```json
{
  "mcpServers": {
    "pdf-tools": {
      "command": "python3",
      "args": [
        "-m",
        "src.main"
      ],
      "cwd": "/Users/glenn/Desktop/procedures/mcp-servers/pdf-tools-mcp"
    },
    "sqlite": {
      "command": "node",
      "args": [
        "/Users/glenn/Desktop/procedures/mcp-servers/mcp-sqlite/mcp-sqlite-server.js",
        "/Users/glenn/Desktop/procedures/scripts/local_db/documents.db"
      ]
    },
    "content-core": {
      "command": "content-core-mcp",
      "args": []
    },
    "summarizer": {
      "command": "node",
      "args": [
        "/Users/glenn/Desktop/procedures/mcp-servers/mcp-summarizer/dist/index.js"
      ],
      "env": {
        "GOOGLE_API_KEY": "votre-clé-google-api-si-nécessaire"
      }
    },
    "faiss": {
      "command": "python3",
      "args": [
        "-m",
        "local_faiss_mcp"
      ]
    }
  }
}
```

## Utilisation par Tâche

### Tâche: create_local_db
- **MCP** : `sqlite`
- **Commandes MCP** : `create_table`, `execute_sql`

### Tâche: enhance_extraction
- **MCP** : `pdf-tools`
- **Commandes MCP** : `extract_text`, `extract_images`, `extract_metadata`

### Tâche: create_ai_analyzer
- **MCPs** : `content-core`, `summarizer`
- **Commandes MCP** : `extract_essentials`, `summarize_text`

### Tâche: create_vision_analyzer
- **MCP** : Aucun (utiliser OpenAI Vision API directement dans le code Python)

### Tâche: create_intelligent_structurer
- **MCP** : `content-core`
- **Commandes MCP** : `extract_structured_data`

### Tâche: create_ai_enricher
- **MCP** : `summarizer`
- **Commandes MCP** : `enrich_content`, `improve_text`

### Tâche: create_migration_script
- **MCP** : `sqlite`
- **Commandes MCP** : `query_data`, `export_data`

### Tâche: import_validated_data
- **MCP** : `faiss`
- **Commandes MCP** : `create_embeddings`, `store_vectors`

## Notes Importantes

1. **Variables d'environnement** : Certains MCPs peuvent nécessiter des clés API (ex: Google API pour mcp-summarizer)

2. **Chemins absolus** : Utiliser des chemins absolus dans la configuration pour éviter les problèmes de résolution

3. **Permissions** : S'assurer que les scripts MCP ont les permissions d'exécution

4. **Dépendances** : Tous les MCPs sont installés avec leurs dépendances. Vérifier que Python et Node.js sont dans le PATH

5. **Base de données SQLite** : Le chemin de la base de données SQLite doit être créé avant d'utiliser mcp-sqlite

## Test des MCPs

Pour tester chaque MCP, utiliser les commandes suivantes :

```bash
# Test pdf-tools-mcp
cd /Users/glenn/Desktop/procedures/mcp-servers/pdf-tools-mcp
python3 -m src.main

# Test mcp-sqlite
cd /Users/glenn/Desktop/procedures/mcp-servers/mcp-sqlite
node mcp-sqlite-server.js /path/to/test.db

# Test content-core
content-core-mcp --help

# Test mcp-summarizer
cd /Users/glenn/Desktop/procedures/mcp-servers/mcp-summarizer
node dist/index.js

# Test local_faiss_mcp
python3 -m local_faiss_mcp --help
```

## Dépannage

### Problème : MCP non reconnu par Cursor
- Vérifier que le chemin dans la configuration est correct
- Vérifier que les dépendances sont installées
- Vérifier les logs Cursor pour les erreurs

### Problème : Erreur de permission
- S'assurer que les scripts ont les permissions d'exécution : `chmod +x script.js`

### Problème : Module non trouvé
- Réinstaller les dépendances : `npm install` ou `pip install -r requirements.txt`
- Vérifier que Python/Node.js sont dans le PATH

## Références

- [Documentation MCP](https://modelcontextprotocol.io/)
- [Cursor MCP Documentation](https://docs.cursor.com/mcp)
