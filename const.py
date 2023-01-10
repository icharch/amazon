import os
from dotenv import load_dotenv

load_dotenv()

LWA_APP_ID = os.environ["LWA_APP_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
AWS_ACCESS_KEY = os.environ["AWS_ACCESS_KEY"]
AWS_SECRET_KEY = os.environ["AWS_SECRET_KEY"]
ROLE_ARN = os.environ["ROLE_ARN"]

GOOGLE_SHEETS_EMAIL = os.environ["GOOGLE_SHEETS_EMAIL"]
GOOGLE_SHEETS_ID = os.environ["GOOGLE_SHEETS_ID"]

# UK
GOOGLE_WORKSHEET_NAME_UK = os.environ["GOOGLE_WORKSHEET_NAME_UK"]
REFRESH_TOKEN_UK = os.environ["REFRESH_TOKEN_UK"]

#DE
GOOGLE_WORKSHEET_NAME_DE = os.environ["GOOGLE_WORKSHEET_NAME_DE"]
REFRESH_TOKEN_DE = os.environ["REFRESH_TOKEN_DE"]