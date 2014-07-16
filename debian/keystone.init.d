#!/bin/sh
### BEGIN INIT INFO
# Provides:          keystone
# Required-Start:    $network $local_fs $remote_fs
# Required-Stop:     $remote_fs
# Should-Start:      mysql postgresql slapd rabbitmq-server ntp
# Should-Stop:       mysql postgresql slapd rabbitmq-server ntp
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: OpenStack cloud identity service
# Description: This is the identity service used by OpenStack for
#              authentication (authN) and high-level authorization (authZ).
### END INIT INFO

# Author: Julien Danjou <acid@debian.org>

# PATH should only include /usr/* if it runs after the mountnfs.sh script
PATH=/sbin:/usr/sbin:/bin:/usr/bin
DESC="OpenStack Identity service"
NAME=keystone
DAEMON=/usr/bin/keystone-all
DAEMON_ARGS=""             # Arguments to run the daemon with
PIDFILE=/var/run/$NAME/${NAME}.pid
SCRIPTNAME=/etc/init.d/$NAME
PID_DIR=/var/run/${NAME}
# if you use systemd as init and change $KEYSTONE_USER and $KEYSTONE_GROUP you 
# will need to copy /usr/lib/tmpfiles.d/keystone.conf to /etc/tmpfiles.d and edit it
KEYSTONE_USER="keystone"
KEYSTONE_GROUP="keystone"

# Exit if the package is not installed
[ -x $DAEMON ] || exit 0

# Read configuration variable file if it is present
[ -r /etc/default/$NAME ] && . /etc/default/$NAME

# Load the VERBOSE setting and other rcS variables
. /lib/init/vars.sh

# Define LSB log_* functions.
# Depend on lsb-base (>= 3.0-6) to ensure that this file is present.
. /lib/lsb/init-functions

mkdir -p ${PID_DIR}
chown ${KEYSTONE_USER}:${KEYSTONE_GROUP} ${PID_DIR}

#
# Function that starts the daemon/service
#
do_start()
{
	start-stop-daemon --start --quiet --pidfile $PIDFILE \
            --background --make-pidfile --chuid ${KEYSTONE_USER}:${KEYSTONE_GROUP} --startas $DAEMON --test > /dev/null \
	    || return 1
	start-stop-daemon --start --quiet --pidfile $PIDFILE \
            --background --make-pidfile --chuid ${KEYSTONE_USER}:${KEYSTONE_GROUP} --startas $DAEMON -- \
	    $DAEMON_ARGS \
	    || return 2
}

#
# Function that stops the daemon/service
#
do_stop()
{
	start-stop-daemon --stop --quiet --retry=TERM/30/KILL/5 --pidfile $PIDFILE
	RETVAL="$?"
	[ "$RETVAL" = 2 ] && return 2
	rm -f $PIDFILE
	return "$RETVAL"
}

case "$1" in
  start)
    log_daemon_msg "Starting $DESC " "$NAME"
    do_start
    case "$?" in
		0|1) log_end_msg 0 ;;
		2) log_end_msg 1 ;;
	esac
  ;;
  stop)
	log_daemon_msg "Stopping $DESC" "$NAME"
	do_stop
	case "$?" in
		0|1) log_end_msg 0 ;;
		2) log_end_msg 1 ;;
	esac
	;;
  status)
       status_of_proc "$DAEMON" "$NAME" && exit 0 || exit $?
       ;;
  restart|force-reload)
	#
	# If the "reload" option is implemented then remove the
	# 'force-reload' alias
	#
	log_daemon_msg "Restarting $DESC" "$NAME"
	do_stop
	case "$?" in
	  0|1)
		do_start
		case "$?" in
			0) log_end_msg 0 ;;
			1) log_end_msg 1 ;; # Old process is still running
			*) log_end_msg 1 ;; # Failed to start
		esac
		;;
	  *)
	  	# Failed to stop
		log_end_msg 1
		;;
	esac
	;;
  systemd-start)
    do_start
    ;;
  systemd-stop)
    do_stop
    ;;
  *)
	echo "Usage: $SCRIPTNAME {start|stop|status|restart|force-reload}" >&2
	exit 3
	;;
esac

:
