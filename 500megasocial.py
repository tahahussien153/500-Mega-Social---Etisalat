import base64
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/etisalat-social', methods=['POST'])
def activate_social():
    # سحب البيانات من صفحة الويب
    number = request.form.get('number') # الرقم الجديد
    email = request.form.get('phone')   # الإيميل
    password = request.form.get('password')

    # --- منطق السكربت الأصلي بالحرف ---
    if "011" in number:
        num = number[1:]
    else:
        num = number

    code = email + ":" + password
    base64_bytes = base64.b64encode(code.encode("ascii"))
    auth = base64_bytes.decode("ascii")
    xauth = "Basic " + auth

    urllog = "https://mab.etisalat.com.eg:11003/Saytar/rest/authentication/loginWithPlan"
    headerslog = {
        "applicationVersion": "2",
        "applicationName": "MAB",
        "Accept": "text/xml",
        "Authorization": xauth,
        "APP-BuildNumber": "964",
        "APP-Version": "27.0.0",
        "OS-Type": "Android",
        "OS-Version": "12",
        "APP-STORE": "GOOGLE",
        "Is-Corporate": "false",
        "Content-Type": "text/xml; charset=UTF-8",
        "Host": "mab.etisalat.com.eg:11003",
        "Connection": "Keep-Alive",
        "User-Agent": "okhttp/5.0.0-alpha.11",
    }

    datalog = "<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><loginRequest><deviceId></deviceId><firstLoginAttempt>true</firstLoginAttempt><modelType></modelType><osVersion></osVersion><platform>Android</platform><udid></udid></loginRequest>"
    
    try:
        log = requests.post(urllog, headers=headerslog, data=datalog, timeout=20)
        
        if "true" in log.text:
            st = log.headers["Set-Cookie"]
            ck = st.split(";")[0]
            br = log.headers["auth"]

            urlsub = "https://mab.etisalat.com.eg:11003/Saytar/rest/servicemanagement/submitOrderV2"
            # استخدام الـ Social Gift كما في كودك الشغال
            datasub = "<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><submitOrderRequest><mabOperation></mabOperation><msisdn>%s</msisdn><operation>REDEEM</operation><productName>DOWNLOAD_GIFT_1_SOCIAL_UNITS</productName></submitOrderRequest>" % (num)

            headerssub = {
                'applicationVersion': '2',
                'applicationName': 'MAB',
                'Accept': 'text/xml',
                'Cookie': ck,
                'Language': 'ar',
                'APP-BuildNumber': '10501',
                'APP-Version': '30.2.0',
                'OS-Type': 'Android',
                'OS-Version': '7.1.2',
                'APP-STORE': 'GOOGLE',
                'auth': "Bearer " + br,
                'Is-Corporate': 'false',
                'Content-Type': 'text/xml; charset=UTF-8',
                'Host': 'mab.etisalat.com.eg:11003',
                'Connection': 'Keep-Alive',
                'User-Agent': 'okhttp/5.0.0-alpha.11',
            }

            subs = requests.post(urlsub, headers=headerssub, data=datasub, timeout=20).text

            if "true" in subs:
                return jsonify({"status": "success", "message": "✅ تم تفعيل هديتك من اتصالات بنجاح ✅"})
            else:
                return jsonify({"status": "error", "message": "⚠️ البيانات غير صحيحة أو العرض متفعل بالفعل ⚠️"})
        else:
            return jsonify({"status": "error", "message": "❌ الرقم أو كلمة السر غير صحيحة ❌"})
    except:
        return jsonify({"status": "error", "message": "❌ فشل الاتصال بسيرفر اتصالات ❌"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)