#!/bin/bash

sleep 1
pkill flask

nmcli device wifi rescan
nmcli device wifi connect "$WIFI_SSID" password "$WIFI_PSWD"
CON_ONLINE=$?	# online = 0

if [ "$CON_ONLINE" -eq 0 ]; then
    nmcli con modify "$WIFI_SSID" autoconnect yes
    nmcli con modify "$WIFI_SSID" connection.autoconnect-priority 1
else
    nmcli con up "Hotspot"
fi