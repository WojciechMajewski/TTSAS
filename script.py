# %%
import os
import json
import re
import urllib.request

# %%
def uniquify(path):
    filename, extension = os.path.splitext(path)
    counter = 1

    while os.path.exists(path):
        path = filename + " (" + str(counter) + ")" + extension
        counter += 1

    return path

# %%
with open("config.txt") as f:
    config_data = f.read()

workshop_dir = re.findall(r'workshop_dir\s*=\s*(.+)', config_data)[0]

key_phrase = re.findall(r'key_phrase\s*=\s*(.+)', config_data)[0]

retrieve_pdf = re.findall(r'retrieve_pdf\s*=\s*(.+)', config_data)[0]
if retrieve_pdf.lower() == "yes" or retrieve_pdf.lower() == "y" or retrieve_pdf.lower() == "true":
    retrieve_pdf = True
else:
    retrieve_pdf = False

retrieve_image = re.findall(r'retrieve_images?\s*=\s*(.+)', config_data)[0]
if retrieve_image.lower() == "yes" or retrieve_image.lower() == "y" or retrieve_image.lower() == "true":
    retrieve_image = True
else:
    retrieve_image = False

# %%
f = []
for (dirpath, dirnames, filenames) in os.walk(workshop_dir):
    f.extend(filenames)
    break

jsons = [i for i in f if i[-5:] == ".json" and i != "WorkshopFileInfos.json"]


mod_numerical_name = "none"

for json_file in jsons:
    # Opening JSON file
    f = open(os.path.join(workshop_dir, json_file), encoding="UTF-8")
    
    # returns JSON object as 
    # a dictionary
    data = json.load(f)

    # Closing file
    f.close()
    

    if key_phrase in data['GameMode']:
        game_name = data['GameMode']
        print(game_name)
        mod_numerical_name = json_file
        print(json_file)
    

# %%
assert mod_numerical_name != "none"

# %%
image_links = []
pdf_links = []
known_links = set()

### Read whole as string and regex find all urls/ImageURL
with open(os.path.join(workshop_dir, mod_numerical_name), encoding="UTF-8") as f:
    file_text = f.read()

lines = file_text.split("\n")

if retrieve_image:
    for index, row in enumerate(lines):
        link = re.findall(r'\s+"ImageURL":\s*"(.+)"', row)
        if len(link) != 1:
            continue
        if link[0] in known_links:
            continue
        else:
            known_links.add(link[0])
        
        for i in range(index, 0, -1):
            name = re.findall(r'\s+"(Name|Nickname|GUID)":\s+"(.+)"', lines[i])
            if len(name) != 1 or len(name[0]) != 2:
                continue
            image_links += [(name[0][1], link[0])]
            break

if retrieve_pdf:
    for index, row in enumerate(lines):
        link = re.findall(r'\s+"PDFUrl":\s*"(.+)"', row)
        if len(link) != 1:
            continue
        if link[0] in known_links:
            continue
        else:
            known_links.add(link[0])
        
        for i in range(index, 0, -1):
            name = re.findall(r'\s+"(Name|Nickname|GUID)":\s+"(.+)"', lines[i])
            if len(name) != 1 or len(name[0]) != 2:
                continue
            pdf_links += [(name[0][1], link[0])]
            break


# %%
# Directory 
directory = game_name.lower()
directory = ''.join(c for c in directory if c.isalnum() or c == " ")
directory = directory.replace(" ", "_")
directory += "_ASSETS"
  
# Current directory
current_dir = os.getcwd()
  
# Path 
asset_dir_path = os.path.join(current_dir, "Exported", directory) 

# %%
try:  
    os.mkdir(os.path.join(current_dir, "Exported"))
except OSError as error:  
    print(error)

try:  
    os.mkdir(asset_dir_path)
except OSError as error:  
    print(error)

# %%
for asset in image_links:
    name = asset[0]
    name = ''.join(c for c in name if c.isalnum() or c == " ")
    link = asset[1]
    path = uniquify(os.path.join(asset_dir_path, name + ".jpg"))
    urllib.request.urlretrieve(link, path)

for asset in pdf_links:
    name = asset[0]
    name = ''.join(c for c in name if c.isalnum() or c == " ")
    link = asset[1]
    path = uniquify(os.path.join(asset_dir_path, name + ".pdf"))
    urllib.request.urlretrieve(link, path)
    
    