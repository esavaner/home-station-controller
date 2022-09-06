
import json
import network
import socket
import time

from machine import Pin, ADC

ssid = 'NETWORK_LOGIN'
password = 'NETWORK_PASSWORD'
allowed_hosts = ['192.168.', 'localhost:3000']


def readTemp(pin):
    try:
        sensor = ADC(pin)
        conversion_factor = 3.3 / (65535)
        reading = sensor.read_u16() * conversion_factor
        temp = 27 - (reading - 0.706)/0.001721
        return temp
    except:
        return '-.-'


def parseURL(url):
    if '?' not in url:
        return url, None
    path, par = url.split('?')
    params = {}
    for p in par.split('&'):
        k, val = p.split('=')
        params[k] = val
    return path, params


def parseRequest(request):
    first, _ = request.decode('utf-8').split('\r\n', 1)
    _, last = request.decode('utf-8').split('\r\n\r\n', 1)
    body = json.loads(last.replace('\r\n', '')) if last is not '' else {}
    method, url, _ = first.split(' ')
    path, params = parseURL(url)
    return method, path, params, body


def readSensors(sensors):
    for sensor in sensors:
        p = int(sensor['pin'])
        if sensor['type'] is "temp":
            t = readTemp(p)
            sensor['value'] = t
        else:
            pin = Pin(p, Pin.OPEN_DRAIN)
            pin.value(1)
            sensor['value'] = not bool(pin.value())
    print(sensors)
    return sensors


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

ip = ''
if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    ip = wlan.ifconfig()[0]
    print('ip = ' + ip)


addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(5)

print('listening on', addr)

while True:
    try:
        cl, addr = s.accept()
        print('client connected from', addr)
        request = cl.recv(1024)

        method, path, params, body = parseRequest(request)
        print(method, path, params, body)
        response = None
        if path == '/read':
            response = readSensors(body['sensors'])
        elif path == '/check':
            response = str({'status': 'ok'})
        elif path == '/temp':
            response = readTemp(4)

        host = addr[0] if any(h in addr[0] for h in allowed_hosts) else ip
        cl.send(
            f'HTTP/1.0 200 OK\r\nContent-type: application/json\r\nAccess-Control-Allow-Headers: Origin, X-Requested-With, Content-Type, Accept\r\nAccess-Control-Allow-Origin: *\r\n\r\n')
        cl.send(json.dumps(response))
        cl.close()

    except OSError as e:
        cl.close()
        print('connection closed')
