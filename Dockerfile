FROM rockylinux:9.3

WORKDIR /
RUN yum -y install procps net-tools squid python3 python3-pip \
    && yum clean all && rm -rf /var/cache/yum

COPY squid.conf /etc/squid/squid.conf
COPY start_squid.sh /start_squid.sh
RUN chmod +x start_squid.sh

COPY src/auth/auth.py /my_auth
RUN chmod +x my_auth

COPY src/agent.py /agent
RUN chmod +x agent

RUN pip3 install Flask requests

CMD ["sh", "-c", "/start_squid.sh"]
