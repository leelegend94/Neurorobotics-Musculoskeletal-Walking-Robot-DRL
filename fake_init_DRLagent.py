CONFIGURATION = {}

# internal keras-rl agent to persist
@nrp.MapVariable("agent", initial_value=None, scope=nrp.GLOBAL)
@nrp.MapVariable("conf",initial_value=CONFIGURATION)
@nrp.Robot2Neuron()
def init_DRLagent(t, agent, conf):
    # initialize the keras-rl agent
    if agent.value is None:

        from fake_agent import *

        nS = 58
        nA = 24

        clientLogger.info('FAKE INIT AGENT')

        # instanstiate rl agent
        agent.value = fake_agent(nS,nA)
        clientLogger.info('***********************')
        clientLogger.info('FAKE DDPG agent ready!')
        clientLogger.info('***********************')
        
