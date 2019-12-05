CONFIGURATION = {}

# internal keras-rl agent to persist
@nrp.MapVariable("agent", initial_value=None, scope=nrp.GLOBAL)
@nrp.MapVariable("conf",initial_value=CONFIGURATION)
@nrp.Robot2Neuron()
def fake_init_DRLagent(t, agent, conf):
    # initialize the keras-rl agent
    if agent.value is None:
        import sys
        sys.path.append("/home/zhenyuli/.opt/nrpStorage/Neurorobotics-Musculoskeletal-Walking-Robot-DRL_0")
        from fake_agent import fake_agent

        nS = 58
        nA = 24

        clientLogger.info('FAKE INIT AGENT')

        # instanstiate rl agent
        agent.value = fake_agent(nS,nA)
        clientLogger.info('***********************')
        clientLogger.info('FAKE DDPG agent ready!')
        clientLogger.info('***********************')
        
