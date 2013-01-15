import re
import nltk

from pyPdf import PdfFileReader 


path='/Users/antoniopenta/Documents/DatiRicerca/partiti/'

nameIn=path+'riv.pdf'
nameOut=path+'tokenRiv.txt'

stop=path+'italianST.txt'

input= PdfFileReader(file(nameIn,"rb"));

content="";
for i in range(0,input.getNumPages()):
	 content+=input.getPage(i).extractText()+"\n";


content = " ".join(content.replace(u"\xa0", " ").strip().split())

content=content.encode('ascii','ignore')

f=open(stop,'r');

l=f.readlines();


ll=map(lambda x: x.strip(),l);


tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+|[^\w\s]+')


tokenized = tokenizer.tokenize(content);


tokenized0=map(lambda x: x.lower(),tokenized);

tokenized2=[ item for item in tokenized0 if item not in  ll];
tokenized3=[ item for item in tokenized2 if not re.match('\s\.,:,;?%',item)];
tokenized4=[ item for item in tokenized3 if not re.match('[0-9]+',item)];
tokenized5=[ item for item in tokenized4 if not re.match(',\)\(\.-',item)];
tokenized6=[ item for item in tokenized5 if not re.match('[\/:,\)\(\.-]+\s',item)]
tokenized7=[ item for item in tokenized6 if len(item)>3];


f=open(nameOut,'w')
f.write("\n".join(tokenized7));
f.close()
