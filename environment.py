CONFIGURATION = {}
#REWARD_FUNC = "5*link_vlin[0].x-link_vlin[0].y-2*link_vlin[0].z-1"
import rospy

rospy.wait_for_service("/gazebo/get_joint_properties")
rospy.wait_for_service("/gazebo/get_link_properties")
rospy.wait_for_service("/gazebo/get_link_state")

@nrp.MapVariable("conf",initial_value=CONFIGURATION)
@nrp.MapVariable("observation",initial_value=None,scope=nrp.GLOBAL)
@nrp.MapVariable("reward",initial_value=None,scope=nrp.GLOBAL)
@nrp.MapVariable("Height",initial_value=None,scope=nrp.GLOBAL)
@nrp.MapVariable("ActiBelt_Data",initial_value=None,scope=nrp.GLOBAL)
@nrp.MapVariable("GetJointPropertiesSrv",initial_value=None)
@nrp.MapVariable("GetLinkPropertiesSrv",initial_value=None)
@nrp.MapVariable("GetLinkStateSrv",initial_value=None)
@nrp.MapVariable("ResetSimulationSrv",initial_value=None,scope=nrp.GLOBAL)
@nrp.MapVariable("link_mass",initial_value=None)

@nrp.Robot2Neuron()
def environment(t, conf, observation, reward, Height, ActiBelt_Data, link_mass, GetJointPropertiesSrv,GetLinkPropertiesSrv,GetLinkStateSrv,ResetSimulationSrv):
	import rospy
	joints = ["hip_r","hip_l","knee_r","knee_l","ankle_r","ankle_l"]
	links = ["pelvis","torso","femur_r","femur_l","tibia_l","tibia_r","talus_r","talus_l","toes_r","toes_l","ActiBelt"]
	if GetJointPropertiesSrv.value is None:
		from gazebo_msgs.srv import GetJointProperties
		GetJointPropertiesSrv.value = rospy.ServiceProxy("/gazebo/get_joint_properties", GetJointProperties)

	if GetLinkPropertiesSrv.value is None:
		from gazebo_msgs.srv import GetLinkProperties
		GetLinkPropertiesSrv.value = rospy.ServiceProxy("/gazebo/get_link_properties", GetLinkProperties)

	if GetLinkStateSrv.value is None:
		from gazebo_msgs.srv import GetLinkState
		GetLinkStateSrv.value = rospy.ServiceProxy("/gazebo/get_link_state",GetLinkState)

	if ResetSimulationSrv is None:
		from cle_ros_msgs.srv import ResetSimulation
		ResetSimulationSrv.value = rospy.ServiceProxy("/ros_cle_simulation/0/reset",ResetSimulation)

	if link_mass.value is None:
		link_mass.value = []
		for link in links:
			try:
				resp = GetLinkPropertiesSrv.value(link)
			except rospy.ServiceException, e:
				print "Service call failed: %s"%e
			link_mass.value.append(resp.mass)

	def update(joints,links):

		joint_pos = []
		joint_vel = []
		for joint in joints:
			try:
				resp = GetJointPropertiesSrv.value(joint)
			except rospy.ServiceException, e:
				print "Service call failed: %s"%e
			#joint_pos.append([resp.position.x,resp.position.y,resp.position.z])
			joint_pos.append(resp.position[0])
			joint_vel.append(resp.rate[0])

		link_pos = []
		link_ori = []
		link_vlin = []
		link_vang = []
		for link in links:
			try:
				resp = GetLinkStateSrv.value(link,"link")
			except rospy.ServiceException, e:
				print "Service call failed: %s"%e
			#link_pos.append([resp.link_state.pose.position.x,resp.link_state.pose.position.y,resp.link_state.pose.position.z])
			#link_vel.append([resp.link_state.twist.linear.x,resp.link_state.twist.linear.y,resp.link_state.twist.linear.z])
			link_pos.append(resp.link_state.pose.position)
			link_ori.append(resp.link_state.pose.orientation)
			link_vlin.append(resp.link_state.twist.linear)
			link_vang.append(resp.link_state.twist.angular)

		ActiBelt_Data.value = [link_pos.pop(),link_ori.pop(),link_vlin.pop(),link_vang.pop()]

		#get observation
		observation = []

		#pelvis pos 7
		observation += [link_pos[0].x,link_pos[0].y,link_pos[0].z,link_ori[0].x,link_ori[0].y,link_ori[0].z,link_ori[0].w]
		Height = link_pos[0].z
		#clientLogger.info([link_pos[0].x,link_pos[0].y,link_pos[0].z,link_ori[0].x,link_ori[0].y,link_ori[0].z,link_ori[0].w])
		#pelvis vel 6
		observation += [link_vlin[0].x,link_vlin[0].y,link_vlin[0].z,link_vang[0].x,link_vang[0].y,link_vang[0].z]

		#joint pos 6
		observation += joint_pos

		#joint vel 6
		observation += joint_vel

		#pos,vel center of mass 6
		pos_cog = np.zeros(3)
		vel_cog = np.zeros(3)
		for idx,(pos,vel) in enumerate(zip(link_pos,link_vlin)):
			pos_cog += link_mass.value[idx]*np.array([pos.x,pos.y,pos.z])
			vel_cog += link_mass.value[idx]*np.array([vel.x,vel.y,vel.z])

		pos_cog /= sum(link_mass.value)
		vel_cog /= sum(link_mass.value)

		observation = observation + list(pos_cog) + list(vel_cog)

		#other link pos 27
		link_pos.pop(0)
		for pos in link_pos:
			observation += [pos.x,pos.y,pos.z]


		reward = eval(conf.value.get('Environment',{}).get('reward_function',"5*link_vlin[0].x-link_vlin[0].y-2*link_vlin[0].z-1"))
		return observation,reward,Height

	observation.value,reward.value,Height.value = update(joints,links)


