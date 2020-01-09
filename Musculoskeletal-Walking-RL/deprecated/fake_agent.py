import numpy as np
class fake_agent():
	def __init__(self,nS,nA):
		self.nS = nS
		self.nA = nA
		self.step = 0

	def forward(self,nS):
		print 'Use random actions instead...'
		return np.random.rand(self.nA)

	def backward(self,reward):
		print 'Pretend to have received the reward...'

	def save_weights(self,path,overwrite=False):
		print 'Pretend to have saved the weights...'
