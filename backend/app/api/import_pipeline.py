from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

import sys

scripts_dir = Path(__file__).parent.parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from pipeline_runner import PipelineRunner
from local_db.db_manager import LocalDBManager


router = APIRouter(prefix="/api/import-pipeline", tags=["Import Pipeline"])


class StepRequest(BaseModel):
    source_dir: Optional[str] = None
    staging_dir: Optional[str] = None
    approved: bool = True


def _get_runner(payload: StepRequest) -> PipelineRunner:
    source_dir = Path(payload.source_dir or "/Users/glenn/Desktop/procedures/docs")
    staging_dir = Path(payload.staging_dir or "/Users/glenn/Desktop/procedures/docs/docs_a_traiter")
    return PipelineRunner(source_dir, staging_dir)


@router.post("/inventory")
async def inventory(payload: StepRequest):
    runner = _get_runner(payload)
    return await asyncio.to_thread(runner.inventory)


@router.post("/import-local")
async def import_local(payload: StepRequest):
    runner = _get_runner(payload)
    return await asyncio.to_thread(runner.import_local)


@router.post("/upload-storage")
async def upload_storage(payload: StepRequest):
    runner = _get_runner(payload)
    return await asyncio.to_thread(runner.upload_storage)


@router.post("/export-json")
async def export_json(payload: StepRequest):
    runner = _get_runner(payload)
    return await asyncio.to_thread(runner.export_json, payload.approved)


@router.post("/import-supabase")
async def import_supabase(payload: StepRequest):
    runner = _get_runner(payload)
    return await asyncio.to_thread(runner.import_supabase)


@router.post("/verify")
async def verify(payload: StepRequest):
    runner = _get_runner(payload)
    return await asyncio.to_thread(runner.verify)


@router.get("/status")
async def status():
    db = LocalDBManager()
    runs = db.read_records("pipeline_runs", limit=5)
    return {"runs": runs}
