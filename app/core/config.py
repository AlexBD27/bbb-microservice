from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    BBB_SECRET = os.getenv("BBB_SECRET")
    BBB_URL = os.getenv("BBB_URL")

settings = Settings()
