import os
import sys
import traceback

from kazoo.client import KazooClient
from loguru import logger

zk_servers = os.environ['ZOOKEEPER_SERVERS']


def get_host_name():
    # function to run the unix command: dig +noall +answer -x "172.24.0.5" | awk '{print $5}' | cut -f1 -d .
    # and return the hostname
    import subprocess
    import socket
    ip = socket.gethostbyname(socket.gethostname())
    cmd = f"dig +noall +answer -x {ip} | awk '{{print $5}}' | cut -f1 -d ."
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    # check if output is empty
    if not output:
        logger.error(f'Error while getting hostname: {error}')
        sys.exit(1)
    # check error
    if error:
        logger.error(f'Error while getting hostname: {error}')
        sys.exit(1)
    return output.decode('utf-8').strip()


try:
    logger.info('Connecting to Zookeeper')
    zk = KazooClient(hosts=zk_servers)
    zk.start()
    zk.ensure_path('/hosts/')
    current_host_name = get_host_name()
    print(f'Current host name: {current_host_name}')
    logger.info(f'Creating ephemeral node for {current_host_name}')
    # check if node exists, if it does log an error and exit
    if zk.exists(f'/hosts/{current_host_name}'):
        logger.warning(f'Node {current_host_name} already exists')
        # successful exit
        sys.exit(0)
    container_id = os.environ['HOSTNAME']
    # create ephemeral node and set the container id as the data
    zk.create(f'/hosts/{current_host_name}', container_id.encode('utf-8'), ephemeral=True)
    logger.info('Node created')
except:
    error_msg = traceback.format_exc()
    logger.error(f'Error while creating ephemeral node: {error_msg}')
    sys.exit(1)
while True:
    pass
