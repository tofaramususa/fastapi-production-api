# need to import firebase_admin
# need to initialize firebase_admin
# need to connect to firebase admin sdk
# need to implement function that takes userid and returns user document
# need to have a schema for a user
import firebase_admin
from firebase_admin import credentials, auth
from typing import Optional
from app.core.config import settings

try:
    cred = credentials.Certificate(settings.GOOGLE_APPLICATION_CREDENTIALS)
    firebase_admin.initialize_app(cred)
except Exception as e:
    print(f"Firebase auth error: {str(e)}")


async def get_firebase_user(token: str) -> Optional[dict]:
    try:
        # Verify the Firebase ID token
        # decoded_token = auth.verify_id_token(token)
        # user_id = decoded_token['uid']
        # Get additional user info from Firebase
        user = auth.get_user(token)

        return {"email": user.email, "uid": user.uid, "is_admin": False}
    except Exception as e:
        print(f"Firebase auth error: {str(e)}")
        return None


# Remove test code
