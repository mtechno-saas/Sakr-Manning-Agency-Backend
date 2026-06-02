import sqlite3
from django.db import connection

def get_abbreviated_schema():
    """
    Returns an abbreviated schema of the SQLite database.
    Focuses on main application tables to avoid context window explosion.
    """
    schema_parts = []
    with connection.cursor() as cursor:
        # Get all relevant application tables
        cursor.execute("""
            SELECT name, sql 
            FROM sqlite_master 
            WHERE type='table' 
              AND name NOT LIKE 'sqlite_%' 
              AND name NOT LIKE 'django_%' 
              AND name NOT LIKE 'auth_%'
              AND name NOT LIKE 'authtoken_%'
              AND sql IS NOT NULL;
        """)
        tables = cursor.fetchall()
        for table_name, table_sql in tables:
            # Clean up the CREATE TABLE statement slightly for the LLM
            clean_sql = " ".join(table_sql.split())
            schema_parts.append(clean_sql)
            
    return "\n".join(schema_parts)

def execute_read_only_query(sql_query):
    """
    Executes a read-only SQL query against the database and returns the results.
    Validates that the query is a SELECT statement.
    """
    sql_query = sql_query.strip()
    if not sql_query.upper().startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed for security reasons.")
    
    # Check for forbidden keywords as an extra precaution
    forbidden = ["DROP", "UPDATE", "DELETE", "INSERT", "ALTER", "CREATE", "GRANT", "REVOKE"]
    upper_query = sql_query.upper()
    for word in forbidden:
        if word in upper_query:
             raise ValueError(f"Forbidden keyword '{word}' detected in query.")
    
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        # Fetch up to 50 rows to avoid blowing up the LLM context limit
        results = cursor.fetchmany(50)
        columns = [col[0] for col in cursor.description] if cursor.description else []
        
    return {
        "columns": columns,
        "results": results
    }
