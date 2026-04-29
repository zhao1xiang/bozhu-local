with open('backend/simple_web_server.py', 'rb') as f:
    content = f.read()
content = content.replace(b'port = 38126  # ', b'port = 38125  # ')
with open('backend/simple_web_server.py', 'wb') as f:
    f.write(content)

with open('backend/simple_web_server.py', 'rb') as f:
    if b'38125' in f.read():
        print('OK: simple_web_server.py -> 38125')
