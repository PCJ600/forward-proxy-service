FROM rockylinux:9.3

WORKDIR /
RUN yum -y install procps net-tools squid python3 python3-pip \
    && yum clean all && rm -rf /var/cache/yum
RUN pip3 install Flask requests

COPY conf/squid.conf /etc/squid/squid.conf
COPY conf/squid.conf /etc/squid/squid.conf.base
COPY src/start_squid.sh /start_squid.sh
RUN chmod +x start_squid.sh

COPY src/auth/auth.py /my_auth
RUN chmod +x my_auth

COPY src/agent.py /agent
COPY src/logging_config.py /logging_config.py
COPY src/reload_squid.py /reload_squid.py

CMD ["sh", "-c", "/start_squid.sh"]
