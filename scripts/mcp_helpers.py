#!/usr/bin/env python3
"""
Helpers pour utiliser les MCPs depuis Python
Ces fonctions documentent comment l'agent Cursor doit utiliser les MCPs
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import json


class MCPHelper:
    """
    Helper pour documenter l'utilisation des MCPs
    Note: L'agent Cursor utilisera directement les outils MCP, ces helpers
    servent de documentation et de référence.
    """
    
    @staticmethod
    def pdf_tools_get_metadata(pdf_name: str) -> Dict[str, Any]:
        """
        Instructions pour utiliser pdf-tools.get_metadata
        
        L'agent Cursor doit utiliser: pdf-tools.get_metadata
        """
        return {
            "mcp_tool": "pdf-tools.get_metadata",
            "args": {"name": pdf_name},
            "description": "Extraire les métadonnées du PDF"
        }
    
    @staticmethod
    def pdf_tools_get_text_json(pdf_name: str) -> Dict[str, Any]:
        """Instructions pour pdf-tools.get_text_json"""
        return {
            "mcp_tool": "pdf-tools.get_text_json",
            "args": {"name": pdf_name},
            "description": "Extraire le texte structuré avec positions"
        }
    
    @staticmethod
    def pdf_tools_display_page(pdf_name: str, page_number: int) -> Dict[str, Any]:
        """Instructions pour pdf-tools.display_page_as_image"""
        return {
            "mcp_tool": "pdf-tools.display_page_as_image",
            "args": {"name": pdf_name, "page_number": page_number},
            "description": "Extraire une page comme image"
        }
    
    @staticmethod
    def content_core_extract(file_path: str) -> Dict[str, Any]:
        """
        Instructions pour utiliser content-core.extract_content
        
        L'agent Cursor doit utiliser: content-core.extract_content
        """
        return {
            "mcp_tool": "content-core.extract_content",
            "args": {"file_path": file_path},
            "description": "Extraction intelligente avec analyse IA"
        }
    
    @staticmethod
    def sqlite_create_record(table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Instructions pour utiliser sqlite.create_record
        
        L'agent Cursor doit utiliser: sqlite.create_record
        """
        return {
            "mcp_tool": "sqlite.create_record",
            "args": {"table": table, "data": data},
            "description": f"Créer un enregistrement dans {table}"
        }
    
    @staticmethod
    def sqlite_read_records(table: str, conditions: Optional[Dict[str, Any]] = None,
                           limit: Optional[int] = None) -> Dict[str, Any]:
        """Instructions pour sqlite.read_records"""
        args = {"table": table}
        if conditions:
            args["conditions"] = conditions
        if limit:
            args["limit"] = limit
        
        return {
            "mcp_tool": "sqlite.read_records",
            "args": args,
            "description": f"Lire des enregistrements depuis {table}"
        }
    
    @staticmethod
    def sqlite_update_records(table: str, data: Dict[str, Any], 
                              conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Instructions pour sqlite.update_records"""
        return {
            "mcp_tool": "sqlite.update_records",
            "args": {"table": table, "data": data, "conditions": conditions},
            "description": f"Mettre à jour des enregistrements dans {table}"
        }
    
    @staticmethod
    def sqlite_execute_sql(sql: str, params: Optional[List[Any]] = None) -> Dict[str, Any]:
        """Instructions pour sqlite.execute_sql"""
        args = {"sql": sql}
        if params:
            args["values"] = params
        
        return {
            "mcp_tool": "sqlite.execute_sql",
            "args": args,
            "description": "Exécuter une requête SQL"
        }
    
    @staticmethod
    def faiss_create_embeddings(text: str, source: str = "unknown") -> Dict[str, Any]:
        """
        Instructions pour utiliser faiss MCP pour créer des embeddings
        
        L'agent Cursor doit utiliser: faiss (outils disponibles via le MCP)
        """
        return {
            "mcp_tool": "faiss",
            "description": "Créer des embeddings vectoriels",
            "note": "Utiliser le MCP faiss pour ingérer le document et créer les embeddings",
            "input": {"document": text, "source": source}
        }


def get_mcp_instructions_for_workflow(workflow_step: str) -> Dict[str, Any]:
    """
    Obtenir les instructions MCP pour une étape du workflow
    
    Args:
        workflow_step: Nom de l'étape ('extraction', 'analysis', 'structuring', etc.)
    
    Returns:
        Instructions pour utiliser les MCPs
    """
    helper = MCPHelper()
    
    instructions = {
        "extraction": {
            "pdf_tools": [
                helper.pdf_tools_get_metadata("document.pdf"),
                helper.pdf_tools_get_text_json("document.pdf"),
                helper.pdf_tools_display_page("document.pdf", 1)
            ],
            "content_core": [
                helper.content_core_extract("/path/to/document.pdf")
            ]
        },
        "analysis": {
            "content_core": [
                helper.content_core_extract("/path/to/document.pdf")
            ]
        },
        "structuring": {
            "content_core": [
                helper.content_core_extract("/path/to/document.pdf")
            ],
            "sqlite": [
                helper.sqlite_create_record("local_procedures", {}),
                helper.sqlite_create_record("local_tips", {})
            ]
        },
        "validation": {
            "sqlite": [
                helper.sqlite_read_records("local_procedures"),
                helper.sqlite_execute_sql("SELECT ..."),
                helper.sqlite_update_records("local_procedures", {}, {})
            ]
        },
        "embeddings": {
            "faiss": [
                helper.faiss_create_embeddings("text content", "source")
            ]
        }
    }
    
    return instructions.get(workflow_step, {})


if __name__ == "__main__":
    print("📚 Helpers MCP disponibles")
    print("\nExemples d'instructions pour chaque MCP:\n")
    
    helper = MCPHelper()
    
    examples = {
        "PDF Tools": helper.pdf_tools_get_metadata("example.pdf"),
        "Content Core": helper.content_core_extract("/path/to/file.pdf"),
        "SQLite Create": helper.sqlite_create_record("local_procedures", {"title": "Test"}),
        "SQLite Read": helper.sqlite_read_records("local_procedures", {"document_id": 1}),
        "Faiss": helper.faiss_create_embeddings("text content")
    }
    
    for name, instruction in examples.items():
        print(f"{name}:")
        print(json.dumps(instruction, indent=2, ensure_ascii=False))
        print()
