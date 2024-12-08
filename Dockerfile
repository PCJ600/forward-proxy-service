FROM rockylinux:9.3

WORKDIR /
RUN yum -y install procps net-tools squid

COPY squid.conf /etc/squid/squid.conf
COPY start_squid.sh /start_squid.sh
RUN chmod +x start_squid.sh

COPY src/auth/auth.py /my_auth
RUN chmod +x my_auth

CMD ["sh", "-c", "/start_squid.sh"]
