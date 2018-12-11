from src.utils.JWTEncoderDecoder import *

# fungsi untuk menggerakan/menjalankan form leave request dari requester ke supervisor
@app.route('/nextflow/supervisor/submit', methods = ['POST'])
def submitToSupervisor(TokenJwt):
    if request.method == 'POST':

        req_sid = request.json['staff_id']
        staffId = decodeStaffID(TokenJwt)
        
        req_comment = request.json['comment']
        
        curData = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        curData.execute("rollback")
        curData.execute("Select * from get_data_employee(%s)", (int(staffId),))

        data = []
        for row in curData.fetchall():
            data.append(dict(row))

        connection.commit()
        user_token = data[0]['tokenstaff']

        record_instance = {
            "data": {
                "definition": {
                    "id" : os.getenv('DEFINITION_ID')
                }
            }
        }

        #submit ke nextflow unutk dapetin record_id tiap pesanan masuk/flow
        header = {
            "Content-Type": "application/json", 
            "authorization":"Bearer %s" % user_token
            }
        r = requests.post((os.getenv("BASE_URL_RECORD")), data=json.dumps(record_instance), headers=header)

        # result from create record
        result = json.loads(r.text)
        record_id = result['data']['id']

        # submit si flow pake record_id dan token dan process id
        process_instance = submit_record(record_id, user_token)
        process_id = process_instance['data']['process_id']

        # gerakin flow dari requester ke manager
        submit_to_manager(req_comment, user_token, process_id)

        # masukin ke database bersama dengan record id dan process id nya
        data_db = submit_to_database(record_id, process_id)

        # return berupa id dan statusnya
        return str(data_db), 200

# funsgi untul meng submit to staff
@app.route('nextflow/supervisor/approval', methods = ['POST'])
def supervisorApproval():
    if request.method == 'POST':

        token_jwt = request.json['staff_id']
        decode = jwt.decode(token_jwt, secret_key, algorithms=['HS256'])
        staff_id = decode['sid']

        req_record_id = request.json['rid']
        req_process_id = request.json['pid']
        req_comment = request.json['comment']

        print("RID",req_record_id)
        print("PID",req_process_id)
        print("SID",req_sid)
        
        curData = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        curData.execute("rollback")
        curData.execute("Select * from getDataEmployee(%s)", (int(req_sid),))

        data = []
        for row in curData.fetchall():
            data.append(dict(row))

        user_token = data[0]['tokenstaff']
        print("Token",user_token)

        # gerakin flow dari requester ke staff
        submit_to_staff(req_comment, user_token, req_process_id)

        # masukin ke database bersama dengan record id dan process id nya
        data_db = edit_status_database(req_record_id, req_process_id)

        # return berupa id dan statusnya
        return str(data_db), 200

# fungsi untuk submit record dan gerakin flow ke requester
def submit_record(record_id, user_token):
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
        r = requests.post((os.getenv("BASE_URL_RECORD")) + "/" + record_id +"/submit", data=request_data, headers=header)

        result = json.loads(r.text)
        return result

# fungsi untuk gerakin flow dari requester ke supervisor
def submit_to_manager(req_comment, user_token, process_id):

    def recursive():
        # get task id and pVApprover name
        query = "folder=app:task:all&filter[name]=Requester&filter[state]=active&filter[definition_id]=%s&filter[process_id]=%s" % (os.getenv("DEFINITION_ID"), process_id)
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
            manager_email = result['data'][0]['form_data']['pvSupervisor']
            task_id = result['data'][0]['id']

            #gerakin flow ke manager dari requester
            submit_data = {
                "data" : {
                    "form_data": {
                        "pvSupervisor" : manager_email
                    },
                    "comment" : req_comment
                }
            }

            header = {
                "Content-Type": "application/json",
                "authorization":"Bearer %s" % user_token
                }
            # r_post = requests.post(str(os.getenv("BASE_URL_TASK")) + "/" + task_id +"/submit", data=str(json.dumps(submit_data)), headers=str(header))
            r_post = requests.post(os.getenv("BASE_URL_TASK") + "/" + task_id +"/submit",data=json.dumps(submit_data), headers=header)
            result = json.loads(r_post.text)

            return result['data']

    recursive()
    return "OK"

# fungsi untuk gerakin flow dari supervisor ke staff
def submit_to_staff(req_comment, user_token, process_id):

    def recursive():
        # get task id and pVApprover name
        query = "folder=app:task:all&filter[name]=Supervisor&filter[state]=active&filter[definition_id]=%s&filter[process_id]=%s" % (os.getenv("DEFINITION_ID"), process_id)
        url = os.getenv("BASE_URL_TASK")+"?"+quote(query, safe="&=")
        r = requests.get(url, headers={"Content-Type": "application/json", "authorization":"Bearer %s" % user_token})
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
                    "comment" : req_comment
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
def submit_to_database(record_id, process_id):
    
    sid = request.json['sid']
    decode = jwt.decode(sid, secret_key, algorithms=['HS256'])
    req_sid = decode['sid']

    req_comment = request.json['comment']
    req_start_date = request.json['sdate']
    req_end_date = request.json['edate']
    req_leave_type = request.json['leave_type']
    req_submission_date = request.json['submission_date']

    curSubmit = con.cursor()
    curSubmit.execute("rollback")
    curSubmit.execute("select * from setLeaveStaff(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(req_start_date, req_end_date, req_leave_type, req_comment, req_submission_date, 'Pending','true','false',record_id,process_id,req_sid))
    con.commit()
    print("Process ID: ",process_id)

    return "Submited", 200

# fungsi untuk mengedit status di db
def edit_status_database(record_id, process_id):
    
    req_lid = request.json['lid']
    req_comment = request.json['comment']
    req_leave_action = request.json['leaveAction']
    req_approval_date = request.json['approval_date']

    curEdit = con.cursor()
    curEdit.execute("rollback")
    curEdit.execute("update leave_detail set status=%s, read_staff=%s where id=%s",(req_leave_action, 'false', req_lid))
    con.commit()
    print("Process ID Edit: ",process_id)

    return "Editted", 200

# fungsi mendapatkan task list di supervisor/ 
@app.route('/nextflow/tasklist/supervisor', methods=['POST'])
def getTasklistSupervisor():
    if request.method == 'POST':
        sid = request.json['sid']
        decode = jwt.decode(sid, secret_key, algorithms=['HS256'])
        req_sid = decode['sid']

        curData = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        curData.execute("Select * from get_data_employee(%s)", (int(req_sid),))

        data = []
        for row in curData.fetchall():
            data.append(dict(row))

        user_token = data[0]['tokenstaff']
        # staff_name = data[0]['staff_name']

        curDataLR = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        curDataLR.execute("rollback")
        curDataLR.execute("select * from getTasklistSupervisor()")

        dataLeaveDetail = []
        for rows in curDataLR.fetchall():
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

            query = "folder=app:task:all&filter[name]=Supervisor&filter[state]=active&filter[definition_id]=%s&filter[process_id]=%s" % (os.getenv("DEFINITION_ID"), process_id)
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
        # return "Oke"

@app.route('/get-tasklist-staff', methods=['POST'])
def getTasklistStaff():

    if request.method == 'POST':
        sid = request.json['sid']
        decode = jwt.decode(sid, secret_key, algorithms=['HS256'])
        req_sid = decode['sid']

        curData = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        curData.execute("Select * from get_data_employee(%s)", (int(req_sid),))

        data = []
        for row in curData.fetchall():
            data.append(dict(row))

        user_token = data[0]['tokenstaff']
        # staff_name = data[0]['staff_name']

        curDataLR = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        curDataLR.execute("rollback")
        curDataLR.execute("select * from get_tasklist_staff()")

        dataLeaveDetail = []
        for rows in curDataLR.fetchall():
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

            query = "folder=app:task:all&filter[name]=Requester&filter[state]=active&filter[definition_id]=%s&filter[process_id]=%s" % (os.getenv("DEFINITION_ID"), process_id)
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
