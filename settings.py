from dotenv import load_dotenv
import os

dotenv_path = '.env'
load_dotenv(dotenv_path)


AWS_KEY = os.environ.get("AWS_KEY")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")


CELERY_BROKER_URL=os.environ.get("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND=os.environ.get("CELERY_RESULT_BACKEND")
