#include <ros/ros.h>
#include <gazebo_msgs/GetJointProperties.h>
#include <gazebo_msgs/GetLinkProperties.h>
#include <gazebo_msgs/GetLinkState.h>
#include <gazebo_msgs/LinkStates.h>
#include <sensor_msgs/JointState.h>
#include <geometry_msgs/PoseArray.h>
#include <geometry_msgs/Vector3.h>
/*
class Transponder{
private:
	ros::Serviceclient_joint client_joint_;
pub_JointStatelic:
	Transponder(ros::NodeHandle nh){
		client_joint_ = nh.serviceclient_joint<gazebo_msgs::GetJointProperties>("/gazebo/get_joint_properties",10);
		pub_JointState_ = nh.advertise<sensor_msgs::JointState>("/joint_states",10);
	}
}
*/

const std::vector<std::string> joints = {"hip_r","hip_l","knee_r","knee_l","ankle_r","ankle_l"};
const std::vector<std::string> links = {"pelvis","torso","femur_r","femur_l","tibia_l","tibia_r","talus_r","talus_l","toes_r","toes_l"};
/////////////////////////////////////////0////////1////////2/////////3/////////4/////////5////////6//////////7/////////8////////9

int main(int argc, char** argv){
	ros::init(argc, argv, "Transponder");
	ros::NodeHandle nh;

	ros::ServiceClient client_joint = nh.serviceClient<gazebo_msgs::GetJointProperties>("/gazebo/get_joint_properties",10);
	ros::ServiceClient client_link_prop = nh.serviceClient<gazebo_msgs::GetLinkProperties>("/gazebo/get_link_properties",10);
	ros::ServiceClient client_link_state = nh.serviceClient<gazebo_msgs::GetLinkState>("/gazebo/get_link_state",10);

	ros::Publisher pub_JointState = nh.advertise<sensor_msgs::JointState>("/joint_states",10);
	ros::Publisher pub_LinkState = nh.advertise<gazebo_msgs::LinkStates>("/link_states",10);
	ros::Publisher pub_COGVel = nh.advertise<geometry_msgs::Vector3>("/cog_velocity",10);

	ros::Rate loop_rate(100);

	gazebo_msgs::GetJointProperties srv_GetJointProperties;
	gazebo_msgs::GetLinkState srv_GetLinkState;
	gazebo_msgs::GetLinkProperties srv_GetLinkProperties;
	sensor_msgs::JointState msg_JointState;
	gazebo_msgs::LinkStates msg_LinkStates;

	float pos_joint_[joints.size()] = {0};
	//std::vector<geometry_msgs::Point> pos_link_[links.size()] = {0};

	ros::Time ti,tf;
	ti = ros::Time::now();
	double dt = 0;

	//init only for calculation vel.
	for (int i = 0; i < joints.size(); ++i){
		srv_GetJointProperties.request.joint_name = joints[i];
		if(client_joint.call(srv_GetJointProperties)){
			pos_joint_[i] = srv_GetJointProperties.response.position[0];
		}else{
			ROS_INFO("service call failed!");
		}
	}

	double total_mass = 0;
	std::vector<double> mass_list;
	for (int i = 0; i < links.size(); ++i){
			srv_GetLinkProperties.request.link_name = links[i];
			if(client_link_prop.call(srv_GetLinkProperties)){
				total_mass += srv_GetLinkProperties.response.mass;
				mass_list.push_back(srv_GetLinkProperties.response.mass);
				//pos_link_.push_back(srv_GetLinkProperties.response.com.position);
				//pos_COG_[0] += srv_GetLinkProperties.response.com.position.x*mass
			}else{
				ROS_INFO("service call failed!");
			}
		}

	geometry_msgs::Pose tmp_COG;
	geometry_msgs::Pose tmp_COG_;
	geometry_msgs::Vector3 vel_COG; 
	while(ros::ok()){

		tf = ros::Time::now();
		dt = tf.toSec() - ti.toSec();
		/*--------------------joint position----------------------*/
		msg_JointState.name.clear();
		msg_JointState.position.clear();
		msg_JointState.velocity.clear();

		for (int i = 0; i < joints.size(); ++i){
			srv_GetJointProperties.request.joint_name = joints[i];
			if(client_joint.call(srv_GetJointProperties)){
				msg_JointState.name.push_back(joints[i]);
				msg_JointState.position.push_back(srv_GetJointProperties.response.position[0]);
				msg_JointState.velocity.push_back((srv_GetJointProperties.response.position[0] - pos_joint_[i])/dt);
				pos_joint_[i] = srv_GetJointProperties.response.position[0];
			}else{
				ROS_INFO("service call failed!");
			}
		}
		pub_JointState.publish(msg_JointState);

		/*--------------------link pose----------------------*/
		msg_LinkStates.name.clear();
		msg_LinkStates.pose.clear();
		msg_LinkStates.twist.clear();
		tmp_COG.position.x = 0; tmp_COG.position.y = 0; tmp_COG.position.z = 0;
		for (int i = 0; i < links.size(); ++i){
			srv_GetLinkState.request.link_name = links[i];
			srv_GetLinkState.request.reference_frame = "link";
			if(client_link_state.call(srv_GetLinkState)){
				msg_LinkStates.name.push_back(srv_GetLinkState.response.link_state.link_name);
				msg_LinkStates.pose.push_back(srv_GetLinkState.response.link_state.pose);
				msg_LinkStates.twist.push_back(srv_GetLinkState.response.link_state.twist);
				tmp_COG.position.x += srv_GetLinkState.response.link_state.pose.position.x*mass_list[i];
				tmp_COG.position.y += srv_GetLinkState.response.link_state.pose.position.y*mass_list[i];
				tmp_COG.position.z += srv_GetLinkState.response.link_state.pose.position.z*mass_list[i];
			}else{
				ROS_INFO("service call failed!");
			}
		}
		tmp_COG.position.x /= total_mass;
		tmp_COG.position.y /= total_mass;
		tmp_COG.position.z /= total_mass;
		msg_LinkStates.name.push_back("COG");
		msg_LinkStates.pose.push_back(tmp_COG);
		pub_LinkState.publish(msg_LinkStates);

		vel_COG.x = (tmp_COG_.position.x - tmp_COG.position.x)/dt;
		vel_COG.y = (tmp_COG_.position.y - tmp_COG.position.y)/dt;
		vel_COG.z = (tmp_COG_.position.z - tmp_COG.position.z)/dt;

		tmp_COG_ = tmp_COG;

		pub_COGVel.publish(vel_COG);

		ti = tf;
		loop_rate.sleep();
	}
	return 0;
}