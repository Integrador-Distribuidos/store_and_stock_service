from json import load
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta
import os
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

def create_test_token(user_id: str = "1000"):
    payload = {
        "user_id": user_id,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=300)  # expira em 300 minutos
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token