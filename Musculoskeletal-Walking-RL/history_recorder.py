CONFIGURATION = {}

NAME = "history_" + CONFIGURATION.get('NAME','default') + ".csv"
@nrp.MapCSVRecorder("recorder", filename=NAME, headers=["Epoch","Reward","X","Z","Vx","Vz"])
@nrp.MapVariable("reward",initial_value=None,scope=nrp.GLOBAL)
@nrp.MapVariable("nb_ep",initial_value=1, scope=nrp.GLOBAL)
@nrp.MapVariable("pos_x",initial_value=None,scope=nrp.GLOBAL)
@nrp.MapVariable("pos_z",initial_value=None,scope=nrp.GLOBAL)
@nrp.MapVariable("vel_x",initial_value=None,scope=nrp.GLOBAL)
@nrp.MapVariable("vel_z",initial_value=None,scope=nrp.GLOBAL)

@nrp.Robot2Neuron()
def history_recorder(t, recorder, reward, nb_ep, pos_x, pos_z, vel_x, vel_z):
	if reward.value is not None:
			recorder.record_entry(nb_ep.value,reward.value, pos_x.value, pos_z.value, vel_x.value, vel_z.value)
			#clientLogger.info('Data Recorded')