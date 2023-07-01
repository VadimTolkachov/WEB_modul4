import json
import pathlib


def send_to_JSON(data:dict = {}):
    path = pathlib.Path('data.json')
    
    if not path.exists():
        with open('data.json', 'w') as f:
            json.dump(data, f)

    else:
        
        with open('data.json') as f:
            js = json.load(f)
         
        js.update(data)  
        
        with open('data.json', 'w') as f:
            json.dump(js, f)

    

send_to_JSON({'1':2})



