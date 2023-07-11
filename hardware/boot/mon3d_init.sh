#!/bin/bash

AP_SSID="MON3D"
AP_PSWD="12345678"
#AP_IP="10.42.0.1/24"
export FLASK_APP=/mon3d/boot/app.py

LED=23
python3 /mon3d/boot/writeLED.py "$LED" 0

nmcli -g GENERAL.STATE con show Hotspot	
AP_EXIST=$?	# exist = 0

if [ "$AP_EXIST" -ne 0 ]; then
    nmcli radio wifi on
    nmcli device wifi hotspot ssid "$AP_SSID" password "$AP_PSWD"
    nmcli con down "Hotspot"
    nmcli con modify "Hotspot" autoconnect yes
    nmcli con modify "Hotspot" connection.autoconnect-priority -1
#   nmcli con modify "Hotspot" ipv4.addr "$AP_IP"
    nmcli con up "Hotspot"
fi

while ! ping -c 1 igbt.eesc.usp.br; do
    AP_CHECK=$(nmcli -g GENERAL.STATE con show Hotspot) # down = NULL
    if [ ! -z "$AP_CHECK" ]; then
        flask run --host=0.0.0.0 --port=80
        sleep 5
    fi
    sleep 1
done

python3 /mon3d/boot/writeLED.py "$LED" 1
python3 /mon3d/controller/main.py
