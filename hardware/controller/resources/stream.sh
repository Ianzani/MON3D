#!/bin/bash
ffmpeg -s 160x120 -r 15 -i /dev/video0 -pix_fmt yuv420p -g 50 -c:v libx264 -b:v 10M -bufsize 40M -maxrate 10M -preset ultrafast -tune zerolatency -rtsp_transport tcp -f rtsp "$1" &
