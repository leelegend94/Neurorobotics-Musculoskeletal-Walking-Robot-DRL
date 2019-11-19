CONFIGURATION = {}

# internal keras-rl agent to persist
@nrp.MapVariable("agent", initial_value=None, scope=nrp.GLOBAL)
@nrp.MapVariable("conf",initial_value=CONFIGURATION)
@nrp.Robot2Neuron()
def init_DRLagent(t, agent, conf):
    # initialize the keras-rl agent
    if agent.value is None:
        # import keras-rl in NRP through virtual env
        clientLogger.info('before import')
        import site, os
        #site.addsitedir(os.path.expanduser('~/env_NRP_py3/lib/python3.5/site-packages'))
        #site.addsitedir(os.path.expanduser('~/workspace/NRP_TF_venv/lib/python2.7/site-packages'))
        #site.addsitedir('/home/zhenyu/workspace/nrp_tf_venv/lib/python2.7/site-packages')
        from keras.models import Model, Sequential
        clientLogger.info('first keras model')
        from keras.layers import Dense, Activation, Flatten, Input, concatenate
        from keras.optimizers import Adam, RMSprop
        
        from rl.agents import DDPGAgent
        from rl.memory import SequentialMemory
        from rl.random import OrnsteinUhlenbeckProcess

        from keras import backend as K
        clientLogger.info('after')
        K.clear_session()

        actor_layers = conf.value.get('DDPG_Agent',{}).get('ActorNet',{}).get('hidden_layers',[[128,'relu'],[128,'relu'],[128,'relu']])
        actor_act = conf.value.get('DDPG_Agent',{}).get('ActorNet',{}).get('output_activation','sigmoid')

        critic_layers = conf.value.get('DDPG_Agent',{}).get('CriticNet',{}).get('hidden_layers',[[512,'relu'],[256,'relu'],[128,'relu']])
        critic_act = conf.value.get('DDPG_Agent',{}).get('CriticNet',{}).get('output_activation','linear')

        memory = conf.value.get('DDPG_Agent',{}).get('memory',"SequentialMemory(limit=100000, window_length=1)")
        random_process = conf.value.get('DDPG_Agent',{}).get('random_process', "OrnsteinUhlenbeckProcess(theta=.15, mu=0., sigma=.2, size=nA)")
        #agent_args = ",".join(conf.value.get('DDPG_Agent',{}).get('agent',["nb_steps_warmup_critic=10", "nb_steps_warmup_actor=10","gamma=.99", "batch_size=5", "target_model_update=1e-3", "delta_clip=1."]))
        #compile_args = ",".join(conf.value.get('DDPG_Agent',{}).get('compiler',['Adam(lr=.001, clipnorm=1.)','metrics=[\'mae\']']))
        #agent_args = conf.value.get('DDPG_Agent',{}).get('agent',{'nb_steps_warmup_critic':10, 'nb_steps_warmup_actor':10,'gamma':.99, 'batch_size':5, 'target_model_update':1e-3, 'delta_clip':1.})
        agent_args = conf.value.get('DDPG_Agent',{}).get('agent',{'nb_steps_warmup_critic':10})
        compiler_args = conf.value.get('DDPG_Agent',{}).get('compiler',{'metrics':['mae']})
        optimizer = conf.value.get('DDPG_Agent',{}).get('optimizer','Adam(lr=.001, clipnorm=1.)')


        nS = 58
        nA = 24

        clientLogger.info('INIT AGENT')
        
        # create the nets for rl agent
        # actor net s --> a
        actor = Sequential()
        actor.add(Flatten(input_shape=(1,nS)))

        #actor.add(Dense(128))
        #actor.add(Activation('relu'))
        #actor.add(Dense(128))
        #actor.add(Activation('relu'))
        #actor.add(Dense(128))
        #actor.add(Activation('relu'))
        #actor.add(Dense(nA))
        #actor.add(Activation('sigmoid'))

        for layer in actor_layers:
            actor.add(Dense(layer[0],activation=layer[1]))
        actor.add(Dense(nA,activation=actor_act))

        # critic net (s,a) --> Q(s,a)
        action_input = Input(shape=(nA,), name='action_input')
        observation_input = Input(shape=(1,) + (nS,), name='observation_input')
        flattened_observation = Flatten()(observation_input)
        x = concatenate([action_input, flattened_observation])

        #x = Dense(512)(x)
        #x = Activation('relu')(x)
        #x = Dense(256)(x)
        #x = Activation('relu')(x)
        #x = Dense(128)(x)
        #x = Activation('relu')(x)
        #x = Dense(1)(x)
        #x = Activation('linear')(x)
        
        for layer in critic_layers:
            x = Dense(layer[0],activation=layer[1])(x)
        x = Dense(1,activation=critic_act)(x)

        critic = Model(inputs=[action_input, observation_input], outputs=x)

        
        # instanstiate rl agent
        agent.value = DDPGAgent(nb_actions=nA, actor=actor, critic=critic, critic_action_input=action_input, memory=memory, nb_steps_warmup_critic=10, nb_steps_warmup_actor=10, random_process=random_process, gamma=.99, batch_size=5, target_model_update=1e-3, delta_clip=1.)
        agent_args = {}
        #agent.value = DDPGAgent(nb_actions=nA, actor=actor, critic=critic, critic_action_input=action_input, memory=eval(memory), random_process=eval(random_process), **{'gamma':0.99})
        agent.value.training = True
        #PATH = '/home/.opt/nrpStorage/template_new_1/ddpg_weights.h5'
        PATH = conf.value.get('DDPG_Agent',{}).get('weights_sav_path',"/home/.opt/nrpStorage/template_new_1/ddpg_weights.h5")
        if os.path.isfile(PATH):
            clientLogger.info('weights loaded!')
            agent.value.load_weights(PATH)
        #agent.value.compile(Adam(lr=.001, clipnorm=1.), metrics=['mae'])
        agent.value.compile(optimizer=eval(optimizer),**compiler_args)
        clientLogger.info('***********************')
        clientLogger.info('DDPG agent ready!')
        clientLogger.info('***********************')
        
