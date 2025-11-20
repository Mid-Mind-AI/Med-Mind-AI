import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load .env.local file from the backend directory
backend_dir = os.path.dirname(os.path.dirname(__file__))
env_local_path = os.path.join(backend_dir, '.env.local')
load_dotenv(env_local_path)

# Get environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "You can get it from Supabase Dashboard > Settings > Database > Connection string (URI format)"
    )

def get_connection():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set")
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
