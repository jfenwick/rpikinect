#!/bin/sh
#/etc/init.d/nodeup

export PATH=$PATH:/usr/local/bin
export NODE_PATH=$NODE_PATH:/usr/local/lib/node_modules

case "$1" in
  start)
  su pi -c "screen -dmS web"
  su pi -c "screen -S web -X stuff 'cd /home/pi/rpikinect/node'"
  su pi -c "screen -S web -X stuff 'node server.js'"
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
