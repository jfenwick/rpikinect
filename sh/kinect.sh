#!/bin/sh
#/etc/init.d/kinect

export PATH=$PATH:/usr/local/bin

case "$1" in
  start)
  echo "Loading Kinect"
  su pi -c "screen -dmS kinect"
  su pi -c "screen -S kinect -X stuff 'cd /home/pi/libfreenect/wrappers/python'"
  su pi -c "screen -S kinect -X stuff 'sudo python kinect_test.py'"
  echo "Loaded Kinect"
  ;;
stop)
  ;;
*)
  echo "Usage: /etc/init.d/kinect {start|stop}"
  exit 1
  ;;
esac

exit 0
