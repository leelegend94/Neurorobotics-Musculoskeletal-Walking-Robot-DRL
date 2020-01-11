#from sensor_msgs.msg import Imu

class ActiBelt_Logger:
	def __init__(self):
		self.buffer = None
	
	def record(self,data):
		ts = data.header.stamp
		ax = data.linear_acceleration.x
		ay = data.linear_acceleration.y
		az = data.linear_acceleration.z
		wx = data.angular_velocity.x
		wy = data.angular_velocity.y
		wz = data.angular_velocity.z
		qx = data.orientation.x
		qy = data.orientation.y
		qz = data.orientation.z
		qw = data.orientation.w
		self.buffer = [ts,ax,ay,az,wx,wy,wz,qx,qy,qz,qw]

	def get_data(self):
		return self.buffer

