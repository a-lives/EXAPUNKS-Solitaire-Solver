import os

root = "./templates/"

paths = os.listdir(root)

for path in paths:
    os.mkdir(root + path.split(".")[0])