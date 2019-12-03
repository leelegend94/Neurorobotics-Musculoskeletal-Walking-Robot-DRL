CONFIGURATION = {}

# internal keras-rl agent to persist
@nrp.MapVariable("agent", initial_value=None, scope=nrp.GLOBAL)
@nrp.MapVariable("conf",initial_value=CONFIGURATION)
@nrp.Robot2Neuron()
def init_DRLagent(t, agent, conf):
    # initialize the keras-rl agent
    if agent.value is None:

        class fake_agent():
            def __init__(self,nS,nA):
                self.nS = nS
                self.nA = nA
            def forward(self,nS):
                clientLogger.info('Use random actions instead...')
                return np.random.rand(nA)

            def backward(self,reward):
                clientLogger.info('Pretend to have received the reward...')

            def save_weights(self,path,ow):
                clientLogger.info('Pretend to have saved the weights...')

        nS = 58
        nA = 24

        clientLogger.info('FAKE INIT AGENT')

        # instanstiate rl agent
        agent.value = fake_agent(nS,nA)
        clientLogger.info('***********************')
        clientLogger.info('FAKE DDPG agent ready!')
        clientLogger.info('***********************')
        
