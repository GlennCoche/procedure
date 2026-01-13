# Plan Complet - Import Documentation Photovoltaïque

## Vue d'ensemble

**Objectif:** Importer les 70 fichiers PDF de `/docs` vers la base de données Supabase, puis déployer sur Vercel.

**Stratégie:** Utiliser les MCP (pdf-tools, content-core, sqlite) pour extraire le contenu des PDFs et créer automatiquement des procédures et tips dans la base de données.

---

## Phase 1: Préparation

### 1.1 Migration SQL Supabase (MANUEL)
Exécuter sur Supabase SQL Editor:
```sql
CREATE TABLE IF NOT EXISTS "message_ratings" (...);
```

### 1.2 Créer le script d'import
Créer `/scripts/import_all_docs.py` qui:
- Liste tous les PDFs par marque (ABB, Delta, Goodwe, Huawei, Sungrow, Webdyn)
- Extrait le texte de chaque PDF via MCP pdf-tools
- Analyse le contenu pour identifier procédures/tips
- Appelle l'API `/api/procedures` ou `/api/tips` pour créer les entrées

---

## Phase 2: Extraction PDF par Marque

### Marques à traiter (70 PDFs):
| Marque | Nombre PDFs | Priorité |
|--------|-------------|----------|
| ABB | 11 | 1 |
| Goodwe | 20 | 2 |
| Huawei | 16 | 3 |
| Delta | 14 | 4 |
| Sungrow | 2 | 5 |
| Webdyn | 3 | 6 |
| WebdynPM | 2 | 7 |
| Bridage | 2 | 8 |

### Pour chaque PDF:
1. `mcp_pdf-tools_get_metadata` - Obtenir nb pages
2. `mcp_pdf-tools_get_text_blocks` - Extraire texte par page
3. Analyser structure (sections, étapes, paramètres)
4. Créer objet Procedure ou Tip selon le contenu

---

## Phase 3: Import en Base de Données

### 3.1 Structure Procedure
```json
{
  "title": "Installation ABB TRIO 50",
  "description": "Procédure de mise en service onduleur ABB TRIO 50",
  "category": "ABB",
  "tags": ["onduleur", "TRIO", "mise en service"],
  "steps": [
    {
      "title": "Vérifications préalables",
      "description": "...",
      "order": 1
    }
  ]
}
```

### 3.2 Structure Tip
```json
{
  "title": "Paramètres réseau France ABB",
  "content": "Tension: 230V, Fréquence: 50Hz...",
  "category": "ABB",
  "tags": ["paramètres", "France", "réseau"]
}
```

### 3.3 Structure Setting
```json
{
  "brand": "ABB",
  "equipmentType": "onduleur",
  "model": "TRIO 50",
  "category": "tension",
  "name": "Tension nominale",
  "value": "230",
  "unit": "V",
  "country": "FR"
}
```

---

## Phase 4: Script d'Exécution

### 4.1 Fichiers à créer:
- `/scripts/import_all_docs.py` - Script principal
- `/scripts/pdf_extractor.py` - Extraction PDF via MCP
- `/scripts/content_analyzer.py` - Analyse IA du contenu
- `/scripts/db_inserter.py` - Insertion en base

### 4.2 Gestion des erreurs:
- Liste des bugs dans `/logs/import_errors.json`
- Continue le processus même si un PDF échoue
- Rapport final avec succès/échecs

---

## Phase 5: Déploiement

### 5.1 Git commit & push
```bash
git add .
git commit -m "feat: import 70 PDF documentation"
git push
```

### 5.2 Vercel Deploy
- Déploiement automatique via GitHub
- Vérifier les logs Vercel

### 5.3 Validation
- Tester l'application déployée
- Vérifier que les procédures sont visibles
- Tester le chat IA avec les nouvelles données

---

## Ordre d'Exécution

1. [ ] Exécuter migration SQL sur Supabase
2. [ ] Créer scripts d'import
3. [ ] Importer ABB (11 PDFs)
4. [ ] Importer Goodwe (20 PDFs)
5. [ ] Importer Huawei (16 PDFs)
6. [ ] Importer Delta (14 PDFs)
7. [ ] Importer Sungrow (2 PDFs)
8. [ ] Importer Webdyn (5 PDFs)
9. [ ] Importer Bridage (2 PDFs)
10. [ ] Git push
11. [ ] Vérifier déploiement Vercel
12. [ ] Corriger bugs listés
13. [ ] Validation finale

---

## Bugs à Suivre

Liste des erreurs rencontrées (sera complétée pendant l'exécution):
- [ ] Bug 1: ...
- [ ] Bug 2: ...
