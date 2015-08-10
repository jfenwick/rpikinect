#!/bin/sh
#/etc/init.d/nodeup

export PATH=$PATH:/usr/local/bin
export NODE_PATH=$NODE_PATH:/usr/local/lib/node_modules

case "$1" in
  start)
  echo "Start screen"
  #exec forever start --sourceDir=/home/pi/web -p /home/pi/web/forever server.js
  su pi -c "screen -dmS web forever --sourceDir=/home/pi/web -p /home/pi/web/forever server.js"
  #su pi -c "screen -dmS web"
  echo "created screen?"
  ;;
stop)
  #exec forever stop --sourceDir=/home/pi/web server.js
  ;;
*)
  echo "Usage: /etc/init.d/nodeup {start|stop}"
  exit 1
  ;;
esac

exit 0
