from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import fitz  # PyMuPDF
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import HumanMessage, SystemMessage

from pipeline_models import ExtractionOutput
from prompts.expert_prompts import EXPERT_ANALYSIS_PROMPT

logger = logging.getLogger(__name__)


def _extract_pages_text(pdf_path: Path) -> List[Tuple[int, str]]:
    pages: List[Tuple[int, str]] = []
    doc = fitz.open(pdf_path)
    for page_index in range(doc.page_count):
        page = doc.load_page(page_index)
        text = page.get_text("text")
        pages.append((page_index + 1, text))
    return pages


def _build_document_text(pages: List[Tuple[int, str]]) -> str:
    chunks = []
    for page_number, text in pages:
        chunks.append(f"=== Page {page_number} ===\n{text.strip()}\n")
    return "\n".join(chunks)


def _guess_page_from_text(step_text: str, pages: List[Tuple[int, str]]) -> int:
    if not step_text:
        return 1
    tokens = [t.lower() for t in step_text.split() if len(t) > 3]
    if not tokens:
        return 1
    best_page = 1
    best_score = 0
    for page_number, page_text in pages:
        page_lower = page_text.lower()
        score = sum(1 for t in tokens if t in page_lower)
        if score > best_score:
            best_score = score
            best_page = page_number
    return best_page


def _ensure_source_pages(output: ExtractionOutput, pages: List[Tuple[int, str]]) -> ExtractionOutput:
    for procedure in output.procedures:
        for step in procedure.steps:
            if not step.source_page or step.source_page <= 0:
                step.source_page = _guess_page_from_text(
                    f"{step.action} {step.description}", pages
                )
    for tip in output.tips:
        if not tip.source_page or tip.source_page <= 0:
            tip.source_page = _guess_page_from_text(tip.content, pages)
    for setting in output.settings:
        if not setting.source_page or setting.source_page <= 0:
            setting.source_page = _guess_page_from_text(
                f"{setting.name} {setting.value} {setting.notes or ''}", pages
            )
    return output


def extract_with_langchain(
    pdf_path: Path,
    brand: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.1,
) -> ExtractionOutput:
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF introuvable: {pdf_path}")

    pages = _extract_pages_text(pdf_path)
    max_pages_env = os.getenv("OLLAMA_MAX_PAGES")
    if max_pages_env:
        try:
            max_pages = int(max_pages_env)
            if max_pages > 0:
                pages = pages[:max_pages]
        except ValueError:
            pass

    parser = PydanticOutputParser(pydantic_object=ExtractionOutput)
    format_instructions = parser.get_format_instructions()

    context = {
        "document_title": pdf_path.name,
        "brand": brand or "Inconnu",
        "file_type": "pdf",
    }
    system_prompt = (
        "Tu es un expert en maintenance photovoltaïque. "
        "Tu dois extraire des procédures et tips structurés. "
        "Chaque étape doit inclure son numéro de page source. "
        "Priorise les normes UTE/VDE et les paramètres France. "
        "Réponds uniquement avec du JSON valide."
    )
    expert_prompt = EXPERT_ANALYSIS_PROMPT.format(**context)

    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model = model or os.getenv("OLLAMA_MODEL", "mistral")

    llm = ChatOllama(
        base_url=ollama_url,
        model=ollama_model,
        temperature=temperature,
    )

    def _invoke(doc_text: str) -> ExtractionOutput:
        user_prompt = (
            f"{expert_prompt}\n\n"
            f"CONTENU DU DOCUMENT (avec pages):\n{doc_text}\n\n"
            f"{format_instructions}"
        )
        response = llm.invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]
        )
        raw_text = response.content if hasattr(response, "content") else str(response)
        try:
            return parser.parse(raw_text)
        except Exception as exc:
            logger.error("Erreur parsing LangChain: %s", exc)
            logger.debug("Réponse brute: %s", raw_text[:2000])
            raise

    max_chars = int(os.getenv("OLLAMA_MAX_CHARS", "50000"))
    chunk_size = int(os.getenv("OLLAMA_PAGE_CHUNK", "6"))
    full_text = _build_document_text(pages)

    if len(full_text) <= max_chars:
        parsed = _invoke(full_text)
        return _ensure_source_pages(parsed, pages)

    logger.warning("Document long, extraction par chunks (%s pages)", chunk_size)
    combined = ExtractionOutput()
    for i in range(0, len(pages), chunk_size):
        chunk_pages = pages[i : i + chunk_size]
        chunk_text = _build_document_text(chunk_pages)
        try:
            chunk_output = _invoke(chunk_text)
        except Exception:
            continue
        combined.procedures.extend(chunk_output.procedures)
        combined.tips.extend(chunk_output.tips)
        combined.settings.extend(chunk_output.settings)

    return _ensure_source_pages(combined, pages)
