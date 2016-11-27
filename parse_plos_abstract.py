import xmltodict
import glob
import subprocess
from collections import OrderedDict
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize
import os

sid=SentimentIntensityAnalyzer()

def term_pgraph(abstract):
    if type(abstract) is str:
        ab_txt=abstract
    elif type(abstract) is OrderedDict:
        ab_txt=abstract['#text']
    return ab_txt
         
def parse_abs(xd):
    if 'abstract' not in xd['article']['front']['article-meta']:
        return '' # no abstract, clearly
    abstract=xd['article']['front']['article-meta']['abstract']
    if type(abstract) is OrderedDict: #going down "normal" 'p' route - still have to divide for structure/unstructure
        if 'sec' in abstract:
            out_str=[]
            for sec in abstract['sec']:
                out_str.append(term_pgraph(sec['p']))
            return ' '.join(out_str)
        else:
            return term_pgraph(abstract['p'])
    if type(abstract) is list: #going down summary rabbit hole 
        prim=abstract[0]
        if 'sec' in prim:
            out_str=[]
            for sec in prim:
                out_str.append(term_pgraph(sec))
            prim_res=' '.join(out_str)
        else:
            prim_res=term_pgraph(prim['p'])
        
        sumar=abstract[1]
        #print(sumar)
        if 'sec' in sumar:
            if type(sumar) is list:
                out_str=[]
                for sec in sumar:
                    out_str.append(term_pgraph(sec))
                sum_res=' '.join(out_str)
            else:
                sum_res=term_pgraph(sumar['sec']['p']) 
        else:
            sum_res=term_pgraph(sumar['p'])
        return prim_res,sum_res
    
def get_epubdate(xml):
    pdate=xml['article']['front']['article-meta']['pub-date']
    for odict in pdate:
        if odict['@pub-type']=='epub':
            return "{}-{}-{}".format(odict['year'],odict['month'],odict['day'])    

def get_numauthors(xml):
    return len(xml['article']['front']['article-meta']['contrib-group'][0]['contrib'])
        
def get_pgraph_sent(pgraph):
    lines_list=tokenize.sent_tokenize(pgraph)
    sum_score=[sid.polarity_scores(line)['compound'] for line in lines_list]
    return (sum(sum_score)/len(sum_score),sum_score[-1])


#main loop v0.002
#assume in ~/plos_corpus/torrent
os.chdir('torrent')
files=glob.glob('*.xml')
print(len(files)) #193271
i=0
j=0
k=0
fbad=open('../needswork_ids.txt','w')
fbad.write('file,exception\n')
journ=open('../journals_abs_sum.csv','w')
#journ2=open('../journals_abs.csv','w')
journ.write('journal,num_authors,abs_type,file_name,sentiment,date,simple_abstract,n_letters\n')
#journ2.write('journal,file_name,sentiment,date\n')
for file in files:
    try:
        xf=xmltodict.parse(open(file).read())
        res=parse_abs(xf)
        if res:
            if type(res) is tuple:
                fout=open('./abstracts/'+file[:-4]+'_abs.txt','w')
                fout.write(res[0])
                fout.close()
                fout=open('./abstracts/'+file[:-4]+'_sum.txt','w')
                fout.write(res[1])
                fout.close()
                i+=1
                jname=file.split('.')[0]
                aname=file[:-4]+'_abs.txt'
                sname=file[:-4]+'_sum.txt'
                a_sent,a_zing=get_pgraph_sent(res[0])
                s_sent,s_zing=get_pgraph_sent(res[1])
                edate=get_epubdate(xf)
                num_authors=get_numauthors(xf)
                journ.write('{},{},{},{},{},{},{},{},{}\n'.format(jname,num_authors,"Abstract",aname,a_sent,a_zing,edate,"FALSE",len(res[0])))
                journ.write('{},{},{},{},{},{},{},{},{}\n'.format(jname,num_authors,"Summary",sname,s_sent,s_zing,edate,"FALSE",len(res[1])))
                
            else:
                fout=open('./abstracts/'+file[:-4]+'_abs.txt','w')
                fout.write(res)
                fout.close()
                aname=file[:-4]+'_abs.txt'
                j+=1
                a_sent,a_zing=get_pgraph_sent(res)
                jname=file.split('.')[0]
                edate=get_epubdate(xf)
                num_authors=get_numauthors(xf)
                journ.write('{},{},{},{},{},{},{},{},{}\n'.format(jname,num_authors,"Abstract",aname,a_sent,a_zing,edate,"TRUE",len(res)))
                
    except Exception as ex:
        k+=1
        fbad.write('{},{}\n'.format(file,type(ex).__name__))
        continue
print('{} articles with an additional summary, {} plain abstract, {} with problems or no abstract'.format(i,j,k))
fbad.close()
journ.close()