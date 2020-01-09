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
        
        import site, os
        site.addsitedir(os.path.expanduser('~/.opt/tensorflow1_venv/lib/python2.7/site-packages'))
        import tensorflow as tf
        hello = tf.constant('Hello, TensorFlow!')
        sess = tf.Session()
        clientLogger.info(sess.run(hello))
        
        nS = 58
        nA = 24

        clientLogger.info('FAKE INIT AGENT')

        # instanstiate rl agent
        agent.value = fake_agent(nS,nA)
        clientLogger.info('***********************')
        clientLogger.info('FAKE DDPG agent ready!')
        clientLogger.info('***********************')
        
