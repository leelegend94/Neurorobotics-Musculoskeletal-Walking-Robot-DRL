@nrp.MapCSVRecorder("recorder", filename="curr_stat.csv", headers=["itr_idx","Height","reward"])
#@nrp.MapCSVRecorder("recorder", filename="curr_stat.csv", headers=["itr_idx","dummy"])
@nrp.MapVariable("Height",initial_value=None,scope=nrp.GLOBAL)
@nrp.MapVariable("reward",initial_value=None,scope=nrp.GLOBAL)
@nrp.MapVariable("agent", initial_value=None, scope=nrp.GLOBAL)
@nrp.Robot2Neuron()
def csv_curr_stat(t, recorder, Height, reward, agent):
	if agent.value is not None and Height.value is not None:
		recorder.record_entry(agent.value.step,Height.value,reward.value)
		#recorder.record_entry(agent.value.step,"1")
		clientLogger.info('Data Recorded')