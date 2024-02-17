FROM ubuntu:20.04
# Install packages: mysql adds a root user with no password
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
  apt-get install python3-pip -y && \
  apt-get -yq install mysql-server && \
  apt-get -y install dnsutils && \
  rm -rf /var/lib/apt/lists/*
## Copy requirements.txt and install the required packages
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
## Change mysql to listen on 0.0.0.0
ADD bind_0.cnf /etc/mysql/my.cnf
## Add the python for zookeeper heartbeats
ADD zk_heartbeat.py /zk_heartbeat.py
## setup our entry point
ADD init.sh /init.sh
RUN chmod 755 /*.sh
ENTRYPOINT ["/init.sh"]
EXPOSE 3306
CMD ["mysqld_safe"]