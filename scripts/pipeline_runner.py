from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Dict, Optional

import requests

from langchain_extractor import extract_with_langchain
from local_db.db_manager import LocalDBManager
from pipeline_models import StepContext, StepProgress, StepResult, StepStatus
from queue_manager import QueueManager
from supabase_client import SupabaseStorageClient, SupabaseTableClient


def _get_resources() -> Dict[str, float]:
    try:
        import psutil

        cpu_percent = psutil.cpu_percent(interval=0.1)
        ram_mb = psutil.virtual_memory().used / (1024 * 1024)
        return {"cpu_percent": round(cpu_percent, 2), "ram_mb": round(ram_mb, 2)}
    except Exception:
        return {"cpu_percent": 0.0, "ram_mb": 0.0}


class PipelineRunner:
    def __init__(
        self,
        source_dir: Path,
        staging_dir: Path,
        db_manager: Optional[LocalDBManager] = None,
    ):
        self.source_dir = Path(source_dir)
        self.staging_dir = Path(staging_dir)
        self.db = db_manager or LocalDBManager()
        self.queue = QueueManager(
            source_dir=self.source_dir,
            staging_dir=self.staging_dir,
        )
        self.context = StepContext(
            source_dir=str(self.source_dir),
            staging_dir=str(self.staging_dir),
        )
        self._ensure_run()

    def _ensure_run(self) -> None:
        existing = self.db.read_records("pipeline_runs", {"status": "running"}, limit=1)
        if existing:
            self.context.run_id = existing[0]["id"]
            self.context.current_file = existing[0].get("current_file")
            return
        run_id = self.db.create_record(
            "pipeline_runs",
            {
                "source_dir": str(self.source_dir),
                "staging_dir": str(self.staging_dir),
                "status": "running",
            },
        )
        self.context.run_id = run_id

    def _log_step(self, result: StepResult) -> None:
        if not self.context.run_id:
            return
        self.db.create_record(
            "pipeline_step_logs",
            {
                "run_id": self.context.run_id,
                "step": result.step,
                "status": result.status.value,
                "progress_current": result.progress.current,
                "progress_total": result.progress.total,
                "message": result.message,
                "error": result.error,
                "data_json": result.data or {},
                "cpu_percent": result.resources.cpu_percent,
                "ram_mb": result.resources.ram_mb,
            },
        )

    def _result(
        self,
        step: str,
        status: StepStatus,
        message: str,
        data: Optional[Dict] = None,
        error: Optional[str] = None,
        progress: Optional[StepProgress] = None,
    ) -> StepResult:
        resources = _get_resources()
        result = StepResult(
            step=step,
            status=status,
            message=message,
            file=self.context.current_file,
            progress=progress or StepProgress(),
            resources={
                "cpu_percent": resources["cpu_percent"],
                "ram_mb": resources["ram_mb"],
            },
            data=data,
            error=error,
        )
        self._log_step(result)
        return result

    def _load_last_step_data(self, step: str) -> Optional[Dict]:
        if not self.db_manager or not self.context.run_id:
            return None
        rows = self.db_manager.execute_sql(
            "SELECT data_json FROM pipeline_step_logs WHERE run_id = ? AND step = ? ORDER BY id DESC LIMIT 1",
            (self.context.run_id, step),
        )
        if not rows:
            return None
        data_json = rows[0].get("data_json")
        if not data_json:
            return None
        try:
            return json.loads(data_json)
        except Exception:
            return None

    def inventory(self) -> StepResult:
        files = self.queue.inventory()
        progress = StepProgress(current=0, total=len(files))
        return self._result(
            step="inventory",
            status=StepStatus.success,
            message=f"{len(files)} fichier(s) détecté(s)",
            data={"files": [str(f) for f in files]},
            progress=progress,
        )

    def import_local(self) -> StepResult:
        if self.queue.has_staging_file():
            staging = self.queue.list_staging()
            self.context.current_file = str(staging[0]) if staging else None
            return self._result(
                step="import-local",
                status=StepStatus.paused,
                message="Un fichier est déjà en staging",
                data={"staging": [str(f) for f in staging]},
            )

        next_file = self.queue.acquire_next_file()
        if not next_file:
            return self._result(
                step="import-local",
                status=StepStatus.paused,
                message="Aucun fichier à importer",
            )

        self.context.current_file = str(next_file)
        self.db.update_records(
            "pipeline_runs",
            {
                "current_file": self.context.current_file,
                "current_step": "import-local",
                "status": "running",
            },
            {"id": self.context.run_id},
        )
        return self._result(
            step="import-local",
            status=StepStatus.success,
            message="Fichier déplacé vers la zone de staging",
            data={"staged_file": self.context.current_file},
        )

    def upload_storage(self) -> StepResult:
        if not self.context.current_file:
            return self._result(
                step="upload-storage",
                status=StepStatus.error,
                message="Aucun fichier en staging",
                error="current_file manquant",
            )

        storage_client = SupabaseStorageClient()
        result = storage_client.upload_pdf(Path(self.context.current_file))
        self.context.storage_url = result["url"]
        return self._result(
            step="upload-storage",
            status=StepStatus.success,
            message="PDF uploadé vers Supabase Storage",
            data=result,
        )

    def export_json(self, approved: bool = True) -> StepResult:
        if not approved:
            return self._result(
                step="export-json",
                status=StepStatus.paused,
                message="Validation manuelle requise avant extraction",
            )

        if not self.context.current_file:
            return self._result(
                step="export-json",
                status=StepStatus.error,
                message="Aucun fichier en staging",
                error="current_file manquant",
            )

        pdf_path = Path(self.context.current_file)
        extraction = extract_with_langchain(pdf_path, brand=None)
        self.context.extraction_output = extraction.model_dump()

        export_dir = Path(__file__).parent / "local_db" / "exports"
        export_dir.mkdir(parents=True, exist_ok=True)
        export_path = export_dir / f"{pdf_path.stem}_extraction.json"
        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(self.context.extraction_output, f, ensure_ascii=False, indent=2)

        return self._result(
            step="export-json",
            status=StepStatus.success,
            message="Extraction LangChain terminée",
            data={"export_path": str(export_path)},
        )

    def import_supabase(self) -> StepResult:
        if not self.context.extraction_output:
            if self.context.current_file:
                pdf_path = Path(self.context.current_file)
                export_path = Path(__file__).parent / "local_db" / "exports" / f"{pdf_path.stem}_extraction.json"
                if export_path.exists():
                    with open(export_path, "r", encoding="utf-8") as f:
                        self.context.extraction_output = json.load(f)
        if not self.context.extraction_output:
            return self._result(
                step="import-supabase",
                status=StepStatus.error,
                message="Extraction absente",
                error="export-json requis",
            )

        api_base_url = os.getenv("PRODUCTION_API_URL", "http://localhost:8000/api")
        admin_email = os.getenv("ADMIN_EMAIL", "admin@procedures.local")
        admin_password = os.getenv("ADMIN_PASSWORD", "AdminSecure123!")

        token = self._login(api_base_url, admin_email, admin_password)
        if not token:
            return self._result(
                step="import-supabase",
                status=StepStatus.error,
                message="Authentification API échouée",
                error="login_failed",
            )

        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        storage_url = self.context.storage_url
        if not storage_url:
            last_upload = self._load_last_step_data("upload-storage")
            if last_upload:
                storage_url = last_upload.get("url")
        procedures_created = 0
        tips_created = 0

        for procedure in self.context.extraction_output.get("procedures", []):
            steps_payload = []
            for step in procedure.get("steps", []):
                page = step.get("source_page", 1)
                source_link = f"{storage_url}#page={page}" if storage_url else ""
                steps_payload.append(
                    {
                        "title": step.get("action", "Étape"),
                        "description": step.get("description", ""),
                        "instructions": step.get("description", ""),
                        "order": step.get("order", 1),
                        "files": [source_link] if source_link else [],
                    }
                )

            payload = {
                "title": procedure.get("title", ""),
                "description": procedure.get("description", ""),
                "category": procedure.get("category", ""),
                "tags": procedure.get("tags", []),
                "steps": steps_payload,
            }

            response = requests.post(
                f"{api_base_url}/procedures/",
                json=payload,
                headers=headers,
                timeout=30,
            )
            if response.status_code in (200, 201):
                procedures_created += 1

        for tip in self.context.extraction_output.get("tips", []):
            page = tip.get("source_page", 1)
            source_link = f"{storage_url}#page={page}" if storage_url else ""
            content = tip.get("content", "")
            if source_link:
                content = f"{content}\n\nSource: {source_link}"

            payload = {
                "title": tip.get("title", ""),
                "content": content,
                "category": tip.get("category", ""),
                "tags": tip.get("tags", []),
            }
            response = requests.post(
                f"{api_base_url}/tips/",
                json=payload,
                headers=headers,
                timeout=30,
            )
            if response.status_code in (200, 201):
                tips_created += 1

        settings_client = SupabaseTableClient()
        settings_created = 0
        for setting in self.context.extraction_output.get("settings", []):
            payload = {
                "brand": setting.get("brand", "Unknown"),
                "equipment_type": setting.get("equipment_type", "inconnu"),
                "model": setting.get("model"),
                "category": setting.get("category", "reseau"),
                "name": setting.get("name", ""),
                "value": setting.get("value", ""),
                "unit": setting.get("unit"),
                "country": setting.get("country", "FR"),
                "notes": setting.get("notes"),
                "page_number": setting.get("source_page"),
                "source_doc": self.context.current_file or "",
            }
            settings_client.insert_setting(payload)
            settings_created += 1

        self.context.supabase_inserted = {
            "procedures": procedures_created,
            "tips": tips_created,
            "settings": settings_created,
        }
        return self._result(
            step="import-supabase",
            status=StepStatus.success,
            message="Insertion Supabase terminée",
            data=self.context.supabase_inserted,
        )

    def verify(self) -> StepResult:
        inserted = self.context.supabase_inserted or {}
        ok = (
            inserted.get("procedures", 0) > 0
            or inserted.get("tips", 0) > 0
            or inserted.get("settings", 0) > 0
        )
        if not ok:
            return self._result(
                step="verify",
                status=StepStatus.error,
                message="Aucune donnée insérée",
                error="insertion_empty",
            )

        if self.context.current_file:
            self.queue.cleanup_success(Path(self.context.current_file))
            self.context.current_file = None

        self.db.update_records(
            "pipeline_runs",
            {
                "last_step": "verify",
                "current_step": None,
                "current_file": None,
                "status": "running",
            },
            {"id": self.context.run_id},
        )

        return self._result(
            step="verify",
            status=StepStatus.success,
            message="Vérification OK, fichier nettoyé",
            data=inserted,
        )

    def _login(self, api_base_url: str, email: str, password: str) -> Optional[str]:
        try:
            response = requests.post(
                f"{api_base_url}/login",
                data={"username": email, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10,
            )
            if response.status_code == 200:
                return response.json().get("access_token")
        except Exception:
            return None
        return None
