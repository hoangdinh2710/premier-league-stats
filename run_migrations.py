"""
Run database migrations for the medallion architecture.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg2

load_dotenv()


def get_connection():
    """Get database connection."""
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        return psycopg2.connect(dsn=database_url)
    else:
        return psycopg2.connect(
            host=os.getenv("DB_HOST") or os.getenv("SUPABASE_DB_HOST"),
            port=os.getenv("DB_PORT") or "5432",
            database=os.getenv("DB_NAME") or "postgres",
            user=os.getenv("DB_USER") or "postgres",
            password=os.getenv("DB_PASSWORD") or os.getenv("SUPABASE_DB_PASSWORD")
        )


def run_migrations():
    """Run all migration files in order."""
    migrations_dir = Path("migrations")

    if not migrations_dir.exists():
        print("Error: migrations/ directory not found")
        return

    # Get migration files sorted by name
    migration_files = sorted(migrations_dir.glob("*.sql"))

    if not migration_files:
        print("No migration files found")
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:
        for migration_file in migration_files:
            print(f"Running {migration_file.name}...")

            sql = migration_file.read_text(encoding='utf-8')
            cursor.execute(sql)
            conn.commit()

            print(f"  ✓ {migration_file.name} applied successfully")

        print("\n" + "=" * 40)
        print("All migrations applied successfully!")
        print("=" * 40)

    except Exception as e:
        conn.rollback()
        print(f"Error applying migration: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    run_migrations()
