f = open('list.txt')
f2 = open('publisher.txt','w')
f3 = open('args.txt','w')
for line in f:
	line = line.strip('\n')
	name = line[30:-15]
	output_line = "@nrp.MapRobotPublisher('"+name+"', Topic('"+line+"',Float64))\n"
	f2.write(output_line)
	f3.write(name+',')
	print(output_line)
f.close()
f2.close()