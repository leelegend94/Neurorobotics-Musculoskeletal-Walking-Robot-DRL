CONFIGURATION = {}

# internal keras-rl agent to persist
@nrp.MapVariable("agent", initial_value=None, scope=nrp.GLOBAL)
@nrp.MapVariable("conf",initial_value=CONFIGURATION)

@nrp.Robot2Neuron()
def init_DRLagent(t, agent, conf):
    # initialize the keras-rl agent
    if agent.value is None:
        # import keras-rl in NRP through virtual env
        import site, os
        site.addsitedir(os.path.expanduser('~/.opt/tensorflow1_venv/lib/python2.7/site-packages'))

        from keras.models import Model, Sequential
        from keras.layers import Dense, Activation, Flatten, Input, concatenate
        from keras.optimizers import Adam

        from rl.agents import DDPGAgent
        from rl.memory import SequentialMemory
        from rl.random import OrnsteinUhlenbeckProcess

        from keras import backend as K
        K.clear_session()

        actor_layers = conf.value.get('DDPG_Agent',{}).get('ActorNet',{}).get('hidden_layers',[[128,'relu'],[128,'relu'],[128,'relu']])
        actor_act = conf.value.get('DDPG_Agent',{}).get('ActorNet',{}).get('output_activation','sigmoid')

        critic_layers = conf.value.get('DDPG_Agent',{}).get('CriticNet',{}).get('hidden_layers',[[512,'relu'],[256,'relu'],[128,'relu']])
        critic_act = conf.value.get('DDPG_Agent',{}).get('CriticNet',{}).get('output_activation','linear')

        memory = conf.value.get('DDPG_Agent',{}).get('memory',"SequentialMemory(limit=100000, window_length=1)")
        random_process = conf.value.get('DDPG_Agent',{}).get('random_process', "OrnsteinUhlenbeckProcess(theta=.15, mu=0., sigma=1, size=nA)")

        agent_args = conf.value.get('DDPG_Agent',{}).get('agent',{'nb_steps_warmup_critic':100, 'nb_steps_warmup_actor':100,'gamma':.99, 'batch_size':5, 'target_model_update':1e-3, 'delta_clip':1.})
        #agent_args = conf.value.get('DDPG_Agent',{}).get('agent',{'nb_steps_warmup_critic':10})
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
        clientLogger.info("Actor Network Structure:")
        for layer in actor_layers:
            clientLogger.info(layer[0],)
            actor.add(Dense(layer[0],activation=layer[1],kernel_initializer='RandomNormal'))
        actor.add(Dense(nA,activation=actor_act,kernel_initializer='RandomNormal'))

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
            clientLogger.info(layer[0])
            x = Dense(layer[0],activation=layer[1],kernel_initializer='RandomNormal')(x)
        x = Dense(1,activation=critic_act,kernel_initializer='RandomNormal')(x)
        critic = Model(inputs=[action_input, observation_input], outputs=x)

        #clientLogger.info(agent_args)
        # instanstiate rl agent
        
        #agent.value = DDPGAgent(nb_actions=nA, actor=actor, critic=critic, critic_action_input=action_input, memory=eval(memory), random_process=eval(random_process), **agent_args)
        #memory = SequentialMemory(limit=100000, window_length=1)
        #random_process = OrnsteinUhlenbeckProcess(theta=.15, mu=0., sigma=.2, size=nA)
        #agent_ = DDPGAgent(nb_actions=nA, actor=actor, critic=critic, critic_action_input=action_input, memory=memory, random_process=random_process)

        agent_ = DDPGAgent(nb_actions=nA, actor=actor, critic=critic, critic_action_input=action_input, memory=eval(memory), random_process=eval(random_process),nb_steps_warmup_critic=100, nb_steps_warmup_actor=100, gamma=.99, batch_size=5, target_model_update=1e-3, delta_clip=1.)

        agent_.training = True

        agent_.compile(optimizer=eval(optimizer),metrics=['mae'])
        
        #Why this strange path? --> cf. "https://github.com/keras-rl/keras-rl/blob/master/rl/agents/ddpg.py" line 158-171
        WeightsPATH = conf.value.get('DDPG_Agent',{}).get('weights_sav_path',"~/.opt/weights")
        #clientLogger.info(WeightsPATH)
        #clientLogger.info(conf.value)
        conf_name = conf.value.get('NAME','default')
        ###
        weights_list = os.listdir(os.path.expanduser(WeightsPATH))
        weights_list = list(filter(lambda x: x.endswith('h5'), weights_list))
        weights_list_without_timestamp = list(lambda x: x.split("_")[2:].join("_"), weights_list)
        ###
        if os.path.isfile(os.path.expanduser(WeightsPATH+"/"+conf_name+"_ddpg_weights_actor.h5")):
            agent_.load_weights(os.path.expanduser(WeightsPATH+"/"+conf_name+"_ddpg_weights.h5"))
            clientLogger.info('weights loaded!')
        
        #agent_.compile(optimizer=Adam(lr=.001, clipnorm=1.),metrics=['mae'])
        #agent_.compile(Adam(lr=.001, clipnorm=1.), metrics=['mae'])
        #agent_.compile('adam', metrics=['mae'])

        agent.value = agent_
        clientLogger.info('***********************')
        clientLogger.info('DDPG agent ready!')
        clientLogger.info('***********************')

        
