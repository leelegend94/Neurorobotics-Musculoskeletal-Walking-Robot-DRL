@nrp.MapCSVRecorder("recorder", filename="actibelt.csv", headers=["time_stamp","lin_acc_x","lin_acc_y","lin_acc_z","ang_vel_x","ang_vel_y","ang_vel_z","quat_x","quat_y","quat_z","quat_w"])

@nrp.MapVariable("logger", initial_value=None)
@nrp.MapVariable("sub", initial_value=None)
@nrp.MapVariable("reward", initial_value=None, scope=nrp.GLOBAL)

@nrp.Robot2Neuron()
def actibelt_recorder(t, recorder, logger, reward, sub):
	if logger.value is None:
		import site, os
		import rospy
		from sensor_msgs.msg import Imu
		site.addsitedir(os.path.expanduser('~/Documents/Musculoskeletal-Walking-RL/Musculoskeletal-Walking-RL'))
		from ActiBelt_Logger import ActiBelt_Logger
		logger.value = ActiBelt_Logger()
		sub.value = rospy.Subscriber("/body/ActiBelt",Imu,logger.value.record)

	if reward.value is not None:
		result = logger.value.get_data()
		if result is not None:
			[ts,ax,ay,az,wx,wy,wz,qx,qy,qz,qw] = result
			recorder.record_entry(ts,ax,ay,az,wx,wy,wz,qx,qy,qz,qw)
			clientLogger.info('acti data Recorded')