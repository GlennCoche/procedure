# Correction Erreur MCP cursor-browser-extension

## Problème

Erreur affichée dans Cursor :
```
MCP configuration errors:
cursor-browser-extension:
Invalid config: mcpServers must be an object
```

## Solution Appliquée

Le fichier `~/.cursor/mcp.json` a été modifié pour inclure la section `mcpServers` requise :

```json
{
  "version": "1.0",
  "description": "Ultimate MCP for autonomous senior-level coding agent",
  "mcpServers": {},
  "tools": { ... }
}
```

## Vérification

1. ✅ Le fichier `~/.cursor/mcp.json` contient maintenant `"mcpServers": {}`
2. ✅ Le JSON est valide
3. ✅ `mcpServers` est bien un objet (dict)

## Si l'erreur persiste

Si l'erreur persiste après cette correction, essayez :

1. **Redémarrer Cursor complètement** (Cmd+Q puis rouvrir)
2. **Vérifier les logs Cursor** dans `~/Library/Application Support/Cursor/logs/`
3. **Vérifier que le fichier est bien lu** : Le chemin exact est `~/.cursor/mcp.json`

## Note

`cursor-browser-extension` est un MCP intégré à Cursor qui ne nécessite normalement pas de configuration spécifique. L'ajout de `mcpServers: {}` devrait résoudre l'erreur de validation.
