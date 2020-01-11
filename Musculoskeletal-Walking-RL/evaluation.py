import os
import time, datetime

def get_latest_csv(path):
	terms = os.listdir(path)
	terms = list(filter(lambda x: x.startswith("csv_records"), terms))
	timeStamps = [term[12:] for term in terms]

	timeStamps_u = [time.mktime(datetime.datetime.strptime(ts, "%Y-%m-%d_%H-%M-%S").timetuple()) for ts in timeStamps]
	idx_latest = timeStamps_u.index(max(timeStamps_u))
	
	folder_name = terms[idx_latest]

	files = os.listdir(path+"/"+folder_name)
	files = list(filter(lambda x: x.endswith("csv"), files))

	path2csv = [path+"/"+folder_name+"/"+file for file in files]

	return path2csv

path2csv = get_latest_csv(os.path.expanduser('~/Documents/Musculoskeletal-Walking-RL/Musculoskeletal-Walking-RL'))
df = pd.read_csv("./history_test.csv")