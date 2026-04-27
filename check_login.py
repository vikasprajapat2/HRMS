import urllib.request
try:
    req = urllib.request.urlopen('http://127.0.0.1:5000/login')
    print('Status:', req.getcode())
except Exception as e:
    print('Error:', e)
