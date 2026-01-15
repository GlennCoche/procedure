from __future__ import annotations

import shutil
from pathlib import Path
from typing import List, Optional


class QueueManager:
    def __init__(
        self,
        source_dir: Path,
        staging_dir: Path,
        quarantine_dir: Optional[Path] = None,
        allowed_extensions: Optional[List[str]] = None,
    ):
        self.source_dir = Path(source_dir)
        self.staging_dir = Path(staging_dir)
        self.quarantine_dir = Path(quarantine_dir) if quarantine_dir else self.staging_dir / "quarantine"
        self.allowed_extensions = allowed_extensions or [".pdf"]

        self.staging_dir.mkdir(parents=True, exist_ok=True)
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)

    def inventory(self) -> List[Path]:
        files: List[Path] = []
        if not self.source_dir.exists():
            return files
        for ext in self.allowed_extensions:
            files.extend(self.source_dir.rglob(f"*{ext}"))
        return sorted([f for f in files if f.is_file()])

    def list_staging(self) -> List[Path]:
        files: List[Path] = []
        if not self.staging_dir.exists():
            return files
        for ext in self.allowed_extensions:
            files.extend(self.staging_dir.glob(f"*{ext}"))
        return sorted([f for f in files if f.is_file()])

    def has_staging_file(self) -> bool:
        return len(self.list_staging()) > 0

    def acquire_next_file(self) -> Optional[Path]:
        if self.has_staging_file():
            return None

        inventory = self.inventory()
        if not inventory:
            return None

        next_file = inventory[0]
        target = self.staging_dir / next_file.name
        target.parent.mkdir(parents=True, exist_ok=True)
        next_file.replace(target)
        return target

    def cleanup_success(self, file_path: Path) -> bool:
        try:
            if file_path.exists():
                file_path.unlink()
            return True
        except Exception:
            return False

    def cleanup_error(self, file_path: Path) -> Optional[Path]:
        try:
            if not file_path.exists():
                return None
            target = self.quarantine_dir / file_path.name
            if target.exists():
                target = self.quarantine_dir / f"{file_path.stem}_failed{file_path.suffix}"
            shutil.move(str(file_path), str(target))
            return target
        except Exception:
            return None
