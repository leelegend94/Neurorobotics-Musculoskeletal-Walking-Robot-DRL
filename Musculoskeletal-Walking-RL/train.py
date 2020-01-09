import time
import pandas as pd
import time
import sys,os
import yaml
import argparse
import seaborn as sns
import matplotlib.pyplot as plt
from multiprocessing import Process
from hbp_nrp_virtual_coach.virtual_coach import VirtualCoach


def sim_start(experiment,server,config_file_path,results_save_path):
	sim = vc.launch_experiment(experiment)
	print "Configuring..."

	#load configurations from .yaml file into a python dictionary
	config = yaml.load(open(config_file_path))

	tf_environment = sim.get_transfer_function('environment').splitlines()
	tf_ddpg = sim.get_transfer_function('init_DRLagent').splitlines()
	tf_controller = sim.get_transfer_function('controller').splitlines()

	#Substritue the first line of the transfer function with the configuration dict..
	tf_environment[0] = "CONFIGURATION = " + str(config)
	tf_ddpg[0] = "CONFIGURATION = " + str(config)
	tf_controller[0] = "CONFIGURATION = " + str(config)

	tf_environment = "\n".join(tf_environment)
	tf_ddpg = "\n".join(tf_ddpg)
	tf_controller = "\n".join(tf_controller)

	sim.edit_transfer_function('environment',tf_environment)
	sim.edit_transfer_function('init_DRLagent',tf_ddpg)
	sim.edit_transfer_function('controller',tf_controller)
	
	sim.start()

	conf_train = config['Training_Script']
	MAX_EP = int(conf_train.get("Max_Epoch",1000))
	MAX_ITER = int(conf_train.get("Max_Iteration_per_Epoch",200))

	print "Max Epochs: ",MAX_EP
	print "Max Iterations: ",MAX_ITER

	#init csv file for the whole training process
	history = pd.DataFrame(columns=['itr_idx','height','reward'])
	for ep in range(MAX_EP):
	#iteration over episodes
		print "Current Ep. : ",ep+1
		nFailed = 0
		while True:
		#restart the simulation by stop&start, quit if failed for more than 15 times
			if nFailed>=15:
				print "Unable to launch the experiment, check the backend."
				sys.exit()
			elif sim.get_state() == "stopped":
				try:
					sim = vc.launch_experiment(experiment)
					sim.start()
					break
				except KeyboardInterrupt:
					sys.exit()
				except Exception as e:
					print "Great Job! got an error: ", e
					nFailed += 1
					print "number of trial: ", nFailed, ", try it again later."
					time.sleep(1)
			else:
				break

		itr_idx = 0
		height = 1
		total_reward = 0
		while(itr_idx<MAX_ITER and height>0.6 and height<1.5):
		#early terminate the simulation if it jump too high or fall down. the hight of pelvis is used here.
		#terminate the simulation when reaches maximum steps.

			#retrive current states from csv file
			csv_curr_stat = sim.get_last_run_csv_file('curr_stat.csv')
			lst_line = csv_curr_stat.splitlines()[-1].split(',') #last line of the csv, namely the newest states.
			if lst_line[0] != "itr_idx": #avoiding the case that the csv file contains only the header.
				print lst_line
				itr_idx = int(lst_line[0])
				height = float(lst_line[1])
				#reward = float(lst_line[2])
				print itr_idx
			time.sleep(0.25)

		sim.stop()

		#transform csv_curr_stat from string to 2D-array
		data = csv_curr_stat.splitlines()
		data = list(map(lambda x: x.split(','),data))
		data.pop(0)# remove csv header
		history = history.append(pd.DataFrame(data=data,columns=['itr_idx','height','reward']),ignore_index=True)

		while sim.get_state() != "stopped":
			pass
	#modify this, so that it saves before it is finished.
	#store the history, file name is the same as the config file's name
	history['itr_idx'] = history['itr_idx'].astype(int)
	history['height'] = history['height'].astype(float)
	history['reward'] = history['reward'].astype(float)
	history.to_csv(results_save_path+'/'+config_file_path.split('/')[-1][:-5]+'.csv')

	sns.lineplot(x=history.index,y="reward",data = history)
	plt.show()
	print "1 job finished!"
	return

def evaluate(results_save_path):
	import seaborn as sns
	results = os.listdir(results_save_path)
	best_config = None
	best_data = None
	largest_reward = -float('Inf')
	for result in results:
		curr_config = result[:-4]
		data = pd.read_csv(results_save_path+'/'+result)
		avg_reward = data['reward'][-100:].astype(float).mean() #average reward for last 100 steps
		if avg_reward >= largest_reward:
			best_config = curr_config
			largest_reward = avg_reward
			best_data = data
	sns.kdeplot(best_data.reward)
	print "the best configuration is: ",best_config


def main(experiment,config_path,results_save_path,environment,storage_username,storage_password):
	vc = VirtualCoach(environment=environment, storage_username=storage_username, storage_password=storage_password)
	global vc
	vc.print_cloned_experiments()

	#retrive the list of availiable servers
	servers = vc.print_available_servers()
	if servers == []:
		print "No available server, exit."
		sys.exit()
	else:
		print len(servers)," server(s) available."

	#list of configuration files 
	configurations = os.listdir(config_path)
	configurations = list(filter(lambda x: x.endswith('yaml'), configurations)) #only yaml file should be in the list

	while True:
		if len(configurations) > 0:
		#check whether there is configuration not being simulated yet.
			if len(servers) > 0:
			#allocate an availiable server to the simulation, if no server is available, just wait. 
				curr_config_path = config_path + "/" + configurations.pop()
				print curr_config_path

				server = servers.pop()

				#create a new process to run the simulation
				p = Process(target=sim_start, args=(experiment,server,curr_config_path,results_save_path))
				p.start()
			else:
				print len(configurations)," configurations in queue. Waiting for available server"
				while vc.print_available_servers() == []:
					time.sleep(1)
				servers = vc.print_available_servers()
		else:
			break
	p.join()
	print "Training Complete!"
	#evaluate(results_save_path)


#----------------------------------------------------------------------#
parser = argparse.ArgumentParser(description='Parallel training script.')
parser.add_argument('--experiment','-x',help='name of the experiment to be launched. default: Neurorobotics-Musculoskeletal-Walking-Robot-DRL_0', default='Neurorobotics-Musculoskeletal-Walking-Robot-DRL_0')
parser.add_argument('--config_path','-c',help='path to configuration files. default: ./simulation_config',default='./simulation_config')
parser.add_argument('--results_path','-r',help='path to simulatuion results. default: ./results', default='./results')
parser.add_argument('--environment','-e',help='environment of NRP backend. default: local', default='local')
parser.add_argument('--storage_username','-n',help='NRP storage user name. default: nrpuser', default='nrpuser')
parser.add_argument('--storage_password','-p',help='NRP storage password. default: password', default='password')
args = parser.parse_args()

if __name__ == "__main__":
	if args.config_path[-1] == '/':
		args.config_path = args.config_path[:,-1]
	main(args.experiment,args.config_path,args.results_path,args.environment,args.storage_username,args.storage_password)