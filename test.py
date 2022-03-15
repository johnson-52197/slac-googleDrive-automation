from matplotlib.font_manager import json_load

old_fileList = json_load('client_secrets.json')

# print(type(old_fileList))


import json
 
with open('client_secrets.json', "r") as f:
    data = json.loads(f.read())
# Reading from file

print(type(data))
