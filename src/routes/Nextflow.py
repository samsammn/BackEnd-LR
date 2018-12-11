from app import *
from src.utils.DBConnection import *
from src.utils.NextflowHeaderCreator import *
from src.utils.JWTEncoderDecoder import *

# fungsi untuk menggerakan/menjalankan form leave request dari requester ke supervisor
@app.route('/nextflow/supervisor/submit', methods = ['POST'])
def submitToSupervisor():
    if request.method == 'POST':

        token = request.json['staff_id']
        staffID = decodeStaffID(token)
        
        comment = request.json['comment']
        
        cursorData = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursorData.execute("rollback")
        cursorData.execute("Select * from get_data_employee(%s)", (int(staffID),))

        data = []
        for row in cursorData.fetchall():
            data.append(dict(row))

        connection.commit()
        user_token = data[0]['tokennextflow']

        record_instance = {
            "data": {
                "definition": {
                    "id" : os.getenv('DEFINITION_ID')
                }
            }
        }

        recordID = getRecordID(record_instance, user_token)

        # submit si flow pake record_id dan token dan process id
        process_instance = submitRecord(recordID, user_token)
        processID = process_instance['data']['process_id']

        # gerakin flow dari requester ke manager
        submitToSupervisor(comment, user_token, processID)

        # masukin ke database bersama dengan record id dan process id nya
        data_db = submitToDatabase(recordID, processID)

        # return berupa id dan statusnya
        return str(data_db), 200

# fungsi untuk memproses form leave request dari requester yang akan di aprroval oleh supervisor 
@app.route('/nextflow/supervisor/approval', methods = ['POST'])
def supervisorApproval():
    if request.method == 'POST':

        token = request.json['staff_id']
        staffID = decodeStaffID(token)

        recordID = request.json['rid']
        processID = request.json['pid']
        comment = request.json['comment']

        print("RID",recordID)
        print("PID",processID)
        print("SID",staffID)
        
        cursorData = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursorData.execute("rollback")
        cursorData.execute("Select * from getDataEmployee(%s)", (int(staffID),))

        data = []
        for row in cursorData.fetchall():
            data.append(dict(row))

        user_token = data[0]['tokennextflow']
        print("Token",user_token)

        # gerakin flow dari requester ke staff
        prosesApproval(comment, user_token, processID)

        # masukin ke database bersama dengan record id dan process id nya
        data_db = editStatusDatabase(recordID, processID)

        # return berupa id dan statusnya
        return str(data_db), 200

# fungsi untuk menyerahkan record dan gerakin flow ke requester
def submitRecord(recordID, user_token):
    #data template untuk ngesubmit record
        record_instance = {
            "data" : {
                "form_data": {
                    "pvRequester" : "kaz_lr@makersinstitute.id",
                    "pvSupervisor" : "smn_lr@makersinstitute.id"
                },
                "comment" : "Initiated aja"
            }
        }
        request_data = json.dumps(record_instance)

        #submit ke nextflow untuk dapetin process_id tiap pesanan masuk/flow
        header = {
            "Content-Type": "application/json",
            "authorization":"Bearer %s" % user_token
            }
        r = requests.post(
                (os.getenv("BASE_URL_RECORD")) + "/" + recordID +"/submit", 
                data=request_data, 
                headers=header
            )

        result = json.loads(r.text)
        return result

# fungsi untuk gerakin flow dari requester ke supervisor
def submitToSupervisor(comment, user_token, processID):

    def recursive():
        # get task id and pVApprover name
        result = getTasklist(user_token, processID, 'Requester')

        print("loading...")

        if result['data'] is None or len(result['data']) == 0:
            recursive()
        else:
            supervisor_email = result['data'][0]['form_data']['pvSupervisor']
            task_id = result['data'][0]['id']

            #gerakin flow ke supervisor dari requester
            submit_data = {
                "data" : {
                    "form_data": {
                        "pvSupervisor" : supervisor_email
                    },
                    "comment" : comment
                }
            }

            header = {
                "Content-Type": "application/json",
                "authorization": "Bearer %s" % user_token
                }
            # r_post = requests.post(str(os.getenv("BASE_URL_TASK")) + "/" + task_id +"/submit", data=str(json.dumps(submit_data)), headers=str(header))
            r_post = requests.post(os.getenv("BASE_URL_TASK") + "/" + task_id +"/submit",data=json.dumps(submit_data), headers=header)
            result = json.loads(r_post.text)

            return result['data']

    recursive()
    return "OK"

# fungsi untuk gerakin flow dari supervisor ke decision approval
# fungsi untuk memproses leave request (reject/approve)
def prosesApproval(comment, user_token, processID):

    def recursive():
        # get task id and pVApprover name
        query = "folder=app:task:all&filter[name]=Supervisor&filter[state]=active&filter[definition_id]=%s&filter[process_id]=%s" % (os.getenv("DEFINITION_ID"), processID)
        url = os.getenv("BASE_URL_TASK")+"?"+quote(query, safe="&=")
        r = requests.get(url, headers={
            "Content-Type": "application/json", 
            "authorization":"Bearer %s" % user_token
            })
        result = json.loads(r.text)

        print("loading...")

        if result['data'] is None or len(result['data']) == 0:
            recursive()
        else:
            # manager_email = result['data'][0]['form_data']['pvSupervisor']
            task_id = result['data'][0]['id']

            #gerakin flow ke manager dari requester
            submit_data = {
                "data" : {
                    "form_data": {
                        "pvAction" : "Approved"
                    },
                    "comment" : comment
                }
            }

            header = {
                "Content-Type": "application/json",
                "authorization":"Bearer %s" % user_token
                }
            r_post = requests.post(os.getenv("BASE_URL_TASK") + "/" + task_id +"/submit",data=json.dumps(submit_data), headers=header)
            result = json.loads(r_post.text)

            return result['data']
    
    recursive()
    return "OK"

# fungsi untuk memasukan data ke db
def submitToDatabase(recordID, processID):
    
    token = request.json['staff_id']
    staffID = decodeStaffID(token)

    comment = request.json['comment']
    startDate = request.json['start_date']
    endDate = request.json['end_date']
    leaveType = request.json['leave_type']
    submissionDate = request.json['submission_date']

    cursorSubmit = connection.cursor()
    cursorSubmit.execute("rollback")
    cursorSubmit.execute("select * from set_leave_staff(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(startDate, endDate, leaveType, comment, submissionDate, 'Pending','true','false',recordID,processID,staffID))
    connection.commit()
    print("Process ID: ",processID)

    return "Submited", 200

# fungsi untuk mengedit status di db
def editStatusDatabase(recordID, processID):
    
    leaveID = request.json['lid']
    comment = request.json['comment']
    leaveAction = request.json['leaveAction']
    approvalDate = request.json['approval_date']

    cursorEdit = connection.cursor()
    cursorEdit.execute("rollback")
    cursorEdit.execute("update leave_detail set status=%s, read_staff=%s where id=%s",(leaveAction, 'false', leaveID))
    connection.commit()
    print("Process ID Edit: ",processID)

    return "Editted", 200

# fungsi mendapatkan task list di supervisor/ 
@app.route('/nextflow/supervisor/tasklist', methods=['POST'])
def getTasklistSupervisor():
    if request.method == 'POST':

        token = request.json['staff_id']
        staffID = decodeStaffID(token)

        cursorData = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursorData.execute("Select * from get_data_employee(%s)", (int(staffID),))

        data = []
        for row in cursorData.fetchall():
            data.append(dict(row))

        user_token = data[0]['tokennextflow']
        # staff_name = data[0]['staff_name']

        cursorDataLR = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursorDataLR.execute("rollback")
        cursorDataLR.execute("select * from get_tasklist_supervisor()")

        dataLeaveDetail = []
        for rows in cursorDataLR.fetchall():
            viewData = dict(rows)
            idgettasklist = viewData['id_gettasklist']
            staff_id = viewData['staffid']
            process_id = viewData['processid']
            record_id = viewData['recordid']
            staff_name = viewData['staffname']
            sdates = viewData['startdate']
            edates = viewData['enddate']
            leaveType = viewData['leavename']
            sub_date = viewData['submissiondate']

            tasklistSupervisor(user_token, process_id)

            leave_detail_json = {
                "id": idgettasklist,
                "process_id": process_id,
                "record_id": record_id,
                "staff_id": staff_id,
                "staff_name": staff_name,
                "sdate": sdates,
                "edate": edates,
                "leave_type": leaveType,
                "submission_date": sub_date
            }

            dataLeaveDetail.append(leave_detail_json)

        return jsonify(dataLeaveDetail), 200
        # return "Oke"

#fungsi 
@app.route('/nextflow/staff/tasklist', methods=['POST'])
def getTasklistStaff():
    if request.method == 'POST':

        token = request.json['staff_id']
        staffID = decodeStaffID(token)

        cursorData = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursorData.execute("Select * from get_data_employee(%s)", (int(staffID),))

        data = []
        for row in cursorData.fetchall():
            data.append(dict(row))

        user_token = data[0]['tokennextflow']
        # staff_name = data[0]['staff_name']

        cursorDataLR = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursorDataLR.execute("rollback")
        cursorDataLR.execute("select * from get_tasklist_staff()")

        dataLeaveDetail = []
        for rows in cursorDataLR.fetchall():
            viewData = dict(rows)
            idgettasklist = viewData['id_gettasklist']
            staff_id = viewData['staffid']
            process_id = viewData['processid']
            record_id = viewData['recordid']
            staff_name = viewData['staffname']
            sdates = viewData['startdate']
            edates = viewData['enddate']
            leaveType = viewData['leavename']
            sub_date = viewData['submissiondate']

            query = "folder=app:task:all&filter[name]=Requester&filter[state]=active&filter[definition_id]=%s&filter[process_id]=%s" % (os.getenv("DEFINITION_ID"), processID)
            url = os.getenv("BASE_URL_TASK")+"?"+quote(query, safe="&=")

            r = requests.get(url, headers={
                "Content-Type": "application/json", 
                "authorization":"Bearer %s" % user_token
                })
            result = json.loads(r.text)

            leave_detail_json = {
                "id": idgettasklist,
                "process_id": process_id,
                "record_id": record_id,
                "staff_id": staff_id,
                "staff_name": staff_name,
                "sdate": sdates,
                "edate": edates,
                "leave_type": leaveType,
                "submission_date": sub_date
            }

            dataLeaveDetail.append(leave_detail_json)

        return jsonify(dataLeaveDetail), 200
