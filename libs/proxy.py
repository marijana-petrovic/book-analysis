import random

ip_addresses = ['https://185.74.4.47:8080',
                'https://103.113.17.94:8080',
                'https://178.128.127.59:8080',
                'https://187.243.255.174:8080',
                'https://217.172.122.2:8080',
                'https://103.215.177.224:8080',
                'https://37.120.192.154:8080',
                'https://201.149.34.167:8080',
                'https://103.102.14.128:8080',
                'https://178.128.245.251:8080']


def proxy_settings(self):
    proxy_index = random.randint(0, len(self.ip_addresses) - 1)
    return self.ip_addresses[proxy_index]
