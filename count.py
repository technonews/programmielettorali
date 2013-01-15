path='/Users/antoniopenta/Documents/DatiRicerca/partiti/'

name1=path+'tokenPDFilterNoun.txt'

name2=path+'dicPDFilterNoun.txt'



f1=open(name1,'r')



l1=f1.readlines()


ll=map(lambda x :x.strip(),l1)

h={}

for item in ll:
	if(h.has_key(item)):
		h[item]+=1
	else:
		h[item]=1

hh=sorted(h.items(), key=lambda x: x[1])



f=open(name2,'w')

for item in hh:
	
	
	f.write('%s --> %d\n'%(item[0],item[1]));
f.close


