with open('backend/simple_web_server.py', 'rb') as f:
    c = f.read()
c = c.replace(b'port = 38127  # ', b'port = 38125  # ')
with open('backend/simple_web_server.py', 'wb') as f:
    f.write(c)
print('backend restored to 38125')
