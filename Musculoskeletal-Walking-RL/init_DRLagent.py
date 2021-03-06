CONFIGURATION = {}

# internal keras-rl agent to persist
@nrp.MapVariable("agent", initial_value=None, scope=nrp.GLOBAL)
@nrp.MapVariable("conf",initial_value=CONFIGURATION)
@nrp.MapVariable("tmp",initial_value=None)
@nrp.Robot2Neuron()
def init_DRLagent(t, agent, conf, tmp):
    # initialize the keras-rl agent
    #clientLogger.info(tmp.value)
    if agent.value is None:
        # import keras-rl in NRP through virtual env
        import site, os
        site.addsitedir(os.path.expanduser('~/.opt/tensorflow_venv/lib/python2.7/site-packages'))

        from keras.models import Model, Sequential
        from keras.layers import Dense, Activation, Flatten, Input, concatenate
        from keras.optimizers import Adam

        from rl.agents import DDPGAgent
        from rl.memory import SequentialMemory
        from rl.random import OrnsteinUhlenbeckProcess

        from keras import backend as K
        K.clear_session()

        actor_layers = conf.value.get('DDPG_Agent',{}).get('ActorNet',{}).get('hidden_layers',[[128,'relu'],[128,'relu']])
        actor_act = conf.value.get('DDPG_Agent',{}).get('ActorNet',{}).get('output_activation','sigmoid')

        critic_layers = conf.value.get('DDPG_Agent',{}).get('CriticNet',{}).get('hidden_layers',[[256,'relu'],[128,'relu']])
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
        
        for layer in critic_layers:
            clientLogger.info(layer[0])
            x = Dense(layer[0],activation=layer[1],kernel_initializer='RandomNormal')(x)
        x = Dense(1,activation=critic_act,kernel_initializer='RandomNormal')(x)
        critic = Model(inputs=[action_input, observation_input], outputs=x)

        #clientLogger.info(agent_args)
        # instanstiate rl agent
        
        #agent_ = DDPGAgent(nb_actions=nA, actor=actor, critic=critic, critic_action_input=action_input, memory=eval(memory), random_process=eval(random_process), **agent_args)
        #agent_ = DDPGAgent(nb_actions=nA, actor=actor, critic=critic, critic_action_input=action_input, memory=eval(memory), random_process=eval(random_process),nb_steps_warmup_critic=100, nb_steps_warmup_actor=100, gamma=.99, batch_size=5, target_model_update=1e-3, delta_clip=1.)

        #tf doesn't support the usage of **kwargs, let's do it in a noob way.
        additional_args = ""
        for key,value in agent_args.items():
            additional_args = additional_args+", "+key+"="+str(value)
        agent_ = eval("DDPGAgent(nb_actions=nA, actor=actor, critic=critic, critic_action_input=action_input, memory=eval(memory), random_process=eval(random_process)" + additional_args + ")")

        agent_.training = True

        #agent_.compile(optimizer=eval(optimizer),metrics=['mae'])
        additional_args = ""
        for key,value in compiler_args.items():
            additional_args = additional_args+", "+key+"="+str(value)
        optimizer=eval(optimizer)
        eval("agent_.compile(optimizer=optimizer"+additional_args+")")
        
        #Why this strange path? --> cf. "https://github.com/keras-rl/keras-rl/blob/master/rl/agents/ddpg.py" line 158-171
        WeightsPATH = conf.value.get('DDPG_Agent',{}).get('weights_sav_path',"~/.opt/weights")
        #clientLogger.info(WeightsPATH)
        #clientLogger.info(conf.value)
        conf_name = conf.value.get('NAME','default')

        ###
        weights_list = os.listdir(os.path.expanduser(WeightsPATH))

        #ensure weights in the list contain timestamp, only works before 2100 :)
        weights_list = list(filter(lambda x: x.endswith('h5') and x.startswith("20") and not x.startswith("20xx"), weights_list))
        weights_list_without_timestamp = [x[20:] for x in weights_list]
        weights_list_timestamp = [x[:19] for x in weights_list]

        actor_name = conf_name+"_ddpg_weights_actor.h5"
        #critic_name = conf_name+"_ddpg_weights_critic.h5"

        idx_ts_actor = [i for i,x in enumerate(weights_list_without_timestamp) if x==actor_name]
        #idx_ts_critic = [i for i,x in enumerate(weights_list_without_timestamp) if x==critic_name]

        name = conf_name+"_ddpg_weights.h5"
        #weights are actually stored with "_actor" or "_critic" suffixes.

        if len(idx_ts_actor)==0:
            clientLogger.info(actor_name+' not availiable. Freash training.')
            tmp.value = "No weights loaded!"
        elif len(idx_ts_actor)==1:
            full_name = weights_list_timestamp[idx_ts_actor[0]]+"_"+name
            agent_.load_weights(os.path.expanduser(WeightsPATH+"/"+full_name))
            clientLogger.info("Weights file: ",full_name," loaded!")
            tmp.value = "single, "+full_name
        else:
            clientLogger.info("Multiple weights file matched, choose the latest one.")
            import time, datetime
            weights_list_timestamp = [weights_list_timestamp[i] for i in idx_ts_actor]
            timestamp = [time.mktime(datetime.datetime.strptime(x, "%Y-%m-%d-%H-%M-%S").timetuple()) for x in weights_list_timestamp]
            idx_ts_actor = timestamp.index(max(timestamp))
            full_name = weights_list_timestamp[idx_ts_actor]+"_"+name
            agent_.load_weights(os.path.expanduser(WeightsPATH+"/"+full_name))
            clientLogger.info("Weights file: ",full_name," loaded!")
            tmp.value = "mult, "+full_name


        agent.value = agent_
        clientLogger.info('***********************')
        clientLogger.info('DDPG agent ready!')
        clientLogger.info('***********************')
    #clientLogger.info(tmp.value)   
