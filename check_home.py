import urllib.request
try:
    req = urllib.request.urlopen('http://127.0.0.1:5000/')
    print('Status:', req.getcode())
    print(req.read().decode()[:200])
except Exception as e:
    print('Error:', e)
