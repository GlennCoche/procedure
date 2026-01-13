# Correction Erreur pdf-tools MCP

## Problème Identifié

L'erreur dans les logs Cursor :
```
ModuleNotFoundError: No module named 'src'
```

### Cause

Quand Python exécute `python3 -m src.main`, il cherche le module `src` dans le **PYTHONPATH**, pas dans le répertoire courant (`cwd`). Même si `cwd` est défini dans la configuration MCP, Python avec l'option `-m` ne l'utilise pas automatiquement pour résoudre les modules.

## Solution Appliquée

Ajout de la variable d'environnement `PYTHONPATH` dans la configuration du MCP `pdf-tools` :

```json
"pdf-tools": {
  "command": "python3",
  "args": [
    "-m",
    "src.main"
  ],
  "cwd": "/Users/glenn/Desktop/procedures/mcp-servers/pdf-tools-mcp",
  "env": {
    "PYTHONPATH": "/Users/glenn/Desktop/procedures/mcp-servers/pdf-tools-mcp"
  }
}
```

## Explication Technique

### Pourquoi `cwd` ne suffit pas ?

- `cwd` définit le répertoire de travail pour la commande
- Mais `python3 -m module` cherche les modules dans `sys.path` (PYTHONPATH)
- Par défaut, `sys.path` inclut le répertoire courant, mais seulement si Python est exécuté directement depuis ce répertoire
- Quand Cursor exécute la commande, le répertoire courant peut être différent

### Solution : PYTHONPATH

En ajoutant `PYTHONPATH` dans `env`, on garantit que Python trouvera le module `src` même si le répertoire courant n'est pas celui du projet.

## Vérification

Après cette correction :

1. **Redémarrer Cursor** (Cmd+Q puis rouvrir)
2. **Vérifier dans Settings → Tools & MCP** que `pdf-tools` n'affiche plus d'erreur
3. Le statut devrait passer de rouge (erreur) à vert (actif)

## Alternative (si le problème persiste)

Si l'erreur persiste, on peut utiliser une commande directe au lieu de `-m` :

```json
"pdf-tools": {
  "command": "python3",
  "args": [
    "/Users/glenn/Desktop/procedures/mcp-servers/pdf-tools-mcp/src/main.py"
  ]
}
```

Mais la solution avec `PYTHONPATH` est préférable car elle respecte la structure du projet.
