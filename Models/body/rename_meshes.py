import os

path = "./meshes"

files = os.listdir(path)

for file in files:
	if file[-8:] == ".col.dae":
		print(file)
		file_ = file[:-8] + "_col.dae"
		os.rename(path+"/"+file,path+"/"+file_)