from dotenv import load_dotenv
import os

load_dotenv()

TG_TOKEN = os.environ.get("TG_TOKEN")
KEY_EXCHANGERATE = os.environ.get("KEY_EXCHANGERATE")
ADMIN_IDS = [int(x) for x in os.environ.get("ADMIN_IDS").split()]
CHANEL_ID = int(os.environ.get("CHANEL_ID"))
DELTA = int(os.environ.get("DELTA"))
VK_TOKEN = os.environ.get("VK_TOKEN")
VK_CHANEL = os.environ.get("VK_CHANEL")

