# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os, shutil

# /Users/lane
gen_path  = os.path.expanduser('~') # your home path

# /Users/lane/.bash_profile
bash_path = "{}/.bash_profile".format(gen_path) # your .bash_profile path

# /Users/lane/temp
temp_path = "{}/temp".format(gen_path) # temp file path

# /Users/lane/Github/wb/src/wb.py
wb_path = "{}/src/wb.py".format(os.path.abspath('..')) # wb.py file path

# alias wb='python /Users/lane/Github/wb/src/wb.py'
alias = "alias wb='python {}'\n".format(wb_path) # the alias command


fr = open(bash_path, 'r')
fw = open(temp_path, 'w')

line = True; add_alias = True
while line:
    line = fr.readline()
    fw.write(line)
    if 'wb.py' in line: # if wb.py already in .bash_profile, no need to add alias command
        add_alias = False
        intalled_command = line
    else:
        pass

if add_alias: # if True, write alias command at the end of the file
    fw.write(alias)
else:
    pass

fr.close()
fw.close()

shutil.copy(temp_path, bash_path) # replace .bash_profile by temp file
os.remove(temp_path) # delete temp file

if add_alias:
    print("The command below:\n\n  {}\n\nis successfully added to .bash_profile\n".format(alias[:-1]))
else:
    print("The command below:\n\n  {}\n\nis detected, installing has canceled with nothing happen".format(intalled_command[:-1]))

try:
    raw_input()
except:
    pass

