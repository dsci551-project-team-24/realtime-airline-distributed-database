# create localhost under /hosts/ in zookeeper
from kazoo.client import KazooClient
from loguru import logger

zk = KazooClient(hosts='localhost:2181')
zk.start()
zk.ensure_path('/hosts/')
# check if node exists, if it does log an error and exit
if zk.exists('/hosts/localhost'):
    logger.warning('Node localhost already exists')
    # successful exit
    exit(0)
zk.create('/hosts/localhost', b'localhost')
zk.stop()

logger.info('Created Z node for localhost')