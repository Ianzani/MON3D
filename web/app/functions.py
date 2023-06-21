import hashlib
from app.instances import *

#===========================================Hash email==============================================
def hash_email(email):
    return hashlib.sha256(email.encode('utf-8')).hexdigest()
#===================================================================================================

#=================================Get status from current printer===================================
def get_status() -> str:
    return db.collection(current_user.uid).document(current_user.current).get().to_dict()['status']
#===================================================================================================