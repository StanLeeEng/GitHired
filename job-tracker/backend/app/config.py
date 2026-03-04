import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

class Config:
    """Application configuration loaded from environment variables"""

    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

    EMAIL_SENDER = os.getenv("EMAIL_SENDER")

    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

    EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")

    CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES"))

    # --- Location filter (e.g. 'USA' to only keep US jobs, empty = no filter) ---
    FILTER_COUNTRY = os.getenv("FILTER_COUNTRY", "")

    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")

    DATABASE_PATH = os.getenv("DATABASE_PATH", "jobs.db")
    

    @staticmethod
    def validate():
        """Makes sure all required env variables are used"""

        required = {
            "GITHUB_TOKEN": Config.GITHUB_TOKEN,
            "EMAIL_SENDER": Config.EMAIL_SENDER,
            "EMAIL_PASSWORD": Config.EMAIL_PASSWORD,
            "EMAIL_RECIPIENT": Config.EMAIL_RECIPIENT
        }
        missing = [k for k, v in required.items() if not v]
        if missing:
            raise ValueError(
                f"Missing required env variables: {', '.join(missing)}"
            )

    