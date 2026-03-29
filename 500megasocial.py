import base64
import requests
import xml.etree.ElementTree as ET
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/etisalat-social', methods=['POST'])
def activate_gift():
    # سحب البيانات من الفورم في صفحة الويب
    email = request.form.get('phone') # ده اسم الحقل في الـ HTML عندك
    password = request.form.get('password')

    if not email or not password:
        return jsonify({"status": "error", "message": "❌ برجاء إدخال البيانات كاملة"})

    # تحضير التوكن الأساسي (Base64)
    auth_str = f"{email}:{password}"
    token = base64.b64encode(auth_str.encode()).decode()

    # الهيدرز المحدثة (المود الجديد)
    headers = {
        'Host': "mab.etisalat.com.eg:11003",
        'User-Agent': "okhttp/5.0.0-alpha.11",
        'Accept': "text/xml",
        'Content-Type': "text/xml; charset=UTF-8",
        'applicationVersion': "2",
        'applicationName': "MAB",
        'Authorization': f"Basic {token}",
        'Language': "ar",
        'APP-BuildNumber': "10650",
        'APP-Version': "33.1.0",
        'OS-Type': "Android",
        'OS-Version': "13",
        'APP-STORE': "GOOGLE"
    }

    # 1. طلب تسجيل الدخول لسحب رقم الهاتف (Dial)
    login_url = "https://mab.etisalat.com.eg:11003/Saytar/rest/authentication/loginWithPlan"
    login_xml = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
    <loginRequest>
        <deviceId></deviceId><firstLoginAttempt>false</firstLoginAttempt>
        <modelType></modelType><osVersion></osVersion>
        <platform>Android</platform><udid></udid>
    </loginRequest>"""

    try:
        r_login = requests.post(login_url, data=login_xml, headers=headers, timeout=15)
        
        # تحليل الـ XML لسحب الرقم
        root = ET.fromstring(r_login.text)
        dial_element = root.find("dial")
        
        if dial_element is None:
            return jsonify({"status": "error", "message": "❌ الإيميل أو كلمة السر غلط"})
        
        number = dial_element.text

        # 2. طلب تفعيل العرض الديناميكي (المود الجديد)
        submit_url = "https://mab.etisalat.com.eg:11003/Saytar/rest/zero11/submitOrder"
        submit_payload = f"""<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
        <submitOrderRequest>
            <mabOperation></mabOperation>
            <msisdn>{number}</msisdn>
            <operation>ACTIVATE</operation>
            <parameters>
                <parameter>
                    <name>GIFT_FULLFILMENT_PARAMETERS</name>
                    <value>Offer_ID:23283;isRTIM:Y</value>
                </parameter>
            </parameters>
            <productName>DYNAMIC_OFFERING_PAY_AND_GET_POOL_BONUS</productName>
        </submitOrderRequest>"""

        response = requests.post(submit_url, data=submit_payload, headers=headers, timeout=15)
        
        # فحص النتيجة النهائية
        if "true" in response.text.lower():
            return jsonify({"status": "success", "message": "✅ تم تفعيل الـ 500 وحدة بنجاح ✅"})
        else:
            return jsonify({"status": "error", "message": "⚠️ العرض غير متاح حالياً أو مفعل مسبقاً"})

    except Exception as e:
        return jsonify({"status": "error", "message": "❌ حدث خطأ في الاتصال بالسيرفر"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)