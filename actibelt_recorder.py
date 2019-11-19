@nrp.MapCSVRecorder("recorder", filename="actibelt.csv", headers=["index","acceleration","lin_vel_x","lin_vel_y","lin_vel_z","ang_vel_x","ang_vel_y","ang_vel_z"])
#@nrp.MapCSVRecorder("recorder", filename="curr_stat.csv", headers=["itr_idx","dummy"])
@nrp.MapVariable("ActiBelt_Data",initial_value=None,scope=nrp.GLOBAL)
@nrp.MapVariable("agent", initial_value=None, scope=nrp.GLOBAL)
@nrp.Robot2Neuron()
def csv_curr_stat(t, recorder, ActiBelt_Data, agent):
	if agent.value is not None and ActiBelt_Data.value is not None:
		data = ActiBelt_Data.value
		recorder.record_entry(agent.value.step,"None",data[2].x,data[2].y,data[2].z,data[3].x,data[3].y,data[3].z)
		#recorder.record_entry(agent.value.step,"1")
		clientLogger.info('Data Recorded')