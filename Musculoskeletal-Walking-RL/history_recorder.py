@nrp.MapCSVRecorder("recorder", filename="curr_stat.csv", headers=["Epoch","Height","reward"])
#@nrp.MapCSVRecorder("recorder", filename="curr_stat.csv", headers=["itr_idx","dummy"])
@nrp.MapVariable("Height",initial_value=None,scope=nrp.GLOBAL)
@nrp.MapVariable("reward",initial_value=None,scope=nrp.GLOBAL)
@nrp.MapVariable("nb_ep",initial_value=1, scope=nrp.GLOBAL)

@nrp.Robot2Neuron()
def csv_curr_stat(t, recorder, Height, reward, nb_ep):
	if Height.value is not None:
		if reward.value != reward_.value:
			recorder.record_entry(nb_ep.value,Height.value,reward.value)
			clientLogger.info('Data Recorded')
			reward_.value = reward.value