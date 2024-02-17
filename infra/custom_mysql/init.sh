#!/bin/bash

if [ -n "$MYSQL_PASSWORD" ] ; then
  echo "Setting up root password..."
	TEMP_FILE='/tmp/mysql-first-time.sql'
	cat > "$TEMP_FILE" <<-EOSQL
		DELETE FROM mysql.user WHERE user = 'root' AND host = '%';
		CREATE USER 'root'@'%' IDENTIFIED BY '${MYSQL_PASSWORD}' ;
		GRANT ALL ON *.* TO 'root'@'%' WITH GRANT OPTION ;
		FLUSH PRIVILEGES ;
	EOSQL

	# set this as an init-file to execute on startup
	set -- "$@" --init-file="$TEMP_FILE"
fi

# Check if the environment variable ZOOKEEPER_SERVERS is set else abort
if [ -z "$ZOOKEEPER_SERVERS" ] ; then
  echo "ZOOKEEPER_SERVERS is not set. Aborting."
  exit 1
fi

# Run python3 zk_heartbeat.py &, but if it fails, then kill the container
python3 zk_heartbeat.py &
ZK_HEARTBEAT_PID=$!

# If the python script fails, then kill the container
trap "kill $ZK_HEARTBEAT_PID" EXIT

# execute the command supplied by CMD
exec "$@"

