#!/usr/bin/env python3

import subprocess
import time
import signal
import sys
import os

class ESP32SystemStarter:
    def __init__(self):
        self.processes = []
        self.running = True
        self.base_dir = os.path.expanduser("~")  # Home-Verzeichnis
    
    def start_pull_api(self):
        """Starte Pull-API (Kamera Download) im pull-api Ordner"""
        try:
            print("📥 Starte Pull-API (Kamera Download)...")
            
            pull_dir = os.path.join(self.base_dir, 'pull-api')
            script_path = os.path.join(pull_dir, 'pull.py')
            
            if not os.path.exists(script_path):
                print(f"   ❌ pull.py nicht in {pull_dir} gefunden")
                return False
            
            process = subprocess.Popen([
                sys.executable, 'pull.py'
            ], cwd=pull_dir)
            
            self.processes.append(('Pull API', process))
            print(f"   ✅ Gestartet (pull.py in {pull_dir})")
            return True
        except Exception as e:
            print(f"   ❌ Fehler: {e}")
            return False
    
    def start_face_monitor(self):
        """Starte Face Recognition Monitor im push-api Ordner"""
        try:
            print("🔍 Starte Face Recognition Monitor...")
            
            # Prüfe ob push.py oder face_monitor.py existiert
            push_dir = os.path.join(self.base_dir, 'push-api')
            
            if os.path.exists(os.path.join(push_dir, 'face_monitor.py')):
                script_name = 'face_monitor.py'
            elif os.path.exists(os.path.join(push_dir, 'push.py')):
                script_name = 'push.py'
            else:
                print(f"   ❌ Kein Face Recognition Script in {push_dir} gefunden")
                return False
            
            process = subprocess.Popen([
                sys.executable, script_name
            ], cwd=push_dir)
            
            self.processes.append(('Face Monitor', process))
            print(f"   ✅ Gestartet ({script_name} in {push_dir})")
            return True
        except Exception as e:
            print(f"   ❌ Fehler: {e}")
            return False
    
    def start_web_dashboard(self):
        """Starte Web Dashboard im web_dashboard Ordner"""
        try:
            print("🌐 Starte Web Dashboard...")
            
            web_dir = os.path.join(self.base_dir, 'web_dashboard')
            script_path = os.path.join(web_dir, 'web_dashboard.py')
            
            if not os.path.exists(script_path):
                print(f"   ❌ web_dashboard.py nicht in {web_dir} gefunden")
                return False
            
            process = subprocess.Popen([
                sys.executable, 'web_dashboard.py'
            ], cwd=web_dir)
            
            self.processes.append(('Web Dashboard', process))
            print(f"   ✅ Gestartet (web_dashboard.py in {web_dir})")
            return True
        except Exception as e:
            print(f"   ❌ Fehler: {e}")
            return False
    
    def setup_file_links(self):
        """Erstelle symbolische Links für gemeinsame Dateien"""
        try:
            push_dir = os.path.join(self.base_dir, 'push-api')
            web_dir = os.path.join(self.base_dir, 'web_dashboard')
            
            # Links für live_status.json und recognition_results.json
            files_to_link = ['live_status.json', 'recognition_results.json']
            
            for file_name in files_to_link:
                push_file = os.path.join(push_dir, file_name)
                web_file = os.path.join(web_dir, file_name)
                
                # Lösche existierenden Link/Datei im web_dashboard
                if os.path.exists(web_file) or os.path.islink(web_file):
                    os.remove(web_file)
                
                # Erstelle symbolischen Link von web_dashboard zu push-api
                if os.path.exists(push_file):
                    os.symlink(push_file, web_file)
                    print(f"   🔗 Link erstellt: {file_name}")
                
        except Exception as e:
            print(f"   ⚠️ Warnung beim Erstellen der Links: {e}")
    
    def check_files(self):
        """Prüfe ob alle Dateien da sind"""
        errors = []
        
        # Prüfe pull-api Ordner
        pull_dir = os.path.join(self.base_dir, 'pull-api')
        if not os.path.exists(pull_dir):
            errors.append(f"Ordner {pull_dir} existiert nicht")
        else:
            pull_script = os.path.join(pull_dir, 'pull.py')
            if not os.path.exists(pull_script):
                errors.append(f"Script {pull_script} fehlt")
        
        # Prüfe push-api Ordner
        push_dir = os.path.join(self.base_dir, 'push-api')
        if not os.path.exists(push_dir):
            errors.append(f"Ordner {push_dir} existiert nicht")
        else:
            # Prüfe auf push.py oder face_monitor.py
            if not (os.path.exists(os.path.join(push_dir, 'face_monitor.py')) or 
                    os.path.exists(os.path.join(push_dir, 'push.py'))):
                errors.append(f"Kein Face Recognition Script in {push_dir}")
            
            # Prüfe Konfiguration
            config_file = os.path.join(push_dir, 'api-config.yaml')
            if not os.path.exists(config_file):
                errors.append(f"Konfiguration {config_file} fehlt")
        
        # Prüfe web_dashboard Ordner
        web_dir = os.path.join(self.base_dir, 'web_dashboard')
        if not os.path.exists(web_dir):
            errors.append(f"Ordner {web_dir} existiert nicht")
        else:
            web_script = os.path.join(web_dir, 'web_dashboard.py')
            if not os.path.exists(web_script):
                errors.append(f"Script {web_script} fehlt")
        
        if errors:
            print("❌ Probleme gefunden:")
            for error in errors:
                print(f"   - {error}")
            return False
        return True
    
    def signal_handler(self, signum, frame):
        """Handle für Ctrl+C"""
        print("\n🛑 Beende alle Prozesse...")
        self.stop_all()
        sys.exit(0)
    
    def stop_all(self):
        """Stoppe alle Prozesse"""
        self.running = False
        
        for name, process in self.processes:
            try:
                print(f"🛑 Stoppe {name}...")
                process.terminate()
                
                # Warte max 5 Sekunden
                try:
                    process.wait(timeout=5)
                    print(f"   ✅ {name} gestoppt")
                except subprocess.TimeoutExpired:
                    print(f"   💀 {name} force-kill")
                    process.kill()
                    
            except Exception as e:
                print(f"   ⚠️ Fehler beim Stoppen: {e}")
        
        self.processes.clear()
    
    def get_pi_ip(self):
        """Hole Pi IP-Adresse"""
        try:
            result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
            if result.returncode == 0:
                ip = result.stdout.strip().split()[0]
                return ip
        except:
            pass
        return "DEINE_PI_IP"
    
    def start_all(self):
        """Starte das komplette System"""
        print("🚀 ESP32 Face Recognition System")
        print("=" * 50)
        print(f"📁 Home-Verzeichnis: {self.base_dir}")
        
        # Prüfe Dateien
        if not self.check_files():
            print("❌ Kann nicht starten - siehe Fehler oben")
            return
        
        # Erstelle File-Links für gemeinsame Dateien
        print("🔗 Erstelle File-Links...")
        self.setup_file_links()
        
        # Signal Handler für Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Starte Pull-API (Kamera Download)
        if not self.start_pull_api():
            print("⚠️ Pull-API konnte nicht gestartet werden - System läuft ohne Kamera-Download")
        
        # Kurz warten
        time.sleep(2)
        
        # Starte Face Monitor
        if not self.start_face_monitor():
            print("❌ Face Monitor konnte nicht gestartet werden")
            self.stop_all()
            return
        
        # Kurz warten
        time.sleep(3)
        
        # Starte Web Dashboard
        if not self.start_web_dashboard():
            print("❌ Web Dashboard konnte nicht gestartet werden")
            self.stop_all()
            return
        
        # Hole Pi IP
        pi_ip = self.get_pi_ip()
        
        print("=" * 50)
        print("✅ System erfolgreich gestartet!")
        print("")
        print("📂 Ordner-Struktur & Prozesse:")
        print(f"   📥 Pull-API:         ~/pull-api/ (Kamera-Download)")
        print(f"   🔍 Face Recognition: ~/push-api/ (Gesichtserkennung)")
        print(f"   🌐 Web Dashboard:    ~/web_dashboard/ (Status-Anzeige)")
        print("")
        print("🌐 Web-Zugriff:")
        print("   🖥️  Lokal:  http://localhost:5000")
        print(f"   📱 Handy:  http://{pi_ip}:5000")
        print("   🐛 Debug:  http://localhost:5000/debug")
        print("")
        print("🚨 Status-Lampe:")
        print("   🟢 GRÜN  = Bekannte Person erkannt")
        print("   🔴 ROT   = Unbekannte Person / Fehler")
        print("   ⚪ GRAU  = Keine Gesichter / System idle")
        print("   🟡 ORANGE = Gerade am Verarbeiten")
        print("")
        print("📁 Datenfluss:")
        print("   📥 ESP32 → Pull-API → ~/pull-api/camera_images/")
        print("   🔍 Face Recognition → ~/push-api/live_status.json")
        print("   🌐 Web Dashboard ← live_status.json")
        print("")
        print("🛑 Zum Beenden: Ctrl+C drücken")
        print("=" * 50)
        
        # Hauptloop - überwache Prozesse
        try:
            while self.running:
                time.sleep(10)
                
                # Prüfe ob Prozesse noch laufen
                for name, process in self.processes[:]:  # Kopie der Liste
                    if process.poll() is not None:
                        print(f"⚠️ {name} wurde beendet")
                        self.processes.remove((name, process))
                        
                        # Versuche Neustart
                        if name == 'Pull API':
                            print("🔄 Starte Pull-API neu...")
                            time.sleep(2)
                            self.start_pull_api()
                        elif name == 'Face Monitor':
                            print("🔄 Starte Face Monitor neu...")
                            time.sleep(2)
                            self.start_face_monitor()
                        elif name == 'Web Dashboard':
                            print("🔄 Starte Web Dashboard neu...")
                            time.sleep(2)
                            self.start_web_dashboard()
                
                # Wenn keine Prozesse mehr laufen, beende
                if not self.processes:
                    print("❌ Alle Prozesse beendet - System stoppt")
                    break
                    
        except KeyboardInterrupt:
            pass

def main():
    """Hauptfunktion"""
    starter = ESP32SystemStarter()
    
    # Hilfe anzeigen
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print("ESP32 Face Recognition System Starter")
        print("")
        print("Ordner-Struktur:")
        print("  ~/pull-api/          - Kamera Download (pull.py)")
        print("  ~/push-api/          - Face Recognition Scripts")
        print("  ~/web_dashboard/     - Web Dashboard")
        print("")
        print("Usage:")
        print("  python start_all.py              # Starte alles")
        print("  python start_all.py --help       # Diese Hilfe")
        print("")
        print("Startet automatisch:")
        print("  - Pull-API: ESP32 Kamera Download (pull-api/)")
        print("  - Face Recognition Monitor (push-api/)")
        print("  - Web Dashboard (web_dashboard/) auf Port 5000")
        print("")
        print("Datenfluss:")
        print("  ESP32 → Pull-API → Face Recognition → Web Dashboard")
        print("")
        print("Bei Problemen:")
        print("  - Prüfe ~/pull-api/camera_config.yaml (Kamera IPs)")
        print("  - Prüfe ~/push-api/api-config.yaml (CompreFace API)")
        print("  - Schaue in ~/push-api/face_recognition.log")
        print("  - Teste http://localhost:5000/debug")
        return
    
    # System starten
    starter.start_all()

if __name__ == "__main__":
    main()
