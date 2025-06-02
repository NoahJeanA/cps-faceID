#!/usr/bin/env python3

import os
import time
import yaml
import requests
import json
import logging
from datetime import datetime
import threading
import glob

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class SimpleCompreFaceAPI:
    """Einfacher CompreFace API Client"""
    
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.endpoint = f"{self.api_url}/api/v1/recognition/recognize"
        
        self.session = requests.Session()
        self.session.headers.update({
            'x-api-key': self.api_key
        })
    
    def recognize_face(self, image_path: str) -> dict:
        """Schnelle Gesichtserkennung - optimiert für häufige Calls"""
        try:
            with open(image_path, 'rb') as f:
                files = {'file': f}
                params = {
                    'det_prob_threshold': 0.75,  
                    'limit': 2,  
                    'prediction_count': 1  
                }
                
                response = self.session.post(
                    self.endpoint,
                    files=files,
                    params=params,
                    timeout=10  
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {'success': True, 'data': data}
                elif "No face is found" in response.text:
                    return {'success': True, 'data': {'result': []}, 'no_face': True}
                else:
                    return {'success': False, 'error': f"HTTP {response.status_code}"}
                    
        except requests.exceptions.Timeout:
            return {'success': False, 'error': "Timeout"}
        except Exception as e:
            return {'success': False, 'error': str(e)}

class SimpleCameraMonitor:
    """Einfacher Kamera Monitor"""
    
    def __init__(self, camera_id: str, config: dict, api: SimpleCompreFaceAPI):
        self.camera_id = camera_id
        self.config = config
        self.api = api
        self.folder_path = config['folder_path']
        self.last_processed = None
        
        self.processing_lock = threading.Lock()
        self.is_busy = False
        
        logger.info(f"📷 {camera_id} - Monitor gestartet: {self.folder_path}")
    
    def get_newest_images(self, max_count=3):
        """Finde die neuesten unverarbeiteten Bilder - für schnelle Batch-Verarbeitung"""
        try:
            pattern = os.path.join(self.folder_path, self.config['file_pattern'])
            files = glob.glob(pattern)
            
            if not files:
                return []
            
            files.sort()
            
            new_files = []
            last_processed_found = False
            
            for file_path in files:
                if self.last_processed and file_path == self.last_processed:
                    last_processed_found = True
                    continue
                
                if not self.last_processed or last_processed_found or file_path > self.last_processed:
                    file_age = time.time() - os.path.getmtime(file_path)
                    if file_age >= 0.5 and os.path.getsize(file_path) > 3000:
                        new_files.append(file_path)
                        if len(new_files) >= max_count:
                            break
            
            return new_files
            
        except Exception as e:
            logger.error(f"❌ {self.camera_id} - Fehler beim Suchen: {e}")
            return []
    
    def process_image(self, image_path: str):
        """Verarbeite ein Bild mit Live-Status Updates"""
        filename = os.path.basename(image_path)
        
        self.update_live_status('processing', f"🔍 Verarbeite {filename}...", image_file=filename)
        
        logger.info(f"🔍 {self.camera_id} - Verarbeite: {filename}")
        
        start_time = time.time()
        result = self.api.recognize_face(image_path)
        duration = time.time() - start_time
        
        if result['success']:
            faces = result['data'].get('result', [])
            
            if not faces:
                logger.info(f"   ❌ {self.camera_id} - Keine Gesichter")
                self.update_live_status('gray', "💤 Keine Gesichter erkannt", image_file=filename)
            else:
                recognized = []
                unknown = 0
                
                for face in faces:
                    subjects = face.get('subjects', [])
                    if subjects:
                        best = max(subjects, key=lambda x: x.get('similarity', 0))
                        if best.get('similarity', 0) >= 0.7:
                            recognized.append(best['subject'])
                        else:
                            unknown += 1
                    else:
                        unknown += 1
                
                if recognized:
                    message = f"✅ Erkannt: {', '.join(recognized)}"
                    logger.info(f"   ✅ {self.camera_id} - Erkannt: {', '.join(recognized)}")
                    self.update_live_status('green', message, recognized=recognized, image_file=filename)
                    
                    if unknown > 0:
                        logger.info(f"   👤 {self.camera_id} - Plus {unknown} unbekannt")
                    
                    self.save_to_history(filename, recognized)
                else:
                    message = f"👤 {unknown} unbekannte Person(en)"
                    logger.info(f"   👤 {self.camera_id} - {unknown} unbekannte Gesichter")
                    self.update_live_status('red', message, image_file=filename)
        
        else:
            if "Timeout" in result['error']:
                logger.warning(f"   ⏰ {self.camera_id} - API langsam ({duration:.1f}s)")
                self.update_live_status('gray', f"⏰ API langsam ({duration:.1f}s)", image_file=filename)
            else:
                logger.error(f"   ❌ {self.camera_id} - Fehler: {result['error']}")
                self.update_live_status('red', f"❌ API Fehler", image_file=filename)
        
        logger.info(f"   ⏱️ {self.camera_id} - Verarbeitung: {duration:.1f}s")
        self.last_processed = image_path
    
    def save_to_history(self, filename: str, recognized: list):
        """Speichere erfolgreiche Erkennung in Historie"""
        try:
            result = {
                'timestamp': datetime.now().isoformat(),
                'camera': self.camera_id,
                'image': filename,
                'recognized': recognized
            }
            
            results_file = 'recognition_results.json'
            
            if os.path.exists(results_file):
                with open(results_file, 'r') as f:
                    all_results = json.load(f)
            else:
                all_results = []
            
            all_results.append(result)
            
            if len(all_results) > 50:
                all_results = all_results[-50:]
            
            with open(results_file, 'w') as f:
                json.dump(all_results, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"❌ Fehler beim Speichern der Historie: {e}")
    
    def update_live_status(self, status_type, message, recognized=None, image_file=None):
        """Schreibe JEDEN Status für Web-Frontend (auch rot/grau)"""
        try:
            live_status = {
                'timestamp': datetime.now().isoformat(),
                'camera_id': self.camera_id,
                'status': status_type,  
                'message': message,
                'recognized': recognized or [],
                'image_file': image_file,
                'last_check': datetime.now().strftime('%H:%M:%S')
            }
            
            with open('live_status.json', 'w') as f:
                json.dump(live_status, f, default=str)
                
        except Exception as e:
            logger.error(f"❌ Fehler beim Schreiben des Live-Status: {e}")
    
    def save_to_history(self, filename: str, recognized: list):
        """Speichere nur erfolgreiche Erkennungen in Historie"""
        try:
            result = {
                'timestamp': datetime.now().isoformat(),
                'camera': self.camera_id,
                'image': filename,
                'recognized': recognized
            }
            
            results_file = 'recognition_results.json'
            
            if os.path.exists(results_file):
                with open(results_file, 'r') as f:
                    all_results = json.load(f)
            else:
                all_results = []
            
            all_results.append(result)
            
            if len(all_results) > 50:
                all_results = all_results[-50:]
            
            with open(results_file, 'w') as f:
                json.dump(all_results, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"❌ Fehler beim Speichern der Historie: {e}")
    
    def run_loop(self):
        """Schnelle Loop für häufige Checks mit Live-Status Updates"""
        check_interval = self.config.get('check_interval', 1.5)  # Standard: 1.5s
        consecutive_empty = 0
        last_heartbeat = 0
        
        logger.info(f"🚀 {self.camera_id} - Turbo-Loop gestartet (Check alle {check_interval}s)")
        
        self.update_live_status('gray', "🔍 System gestartet - suche nach Bildern...")
        
        while True:
            try:
                current_time = time.time()
                
                if self.processing_lock.acquire(blocking=False):
                    try:
                        if not self.is_busy:
                            self.is_busy = True
                            
                            new_images = self.get_newest_images(max_count=3)
                            
                            if new_images:
                                logger.info(f"📦 {self.camera_id} - {len(new_images)} neue Bilder gefunden")
                                
                                for image_path in new_images:
                                    self.process_image(image_path)
                                
                                consecutive_empty = 0
                            else:
                                consecutive_empty += 1
                                
                                if current_time - last_heartbeat > 30:
                                    self.update_live_status('gray', f"💤 Überwache... (keine neuen Bilder seit {consecutive_empty} Checks)")
                                    last_heartbeat = current_time
                                
                                if consecutive_empty % 30 == 0:
                                    logger.debug(f"💤 {self.camera_id} - {consecutive_empty} leere Checks")
                            
                            self.is_busy = False
                        else:
                            logger.debug(f"⏸️ {self.camera_id} - Noch beschäftigt")
                    finally:
                        self.processing_lock.release()
                else:
                    logger.debug(f"🔒 {self.camera_id} - Lock belegt")
                
                if consecutive_empty == 0:
                    time.sleep(0.2)
                elif consecutive_empty < 3:
                    time.sleep(check_interval * 0.3)
                elif consecutive_empty < 10:
                    time.sleep(check_interval)
                else:
                    time.sleep(check_interval * 1.2)
                
            except KeyboardInterrupt:
                logger.info(f"🛑 {self.camera_id} - Turbo-Loop beendet")
                self.update_live_status('red', "🛑 System gestoppt")
                break
            except Exception as e:
                logger.error(f"❌ {self.camera_id} - Loop Fehler: {e}")
                self.update_live_status('red', f"❌ System Fehler: {str(e)}")
                time.sleep(check_interval)

class SimpleMonitorSystem:
    """Einfaches Monitoring System"""
    
    def __init__(self, config_file='api-config.yaml'):
        self.config = self.load_config(config_file)
        
        api_config = self.config['compreface']
        self.api = SimpleCompreFaceAPI(api_config['url'], api_config['api_key'])
        
        self.monitors = {}
        for camera_id, camera_config in self.config['cameras'].items():
            if camera_config.get('enabled', True):
                self.monitors[camera_id] = SimpleCameraMonitor(camera_id, camera_config, self.api)
        
        logger.info(f"🚀 System initialisiert - {len(self.monitors)} Kameras aktiv")
    
    def load_config(self, config_file):
        """Lade Konfiguration"""
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            config = {
                'compreface': {
                    'url': 'https://faceid.tappe.dev',
                    'api_key': '7c5b7fb1-e2ef-4085-a2d1-0849063303bd'
                },
                'cameras': {
                    'ESP32-001': {
                        'folder_path': '/home/pi/pull-api/camera_images/ESP32-001',
                        'file_pattern': 'esp32-001_*.jpg',
                        'enabled': True,
                        'check_interval': 1.5  
                    }
                }
            }
            
            with open(config_file, 'w') as f:
                yaml.dump(config, f, indent=2)
            
            logger.info(f"✅ Standard-Konfiguration erstellt: {config_file}")
            return config
    
    def start(self):
        """Starte alle Monitore"""
        threads = []
        
        for camera_id, monitor in self.monitors.items():
            thread = threading.Thread(
                target=monitor.run_loop,
                name=f"Monitor-{camera_id}",
                daemon=True
            )
            thread.start()
            threads.append(thread)
        
        logger.info("✅ Alle Monitore gestartet")
        logger.info("🎯 Drücke Ctrl+C zum Beenden")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Beende System...")

def main():
    """Hauptfunktion"""
    logger.info("🚀 ESP32 TURBO Face Recognition Monitor")
    logger.info("=" * 50)
    logger.info("⚡ Optimiert für 100-Bilder-Buffer")
    logger.info("⚡ Maximale Geschwindigkeit & Häufigkeit")
    logger.info("⚡ Batch-Verarbeitung aktiv")
    logger.info("=" * 50)
    
    try:
        system = SimpleMonitorSystem()
        system.start()
    except Exception as e:
        logger.error(f"❌ Systemfehler: {e}")

if __name__ == "__main__":
    main()
