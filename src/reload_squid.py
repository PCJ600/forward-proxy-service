import logging_config
import traceback
import os
import ipaddress

SQUID_BASECONF_PATH='/etc/squid/squid.conf.base'
SQUID_CONF_PATH='/etc/squid/squid.conf'
logger = logging_config.logger

class ProxyItem():
    def __init__(self):
        self.host = ""
        self.port = ""
        self.user = ""
        self.passwd = ""
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

class SquidConf():
    def __init__(self):
        self.whitelist = ""
        self.whitelist_flag = ""
        self.upstream_proxy = ProxyItem()

# Global variables
g_squid_conf = SquidConf()

def get_squid_conf_from_host_conf(host_conf):
    conf = SquidConf()
    conf.whitelist_flag = host_conf.get("whitelistFlag")
    conf.whitelist = host_conf.get("whitelist")
    conf.upstream_proxy.host = host_conf.get("proxyHost")
    conf.upstream_proxy.port = host_conf.get("proxyPort")
    return conf


def need_reload_squid(old_conf, new_conf):
    is_whitelist_change = (old_conf.whitelist_flag != new_conf.whitelist_flag) or (old_conf.whitelist != new_conf.whitelist)
    is_upstream_proxy_change = not (old_conf.upstream_proxy == new_conf.upstream_proxy)
    return is_whitelist_change or is_upstream_proxy_change


def rollback_squid_conf():
    ret = os.system("cp -f {src} {dst}".format(src=SQUID_BASECONF_PATH, dst=SQUID_CONF_PATH))
    logger.info("rollback squid conf ret: %d", ret)


def fqdn_is_ipaddr(fqdn):
    try:
        ip = ipaddress.ip_network(fqdn, strict=False)
        return True
    except ValueError:
        return False


def parse_whitelist(whitelist_str):
    dst_domain_list, dst_ip_list = [], []
    try:
        whitelist = whitelist_str.split(',')
        for e in whitelist:
            e = e.replace(" ", "")
            e = e.lstrip("*") # left * need to be deleted in squid.conf
            fqdn, port = e, 443
            if fqdn_is_ipaddr(fqdn):
                if fqdn not in dst_ip_list:
                    dst_ip_list.append(fqdn)
            else:
                if fqdn not in dst_domain_list:
                    dst_domain_list.append(fqdn)
    except:
        logger.error("parse whitelist_str exception. traceback: %r", traceback.format_exc())
    return dst_domain_list, dst_ip_list


def update_whitelist_to_squid_conf(whitelist_str, whitelist_flag):
    if whitelist_flag != "on":
        logger.info("whitelist_flag is off, nothing to update")
        return
    try:
        dst_domain_list, dst_ip_list = parse_whitelist(whitelist_str)
        logger.info("whitelist_flag is on, whitelist: %r, dstIps: %r, dstDomains: %r", whitelist_str, dst_ip_list, dst_domain_list)

        # Add whitelist to squid.conf
        ret = os.system("sed -i '/http_access allow AuthUsers/d' {squid_conf}".format(squid_conf=SQUID_CONF_PATH))
        logger.info("delete rule http_access allow AuthUsers, ret: %r", ret)

        dst_domains_str = ' '.join(dst_domain_list)
        dst_ips_str =  ''.join(dst_ip_list)
        cmd = '''sed -i '/SED_WHITELIST_FLAG/i acl PORT_{port} port {port}' {cfg_path}; \
                 sed -i '/SED_WHITELIST_FLAG/i acl allowlist_domain_{port} dstdomain {dstdomains}' {cfg_path}; \
                 sed -i '/SED_WHITELIST_FLAG/i acl allowlist_ip_{port} dst {dstips}' {cfg_path}; \
                 sed -i '/SED_WHITELIST_FLAG/i http_access allow allowlist_domain_{port} PORT_{port} AuthUsers' {cfg_path}; \
                 sed -i '/SED_WHITELIST_FLAG/i http_access allow allowlist_ip_{port} PORT_{port} AuthUsers' {cfg_path}; \
              '''.format(port=443, dstdomains=dst_domains_str, dstips=dst_ips_str, cfg_path=SQUID_CONF_PATH)
        ret = os.system(cmd)
        logger.info("update whitelist done, dstdomains: %r, dstips: %r, ret: %r", dst_domains_str, dst_ips_str, ret)
    except:
        logger.error("update whitelist exception, traceback: %r", traceback.format_exc())


def update_upstream_proxy_to_squid_conf(upstream_proxy):
    login_str = ''
    if upstream_proxy.user != "" and upstream_proxy.passwd != "":
        login_str = 'login={u}:{p}'.format(u=upstream_proxy.user, p=upstream_proxy.passwd)		

    cmd = '''sed -i '$a\\cache_peer {host} parent {port} 0 no-query default {login_str}' {cfg_path}; \
             sed -i '$a\\never_direct allow all' {cfg_path}; \
          '''.format(host=upstream_proxy.host, port=upstream_proxy.port, cfg_path=SQUID_CONF_PATH, login_str=login_str)
    ret = os.system(cmd)
    logger.info("update squid conf, ret: %r", ret)
    

def update_squid_conf(latest_squid_conf):
    whitelist = latest_squid_conf.whitelist
    whitelist_flag = latest_squid_conf.whitelist_flag
    upstream_proxy = latest_squid_conf.upstream_proxy
    logger.info("ready to update squid conf, whitelist_flag: %r, whitelist: %r, upstream_proxy: %r", whitelist_flag, whitelist, upstream_proxy)

    update_whitelist_to_squid_conf(whitelist, whitelist_flag)
    update_upstream_proxy_to_squid_conf(upstream_proxy)


def restart_squid():
    ret = os.system("squid -k reconfigure")
    logger.info("restart squid ret: %d", ret)


def reload_squid(latest_squid_conf):
    rollback_squid_conf()
    update_squid_conf(latest_squid_conf)
    restart_squid()


def reload_squid_if_needed(host_conf):
    global g_squid_conf
    try:
        latest_squid_conf = get_squid_conf_from_host_conf(host_conf)
        if need_reload_squid(g_squid_conf, latest_squid_conf):
            reload_squid(latest_squid_conf)
        g_squid_conf = latest_squid_conf
    except:
        logger.error("reload squid exception, traceback: %r", traceback.format_exc())
