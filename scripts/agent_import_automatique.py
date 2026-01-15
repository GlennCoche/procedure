"""
Agent principal d'import automatique qui orchestre tous les composants.

Utilise:
- file_watcher pour détecter les nouveaux fichiers
- document_processor pour traiter les documents
- enrichment_engine pour enrichir les entités
- git_auto_push pour push automatique
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Optional, List

# Ajouter le répertoire scripts au path
sys.path.insert(0, str(Path(__file__).parent))

from file_watcher import FileWatcher
from document_processor import DocumentProcessor
from enrichment_engine import EnrichmentEngine
from git_auto_push import GitAutoPush
from mcp_orchestrator import MCPOrchestrator
from pipeline_runner import PipelineRunner

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentImportAutomatique:
    """
    Agent principal qui orchestre l'import automatique de documents.
    
    Workflow:
    1. Surveille le dossier docs avec file_watcher
    2. Détecte les nouveaux fichiers
    3. Traite avec document_processor (4 phases)
    4. Enrichit avec enrichment_engine
    5. Push automatique vers GitHub
    """
    
    def __init__(
        self,
        docs_directory: Path,
        watch_mode: bool = True
    ):
        """
        Initialise l'agent d'import automatique.
        
        Args:
            docs_directory: Dossier à surveiller
            watch_mode: Si True, surveille en continu. Si False, traite une fois
        """
        self.docs_directory = Path(docs_directory)
        self.watch_mode = watch_mode
        
        # Initialiser les composants
        self.orchestrator = MCPOrchestrator()
        self.processor = DocumentProcessor(self.orchestrator)
        self.enrichment_engine = EnrichmentEngine()
        self.git_push = GitAutoPush()
        self.file_watcher: Optional[FileWatcher] = None
        self.pipeline_runner: Optional[PipelineRunner] = None

        if os.getenv("PIPELINE_STEP_MODE") == "1":
            staging_dir = Path("/Users/glenn/Desktop/procedures/docs/docs_a_traiter")
            self.pipeline_runner = PipelineRunner(self.docs_directory, staging_dir)
        
        logger.info("🤖 Agent d'import automatique initialisé")
    
    async def process_file(self, file_path: Path):
        """
        Traite un fichier détecté.
        
        Args:
            file_path: Chemin vers le fichier à traiter
        """
        logger.info(f"🚀 Traitement du fichier: {file_path.name}")
        
        try:
            # 1. Traiter le document (4 phases)
            result = await self.processor.process_document(file_path)
            
            if result.get("errors"):
                logger.error(f"❌ Erreurs lors du traitement: {result['errors']}")
                return
            
            # 2. Enrichir les entités créées
            entities = result.get("entities_created", {})
            
            # Enrichir les procédures
            for procedure in entities.get("procedures", []):
                enriched = self.enrichment_engine.enrich_procedure(
                    procedure,
                    self._detect_brand(file_path),
                    {"file_name": file_path.name, "page": 0, "section": ""}
                )
                procedure.update(enriched)
            
            # Enrichir les réglages
            for setting in entities.get("settings", []):
                enriched = self.enrichment_engine.enrich_setting(
                    setting,
                    self._detect_brand(file_path),
                    {"file_name": file_path.name, "page": 0, "section": ""}
                )
                setting.update(enriched)
            
            # Enrichir les tips
            for tip in entities.get("tips", []):
                enriched = self.enrichment_engine.enrich_tip(
                    tip,
                    self._detect_brand(file_path),
                    {"file_name": file_path.name, "page": 0, "section": ""}
                )
                tip.update(enriched)
            
            # 3. Push automatique vers GitHub
            logger.info("🔄 Push automatique vers GitHub...")
            push_result = await self.git_push.push_after_import(result)
            
            if push_result.get("success"):
                logger.info("✅ Import terminé avec succès!")
                logger.info(f"   - Procédures: {len(entities.get('procedures', []))}")
                logger.info(f"   - Réglages: {len(entities.get('settings', []))}")
                logger.info(f"   - Tips: {len(entities.get('tips', []))}")
                logger.info(f"   - Commit: {push_result.get('commit_hash', 'N/A')}")
            else:
                logger.warning(f"⚠️ Push échoué: {push_result.get('reason', 'Unknown')}")
        
        except Exception as e:
            logger.error(f"❌ Erreur lors du traitement de {file_path.name}: {e}", exc_info=True)
    
    def _detect_brand(self, file_path: Path) -> str:
        """Détecte la marque depuis le chemin"""
        parts = file_path.parts
        for part in parts:
            if part.upper() in ["ABB", "DELTA", "GOODWE", "HUAWEI", "SUNGROW", "WEBDYN"]:
                return part.upper()
        return "Unknown"
    
    async def start_watching(self):
        """Démarre la surveillance continue du dossier"""
        logger.info(f"👀 Démarrage de la surveillance: {self.docs_directory}")
        
        # Créer le file watcher
        self.file_watcher = FileWatcher(
            self.docs_directory,
            self.process_file
        )
        
        # Scanner les fichiers existants
        self.file_watcher.scan_existing_files()
        
        # Démarrer la surveillance
        self.file_watcher.start()
        
        logger.info("✅ Surveillance active. Appuyez sur Ctrl+C pour arrêter.")
        
        try:
            # Maintenir le processus actif
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n🛑 Arrêt demandé...")
        finally:
            if self.file_watcher:
                self.file_watcher.stop()
            logger.info("👋 Agent arrêté")
    
    async def process_all_existing(self):
        """Traite tous les fichiers existants une fois"""
        logger.info(f"📂 Traitement des fichiers existants: {self.docs_directory}")

        if self.pipeline_runner:
            while True:
                inventory = self.pipeline_runner.inventory()
                if inventory.progress.total == 0:
                    break
                self.pipeline_runner.import_local()
                self.pipeline_runner.upload_storage()
                self.pipeline_runner.export_json(approved=True)
                self.pipeline_runner.import_supabase()
                self.pipeline_runner.verify()
                await asyncio.sleep(1)
            return
        
        pdf_files = list(self.docs_directory.rglob("*.pdf"))
        mms_files = list(self.docs_directory.rglob("*.mms"))
        mms_files.extend(self.docs_directory.rglob("*.MMS"))
        
        all_files = pdf_files + mms_files
        
        logger.info(f"📄 {len(all_files)} fichier(s) trouvé(s)")
        
        for file_path in all_files:
            await self.process_file(file_path)
            # Petite pause entre les fichiers
            await asyncio.sleep(1)
        
        logger.info("✅ Traitement terminé")
    
    async def process_specific_files(self, file_paths: List[Path]):
        """
        Traite une liste spécifique de fichiers (mode API direct).
        
        Args:
            file_paths: Liste des chemins de fichiers à traiter
        
        Returns:
            Résultat du traitement
        """
        logger.info(f"📂 Traitement de {len(file_paths)} fichier(s) spécifique(s)")
        
        results = {
            "total": len(file_paths),
            "processed": 0,
            "procedures_created": 0,
            "settings_created": 0,
            "tips_created": 0,
            "errors": []
        }
        
        for file_path in file_paths:
            try:
                await self.process_file(file_path)
                results["processed"] += 1
                
                # Compter les entités créées (approximation)
                # Le vrai comptage se fait dans process_file
            except Exception as e:
                results["errors"].append({
                    "file": str(file_path),
                    "error": str(e)
                })
                logger.error(f"Erreur traitement {file_path.name}: {e}")
        
        return results


async def main():
    """Fonction principale"""
    import sys
    
    # Dossier à surveiller
    docs_dir = Path("/Users/glenn/Desktop/procedures/docs")
    
    # Mode: watch (surveillance continue) ou process (traitement unique)
    watch_mode = "--watch" in sys.argv or "-w" in sys.argv
    
    # Créer l'agent
    agent = AgentImportAutomatique(docs_dir, watch_mode=watch_mode)
    
    if watch_mode:
        # Mode surveillance continue
        await agent.start_watching()
    else:
        # Mode traitement unique
        await agent.process_all_existing()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Au revoir!")
