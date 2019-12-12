CONFIGURATION = {}
"""
This module contains the transfer function which is responsible for determining the muscle movements of the myoarm
"""
from geometry_msgs.msg import PoseArray
from geometry_msgs.msg import Vector3
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64

@nrp.MapVariable("agent", initial_value=None, scope=nrp.GLOBAL)
@nrp.MapVariable("observation",initial_value=None,scope=nrp.GLOBAL)
@nrp.MapVariable("reward",initial_value=None,scope=nrp.GLOBAL)
@nrp.MapVariable("ResetSimulationSrv",initial_value=None,scope=nrp.GLOBAL)
@nrp.MapVariable("Height",initial_value=None,scope=nrp.GLOBAL)
@nrp.MapVariable("conf",initial_value=CONFIGURATION)
@nrp.MapVariable("t_", initial_value=0)
#muscles

@nrp.MapRobotPublisher('bifemlh_l', Topic('/gazebo_muscle_interface/body/bifemlh_l/cmd_activation',Float64))
@nrp.MapRobotPublisher('bifemlh_r', Topic('/gazebo_muscle_interface/body/bifemlh_r/cmd_activation',Float64))
@nrp.MapRobotPublisher('bifemsh_l', Topic('/gazebo_muscle_interface/body/bifemsh_l/cmd_activation',Float64))
@nrp.MapRobotPublisher('bifemsh_r', Topic('/gazebo_muscle_interface/body/bifemsh_r/cmd_activation',Float64))
@nrp.MapRobotPublisher('glut_max2_l', Topic('/gazebo_muscle_interface/body/glut_max2_l/cmd_activation',Float64))
@nrp.MapRobotPublisher('glut_max2_r', Topic('/gazebo_muscle_interface/body/glut_max2_r/cmd_activation',Float64))
@nrp.MapRobotPublisher('iliacus_l', Topic('/gazebo_muscle_interface/body/iliacus_l/cmd_activation',Float64))
@nrp.MapRobotPublisher('iliacus_r', Topic('/gazebo_muscle_interface/body/iliacus_r/cmd_activation',Float64))
@nrp.MapRobotPublisher('lat_gas_l', Topic('/gazebo_muscle_interface/body/lat_gas_l/cmd_activation',Float64))
@nrp.MapRobotPublisher('lat_gas_r', Topic('/gazebo_muscle_interface/body/lat_gas_r/cmd_activation',Float64))
@nrp.MapRobotPublisher('med_gas_l', Topic('/gazebo_muscle_interface/body/med_gas_l/cmd_activation',Float64))
@nrp.MapRobotPublisher('med_gas_r', Topic('/gazebo_muscle_interface/body/med_gas_r/cmd_activation',Float64))
@nrp.MapRobotPublisher('rect_fem_l', Topic('/gazebo_muscle_interface/body/rect_fem_l/cmd_activation',Float64))
@nrp.MapRobotPublisher('rect_fem_r', Topic('/gazebo_muscle_interface/body/rect_fem_r/cmd_activation',Float64))
@nrp.MapRobotPublisher('semimem_l', Topic('/gazebo_muscle_interface/body/semimem_l/cmd_activation',Float64))
@nrp.MapRobotPublisher('semimem_r', Topic('/gazebo_muscle_interface/body/semimem_r/cmd_activation',Float64))
@nrp.MapRobotPublisher('semiten_l', Topic('/gazebo_muscle_interface/body/semiten_l/cmd_activation',Float64))
@nrp.MapRobotPublisher('semiten_r', Topic('/gazebo_muscle_interface/body/semiten_r/cmd_activation',Float64))
@nrp.MapRobotPublisher('soleus_l', Topic('/gazebo_muscle_interface/body/soleus_l/cmd_activation',Float64))
@nrp.MapRobotPublisher('soleus_r', Topic('/gazebo_muscle_interface/body/soleus_r/cmd_activation',Float64))
@nrp.MapRobotPublisher('tib_ant_l', Topic('/gazebo_muscle_interface/body/tib_ant_l/cmd_activation',Float64))
@nrp.MapRobotPublisher('tib_ant_r', Topic('/gazebo_muscle_interface/body/tib_ant_r/cmd_activation',Float64))
@nrp.MapRobotPublisher('vas_lat_l', Topic('/gazebo_muscle_interface/body/vas_lat_l/cmd_activation',Float64))
@nrp.MapRobotPublisher('vas_lat_r', Topic('/gazebo_muscle_interface/body/vas_lat_r/cmd_activation',Float64))

@nrp.Neuron2Robot()
def controller(t, t_, agent, conf, observation, reward, Height, ResetSimulationSrv, bifemlh_l,bifemlh_r,bifemsh_l,bifemsh_r,glut_max2_l,glut_max2_r,iliacus_l,iliacus_r,lat_gas_l,lat_gas_r,med_gas_l,med_gas_r,rect_fem_l,rect_fem_r,semimem_l,semimem_r,semiten_l,semiten_r,soleus_l,soleus_r,tib_ant_l,tib_ant_r,vas_lat_l,vas_lat_r):
	if agent.value is not None and observation.value is not None and t-t_.value>0.05:

		if observation.value[2] >= 0.6:

			clientLogger.info("FORWARD PASS")
			import math
			import numpy as np

			muscles_list = [bifemlh_l,bifemlh_r,bifemsh_l,bifemsh_r,glut_max2_l,glut_max2_r,iliacus_l,iliacus_r,lat_gas_l,lat_gas_r,med_gas_l,med_gas_r,rect_fem_l,rect_fem_r,semimem_l,semimem_r,semiten_l,semiten_r,soleus_l,soleus_r,tib_ant_l,tib_ant_r,vas_lat_l,vas_lat_r]

			action = agent.value.forward(np.array(observation.value))

			for idx,muscle in enumerate(muscles_list):
				muscle.send_message(std_msgs.msg.Float64(action[idx]))

			#learn from the reward
			agent.value.backward(reward.value)
			agent.value.step = agent.value.step + 1

			clientLogger.info('BACKWARD PASS, step ', agent.value.step)
			clientLogger.info('Amount of reward ', reward.value)
			
			if agent.value.step%10 == 0:
				clientLogger.info('saving weights')
				import os
				WeightsPATH = conf.value.get('DDPG_Agent',{}).get('weights_sav_path',"~/.opt/weights")
				agent.value.save_weights(os.path.expanduser(WeightsPATH+"/ddpg_weights.h5"), overwrite=True)
				#agent.value.save_weights("/home/zhenyuli/.opt/weights/ddpg_weights.h5", overwrite=True)
		else:
			clientLogger.info(str(observation.value[2]))
			clientLogger.info("failed, waiting for restart")

		t_.value = t
