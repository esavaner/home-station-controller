
import json
import network
import socket
import time

from machine import Pin, ADC

ssid = 'Jamnik'
password = '41443170'

sensors = []


def readTemp():
    sensor = ADC(4)
    conversion_factor = 3.3 / (65535)
    reading = sensor.read_u16() * conversion_factor
    temp = 27 - (reading - 0.706)/0.001721
    return temp


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


def readSensors():
    output = {}
    for sensor in sensors:
        print(sensor)
        output[sensor['name']] = sensor['pin'].value()
    return output


def addSensors(params):
    for k, val in params.items():
        sensor = {}
        pin = Pin(int(val), Pin.OPEN_DRAIN)
        # pin.value(1)
        sensor['pin'] = pin
        sensor['name'] = k
        sensors.append(sensor)
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

if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print('ip = ' + status[0])


addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(5)

print('listening on', addr)

print(readTemp())

while True:
    try:
        cl, addr = s.accept()
        print('client connected from', addr)
        request = cl.recv(1024)

        method, path, params, body = parseRequest(request)
        print(method, path, params, body)
        response = None
        if path == '/read':
            response = readSensors()
        elif path == '/add':
            response = addSensors(params)
        elif path == '/check':
            response = str({status: 'ok'})

        cl.send('HTTP/1.0 200 OK\r\nContent-type: application/json\r\n\r\n')
        cl.send(str(response))
        cl.close()

    except OSError as e:
        cl.close()
        print('connection closed')
