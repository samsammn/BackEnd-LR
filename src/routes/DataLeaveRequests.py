from app import *
from src.utils.DBConnection import *

# fungsi untuk signIn
@app.route('/signIn', methods=['POST'])
def signIn():

    sid = request.json['sid']
    pwd = request.json['pwd']

    curSignIn = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    curSignIn.execute("rollback")
    curSignIn.execute("Select * from signin(%s,%s)",(int(sid),pwd))
    jml = curSignIn.rowcount

    data = []
    for row in curSignIn.fetchall():
        encode = jwt.encode({'sid':row[0]}, secret_key, algorithm='HS256').decode('utf-8')
        data.append(dict(row))

    connection.commit()
    data[0].update({'token':str(encode)})

    if jml > 0:
        return jsonify(data), 200
    else:
        return "Failed", 400

# fungsi membuat leave type
@app.route('/getLeaveType')
def getLeaveType():
    curLeaveType = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    curLeaveType.execute("Select * from getLeaveType()")

    data = []
    for row in curLeaveType.fetchall():
        data.append(dict(row))

    return jsonify(data), 200

# fungsi membuat leave type berdasarkan id leave type
@app.route('/getLeaveTypeBy/<id_leave_type>')
def getLeaveTypeBy(id_leave_type):

    curLeaveType = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    curLeaveType.execute("Select * from getLeaveTypeBy(%s)",(id_leave_type,))

    data = []
    for row in curLeaveType.fetchall():
        data.append(dict(row))

    return jsonify(data), 200

# fungsi untuk get data employee
@app.route('/getDataEmployee/<sidToken>')
def getDataEmployee(sidToken):

    decode = jwt.decode(sidToken, secret_key, algorithms=['HS256'])
    sid = decode['sid']

    curGetEmployee = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    curGetEmployee.execute("Select * from getDataEmployee(%s)", (sid,))

    data = []
    for row in curGetEmployee.fetchall():
        data.append(dict(row))

    con.commit()
    return jsonify(data), 200

# fungsi membuat get leave detail
@app.route('/getLeaveDetail/<leave_id>')
def getLeaveDetails(leave_id):
    curLeaveDetails = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    curLeaveDetails.execute('rollback')
    curLeaveDetails.execute("Select * from getleavedetail(%s)",(leave_id,))

    data = []
    for row in curLeaveDetails.fetchall():
        data.append(dict(row))

    return jsonify(data), 200

