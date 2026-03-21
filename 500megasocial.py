from flask import Flask, request, jsonify
import requests
import base64
import os

app = Flask(__name__)

# إعدادات CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

def redeem_social_gift(email, password):
    try:
        # تجهيز الـ Auth
        code = f"{email}:{password}"
        auth_base64 = base64.b64encode(code.encode("ascii")).decode("ascii")
        xauth = f"Basic {auth_base64}"

        # 1. تسجيل الدخول
        login_url = "https://mab.etisalat.com.eg:11003/Saytar/rest/authentication/loginWithPlan"
        login_headers = {
            "applicationVersion": "2",
            "applicationName": "MAB",
            "Accept": "text/xml",
            "Authorization": xauth,
            "Content-Type": "text/xml; charset=UTF-8",
            "User-Agent": "okhttp/5.0.0-alpha.11"
        }
        login_data = "<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><loginRequest><platform>Android</platform></loginRequest>"
        
        login_res = requests.post(login_url, headers=login_headers, data=login_data, timeout=15)

        if "true" in login_res.text:
            # جلب التوكن والكوكيز من الـ Headers
            cookie = login_res.headers.get("Set-Cookie", "").split(";")[0]
            bearer = login_res.headers.get("auth", "")
            
            # جلب رقم الهاتف من الرد (MSISDN) لضمان الدقة
            import xml.etree.ElementTree as ET
            root = ET.fromstring(login_res.text)
            msisdn = root.find("dial").text

            # 2. طلب الهدية
            sub_url = "https://mab.etisalat.com.eg:11003/Saytar/rest/servicemanagement/submitOrderV2"
            sub_data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><submitOrderRequest><msisdn>{msisdn}</msisdn><operation>REDEEM</operation><productName>DOWNLOAD_GIFT_1_SOCIAL_UNITS</productName></submitOrderRequest>"
            
            sub_headers = {
                'applicationVersion': '2',
                'applicationName': 'MAB',
                'Accept': 'text/xml',
                'Cookie': cookie,
                'auth': f"Bearer {bearer}",
                'Content-Type': 'text/xml; charset=UTF-8',
                'User-Agent': 'okhttp/5.0.0-alpha.11'
            }

            sub_res = requests.post(sub_url, headers=sub_headers, data=sub_data, timeout=15)

            if "true" in sub_res.text:
                return {"status": "success", "message": "تم تفعيل الـ 500 ميجا سوشيال بنجاح ✅"}
            else:
                return {"status": "error", "message": "العرض غير متاح حالياً أو تم استخدامه مسبقاً ⚠️"}
        else:
            return {"status": "error", "message": "الإيميل أو كلمة السر غير صحيحة ❌"}

    except Exception as e:
        return {"status": "error", "message": "حدث خطأ في الاتصال بسيرفر اتصالات"}

@app.route('/etisalat-social', methods=['POST', 'OPTIONS'])
def social_route():
    if request.method == 'OPTIONS': return jsonify({"status": "ok"}), 200
    
    # الإيميل والباسورد من الفورم
    email = request.form.get('phone') 
    password = request.form.get('password')

    if not email or not password:
        return jsonify({"status": "error", "message": "برجاء إدخال كافة البيانات"}), 400
        
    result = redeem_social_gift(email, password)
    return jsonify(result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)