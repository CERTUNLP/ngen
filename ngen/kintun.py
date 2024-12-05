from constance import config
import requests
import json
from time import sleep

def retest_event_kintun(event, mapping_to, ports=[]):
    """
    Celery task to retest an event.
    """

    KINTUN_HOST = f"http://{config.KINTUN_HOST}/api"

    try:
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'x-api-key': config.KINTUN_APIKEY
        }
        
        if (mapping_to):
            data = {
                "vuln" : mapping_to,
                "network" : event.address_value,
                "ports" : [],
                "params" : {"feed":"test", "send-nmap-report":0},
                "outputs" : [],
                "report_to" : ""
            }
            evidence = []

            r = requests.post(KINTUN_HOST+'/scan', headers=headers, json=data)

            id = r.json()['_id']
            kintun_url = KINTUN_HOST+'/scan/'+id

            response = requests.get(kintun_url, headers=headers)
    
            while (response.json()['status'] == 'started'):
                sleep(1)
                response = requests.get(kintun_url, headers=headers)

            result = response.json()['result']
            
            if result:
                vulnerable = len(result['vulnerables']) > 0
                evidence = " ".join([vuln['evidence'] for vuln in (result['vulnerables'] if vulnerable else result['no_vulnerables'])])
            else:
                vulnerable = False
                evidence = "kintun_error"
                
            return {"vulnerable": vulnerable, "evidence": evidence, "_id": kintun_url, "vuln_type": response.json()['vulnerability']}
        return {"error": "No vulnerability found"}

    except Exception as e:
        return {"error": str(e)}