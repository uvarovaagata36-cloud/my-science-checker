from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time
import os

app = Flask(__name__)

# РАЗРЕШАЕМ ВСЕ ЗАПРОСЫ С ЛЮБЫХ САЙТОВ
CORS(app, resources={r"/*": {"origins": "*"}})

WEBHOOK_URL = "https://api.apimonster.ru/webhooks/153486/33962/11/b41f3f6799dab033147d65211151aee2/"

@app.route('/')
def home():
    return '✅ Сервер работает!'

@app.route('/check', methods=['GET', 'POST'])
def check_article():
    # Если пришёл GET-запрос — отвечаем, что всё ок
    if request.method == 'GET':
        return jsonify({"status": "ok", "message": "Сервер готов принимать POST-запросы"}), 200
    
    try:
        data = request.get_json()
        link = data.get('link')
        
        if not link:
            return jsonify({"error": "Ссылка не указана"}), 400
        
        response = requests.post(WEBHOOK_URL, json={"link": link})
        webhook_data = response.json()
        webhook_id = webhook_data.get('webhook_id')
        
        if not webhook_id:
            return jsonify({"error": "Не удалось отправить в ApiMonster"}), 500
        
        time.sleep(25)
        
        result_url = f"https://api.apimonster.ru/webhooks/{webhook_id}/result"
        result_response = requests.get(result_url, timeout=10)
        
        if result_response.status_code == 200:
            return jsonify({
                "status": "success",
                "result": result_response.json()
            })
        else:
            return jsonify({
                "status": "processing",
                "message": "Нейросеть ещё думает"
            })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
