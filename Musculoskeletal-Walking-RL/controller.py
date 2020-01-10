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
@nrp.MapVariable("reward_",initial_value=None,scope=nrp.GLOBAL)
@nrp.MapVariable("reward",initial_value=None,scope=nrp.GLOBAL)
@nrp.MapVariable("ResetSimulationSrv",initial_value=None)
@nrp.MapVariable("conf",initial_value=CONFIGURATION)
#@nrp.MapVariable("t_", initial_value=0)

@nrp.MapVariable("nb_itr",initial_value=1)
@nrp.MapVariable("nb_ep",initial_value=1, scope=nrp.GLOBAL)
@nrp.MapVariable("MAX_ITR",initial_value=CONFIGURATION.get('Training',{}).get('Max_Iteration_per_Epoch',200))

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
def controller(t, agent, conf, observation, MAX_ITR, reward, reward_, nb_ep, nb_itr, ResetSimulationSrv, bifemlh_l,bifemlh_r,bifemsh_l,bifemsh_r,glut_max2_l,glut_max2_r,iliacus_l,iliacus_r,lat_gas_l,lat_gas_r,med_gas_l,med_gas_r,rect_fem_l,rect_fem_r,semimem_l,semimem_r,semiten_l,semiten_r,soleus_l,soleus_r,tib_ant_l,tib_ant_r,vas_lat_l,vas_lat_r):
	if ResetSimulationSrv.value is None:
		import rospy
		from std_srvs.srv import Empty
		ResetSimulationSrv.value = rospy.ServiceProxy("/gazebo/reset_simulation",Empty)

	if agent.value is not None and observation.value is not None:

		if observation.value[2] >= 0.7 and nb_itr.value<MAX_ITR.value:

			clientLogger.info("FORWARD PASS")
			import math
			import numpy as np

			muscles_list = [bifemlh_l,bifemlh_r,bifemsh_l,bifemsh_r,glut_max2_l,glut_max2_r,iliacus_l,iliacus_r,lat_gas_l,lat_gas_r,med_gas_l,med_gas_r,rect_fem_l,rect_fem_r,semimem_l,semimem_r,semiten_l,semiten_r,soleus_l,soleus_r,tib_ant_l,tib_ant_r,vas_lat_l,vas_lat_r]

			action = agent.value.forward(np.array(observation.value))

			for idx,muscle in enumerate(muscles_list):
				muscle.send_message(std_msgs.msg.Float64(action[idx]))

			#learn from the raeward
			reward.value = reward_.value-sum(action)/24
			agent.value.backward(reward.value)
			agent.value.step = agent.value.step + 1

			clientLogger.info('BACKWARD PASS, step ', agent.value.step)
			clientLogger.info('itr. No. ', nb_itr.value)
			clientLogger.info('ep. No. ', nb_ep.value)
			clientLogger.info('Amount of reward ', reward.value)
			
			if agent.value.step%10 == 0:
				import os
				WeightsPATH = conf.value.get('DDPG_Agent',{}).get('weights_sav_path',"~/.opt/weights")
				conf_name = conf.value.get('NAME','default')
				time_stamp = conf.value.get('START_TIME_STAMP','20xx-yy-dd-hh-mm-ss')
				full_name = time_stamp+"_"+conf_name+"_ddpg_weights.h5"
				agent.value.save_weights(os.path.expanduser(WeightsPATH+"/"+full_name))
				clientLogger.info('weights saved in ', full_name, " (with extra suffix)")
			nb_itr.value = nb_itr.value + 1
		else:
			clientLogger.info(str(observation.value[2]))
			clientLogger.info("failed, restart")
			from std_srvs.srv import Empty
			ResetSimulationSrv.value()
			nb_itr.value = 0
			nb_ep.value = nb_ep.value + 1

		#t_.value = t
