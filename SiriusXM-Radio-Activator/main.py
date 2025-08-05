
import requests
import uuid
from flask import Flask, render_template, request, jsonify, session
import threading
import time

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Global variables to track progress
activation_progress = []
activation_status = "idle"

def log_progress(message):
    global activation_progress
    activation_progress.append(message)
    print(message)

def appconfig():
    try:
        response = requests.post(
            url="https://dealerapp.siriusxm.com/authService/100000002/appconfig",
            headers={
                "X-Kony-Integrity":
                "GWSUSEVMJK;FEC9AA232EC59BE8A39F0FAE1B71300216E906B85F40CA2B1C5C7A59F85B17A4",
                "X-HTTP-Method-Override": "GET",
                "X-Voltmx-App-Key": "67cfe0220c41a54cb4e768723ad56b41",
                "Accept": "*/*",
                "X-Voltmx-App-Secret": "c086fca8646a72cf391f8ae9f15e5331",
                "Accept-Language": "en-us",
                "Accept-Encoding": "br, gzip, deflate",
                "User-Agent": "SiriusXM%20Dealer/3.1.0 CFNetwork/1568.200.51 Darwin/24.1.0",
            },
        )
        log_progress("✓ App config completed")
    except requests.exceptions.RequestException:
        log_progress("✗ App config failed")

def login():
    try:
        response = requests.post(
            url="https://dealerapp.siriusxm.com/authService/100000002/login",
            headers={
                "X-Voltmx-Platform-Type": "ios",
                "Accept": "application/json",
                "X-Voltmx-App-Secret": "c086fca8646a72cf391f8ae9f15e5331",
                "Accept-Language": "en-us",
                "X-Voltmx-SDK-Type": "js",
                "Accept-Encoding": "br, gzip, deflate",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "SiriusXM%20Dealer/3.1.0 CFNetwork/1568.200.51 Darwin/24.1.0",
                "X-Voltmx-SDK-Version": "9.5.36",
                "X-Voltmx-App-Key": "67cfe0220c41a54cb4e768723ad56b41",
            },
        )
        token = response.json().get('claims_token').get('value')
        log_progress("✓ Login completed")
        return token
    except requests.exceptions.RequestException:
        log_progress("✗ Login failed")
        return None

def versionControl(auth_token, uuid4):
    try:
        response = requests.post(
            url="https://dealerapp.siriusxm.com/services/DealerAppService7/VersionControl",
            headers={
                "Accept": "*/*",
                "X-Voltmx-API-Version": "1.0",
                "X-Voltmx-DeviceId": uuid4,
                "Accept-Language": "en-us",
                "Accept-Encoding": "br, gzip, deflate",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "SiriusXM%20Dealer/3.1.0 CFNetwork/1568.200.51 Darwin/24.1.0",
                "X-Voltmx-Authorization": auth_token,
            },
            data={
                "deviceCategory": "iPhone",
                "appver": "3.1.0",
                "deviceLocale": "en_US",
                "deviceModel": "iPhone%206%20Plus",
                "deviceVersion": "12.5.7",
                "deviceType": "",
            },
        )
        log_progress("✓ Version control completed")
    except requests.exceptions.RequestException:
        log_progress("✗ Version control failed")

def getProperties(auth_token, uuid4):
    try:
        response = requests.post(
            url="https://dealerapp.siriusxm.com/services/DealerAppService7/getProperties",
            headers={
                "Accept": "*/*",
                "X-Voltmx-API-Version": "1.0",
                "X-Voltmx-DeviceId": uuid4,
                "Accept-Language": "en-us",
                "Accept-Encoding": "br, gzip, deflate",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "SiriusXM%20Dealer/3.1.0 CFNetwork/1568.200.51 Darwin/24.1.0",
                "X-Voltmx-Authorization": auth_token,
            },
        )
        log_progress("✓ Properties retrieved")
    except requests.exceptions.RequestException:
        log_progress("✗ Get properties failed")

def update_1(auth_token, uuid4, radio_id):
    try:
        response = requests.post(
            url="https://dealerapp.siriusxm.com/services/USUpdateDeviceSATRefresh/updateDeviceSATRefreshWithPriority",
            headers={
                "Accept": "*/*",
                "X-Voltmx-API-Version": "1.0",
                "X-Voltmx-DeviceId": uuid4,
                "Accept-Language": "en-us",
                "Accept-Encoding": "br, gzip, deflate",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "SiriusXM%20Dealer/3.1.0 CFNetwork/1568.200.51 Darwin/24.1.0",
                "X-Voltmx-Authorization": auth_token,
            },
            data={
                "deviceId": radio_id,
                "appVersion": "3.1.0",
                "lng": "-86.210313195",
                "deviceID": uuid4,
                "provisionPriority": "2",
                "provisionType": "activate",
                "lat": "32.37436705",
            },
        )
        seq = response.json().get('seqValue')
        log_progress(f"✓ Update 1 completed - Seq: {seq}")
        return seq
    except requests.exceptions.RequestException:
        log_progress("✗ Update 1 failed")
        return None

def getCRM(auth_token, uuid4, radio_id, seq):
    try:
        response = requests.post(
            url="https://dealerapp.siriusxm.com/services/DemoConsumptionRules/GetCRMAccountPlanInformation",
            headers={
                "Accept": "*/*",
                "X-Voltmx-API-Version": "1.0",
                "X-Voltmx-DeviceId": uuid4,
                "Accept-Language": "en-us",
                "Accept-Encoding": "br, gzip, deflate",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "SiriusXM%20Dealer/3.1.0 CFNetwork/1568.200.51 Darwin/24.1.0",
                "X-Voltmx-Authorization": auth_token,
            },
            data={
                "seqVal": seq,
                "deviceId": radio_id,
            },
        )
        log_progress("✓ CRM information retrieved")
    except requests.exceptions.RequestException:
        log_progress("✗ Get CRM failed")

def dbUpdate(auth_token, uuid4, radio_id, seq):
    try:
        response = requests.post(
            url="https://dealerapp.siriusxm.com/services/DBSuccessUpdate/DBUpdateForGoogle",
            headers={
                "Accept": "*/*",
                "X-Voltmx-API-Version": "1.0",
                "X-Voltmx-DeviceId": uuid4,
                "Accept-Language": "en-us",
                "Accept-Encoding": "br, gzip, deflate",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "SiriusXM%20Dealer/3.1.0 CFNetwork/1568.200.51 Darwin/24.1.0",
                "X-Voltmx-Authorization": auth_token,
            },
            data={
                "OM_ELIGIBILITY_STATUS": "Eligible",
                "appVersion": "3.1.0",
                "flag": "failure",
                "Radio_ID": radio_id,
                "deviceID": uuid4,
                "G_PLACES_REQUEST": "",
                "OS_Version": "iPhone 12.5.7",
                "G_PLACES_RESPONSE": "",
                "Confirmation_Status": "SUCCESS",
                "seqVal": seq,
            },
        )
        log_progress("✓ Database updated")
    except requests.exceptions.RequestException:
        log_progress("✗ Database update failed")

def blocklist(auth_token, uuid4):
    try:
        response = requests.post(
            url="https://dealerapp.siriusxm.com/services/USBlockListDevice/BlockListDevice",
            headers={
                "Accept": "*/*",
                "X-Voltmx-API-Version": "1.0",
                "X-Voltmx-DeviceId": uuid4,
                "Accept-Language": "en-us",
                "Accept-Encoding": "br, gzip, deflate",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "SiriusXM%20Dealer/3.1.0 CFNetwork/1568.200.51 Darwin/24.1.0",
                "X-Voltmx-Authorization": auth_token,
            },
            data={
                "deviceId": uuid4,
            },
        )
        log_progress("✓ Device blocklist checked")
    except requests.exceptions.RequestException:
        log_progress("✗ Blocklist check failed")

def oracle():
    try:
        response = requests.post(
            url="https://oemremarketing.custhelp.com/cgi-bin/oemremarketing.cfg/php/custom/src/oracle/program_status.php",
            params={
                "google_addr": "395 EASTERN BLVD, MONTGOMERY, AL 36117, USA",
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "*/*",
                "User-Agent": "SiriusXM%20Dealer/3.1.0 CFNetwork/1568.200.51 Darwin/24.1.0",
                "Accept-Language": "en-us",
                "Accept-Encoding": "br, gzip, deflate",
            },
        )
        log_progress("✓ Oracle check completed")
    except requests.exceptions.RequestException:
        log_progress("✗ Oracle check failed")

def createAccount(auth_token, uuid4, radio_id, seq):
    try:
        response = requests.post(
            url="https://dealerapp.siriusxm.com/services/DealerAppService3/CreateAccount",
            headers={
                "Accept": "*/*",
                "X-Voltmx-API-Version": "1.0",
                "X-Voltmx-DeviceId": uuid4,
                "Accept-Language": "en-us",
                "Accept-Encoding": "br, gzip, deflate",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "SiriusXM%20Dealer/3.1.0 CFNetwork/1568.200.51 Darwin/24.1.0",
                "X-Voltmx-Authorization": auth_token,
            },
            data={
                "seqVal": seq,
                "deviceId": radio_id,
                "oracleCXFailed": "1",
                "appVersion": "3.1.0",
            },
        )
        result = response.json()
        if 'SUCCESS' in str(result):
            log_progress("✓ Account created successfully")
            return True
        else:
            log_progress("✗ Account creation failed")
            return False
    except requests.exceptions.RequestException:
        log_progress("✗ Create account failed")
        return False

def update_2(auth_token, uuid4, radio_id):
    try:
        response = requests.post(
            url="https://dealerapp.siriusxm.com/services/USUpdateDeviceRefreshForCC/updateDeviceSATRefreshWithPriority",
            headers={
                "Accept": "*/*",
                "X-Voltmx-API-Version": "1.0",
                "X-Voltmx-DeviceId": uuid4,
                "Accept-Language": "en-us",
                "Accept-Encoding": "br, gzip, deflate",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "SiriusXM%20Dealer/3.1.0 CFNetwork/1568.200.51 Darwin/24.1.0",
                "X-Voltmx-Authorization": auth_token,
            },
            data={
                "deviceId": radio_id,
                "provisionPriority": "2",
                "appVersion": "3.1.0",
                "device_Type": "iPhone iPhone 6 Plus",
                "deviceID": uuid4,
                "os_Version": "iPhone 12.5.7",
                "provisionType": "activate",
            },
        )
        result = response.json()
        if 'SUCCESS' in str(result):
            log_progress("✓ Final update completed successfully")
            return True
        else:
            log_progress("✗ Final update failed")
            return False
    except requests.exceptions.RequestException:
        log_progress("✗ Update 2 failed")
        return False

def run_activation(radio_id):
    global activation_status, activation_progress
    activation_status = "running"
    activation_progress = []
    
    session_requests = requests.Session()
    radio_id = radio_id.upper()
    uuid4 = str(uuid.uuid4())
    
    log_progress(f"Starting activation for Radio ID: {radio_id}")
    
    appconfig()
    auth_token = login()
    if not auth_token:
        activation_status = "failed"
        return
    
    versionControl(auth_token, uuid4)
    getProperties(auth_token, uuid4)
    seq = update_1(auth_token, uuid4, radio_id)
    if not seq:
        activation_status = "failed"
        return
    
    getCRM(auth_token, uuid4, radio_id, seq)
    dbUpdate(auth_token, uuid4, radio_id, seq)
    blocklist(auth_token, uuid4)
    oracle()
    
    account_success = createAccount(auth_token, uuid4, radio_id, seq)
    update_success = update_2(auth_token, uuid4, radio_id)
    
    if account_success and update_success:
        activation_status = "success"
        log_progress("🎉 Activation completed successfully!")
    else:
        activation_status = "failed"
        log_progress("❌ Activation failed")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/activate', methods=['POST'])
def activate():
    global activation_status
    if activation_status == "running":
        return jsonify({"error": "Activation already in progress"}), 400
    
    radio_id = request.json.get('radio_id', '').strip()
    if not radio_id:
        return jsonify({"error": "Radio ID is required"}), 400
    
    # Start activation in a separate thread
    thread = threading.Thread(target=run_activation, args=(radio_id,))
    thread.start()
    
    return jsonify({"message": "Activation started"})

@app.route('/status')
def status():
    global activation_status, activation_progress
    return jsonify({
        "status": activation_status,
        "progress": activation_progress
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
