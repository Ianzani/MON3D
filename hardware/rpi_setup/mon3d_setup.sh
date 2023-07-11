#!/bin/bash

# TODO: check and fix everything
# chmod controller scripts

AP_SSID="MON3D"
AP_PSWD="12345678"
#AP_IP="10.42.0.1/24"

### Folder ###
cp -r ./mon3d /

### Boot ###
cp /mon3d/boot/mon3d.service /etc/systemd/system/
chmod 744 /mon3d/boot/mon3d_init.sh
chmod 664 /etc/systemd/system/mon3d.service
systemctl daemon-reload
systemctl enable mon3d.service

### Python ###
apt install python3-pip -y
apt install python3-lgpio -y
apt install python3-flask -y
pip install -r /mon3d/controller/requirements.txt

### Network ###
apt install network-manager -y
nmcli radio wifi on
nmcli device wifi hotspot ssid "$AP_SSID" password "$AP_PSWD"
nmcli con down "Hotspot"
nmcli con modify "Hotspot" autoconnect yes
nmcli con modify "Hotspot" connection.autoconnect-priority -1
#nmcli con modify "Hotspot" ipv4.addr "$AP_IP"

### Extra ###
apt install ffmpeg -y
chmod +x /mon3d/boot/mon3d_wifi.sh
apt autoremove
apt clean
