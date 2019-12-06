import time
import pandas as pd
import time
import sys,os
import yaml
import argparse
from multiprocessing import Process
from hbp_nrp_virtual_coach.virtual_coach import VirtualCoach


def sim_start(experiment,server,configuration={}):
	sim = vc.launch_experiment(experiment)
	print "Configuring..."

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

	history = {'height':[],'reward':[],'total_reward':[]} #a very large dict contains all history
	history_total_reward = {'total_reward':[]} #only contains the total reward for each epoch, much faster to read.
	
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

		#--------------------------------------------------#
		#                      TODO                        #
		#--------------------------------------------------#
		sim.stop()
		while sim.get_state() != "stopped":
			pass


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
				curr_path = config_path + "/" + configurations.pop()
				print curr_path
				
				#load configurations from .yaml file into a python dictionary
				config = yaml.load(open(curr_path))

				server = servers.pop()

				#create a new process to run the simulation
				p = Process(target=sim_start, args=(experiment,server,config))
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