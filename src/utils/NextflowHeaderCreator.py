import os, requests, json
from requests.utils import quote

def getTasklist(user_token, process_id, filter_name):
    query = "folder=app:task:all&filter[name]=%s&filter[state]=active&filter[definition_id]=%s&filter[process_id]=%s" % (filter_name, os.getenv("DEFINITION_ID"), process_id)
    url = os.getenv("BASE_URL_TASK")+"?"+quote(query, safe="&=")

    res = requests.get(url, headers={
            "Content-Type": "application/json", 
            "authorization": "Bearer %s" % user_token
        })

    result = json.loads(res.text)
    print(os.getenv("BASE_URL_TASK"))
    return result

#submit ke nextflow untuk dapetin record_id tiap pesanan masuk/flow
def getRecordID(record_instance, user_token):
    header = {
            "Content-Type": "application/json", 
            "authorization": "Bearer %s" % user_token
        }

    r = requests.post(
            (os.getenv("BASE_URL_RECORD")), 
            data=json.dumps(record_instance), 
            headers=header
        )

    # result from create record
    result = json.loads(r.text)
    return result['data']['id']