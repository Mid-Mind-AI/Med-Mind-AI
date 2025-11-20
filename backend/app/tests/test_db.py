import os
import sys
import traceback
from urllib.parse import urlparse
from app.db import get_connection
from dotenv import load_dotenv
# Load environment variables from .env.local
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
env_local_path = os.path.join(backend_dir, '.env.local')
load_dotenv(env_local_path)

def check_environment():
    """Check if required environment variables and modules are available"""
    print("=" * 60)
    print("ENVIRONMENT CHECK")
    print("=" * 60)

    # Check for psycopg2
    try:
        import psycopg2  # pyright: ignore[reportMissingModuleSource]
        print("psycopg2 module found")
    except ImportError as e:
        print("ERROR: psycopg2 module not found")
        print(f"  {e}")
        print("  Run: pip install psycopg2-binary")
        return False

    # Check environment variables
    database_url = os.getenv("DATABASE_URL")

    print(f"\nEnvironment Variables:")
    print(f"  DATABASE_URL: {'Set' if database_url else 'Not set'}")
    if database_url:
        parsed = urlparse(database_url)
        if parsed.password:
            masked_url = database_url.replace(parsed.password, "***")
        else:
            masked_url = database_url
        print(f"    Value: {masked_url[:80]}..." if len(masked_url) > 80 else f"    Value: {masked_url}")
        print(f"    Host: {parsed.hostname}")
        print(f"    Port: {parsed.port}")
        print(f"    Database: {parsed.path.lstrip('/')}")
    else:
        print("  ERROR: DATABASE_URL is required")

    print("=" * 60)
    return True

def test_connection():
    print("\n" + "=" * 60)
    print("TEST 1: Database Connection")
    print("=" * 60)

    try:
        from app.db import get_connection

        conn = get_connection()
        print("Connection established")

        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()
            print(f"PostgreSQL version: {version['version']}")

            cur.execute("SELECT current_database(), current_user, inet_server_addr(), inet_server_port();")
            info = cur.fetchone()
            print(f"Database: {info['current_database']}, User: {info['current_user']}")
            if info['inet_server_addr']:
                print(f"Server: {info['inet_server_addr']}:{info['inet_server_port']}")

        conn.close()
        return True

    except ImportError as e:
        print(f"ERROR: Import failed - {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"ERROR: Connection failed - {type(e).__name__}: {e}")
        traceback.print_exc()
        return False

def test_events_table():
    print("\n" + "=" * 60)
    print("TEST 2: Events Table Check")
    print("=" * 60)

    try:
        from app.db import get_connection

        conn = get_connection()
        with conn.cursor() as cur:
            # Check if table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'events'
                );
            """)
            table_exists = cur.fetchone()['exists']

            if not table_exists:
                print("ERROR: Events table does not exist")
                conn.close()
                return False

            print("Events table exists")

            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = 'events'
                ORDER BY ordinal_position;
            """)
            columns = cur.fetchall()
            print(f"Columns ({len(columns)}): {', '.join([col['column_name'] for col in columns])}")

            cur.execute("SELECT * FROM events LIMIT 5;")
            rows = cur.fetchall()
            print(f"Query successful ({len(rows)} rows)")

        conn.close()
        return True

    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        traceback.print_exc()
        return False

def test_insert_event():
    print("\n" + "=" * 60)
    print("TEST 3: Insert Event Test")
    print("=" * 60)

    event_id = None
    try:
        from app.db import get_connection

        conn = get_connection()

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO events (patient_name, doctor_name, title, start_at, end_at)
                    VALUES ('Test User', 'Dr. Demo', 'Test Appointment',
                            NOW(), NOW() + INTERVAL '30 minutes')
                    RETURNING id;
                    """
                )
                result = cur.fetchone()
                event_id = result["id"]
                conn.commit()
                print(f"Insert successful - Event ID: {event_id}")

                cur.execute("DELETE FROM events WHERE id = %s;", (event_id,))
                conn.commit()
                print("Test event cleaned up")

            conn.close()
            return True

        except Exception as e:
            # Try to rollback if there's an error
            try:
                conn.rollback()
            except:
                pass
            raise e

    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        traceback.print_exc()

        if event_id:
            try:
                from app.db import get_connection
                conn = get_connection()
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM events WHERE id = %s;", (event_id,))
                    conn.commit()
                conn.close()
            except:
                pass

        return False

def run_all_tests():
    print("\n" + "=" * 60)
    print("POSTGRESQL DATABASE TESTS")
    print("=" * 60)

    # First check environment
    if not check_environment():
        print("\nERROR: Environment check failed. Fix issues above before running tests.")
        return

    # Run tests
    results = []
    results.append(("Connection Test", test_connection()))
    results.append(("Events Table Test", test_events_table()))
    results.append(("Insert Event Test", test_insert_event()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"  {test_name}: {status}")

    print(f"\n  Total: {passed}/{total} tests passed")
    print("=" * 60)

    if passed == total:
        print("\nAll tests passed")
    else:
        print(f"\n{total - passed} test(s) failed")

    print()

if __name__ == "__main__":
    run_all_tests()
