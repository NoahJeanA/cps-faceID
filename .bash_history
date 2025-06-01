ip a
sudo systemctl status hostapd
sudo hostapd -d /etc/hostapd/hostapd.conf
ip a
ip a show wlan0
sudo rfkill list all
sudo rfkill unblock wifi
sudo rfkill list all
sudo ip link set wlan0 up
sudo systemctl stop NetworkManager
sudo systemctl disable NetworkManager
sudo systemctl mask NetworkManager
sudo systemctl stop wpa_supplicant
sudo systemctl disable wpa_supplicant
sudo killall wpa_supplicant
sudo hostapd -t /etc/hostapd/hostapd.conf
cat /etc/hostapd/hostapd.conf
ip a
sudo systemctl status hostapd
sudo systemctl rebooz
sudo systemctl reboot
ip a
sudo systemctl status hostapd
ip a
sudo systemctl reboot
ip a
systemctl status hostapd.service 
cd pull-api/camera_images/
ls
cd ESP32-001/
ls
pwd
ls
cd ..
ls
cd ESP32-001/
ls
pwd
ls
cd ..
ls
cd ..
ls
python3 pull.py 
cat pull.py 
python3 pull.py 
ls
cd ..
ls
cd pull-api/
ls
ls -al
cat pull.py 
cat camera_config.yaml 
nano camera_config.yaml
TERM=xterm
nano camera_config.yaml
python3 pull.py 
ls
sudo journalctl -f
ld
ls
ls -al
mkdir pull-api.py
mv pull-api.py pull-api
cd pull-api/
ls
nano pull.py
export TERM=xterm
nano pull.py
python image_downloader.py
python3 pull.py 
ls
rm * captured_images/
cd captured_images/
ls
rm *
ls
cd ..
ls
nano pull.py
python3 pull.py 
echo "" > import requests
import time
import os
import yaml
from datetime import datetime
import threading
from pathlib import Path
import concurrent.futures
class MultiCameraDownloader:
# Beispiel für die Verwendung
if __name__ == "__main__":
    downloader = MultiCameraDownloader("camera_config.yaml")
# Verwendung:
# create_simple_config(['192.168.4.40', '192.168.4.41', '192.168.4.42'])
echo "" > pull.py 
nano pull.py 
python3 pull.py 
pip3 install yaml
pip3 install pyyaml
sudo apt install pip3
sudo apt install python3-pip
pip3 install pyyaml
pip3 install pyyaml --break-system-packages
python3 pull.py 
ls
cat import 
rm -rf camera_images  captured_images import camera_config.yaml
python3 pull.py 
ls
nano camera_config.yaml
rm -rf camera_images/
python3 pull.py 
ls
cd camera_images/
ös
ls
ls -la
cd ESP32-001/
ls
cd ..
ls
cd ..
ls
cd ..
ls
mkdir push-api
cd push-api/
ls
nano seeu.py
nano api-config.yaml
python3 seeu.py 
curl -X POST "https://faceid.tappe.dev/api/v1/recognition/recognize"   -H "accept: application/json"   -H "x-api-key: 7c5b7fb1-e2ef-4085-a2d1-0849063303bd"   -H "Content-Type: multipart/form-data"   -F "file=@/mnt/c/Users/Jona/Pictures/Screenshots/Screenshot2024-11-25080610.png"
{curl -X POST "https://faceid.tappe.dev/api/v1/recognition/recognize"   -H "accept: application/json"   -H "x-api-key: 7c5b7fb1-e2ef-4085-a2d1-0849063303bd"   -H "Content-Type: multipart/form-data"   -F "file=@/mnt/c/Users/Jona/Pictures/Screenshots/Screenshot2024-11-25080610.png"
curl -X POST "https://faceid.tappe.dev/api/v1/recognition/recognize" >   -H "accept: application/json" >   -H "x-api-key: 7c5b7fb1-e2ef-4085-a2d1-0849063303bd" >   -H "Content-Type: multipart/form-data" >   -F "file=/home/pi/pull-api/camera_images/ESP32-001/esp32-001_20250601_154849_205.jpg"
ls
rm "-F"
ls
ls -al
rm -rf "-F" "-H" 
rm ./-F
rm ./-H
ls
cat camera_monitor.log
nano test.sh
bash test.sh 
ls
cat test.sh 
ls /home/pi/pull-api/camera_images/ESP32-001/esp32-001_20250601_154849_205.jpg
cat test.sh 
bahs test.sh 
bash test.sh 
nano test.sh
bash test.sh 
ls
python3 seeu.py
cta ../pull-api/pull.py 
cat ../pull-api/pull.py 
ls
echo "" seeu.py 
echo "" > seeu.py 
mv seeu.py push.py
ls
nano push.py 
echo "" > api-config.yaml 
nano api-config.yaml
l
ls
python3 push.py
pip3 install watchdog
pip3 install watchdog --break-system-packages
pip3 install watchdog
python3 push.py
ls
rm test.sh
ls
cat face_recognition.log
cat recognition_results.json
ls
rm face_recognition.logface_recognition.log recognition_results.json
ls
rm camera_monitor.log face_recognition.log
ls
python3 push.py
ls
echo "" > api-config.yaml
nano api-config.yaml
ls
echo "" > push.py 
nano push.py 
python3 push.py
ls
echo "" > push.py 
nano push.py 
python3 push.py
ls
cd ..
mkdir web_dashboard
ls
cd web_dashboard/
python web_dashboard.py
nano web_dashboard.py
python3 web_dashboard.py
pip3 install flask
pip3 install flask --break-system-packages
python3 web_dashboard.py
sl
ls
cd push-api/
python3 push.py 
ls
cp push.py push-backup.py 
ls
echo "" > push.py
nano push.py 
export TERM=xterm
nano push.py 
python3 push.py 
ls
cat live_status.json 
python3 push.py 
cat live_status.json 
ls
ln -s ~/push-api/recognition_results.json ~/web_dashboard/recognition_results.json
ln -s ~/push-api/live_status.json ~/web_dashboard/live_status.json
ls
python3 push.py 
ls
cd push-api/
ls
cat recognition_results.json
ln -s recognition_results.json ../web_dashboard/recognition_results.json
ls
cd ..
ls
cd web_dashboard/
ls
ls -a
ls -al
cat recognition_results.json 
ls
ln -s ~/push-api/recognition_results.json ~/web_dashboard/recognition_results.json
ls
cat recognition_results.json
python3 web_dashboard.py 
ls
cat recognition_results.json
ls
python3 web_dashboard.py 
cat recognition_results.json
nano web_dashboard.py 
export TERM=xterm
nano web_dashboard.py 
export TERM=xterm
python3 web_dashboard.py 
cat live_status.json 
python3 web_dashboard.py 
ls
echo "" > web_dashboard.py
nano web_dashboard.py 
python3 web_dashboard.py 
ls
cd ..
ls
mkdir start
cd start/
ls
nano start.sh
ls
cd ..
ls
tree pull-api push-api start web_dashboard
ls pull-api
ls push-api
ls web_dashboard
ls
nano start.py
python3 start.py
ls
tm -rf start
rm -rf start
echo "" > start.py
nano start.py 
python3 start.py
shutdown 
sudo shutdown 
sudo shutdown now
rm ~/web_dashboard/recognition_results.json
cd pull-api/
ls
python3 pull.py
ls
python3 pull.py
python3 start.sh
ls
python3 start.py
