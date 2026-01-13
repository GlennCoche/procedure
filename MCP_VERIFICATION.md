# Vérification et Configuration MCPs

## Problème Identifié

Les MCPs n'apparaissaient pas dans "Installed MCP Servers" car la configuration était dans `settings.json` (configuration globale) au lieu de `~/.cursor/mcp.json` (configuration projet).

## Solution Appliquée

La configuration des MCPs a été déplacée vers `~/.cursor/mcp.json` qui est le fichier que Cursor lit pour les MCPs spécifiques au projet.

## Configuration Actuelle

Les MCPs suivants sont maintenant configurés dans `~/.cursor/mcp.json` :

1. **sqlite** - Gestion base SQLite locale
2. **pdf-tools** - Extraction PDF améliorée
3. **content-core** - Extraction d'informations (avec OpenAI)
4. **faiss** - Stockage vectoriel pour embeddings

## Vérification

### Chemins et Fichiers

- ✅ `mcp-servers/pdf-tools-mcp/src/main.py` existe
- ✅ `mcp-servers/mcp-sqlite/mcp-sqlite-server.js` existe
- ✅ Répertoire `scripts/local_db/` créé

### Modules Python

- ⚠️ **pdf-tools** : Nécessite dépendances (pydantic)
- ⚠️ **content-core** : Module installé mais peut avoir des dépendances manquantes
- ⚠️ **faiss** : Module installé mais peut avoir des dépendances manquantes

## Actions Requises

1. **Redémarrer Cursor** pour que les changements dans `~/.cursor/mcp.json` soient pris en compte

2. **Vérifier dans Cursor** :
   - Ouvrir Settings → Tools & MCP
   - Les MCPs devraient maintenant apparaître dans "Installed MCP Servers"

3. **Si les MCPs ne fonctionnent pas** :
   - Vérifier les logs Cursor dans `~/Library/Application Support/Cursor/logs/`
   - Vérifier que les chemins sont corrects
   - Vérifier que les dépendances Python sont installées

## Fichiers de Configuration

- **Configuration projet** : `~/.cursor/mcp.json` ← **Utilisé par Cursor**
- **Configuration globale** : `~/Library/Application Support/Cursor/User/settings.json` (pour MCPs globaux)

## Note Importante

Cursor lit les MCPs depuis deux endroits :
1. **Configuration globale** (`settings.json`) : Pour tous les projets
2. **Configuration projet** (`~/.cursor/mcp.json`) : Spécifique au projet actuel

Pour ce projet, les MCPs sont configurés dans `~/.cursor/mcp.json` car ils sont spécifiques au projet d'import de documentation photovoltaïque.
