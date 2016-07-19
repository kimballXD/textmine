# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 15:31:13 2016

@author: KimballWu
"""

import xml.etree.ElementTree as etree
import pandas as pd
xml='textmine/corpus/zhwiki-20160701-pages-articles-multistream.xml'
#%%
tagN=0
level=0
order=0        
elementList=[]
levelList=[]
orderList=[]
for event, tag in etree.iterparse(xml, events=['start','end']):
    if tagN<1000:
        tagN +=1
        if event=='start':
            level+=1
            order+=1
            levelList.append(level)
        elif event=='end':
            level-=1    
            order+=1                
            elementList.append(tag)
        continue
    else:
        break      
#%%    
textList=[x.text for x in elementList]
tagList=[x.tag.split('}')[1] for x in elementList] 
attrList=[x.attrib for x in elementList]
data=pd.DataFrame([tagList,levelList,textList, attrList]).T
data.columns=['tag','level','text', 'attrList']
data['size']=data['text'].apply(lambda x: len(unicode(x)) if x!=None else 0)
#data=data.sort_values(by=['size'],ascending=False)
cDict=data['tag'].value_counts()


#%%

read=


#%%

def getTagText(data,tagName):
    for x in data.ix[data['tag']==tag,'text']:
        print x
        #%%
for x in data.ix[data['tag']=='title','text']:
    print x
#%%
title=data.ix[data['tag']=='title',:]
page