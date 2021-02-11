import re
file = open("setup.txt")
output = open("output.txt", "w")

role_name = ""
for line in file.readlines():
    if "document.querySelector" in line:
        property = re.search('".*":', line).group(0)
        match = re.search('document.querySelector\(".*', line).group(0)
        if ".checked," in match:
            output.write(f'{match[:-1]}=data["setup"]["options"]["role_setting"][{role_name}][{property[:-1]}];\n')
        elif ".value" in match:
            match = match.replace('"', '`')
            checked_start = match.index(']')+1
            role_name = role_name.replace('"', "'", 2)
            property = property[:-1].replace('"', "'", 2)
            match = match[:checked_start]
            match += "[value="
            match += '"'
            match += "${data['setup']['options']['role_setting']"
            match += f"[{role_name}]"
            match += f'[{property}]'
            match += '}"`)'
            output.write(f'{match}.checked = true;\n')
    elif ":" in line:
        role_name = re.search('".*"', line).group(0)
file.close()
