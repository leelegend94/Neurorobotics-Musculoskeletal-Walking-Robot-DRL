import time
import pandas as pd
import time
import sys,os
import yaml
import argparse
from multiprocessing import Process
from hbp_nrp_virtual_coach.virtual_coach import VirtualCoach


def sim_start(experiment,server,config_file_path):
	sim = vc.launch_experiment(experiment)
	print "Configuring..."

	#load configurations from .yaml file into a python dictionary
	config = yaml.load(open(config_file_path))

	tf_environment = sim.get_transfer_function('environment').splitlines()
	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!TODO!!!!!!!!!!!!!!!!!!!!!!!
	tf_ddpg = sim.get_transfer_function('fake_init_DRLagent').splitlines()#############
	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!TODO!!!!!!!!!!!!!!!!!!!!!!!

	#Substritue the first line of the transfer function with the configuration dict..
	tf_environment[0] = "CONFIGURATION = " + str(config)
	tf_ddpg[0] = "CONFIGURATION = " + str(config)

	"\n".join(tf_environment)
	"\n".join(tf_ddpg)

	sim.edit_transfer_function('environment',tf_environment)
	sim.edit_transfer_function('init_DRLagent',tf_ddpg)

	sim.start()

	conf_train = config['Training_Script']
	MAX_EP = int(conf_train.get("Max_Epoch",100))
	RESULT_SAV_PATH = conf_train.get("result_save_path", "./results")

	#init csv file for the whole training process
	history = pd.DataFrame(columns=['itr_idx','height','reward'])
	for ep in range(MAX_EP):
	#iteration over episodes
		nFailed = 0
		while True:
		#restart the simulation by stop&start, quit if failed for more than 15 times
			if nFailed>=15:
				print "Unable to launch the experiment, check the backend."
				sys.exit()
			elif: sim.get_state() == "stopped":
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
		while(itr_idx<5 and height>0.5 and height<1.5):
		#early terminate the simulation if it jump too high or fall down. the hight of pelvis is used here.
		#terminate the simulation when reaches maximum steps.

			#retrive current states from csv file
			csv_curr_stat = sim.get_last_run_csv_file('curr_stat.csv')
			lst_line = csv_curr_stat.splitlines()[-1].split(',') #last line of the csv, namely the newest states.
			if lst_line[0] != "itr_idx": #avoiding the case that the csv file contains only the header.
				#print lst_line
				itr_idx = int(lst_line[0])
				height = float(lst_line[1])
				#reward = float(lst_line[2])
			time.sleep(0.25)

		sim.stop()

		#transform csv_curr_stat from string to 2D-array
		data = csv_curr_stat.splitlines()
		data = list(map(lambda x: x.split(','),data))
		history = history.append(pd.DataFrame(data=data,columns=['itr_idx','height','reward']))

		while sim.get_state() != "stopped":
			pass

	#store the history, file name is the same as the config file's name
	pd.DataFrame(history).to_csv(RESULT_SAV_PATH+'/'+conf.split('/')[-1][:-5]+'.csv')

		#--------------------------------------------------#
		#                      TODO                        #
		#--------------------------------------------------#
		#eval
def main(experiment,config_path,environment,storage_username,storage_password):
	vc = VirtualCoach(environment=environment, storage_username=storage_username, storage_password=storage_password)
	vc.print_cloned_experiments()

	#retrive the list of availiable servers
	servers = vc.print_available_servers()
	if servers == []:
		print "No available server, exit."
		sys.exit()
	else:
		print len(servers)," server(s) available."

	#list of configuration files 
	configurations = os.listdir(CONFIG_PATH)
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
				p = Process(target=sim_start, args=(experiment,server,curr_config_path))
				p.start()
			else:
				print len(configurations)," configurations in queue. Waiting for available server"
				while vc.print_available_servers() == []:
					time.sleep(1)
				servers = vc.print_available_servers()



#----------------------------------------------------------------------#
parser = argparse.ArgumentParser(description='Parallel training script.')
parser.add_argument('--experiment','-x',help='name of the experiment to be launched. default: Neurorobotics-Musculoskeletal-Walking-Robot-DRL_0', default='Neurorobotics-Musculoskeletal-Walking-Robot-DRL_0')
parser.add_argument('--config_path','-c',help='path to configuration files. default: ./simulation_config',default='./simulation_config')
parser.add_argument('--environment','-e',help='environment of NRP backend. default: local', default='local')
parser.add_argument('--storage_username','-n',help='NRP storage user name. default: nrpuser', default='nrpuser')
parser.add_argument('--storage_password','-p',help='NRP storage password. default: password', default='password')
args = parser.parse_args()

if __name__ == "__main__":
	if args.config_path[-1] == '/':
		args.config_path = args.config_path[:,-1]
	main(args.experiment,args.config_path,args.environment,args.storage_username,args.storage_password)