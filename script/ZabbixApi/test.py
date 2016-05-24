


import json

json_data = {
    "method":"host.get",
    "params":{
           "output":"extend", 
    }
}

json_base = {
    "jsonrpc":"2.0",
    "auth":"xzcxz",
    "id":1,
    "params":{
     "wye":"age",
    }
}

json_data.update(json_base)

print json_data