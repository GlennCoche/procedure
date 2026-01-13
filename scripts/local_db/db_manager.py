#!/usr/bin/env python3
"""
Gestionnaire de base de données locale utilisant le MCP sqlite
Wrapper pour faciliter l'utilisation du MCP sqlite depuis Python
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class LocalDBManager:
    """Gestionnaire de base de données locale SQLite"""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Args:
            db_path: Chemin vers la base de données SQLite
        """
        if db_path is None:
            db_path = Path(__file__).parent / "documents.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def get_connection(self):
        """Obtenir une connexion à la base de données"""
        return sqlite3.connect(str(self.db_path))
    
    def execute_sql(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Exécuter une requête SQL
        
        Args:
            sql: Requête SQL à exécuter
            params: Paramètres pour la requête
        
        Returns:
            Liste de dictionnaires avec les résultats
        """
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql, params)
            
            # Pour les SELECT, retourner les résultats
            if sql.strip().upper().startswith('SELECT'):
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            else:
                # Pour INSERT/UPDATE/DELETE, commit et retourner le nombre de lignes affectées
                conn.commit()
                return [{"rows_affected": cursor.rowcount}]
        except Exception as e:
            conn.rollback()
            raise Exception(f"Erreur SQL: {e}")
        finally:
            conn.close()
    
    def create_record(self, table: str, data: Dict[str, Any]) -> int:
        """
        Créer un enregistrement dans une table
        
        Args:
            table: Nom de la table
            data: Données à insérer (dictionnaire)
        
        Returns:
            ID de l'enregistrement créé
        """
        # Convertir les valeurs JSON en string
        data = self._prepare_data(data)
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        values = tuple(data.values())
        
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql, values)
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            raise Exception(f"Erreur lors de la création: {e}")
        finally:
            conn.close()
    
    def read_records(self, table: str, conditions: Optional[Dict[str, Any]] = None, 
                     limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Lire des enregistrements d'une table
        
        Args:
            table: Nom de la table
            conditions: Conditions de filtrage (dictionnaire)
            limit: Nombre maximum de résultats
            offset: Nombre de résultats à ignorer
        
        Returns:
            Liste de dictionnaires avec les résultats
        """
        sql = f"SELECT * FROM {table}"
        params = []
        
        if conditions:
            where_clauses = []
            for key, value in conditions.items():
                where_clauses.append(f"{key} = ?")
                params.append(value)
            sql += " WHERE " + " AND ".join(where_clauses)
        
        if limit:
            sql += f" LIMIT {limit}"
            if offset:
                sql += f" OFFSET {offset}"
        
        return self.execute_sql(sql, tuple(params))
    
    def update_records(self, table: str, data: Dict[str, Any], 
                      conditions: Dict[str, Any]) -> int:
        """
        Mettre à jour des enregistrements
        
        Args:
            table: Nom de la table
            data: Données à mettre à jour
            conditions: Conditions de filtrage
        
        Returns:
            Nombre de lignes affectées
        """
        # Convertir les valeurs JSON en string
        data = self._prepare_data(data)
        
        # Ajouter updated_at automatiquement
        if 'updated_at' not in data:
            data['updated_at'] = datetime.now().isoformat()
        
        set_clauses = [f"{key} = ?" for key in data.keys()]
        where_clauses = [f"{key} = ?" for key in conditions.keys()]
        
        sql = f"UPDATE {table} SET {', '.join(set_clauses)} WHERE {' AND '.join(where_clauses)}"
        params = tuple(list(data.values()) + list(conditions.values()))
        
        result = self.execute_sql(sql, params)
        return result[0].get("rows_affected", 0) if result else 0
    
    def delete_records(self, table: str, conditions: Dict[str, Any]) -> int:
        """
        Supprimer des enregistrements
        
        Args:
            table: Nom de la table
            conditions: Conditions de filtrage
        
        Returns:
            Nombre de lignes supprimées
        """
        where_clauses = [f"{key} = ?" for key in conditions.keys()]
        sql = f"DELETE FROM {table} WHERE {' AND '.join(where_clauses)}"
        params = tuple(conditions.values())
        
        result = self.execute_sql(sql, params)
        return result[0].get("rows_affected", 0) if result else 0
    
    def list_tables(self) -> List[str]:
        """Lister toutes les tables de la base"""
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        results = self.execute_sql(sql)
        return [row['name'] for row in results]
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Obtenir le schéma d'une table"""
        sql = f"PRAGMA table_info({table_name})"
        columns = self.execute_sql(sql)
        return {"table": table_name, "columns": columns}
    
    def _prepare_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Préparer les données pour l'insertion (convertir JSON en string)"""
        prepared = {}
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                prepared[key] = json.dumps(value, ensure_ascii=False)
            else:
                prepared[key] = value
        return prepared
    
    def init_schema(self) -> bool:
        """Initialiser le schéma de la base de données"""
        schema_path = Path(__file__).parent / "schema.sql"
        
        if not schema_path.exists():
            print(f"❌ Erreur: schema.sql non trouvé: {schema_path}")
            return False
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Exécuter le schéma
        try:
            # Séparer les commandes SQL
            commands = [cmd.strip() for cmd in schema_sql.split(';') if cmd.strip()]
            
            for command in commands:
                if command:
                    self.execute_sql(command)
            
            print(f"✅ Schéma initialisé avec succès")
            print(f"   Tables créées: {', '.join(self.list_tables())}")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation du schéma: {e}")
            return False


def main():
    """Fonction principale pour tests"""
    db = LocalDBManager()
    
    print("🔧 Initialisation de la base de données locale...")
    success = db.init_schema()
    
    if success:
        print("\n📊 Tables disponibles:")
        for table in db.list_tables():
            schema = db.get_table_schema(table)
            print(f"   - {table}: {len(schema['columns'])} colonnes")
    
    return success


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
