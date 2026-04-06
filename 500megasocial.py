from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import base64
import xml.etree.ElementTree as ET

app = Flask(__name__)
CORS(app) # لكي يسمح للمتصفح بالاتصال بالسيرفر

@app.route('/etisalat-social', methods=['POST'])
def get_gift():
    try:
        # استقبال البيانات من الفورم
        email = request.form.get('phone') # تم استخدام اسم phone بناءً على كود JS الخاص بك
        password = request.form.get('password')

        if not email or not password:
            return jsonify({"status": "error", "message": "البريد أو كلمة السر ناقصة"}), 400

        # تجهيز التوكن
        tok = f"{email}:{password}"
        token = base64.b64encode(tok.encode()).decode()

        headers = {
            'Host': "mab.etisalat.com.eg:11003",
            'User-Agent': "okhttp/5.0.0-alpha.11",
            'Accept': "text/xml",
            'Content-Type': "text/xml; charset=UTF-8",
            'Authorization': f"Basic {token}",
            'Language': "ar",
            'OS-Type': "Android",
        }

        # مرحلة تسجيل الدخول لجلب الرقم
        login_url = "https://mab.etisalat.com.eg:11003/Saytar/rest/authentication/loginWithPlan"
        login_body = "<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><loginRequest><platform>Android</platform></loginRequest>"
        
        r_login = requests.post(login_url, data=login_body, headers=headers)
        
        try:
            root = ET.fromstring(r_login.text)
            number = root.find("dial").text
        except:
            return jsonify({"status": "error", "message": "خطأ في البريد أو كلمة السر"}), 401

        # مرحلة تفعيل الهدية
        gift_url = "https://mab.etisalat.com.eg:11003/Saytar/rest/servicemanagement/submitOrderV2"
        gift_body = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><submitOrderRequest><msisdn>{number}</msisdn><operation>REDEEM</operation><productName>DOWNLOAD_GIFT_1_SOCIAL_UNITS</productName></submitOrderRequest>"
        
        r_gift = requests.post(gift_url, data=gift_body, headers=headers)

        if "success" in r_gift.text.lower() or "0" in r_gift.text:
            return jsonify({"status": "success", "message": "تم طلب الهدية بنجاح! انتظر رسالة التأكيد."})
        else:
            return jsonify({"status": "error", "message": "العرض غير متاح حالياً أو تم استخدامه."})

    except Exception as e:
        return jsonify({"status": "error", "message": "حدث خطأ فني بالسيرفر"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
