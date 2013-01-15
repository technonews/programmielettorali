import re

path='/Users/antoniopenta/Documents/DatiRicerca/partiti/'

name=path+'token5sPos.txt'

nameOutNoun=path+'token5sFilterNoun.txt'

nameOutVerb=path+'token5sFilterVerb.txt'



f=open(name)

l=f.readlines()

ll=map(lambda x :x.strip(),l)

lll=map(lambda x: x.split('\t'),ll)

llln=[item[2] for item in lll if item[1]=='NOM']

lllln=[item for item in llln if item!='<unknown>']

lllv=[item[2] for item in lll if re.match('VER.+', item[1])]

llllv=[item for item in lllv if item!='<unknown>']


fn=open(nameOutNoun,'w')
fn.write('\n'.join(lllln))
fn.close()


fv=open(nameOutVerb,'w')
fv.write('\n'.join(llllv))
fv.close()


