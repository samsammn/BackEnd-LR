from app import *
from src.utils.DBConnection import *
from src.utils.JWTEncoderDecoder import *

#1. fungsi untuk signin 
@app.route('/sign-in', methods=['POST'])
def signIn():

    sid = request.json['staff_id']
    pwd = request.json['password']

    cursorSignIn = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursorSignIn.execute("rollback")
    cursorSignIn.execute("Select * from sign_in(%s,%s)",(int(sid),pwd))
    rowCount = cursorSignIn.rowcount

    data = []
    for row in cursorSignIn.fetchall():
        token = encodeStaffID(row[0])
        data.append(dict(row))

    connection.commit()
    data[0].update({'token_jwt':str(token)})

    if rowCount > 0:
        return jsonify(data), 200
    else:
        return "Failed", 400

#2. fungsi membuat leave type
@app.route('/leave-type', methods=['GET'])
def getLeaveType():
    cursorLeaveType = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursorLeaveType.execute("Select * from get_leave_type()")

    data = []
    for row in cursorLeaveType.fetchall():
        data.append(dict(row))

    return jsonify(data), 200

#3. fungsi membuat leave type berdasarkan id leave type
@app.route('/leave-type-by/<id_leave_type>', methods=['GET'])
def getLeaveTypeBy(id_leave_type):

    cursorLeaveType = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursorLeaveType.execute("Select * from get_leave_type_by(%s)",(id_leave_type,))

    data = []
    for row in cursorLeaveType.fetchall():
        data.append(dict(row))

    return jsonify(data), 200

#4. fungsi untuk get data employee
@app.route('/data-employee/<TokenJwt>', methods=['GET'])
def getDataEmployee(TokenJwt):

    staffId = decodeStaffID(TokenJwt)

    cursorGetEmployee = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursorGetEmployee.execute("Select * from get_data_employee(%s)", (staffId,))

    data = []
    for row in cursorGetEmployee.fetchall():
        data.append(dict(row))

    connection.commit()
    return jsonify(data), 200

#5. fungsi membuat get leave detail = berfungsi menampilkan transaksi detail request cuti 
@app.route('/leave-detail/<leave_id>', methods=['GET'])
def getLeaveDetails(leave_id):
    cursorLeaveDetails = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursorLeaveDetails.execute('rollback') #rollback untuk meng-eksekusi perintah hingga berhasil
    cursorLeaveDetails.execute("Select * from get_leave_detail(%s)",(leave_id,))

    data = []
    for row in cursorLeaveDetails.fetchall():
        data.append(dict(row))

    return jsonify(data), 200

