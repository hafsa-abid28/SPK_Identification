"""
Database Setup Script for Speaker Recognition System

This script will:
1. Create the database if it doesn't exist
2. Create the speakers table
3. Set up necessary indexes and triggers
"""
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "database": "mydb", 
    "user": "postgres",
    "password": "Pass,822",
    "port": 5432
}

def create_database():
    """Create the database if it doesn't exist."""
    try:
        # Connect to PostgreSQL server (default postgres database)
        conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            database="postgres",  # Connect to default database first
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            port=DB_CONFIG["port"]
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Check if database exists
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_CONFIG["database"],))
        exists = cur.fetchone()
        
        if not exists:
            cur.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(DB_CONFIG["database"])
            ))
            print(f"✓ Database '{DB_CONFIG['database']}' created successfully!")
        else:
            print(f"✓ Database '{DB_CONFIG['database']}' already exists")
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

def create_tables():
    """Create the speakers table with all necessary fields."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Create speakers table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS speakers (
                id SERIAL PRIMARY KEY,
                speaker_code VARCHAR(50) UNIQUE NOT NULL,
                display_name VARCHAR(255) NOT NULL,
                embedding_path VARCHAR(500) NOT NULL,
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_speaker_code ON speakers(speaker_code)
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_active ON speakers(active)
        """)
        
        # Create update timestamp function
        cur.execute("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql
        """)
        
        # Create trigger
        cur.execute("""
            DROP TRIGGER IF EXISTS update_speakers_updated_at ON speakers
        """)
        cur.execute("""
            CREATE TRIGGER update_speakers_updated_at
                BEFORE UPDATE ON speakers
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column()
        """)
        
        conn.commit()
        print("✓ Tables created successfully!")
        print("✓ Indexes created successfully!")
        print("✓ Triggers created successfully!")
        
        # Display table info
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'speakers'
            ORDER BY ordinal_position
        """)
        
        print("\n" + "="*60)
        print("SPEAKERS TABLE STRUCTURE:")
        print("="*60)
        for row in cur.fetchall():
            print(f"  {row[0]:<20} {row[1]:<20} Nullable: {row[2]}")
        print("="*60)
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating tables: {e}")
        return False

def test_connection():
    """Test database connection."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT version()")
        version = cur.fetchone()
        print(f"\n✓ Connected to PostgreSQL!")
        print(f"  Version: {version[0]}")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

def main():
    print("="*60)
    print("Speaker Recognition Database Setup")
    print("="*60)
    print()
    
    # Step 1: Create database
    print("Step 1: Creating database...")
    if not create_database():
        print("Failed to create database. Please check your credentials.")
        return
    
    print()
    
    # Step 2: Test connection
    print("Step 2: Testing connection...")
    if not test_connection():
        print("Failed to connect to database. Please check your credentials.")
        return
    
    print()
    
    # Step 3: Create tables
    print("Step 3: Creating tables and indexes...")
    if not create_tables():
        print("Failed to create tables.")
        return
    
    print()
    print("="*60)
    print("✓ Database setup completed successfully!")
    print("="*60)
    print()
    print("Next steps:")
    print("1. Update DB_CONFIG in Register_Speaker.py with your credentials")
    print("2. Register speakers using: python register_speaker_script.py")
    print("3. Verify speakers using: python verify_speaker_script.py")

if __name__ == "__main__":
    print()
    print("IMPORTANT: Update DB_CONFIG in this file with your PostgreSQL credentials!")
    print()
    input("Press Enter to continue with database setup...")
    print()
    main()
