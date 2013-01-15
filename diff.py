path='/Users/antoniopenta/Documents/DatiRicerca/partiti/'

name1=path+'tokenPDFilterNoun.txt'
name2=path+'tokenRivFilterNoun.txt'

name12=path+'PD_vs_Riv_noun.txt'

name21=path+'Riv_vs_PD_moun.txt'

nameInte=path+'PD_int_Riv_noun.txt'


f1=open(name1,'r')

f2=open(name2,'r')


l1=f1.readlines()

l2=f2.readlines()

ll1=map(lambda x :x.strip(),l1)

ll2=map(lambda x : x.strip(),l2)

ll12=[item for item in ll1 if item not in ll2];
ll21=[item for item in ll2 if item not in ll1]

l3=set(l1).intersection(set(l2))
l4=set(l1).union(set(l2))

#print float(len(l3))/float(len(l4))

f12=open(name12,'w')
f12.write('\n'.join(ll12));
f12.close


f21=open(name21,'w')
f21.write('\n'.join(ll21));
f21.close


f3=open(nameInte,'w')
f3.write('\n'.join(l3))
f3.write(str(float(len(l3))/float(len(l4))))
f3.close();
