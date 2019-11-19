import yaml

f = open("test.yaml")
conf = yaml.load(f)

print type(conf.get('DDPG_Agent',{}))