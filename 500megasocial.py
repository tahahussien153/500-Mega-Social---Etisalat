import base64
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # للسماح بطلبات الويب من نطاقات مختلفة

@app.route('/etisalat-social', methods=['POST'])
def activate_gift():
    # استقبال البيانات من الفورم
    email = request.form.get('phone') # تم تسميته phone في HTML الخاص بك
    password = request.form.get('password')
    
    # استخراج الرقم من الإيميل أو استخدامه مباشرة (حسب منطقك)
    # ملاحظة: السكربت الأصلي كان يطلب الرقم والآن الويب يطلب إيميل
    # سنفترض أن المستخدم يدخل الرقم في خانة الإيميل أو أنك ستعدله
    num = email
    if "011" in num:
        num = num[1:]

    # تشفير البيانات (Base64)
    code = f"{email}:{password}"
    auth = base64.b64encode(code.encode("ascii")).decode("ascii")
    xauth = f"Basic {auth}"

    # الخطوة 1: تسجيل الدخول
    urllog = "https://mab.etisalat.com.eg:11003/Saytar/rest/authentication/loginWithPlan"
    headerslog = {
        "applicationVersion": "2", "applicationName": "MAB", "Accept": "text/xml",
        "Authorization": xauth, "APP-BuildNumber": "964", "APP-Version": "27.0.0",
        "OS-Type": "Android", "OS-Version": "12", "APP-STORE": "GOOGLE",
        "Content-Type": "text/xml; charset=UTF-8", "Host": "mab.etisalat.com.eg:11003",
        "User-Agent": "okhttp/5.0.0-alpha.11",
    }
    datalog = "<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><loginRequest><deviceId></deviceId><firstLoginAttempt>true</firstLoginAttempt><platform>Android</platform><udid></udid></loginRequest>"

    try:
        log = requests.post(urllog, headers=headerslog, data=datalog, timeout=10)
        
        if "true" in log.text:
            st = log.headers.get("Set-Cookie", "")
            ck = st.split(";")[0]
            br = log.headers.get("auth", "")

            # الخطوة 2: طلب الهدية
            urlsub = "https://mab.etisalat.com.eg:11003/Saytar/rest/servicemanagement/submitOrderV2"
            datasub = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><submitOrderRequest><mabOperation></mabOperation><msisdn>{num}</msisdn><operation>REDEEM</operation><productName>DOWNLOAD_GIFT_1_SOCIAL_UNITS</productName></submitOrderRequest>"
            
            headerssub = {
                'applicationVersion': '2', 'applicationName': 'MAB', 'Accept': 'text/xml',
                'Cookie': ck, 'auth': f"Bearer {br}", 'Content-Type': 'text/xml; charset=UTF-8',
                'Host': 'mab.etisalat.com.eg:11003', 'User-Agent': 'okhttp/5.0.0-alpha.11',
            }

            subs = requests.post(urlsub, headers=headerssub, data=datasub, timeout=10).text

            if "true" in subs:
                return jsonify({"status": "success", "message": "✅ تم تفعيل هديتك بنجاح ✅"})
            else:
                return jsonify({"status": "error", "message": "⚠️ العرض مفعل بالفعل أو غير متاح ⚠️"})
        else:
            return jsonify({"status": "error", "message": "❌ البيانات غير صحيحة ❌"})

    except Exception as e:
        return jsonify({"status": "error", "message": "⚠️ فشل الاتصال بالسيرفر ⚠️"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
