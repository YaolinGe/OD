"""
This function checks if a given folder path exists, if not, create one. 

Author: Yaolin Ge
Email: geyaolin@gmail.com
Date: 2023-11-23
"""

import os

def checkfolder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
        print("Folder %s created." % folder)
    else:
        print("Folder %s already exists." % folder)
    pass
