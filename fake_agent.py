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
