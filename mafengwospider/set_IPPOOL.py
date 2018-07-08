from mafengwospider.proxies import Proxies


def set_ip_pool():
    a = Proxies()
    a.verify_proxies()
    print(a.proxies)
    proxie = a.proxies
    ip_pool = []
    for proxy in proxie:
        proxy_new = proxy.split('//')[-1]
        ip = {'ipaddr': proxy_new}
        ip_pool.append(ip)
    return ip_pool