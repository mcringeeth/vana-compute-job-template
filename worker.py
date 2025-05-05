from pathlib import Path
import sqlite3
import json
import os
import sys
from query_engine_client import QueryEngineClient

# Paths to the database and output file
DB_PATH = Path(os.getenv("INPUT_PATH", "/mnt/input")) / "query_results.db"  # Default path to the SQLite database
OUTPUT_PATH = Path(os.getenv("OUTPUT_PATH", "/mnt/output")) / "stats.json"  # Default output JSON path
DEV_MODE = os.getenv("DEV_MODE", "0").lower() in ("1", "true", "yes")  # Enable development mode

def get_user_locales():
    """Connects to the SQLite DB and retrieves user_id and locale."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Query user_id and locale from the results table
        cursor.execute('SELECT user_id, locale FROM results')
        
        # Create a dictionary with user_id as keys and locale as values
        user_locales = {}
        for row in cursor.fetchall():
            user_id, locale = row
            user_locales[str(user_id)] = locale
        
        conn.close()
        return user_locales
    except Exception as e:
        print(f"Error querying database: {e}")
        raise e

def save_stats_to_json(user_locales, output_path):
    """Saves the user_id: locale mapping to a JSON file."""
    try:
        # Ensure the output directory exists
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)
        
        # Save to JSON
        with open(output_path, "w") as f:
            json.dump(user_locales, f, indent=4)
        print(f"Stats saved to {output_path}")
    except Exception as e:
        print(f"Error saving JSON: {e}")

def main():
    # Check if we're in development mode
    if DEV_MODE:
        print("Running in DEVELOPMENT MODE - using local database file")
        print(f"Processing query results from {DB_PATH}")
    else:
        # Get query and signature from environment variables
        query = os.getenv("QUERY", "")
        query_signature = os.getenv("QUERY_SIGNATURE", "")
        
        if not query or not query_signature:
            print("Error: Missing required QUERY or QUERY_SIGNATURE environment variables")
            print("Set DEV_MODE=1 to use local database file without query execution")
            sys.exit(1)
        
        # Initialize query engine client
        query_engine_client = QueryEngineClient(query, query_signature, str(DB_PATH))
        
        # Execute query
        print(f"Executing query: {query}")
        query_result = query_engine_client.execute_query()
        
        if not query_result.success:
            print(f"Error executing query: {query_result.error}")
            sys.exit(2)
        
        # Query executed successfully, now process the results
        print(f"Query executed successfully, processing results from {DB_PATH}")
    
    # Process the database file (whether it came from dev mode or query execution)
    user_locales = get_user_locales()
    if user_locales:
        print(f"Found {len(user_locales)} users in the database")
        save_stats_to_json(user_locales, OUTPUT_PATH)
    else:
        print("No user stats found in the database")
        # Create an empty stats file to indicate processing completed
        save_stats_to_json({}, OUTPUT_PATH)

if __name__ == "__main__":
    main()