from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Dict, Optional

from supabase import create_client, Client


class SupabaseStorageClient:
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL et SUPABASE_SERVICE_KEY sont requis")

        self.client: Client = create_client(supabase_url, supabase_key)
        self.bucket = os.getenv("SUPABASE_PDF_BUCKET", "procedure-pdfs")

    def upload_pdf(self, file_path: Path) -> Dict[str, str]:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"PDF introuvable: {file_path}")

        file_name = f"{int(time.time())}_{file_path.name}"
        storage_path = f"pdfs/{file_name}"

        with open(file_path, "rb") as f:
            data = f.read()

        result = self.client.storage.from_(self.bucket).upload(
            storage_path,
            data,
            file_options={"content-type": "application/pdf", "upsert": False},
        )
        if isinstance(result, dict) and result.get("error"):
            raise RuntimeError(f"Erreur upload Supabase: {result['error']}")

        public_url = self.client.storage.from_(self.bucket).get_public_url(storage_path)
        if isinstance(public_url, dict):
            url = public_url.get("publicUrl") or public_url.get("public_url")
        else:
            url = getattr(public_url, "public_url", None)

        if not url:
            raise RuntimeError("Impossible d'obtenir l'URL publique du PDF")

        return {"url": url, "path": storage_path}


class SupabaseTableClient:
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL et SUPABASE_SERVICE_KEY sont requis")

        self.client: Client = create_client(supabase_url, supabase_key)

    def insert_procedure(self, payload: Dict) -> Dict:
        return self.client.table("procedures").insert(payload).execute().data

    def insert_step(self, payload: Dict) -> Dict:
        return self.client.table("steps").insert(payload).execute().data

    def insert_tip(self, payload: Dict) -> Dict:
        return self.client.table("tips").insert(payload).execute().data

    def insert_setting(self, payload: Dict) -> Dict:
        return self.client.table("settings").insert(payload).execute().data
