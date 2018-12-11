import jwt

secret_key = "LeaveRequestMashaf"

def encodeStaffID(staff_id):
    return jwt.encode({'staff_id':staff_id}, secret_key, algorithm='HS256').decode('utf-8')

def decodeStaffID(token):
    decode = jwt.decode(token, secret_key, algorithm=['HS256'])
    return decode['staff_id']