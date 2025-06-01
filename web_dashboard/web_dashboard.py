#!/usr/bin/env python3

from flask import Flask, render_template_string, jsonify
import json
import os
import time
from datetime import datetime, timedelta

app = Flask(__name__)

def get_latest_status():
    """Hole den aktuellen Live-Status"""
    try:
        # Lese Live-Status (wird bei JEDEM Durchlauf geschrieben)
        if os.path.exists('live_status.json'):
            with open('live_status.json', 'r') as f:
                status = json.load(f)
            
            # Prüfe wie alt der Status ist
            timestamp = datetime.fromisoformat(status['timestamp'])
            age_minutes = (datetime.now() - timestamp).total_seconds() / 60
            
            if age_minutes < 5:  # Nur wenn weniger als 5 Minuten alt
                return {
                    'status': status['status'],  # 'green', 'red', 'gray', 'processing'
                    'message': status['message'],
                    'time': timestamp.strftime('%H:%M:%S'),
                    'camera': status.get('camera_id', 'ESP32'),
                    'image': status.get('image_file', ''),
                    'age_minutes': int(age_minutes),
                    'recognized': status.get('recognized', [])
                }
        
        # Fallback: Kein Live-Status oder zu alt
        return {
            'status': 'gray',
            'message': "💤 System nicht aktiv",
            'time': 'N/A',
            'camera': 'N/A',
            'image': 'N/A', 
            'age_minutes': 999,
            'recognized': []
        }
        
    except Exception as e:
        return {
            'status': 'red',
            'message': f"❌ Fehler: {str(e)}",
            'time': 'ERROR',
            'camera': 'ERROR',
            'image': 'ERROR',
            'age_minutes': 999,
            'recognized': []
        }

@app.route('/')
def status_lamp():
    """Einfache Status-Lampe"""
    
    html_template = """
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ESP32 Status</title>
        <style>
            * { 
                margin: 0; 
                padding: 0; 
                box-sizing: border-box; 
            }
            
            body {
                font-family: 'Arial', sans-serif;
                background: #1a1a1a;
                color: white;
                height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                overflow: hidden;
            }
            
            .status-container {
                text-align: center;
                padding: 40px;
            }
            
            .status-lamp {
                width: 300px;
                height: 300px;
                border-radius: 50%;
                margin: 0 auto 40px auto;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 4em;
                box-shadow: 0 0 50px rgba(0,0,0,0.5);
                transition: all 0.5s ease;
                position: relative;
            }
            
            .status-lamp.green {
                background: linear-gradient(45deg, #4CAF50, #66BB6A);
                box-shadow: 0 0 80px rgba(76, 175, 80, 0.6), inset 0 0 50px rgba(255,255,255,0.1);
                animation: pulse-green 2s infinite;
            }
            
            .status-lamp.red {
                background: linear-gradient(45deg, #f44336, #e57373);
                box-shadow: 0 0 80px rgba(244, 67, 54, 0.6), inset 0 0 50px rgba(255,255,255,0.1);
                animation: pulse-red 2s infinite;
            }
            
            .status-lamp.gray {
                background: linear-gradient(45deg, #757575, #9E9E9E);
                box-shadow: 0 0 40px rgba(117, 117, 117, 0.4), inset 0 0 50px rgba(255,255,255,0.1);
                animation: pulse-gray 3s infinite;
            }
            
            .status-lamp.processing {
                background: linear-gradient(45deg, #FF9800, #FFB74D);
                box-shadow: 0 0 80px rgba(255, 152, 0, 0.6), inset 0 0 50px rgba(255,255,255,0.1);
                animation: pulse-processing 1s infinite;
            }
            
            @keyframes pulse-green {
                0%, 100% { transform: scale(1); opacity: 1; }
                50% { transform: scale(1.05); opacity: 0.9; }
            }
            
            @keyframes pulse-red {
                0%, 100% { transform: scale(1); }
                25% { transform: scale(1.03); }
                75% { transform: scale(0.97); }
            }
            
            @keyframes pulse-gray {
                0%, 100% { opacity: 0.7; }
                50% { opacity: 1; }
            }
            
            @keyframes pulse-processing {
                0%, 100% { transform: scale(1); opacity: 0.8; }
                50% { transform: scale(1.1); opacity: 1; }
            }
            
            .status-message {
                font-size: 2em;
                margin-bottom: 20px;
                font-weight: bold;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            }
            
            .status-details {
                font-size: 1.2em;
                color: #ccc;
                line-height: 1.6;
                margin-bottom: 30px;
            }
            
            .status-details div {
                margin: 5px 0;
            }
            
            .refresh-info {
                position: fixed;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                background: rgba(0,0,0,0.7);
                padding: 10px 20px;
                border-radius: 20px;
                font-size: 0.9em;
                color: #ccc;
            }
            
            .time-badge {
                position: fixed;
                top: 20px;
                right: 20px;
                background: rgba(0,0,0,0.7);
                padding: 10px 20px;
                border-radius: 20px;
                font-size: 1.1em;
            }
            
            .camera-badge {
                position: fixed;
                top: 20px;
                left: 20px;
                background: rgba(0,0,0,0.7);
                padding: 10px 20px;
                border-radius: 20px;
                font-size: 1.1em;
            }
            
            .age-indicator {
                position: absolute;
                bottom: -10px;
                right: -10px;
                background: rgba(255,255,255,0.2);
                color: white;
                padding: 5px 10px;
                border-radius: 15px;
                font-size: 0.8em;
                font-weight: bold;
            }
            
            .age-indicator.fresh {
                background: rgba(76, 175, 80, 0.8);
            }
            
            .age-indicator.old {
                background: rgba(244, 67, 54, 0.8);
            }
            
            @media (max-width: 768px) {
                .status-lamp {
                    width: 250px;
                    height: 250px;
                    font-size: 3em;
                }
                
                .status-message {
                    font-size: 1.5em;
                }
                
                .status-details {
                    font-size: 1em;
                }
                
                .time-badge, .camera-badge {
                    position: static;
                    margin: 10px auto;
                    display: inline-block;
                }
            }
        </style>
    </head>
    <body>
        <div class="camera-badge">📷 {{ status.camera }}</div>
        <div class="time-badge">🕐 {{ status.time }}</div>
        
        <div class="status-container">
            <div class="status-lamp {{ status.status }}">
                {% if status.status == 'green' %}
                    ✅
                {% elif status.status == 'red' %}
                    ❌
                {% elif status.status == 'processing' %}
                    🔍
                {% else %}
                    💤
                {% endif %}
                
                <div class="age-indicator {{ 'fresh' if status.age_minutes < 2 else 'old' }}">
                    {% if status.age_minutes < 1 %}
                        LIVE
                    {% elif status.age_minutes < 5 %}
                        {{ status.age_minutes }}min
                    {% else %}
                        ALT
                    {% endif %}
                </div>
            </div>
            
            <div class="status-message">
                {{ status.message }}
            </div>
            
            <div class="status-details">
                {% if status.age_minutes < 5 %}
                    {% if status.recognized %}
                        <div>👥 {{ status.recognized | join(', ') }}</div>
                    {% endif %}
                    <div>🕐 Vor {{ status.age_minutes }} Minute(n)</div>
                    {% if status.image != 'N/A' %}
                        <div>📁 {{ status.image }}</div>
                    {% endif %}
                {% else %}
                    <div>⏰ Keine aktuellen Daten</div>
                    <div>🔍 System möglicherweise nicht aktiv</div>
                {% endif %}
            </div>
        </div>
        
        <div class="refresh-info">
            🔄 Aktualisiert alle 2 Sekunden | Status: {{ status.status.upper() }}
        </div>
        
        <script>
            // Auto-Refresh alle 2 Sekunden (schneller für Live-Updates)
            setTimeout(function() {
                window.location.reload();
            }, 2000);
        </script>
    </body>
    </html>
    """
    
    status = get_latest_status()
    
    return render_template_string(html_template, status=status)

@app.route('/api/status')
def api_status():
    """API für aktuellen Status"""
    return jsonify(get_latest_status())

@app.route('/debug')
def debug_info():
    """Debug-Seite für Entwicklung"""
    debug_data = {}
    
    # Live Status
    try:
        if os.path.exists('live_status.json'):
            with open('live_status.json', 'r') as f:
                debug_data['live_status'] = json.load(f)
        else:
            debug_data['live_status'] = "Datei nicht gefunden"
    except Exception as e:
        debug_data['live_status'] = f"Fehler: {e}"
    
    # Historie
    try:
        if os.path.exists('recognition_results.json'):
            with open('recognition_results.json', 'r') as f:
                results = json.load(f)
                debug_data['history_count'] = len(results)
                debug_data['last_3_results'] = results[-3:] if len(results) >= 3 else results
        else:
            debug_data['history'] = "Datei nicht gefunden"
    except Exception as e:
        debug_data['history'] = f"Fehler: {e}"
    
    # Dateisystem Info
    debug_data['current_time'] = datetime.now().isoformat()
    debug_data['files_exist'] = {
        'live_status.json': os.path.exists('live_status.json'),
        'recognition_results.json': os.path.exists('recognition_results.json'),
        'api-config.yaml': os.path.exists('api-config.yaml')
    }
    
    if os.path.exists('live_status.json'):
        stat = os.stat('live_status.json')
        debug_data['live_status_age'] = int((time.time() - stat.st_mtime) / 60)  # Minuten
    
    return f"<pre>{json.dumps(debug_data, indent=2, default=str)}</pre>"

if __name__ == '__main__':
    print("🚨 ESP32 Status Lampe - LIVE VERSION")
    print("=" * 40)
    print("🌐 Status Lampe: http://localhost:5000")
    print("🐛 Debug Info:   http://localhost:5000/debug")
    print("📡 API:          http://localhost:5000/api/status")
    print("")
    print("🔴 ROT:    Unbekannte Person / Fehler")
    print("🟢 GRÜN:   Bekannte Person erkannt")
    print("⚪ GRAU:   Keine Gesichter / System idle")
    print("🟡 GELB:   Gerade am Verarbeiten")
    print("")
    print("🔄 Auto-Refresh alle 2 Sekunden")
    print("📡 Liest live_status.json für sofortige Updates")
    print("=" * 40)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
