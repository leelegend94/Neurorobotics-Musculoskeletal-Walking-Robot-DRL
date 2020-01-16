import os
import time, datetime
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
def get_latest_csv(path,config_name):
	terms = os.listdir(path)
	terms = list(filter(lambda x: x.startswith("csv_records"), terms))
	timeStamps = [term[12:] for term in terms]

	timeStamps_u = [time.mktime(datetime.datetime.strptime(ts, "%Y-%m-%d_%H-%M-%S").timetuple()) for ts in timeStamps]
	#idx_latest = timeStamps_u.index(max(timeStamps_u))
	idx_latest = sorted(range(len(timeStamps_u)),key = lambda k: timeStamps_u[k])

	while True:
		folder_name = terms[idx_latest.pop()]
		path2csv = path+"/"+folder_name+"/"+"history_"+config_name+".csv"
		if os.path.isfile(path2csv):
			break
		if idx_latest == []:
			print "can't find "+path2csv
			import sys
			sys.exit()

	return path2csv


CONFIG_PATH = os.path.expanduser("~/Documents/Musculoskeletal-Walking-RL/Musculoskeletal-Walking-RL/simulation_config")
CSV_PATH = os.path.expanduser('~/Documents/Musculoskeletal-Walking-RL/Musculoskeletal-Walking-RL')

configurations = os.listdir(CONFIG_PATH)
configurations = list(filter(lambda x: x.endswith('yaml'), configurations)) #only yaml file should be in the list
names = [conf[:-5] for conf in configurations]

avg_rewards = []
for name in names:
	path2csv = get_latest_csv(CSV_PATH,name)
	df = pd.read_csv(path2csv)
	avg_rewards.append(np.mean(df['Reward']))

print names[avg_rewards.index(max(avg_rewards))] + " has the highest reward"

sns.lineplot(x=df.index,y="Reward",data=df)
sns.lineplot(x=df.index,y="Z",data=df)
plt.show()