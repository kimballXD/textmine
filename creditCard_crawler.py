# -*- coding: utf-8 -*-
"""
Created on Fri May 20 15:05:08 2016

@author: Wu
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
import re
import time
#%%
#constant config
creditCard='https://www.ptt.cc/bbs/creditcard/index.html'
host='https://www.ptt.cc'
#pttIp=u'※ 發信站: 批踢踢實業坊\\(ptt\\.cc\\), 來自: (((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))'
pttIp=u'※.+?(((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))'
pushTypeTrans={u'→':'comment',u'推':'push',u'噓':'boo'}

#%%


#%%
#get indexPage
rep=requests.get(creditCard)
rep.encoding='utf8'
soup=bs(rep.text,'lxml')


#%%
articleList=[]
articleUrl=[]
pushTypeList=[]
pushUser=[]
pushContent=[]
pushDateTime=[]
userList=[]

for url in urls:
    page=requests.get(url)
    page.encoding='utf8'
    soup=bs(page.text,'lxml')
    
    #article content
    headers=soup.select('.article-meta-value')    
    rawTime=headers[3].text
    postTime=time.strftime('%Y-%m-%d %H:%M:%S',time.strptime(rawTime))
    year=postTime[0:4]
    ipLog=soup.select('.f2') # green sys log
    ipLog=[re.search(pttIp,x.text) for x in ipLog] 
    ip=[x.group(1) for x in ipLog if x!=None]  
    mainPattern=re.compile(rawTime+'</span></div>'+u'\n(.+?)<span class="f2">※',flags=re.DOTALL) # 預設 . 不認 \n，要開flag
    mainContent=re.search(mainPattern,unicode(soup)).group(1)
    signaturePattern=u'(--\n((.+?)\n){,6}\n)--\n※'
    signature=''
    if re.search(signaturePattern,mainContent)!=None:
        signature=re.search(signaturePattern,mainContent).group(1)
        mainContent=mainContent.replace(signature,'')

    #push content
    pushType=[x.text.strip() for x in soup.select('.push-tag')]
    pushTypeDict=pd.Series(pushType).value_counts().to_dict()
    articleUrl.extend([url]*sum(pushTypeDict.values()))
    pushTypeList.extend([pushTypeTrans[x] for x in pushType])
    pushContent.extend([x.text[2:] for x in soup.select('.push-content')])
    pushUser.extend([x.text for x in soup.select('.push-userid')])
    pushTimeList=[year+'/'+x.text.strip() for x in soup.select('.push-ipdatetime')]
    pushTimeList=[time.strftime('%Y-%m-%d %H:%M:%S',time.strptime(x,'%Y/%m/%d %H:%M')) for x in pushTimeList]
    pushDateTime.extend(pushTimeList)
    
    #storing articles
    articleDict={
        'user':headers[0].text.split(' ')[0],
        'title':headers[2].text,
        'time':postTime,
        'ip':ip[0],
        'postContent':mainContent,
        'signature':signature,
        'pushCount':pushTypeDict.get(u'推',0),
        'commentCount':pushTypeDict.get(u'→',0),
        'booCount':pushTypeDict.get(u'噓',0),
        'actType':'post',
        'url':url #primary key
    }
    articleList.append(articleDict)
    
# data output    
articles=pd.DataFrame(articleList)
pushes=pd.DataFrame({'url':articleUrl, 
                     'pushContent':pushContent,
                     'actType':pushTypeList,
                     'user':pushUser,
                     'time':pushDateTime
}) # need to assign another primary key
userAct=pd.concat([articles,pushes],join='inner')



#%%


#==============================================================================
# rep=requests.get('https://www.ptt.cc/bbs/creditcard/M.1463693213.A.535.html')
# rep.encoding='utf8'
# soup=bs(rep.text,'lxml')
# print soup.select('body')[0].text
# print soup.select('#main-container')[0].text
# #%%
#==============================================================================



import jieba
title=articles['title']
cut=[jieba.lcut(x,HMM=True) for x in title]
prcut=[','.join([y.encode('utf8') for y in x]) for x in cut]
for x in prcut:
    print x