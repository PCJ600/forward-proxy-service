FROM rockylinux:9.3

WORKDIR /
RUN yum -y install procps net-tools squid
COPY squid.conf /etc/squid/squid.conf
COPY start_squid.sh /start_squid.sh

RUN ulimit -n 65536
RUN chmod +x start_squid.sh

CMD ["sh", "-c", "/start_squid.sh"]
