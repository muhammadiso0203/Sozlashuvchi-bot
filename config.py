import os
from pathlib import Path
from dotenv import load_dotenv

# Asosiy papka yo'li
BASE_DIR = Path(__file__).resolve().parent

# .env faylini yuklash
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Adminlar ID ro'yxati
admin_ids_raw = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(i.strip()) for i in admin_ids_raw.split(",") if i.strip().isdigit()]

# Ma'lumotlar bazasi fayli yo'li
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
RESPONSES_FILE = DATA_DIR / "responses.json"
