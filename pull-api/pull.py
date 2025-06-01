import requests
import time
import os
import yaml
from datetime import datetime
import threading
from pathlib import Path
import concurrent.futures

class MultiCameraDownloader:
    def __init__(self, config_file="config.yaml"):
        """
        Initialisiert den Multi-Camera Downloader
        
        Args:
            config_file (str): Pfad zur YAML-Konfigurationsdatei
        """
        self.config_file = config_file
        self.config = self._load_config()
        self.running = False
        self.download_threads = []
        
        # Ordner für alle Kameras erstellen
        self._create_directories()
    
    def _load_config(self):
        """Lädt die Konfiguration aus der YAML-Datei"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                self._validate_config(config)
                return config
        except FileNotFoundError:
            print(f"Konfigurationsdatei '{self.config_file}' nicht gefunden. Erstelle Beispiel-Konfiguration...")
            self._create_example_config()
            return self._load_config()
        except yaml.YAMLError as e:
            print(f"Fehler beim Laden der YAML-Datei: {e}")
            raise
        except Exception as e:
            print(f"Fehler beim Laden der Konfiguration: {e}")
            raise
    
    def _validate_config(self, config):
        """Validiert die Konfiguration"""
        if not isinstance(config, dict):
            raise ValueError("Konfiguration muss ein Dictionary sein")
        
        if 'cameras' not in config:
            raise ValueError("'cameras' Sektion fehlt in der Konfiguration")
        
        if not isinstance(config['cameras'], list):
            raise ValueError("'cameras' muss eine Liste sein")
        
        if len(config['cameras']) == 0:
            raise ValueError("Mindestens eine Kamera muss konfiguriert sein")
        
        # Validiere jede Kamera
        for i, camera in enumerate(config['cameras']):
            if 'name' not in camera:
                raise ValueError(f"Kamera {i+1}: 'name' fehlt")
            if 'ip' not in camera:
                raise ValueError(f"Kamera {i+1}: 'ip' fehlt")
    
    def _create_example_config(self):
        """Erstellt eine Beispiel-Konfigurationsdatei"""
        example_config = {
            'global_settings': {
                'interval': 2,
                'max_images': 5,
                'timeout': 10,
                'base_folder': 'camera_images'
            },
            'cameras': [
                {
                    'name': 'Hauptkamera',
                    'ip': '192.168.4.40',
                    'port': 80,
                    'endpoint': '/api/capture',
                    'enabled': True,
                    'folder': 'main_camera',
                    'interval': 2,
                    'max_images': 5
                },
                {
                    'name': 'Eingangskamera',
                    'ip': '192.168.4.41',
                    'port': 80,
                    'endpoint': '/api/capture',
                    'enabled': True,
                    'folder': 'entrance_camera',
                    'interval': 3,
                    'max_images': 3
                },
                {
                    'name': 'Gartenkamera',
                    'ip': '192.168.4.42',
                    'port': 8080,
                    'endpoint': '/snapshot',
                    'enabled': False,
                    'folder': 'garden_camera',
                    'interval': 5,
                    'max_images': 10
                }
            ]
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as file:
            yaml.dump(example_config, file, default_flow_style=False, 
                     allow_unicode=True, indent=2)
        
        print(f"Beispiel-Konfiguration erstellt: {self.config_file}")
        print("Bitte passe die Konfiguration an deine Kameras an!")
    
    def _create_directories(self):
        """Erstellt alle benötigten Ordner"""
        base_folder = self.config.get('global_settings', {}).get('base_folder', 'camera_images')
        Path(base_folder).mkdir(parents=True, exist_ok=True)
        
        for camera in self.config['cameras']:
            if camera.get('enabled', True):
                camera_folder = camera.get('folder', f"camera_{camera['name'].lower().replace(' ', '_')}")
                full_path = os.path.join(base_folder, camera_folder)
                Path(full_path).mkdir(parents=True, exist_ok=True)
    
    def _get_camera_url(self, camera):
        """Generiert die vollständige URL für eine Kamera"""
        ip = camera['ip']
        port = camera.get('port', 80)
        endpoint = camera.get('endpoint', '/api/capture')
        
        if port == 80:
            return f"http://{ip}{endpoint}"
        else:
            return f"http://{ip}:{port}{endpoint}"
    
    def _get_camera_folder(self, camera):
        """Gibt den vollständigen Pfad zum Kamera-Ordner zurück"""
        base_folder = self.config.get('global_settings', {}).get('base_folder', 'camera_images')
        camera_folder = camera.get('folder', f"camera_{camera['name'].lower().replace(' ', '_')}")
        return os.path.join(base_folder, camera_folder)
    
    def _generate_filename(self, camera_name):
        """Generiert einen sinnvollen Dateinamen"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        safe_name = camera_name.lower().replace(' ', '_').replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue')
        return f"{safe_name}_{timestamp}.jpg"
    
    def _cleanup_old_images(self, folder_path, max_images):
        """Löscht alte Bilder in einem Ordner"""
        try:
            image_files = []
            for file in os.listdir(folder_path):
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    filepath = os.path.join(folder_path, file)
                    creation_time = os.path.getctime(filepath)
                    image_files.append((filepath, creation_time))
            
            image_files.sort(key=lambda x: x[1], reverse=True)
            
            if len(image_files) >= max_images:
                files_to_delete = image_files[max_images-1:]
                for filepath, _ in files_to_delete:
                    os.remove(filepath)
                    camera_name = os.path.basename(os.path.dirname(filepath))
                    print(f"[{camera_name}] Altes Bild gelöscht: {os.path.basename(filepath)}")
                    
        except Exception as e:
            print(f"Fehler beim Aufräumen alter Bilder in {folder_path}: {e}")
    
    def _download_image_for_camera(self, camera):
        """Lädt ein Bild für eine spezifische Kamera herunter"""
        try:
            # Konfiguration für diese Kamera
            url = self._get_camera_url(camera)
            folder_path = self._get_camera_folder(camera)
            max_images = camera.get('max_images', 
                                  self.config.get('global_settings', {}).get('max_images', 5))
            timeout = camera.get('timeout', 
                               self.config.get('global_settings', {}).get('timeout', 10))
            
            # Alte Bilder aufräumen
            self._cleanup_old_images(folder_path, max_images)
            
            # Bild herunterladen
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            
            # Dateiname generieren und speichern
            filename = self._generate_filename(camera['name'])
            filepath = os.path.join(folder_path, filename)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"[{camera['name']}] Bild gespeichert: {filename}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"[{camera['name']}] Netzwerkfehler: {e}")
            return False
        except Exception as e:
            print(f"[{camera['name']}] Unerwarteter Fehler: {e}")
            return False
    
    def _camera_download_loop(self, camera):
        """Download-Schleife für eine einzelne Kamera"""
        camera_name = camera['name']
        interval = camera.get('interval', 
                            self.config.get('global_settings', {}).get('interval', 2))
        
        print(f"[{camera_name}] Download-Thread gestartet (Intervall: {interval}s)")
        
        while self.running:
            self._download_image_for_camera(camera)
            time.sleep(interval)
        
        print(f"[{camera_name}] Download-Thread beendet")
    
    def start(self):
        """Startet den Download für alle aktivierten Kameras"""
        if self.running:
            print("Download läuft bereits!")
            return
        
        enabled_cameras = [cam for cam in self.config['cameras'] if cam.get('enabled', True)]
        
        if not enabled_cameras:
            print("Keine aktivierten Kameras gefunden!")
            return
        
        print(f"Starte Download für {len(enabled_cameras)} Kamera(s):")
        for camera in enabled_cameras:
            url = self._get_camera_url(camera)
            print(f"  - {camera['name']}: {url}")
        
        self.running = True
        self.download_threads = []
        
        # Thread für jede Kamera starten
        for camera in enabled_cameras:
            thread = threading.Thread(
                target=self._camera_download_loop, 
                args=(camera,),
                name=f"Camera-{camera['name']}"
            )
            thread.daemon = True
            thread.start()
            self.download_threads.append(thread)
    
    def stop(self):
        """Stoppt den Download für alle Kameras"""
        if not self.running:
            print("Download läuft nicht!")
            return
        
        print("Stoppe alle Downloads...")
        self.running = False
        
        # Warte auf alle Threads
        for thread in self.download_threads:
            thread.join(timeout=5)
        
        self.download_threads = []
        print("Alle Downloads gestoppt.")
    
    def download_single_all(self):
        """Lädt ein einzelnes Bild von allen aktivierten Kameras herunter"""
        enabled_cameras = [cam for cam in self.config['cameras'] if cam.get('enabled', True)]
        
        if not enabled_cameras:
            print("Keine aktivierten Kameras gefunden!")
            return
        
        print(f"Lade Einzelbilder von {len(enabled_cameras)} Kamera(s)...")
        
        # Parallel download für bessere Performance
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(enabled_cameras)) as executor:
            futures = [executor.submit(self._download_image_for_camera, camera) 
                      for camera in enabled_cameras]
            
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        successful = sum(results)
        print(f"Erfolgreich: {successful}/{len(enabled_cameras)} Bilder heruntergeladen")
    
    def get_status(self):
        """Gibt den aktuellen Status zurück"""
        enabled_cameras = [cam for cam in self.config['cameras'] if cam.get('enabled', True)]
        
        status = {
            "running": self.running,
            "total_cameras": len(self.config['cameras']),
            "enabled_cameras": len(enabled_cameras),
            "cameras": []
        }
        
        for camera in self.config['cameras']:
            folder_path = self._get_camera_folder(camera)
            image_count = 0
            try:
                image_count = len([f for f in os.listdir(folder_path) 
                                 if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            except:
                pass
            
            camera_status = {
                "name": camera['name'],
                "enabled": camera.get('enabled', True),
                "url": self._get_camera_url(camera),
                "folder": folder_path,
                "images_count": image_count,
                "interval": camera.get('interval', 
                                    self.config.get('global_settings', {}).get('interval', 2))
            }
            status["cameras"].append(camera_status)
        
        return status
    
    def reload_config(self):
        """Lädt die Konfiguration neu"""
        print("Lade Konfiguration neu...")
        old_running = self.running
        
        if self.running:
            self.stop()
        
        self.config = self._load_config()
        self._create_directories()
        
        if old_running:
            self.start()
        
        print("Konfiguration erfolgreich neu geladen!")


# Beispiel für die Verwendung
if __name__ == "__main__":
    # Multi-Camera Downloader erstellen
    downloader = MultiCameraDownloader("camera_config.yaml")
    
    try:
        # Status anzeigen
        status = downloader.get_status()
        print(f"\nKonfigurierte Kameras: {status['total_cameras']}")
        print(f"Aktivierte Kameras: {status['enabled_cameras']}")
        
        # Kontinuierlichen Download starten
        downloader.start()
        
        # Programm läuft kontinuierlich - mit Ctrl+C beenden
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nProgramm wird beendet...")
        downloader.stop()


# Hilfsfunktionen für einfache Verwendung
def create_simple_config(cameras_ips, config_file="simple_config.yaml"):
    """
    Erstellt eine einfache Konfiguration aus einer Liste von IPs
    
    Args:
        cameras_ips (list): Liste von IP-Adressen ['192.168.4.40', '192.168.4.41']
        config_file (str): Name der Konfigurationsdatei
    """
    config = {
        'global_settings': {
            'interval': 2,
            'max_images': 5,
            'timeout': 10,
            'base_folder': 'camera_images'
        },
        'cameras': []
    }
    
    for i, ip in enumerate(cameras_ips, 1):
        camera = {
            'name': f'Kamera_{i}',
            'ip': ip,
            'port': 80,
            'endpoint': '/api/capture',
            'enabled': True,
            'folder': f'camera_{i}'
        }
        config['cameras'].append(camera)
    
    with open(config_file, 'w', encoding='utf-8') as file:
        yaml.dump(config, file, default_flow_style=False, allow_unicode=True, indent=2)
    
    print(f"Einfache Konfiguration erstellt: {config_file}")
    return config_file

# Verwendung:
# create_simple_config(['192.168.4.40', '192.168.4.41', '192.168.4.42'])
# downloader = MultiCameraDownloader("simple_config.yaml")
