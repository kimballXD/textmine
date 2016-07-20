# -*- coding: utf-8 -*-
"""
Created on Tue May 24 14:35:06 2016

@author: Wu
"""
import time, datetime
import requests
from bs4 import BeautifulSoup as bs
import re

#%%
#arguments
backDates=1
board='creditcard'
#%%
pageTemplate='https://www.ptt.cc/bbs/{}/index{}.html'
host='https://www.ptt.cc'

#%%
#get indexPage
indexPage=pageTemplate.format(board,'')
rep=requests.get(indexPage)
rep.encoding='utf8'
soup=bs(rep.text,'lxml')
indexPattern=u'<a class="btn wide" href=\"/bbs/'+board+u'/index(\d+).html\">&lsaquo; 上頁</a>'
pages=int(re.search(indexPattern,rep.text).group(1))+1

#%%

def urlGrab(borad, backDate):
    startDate=datetime.date.today()-datetime.timedelta(days=backDates)
    urls=[]
    for page in range(pages,1,-1):
        rep=requests.get(pageTemplate.format(board,page))
        rep.encoding='utf8'
        soup=bs(rep.text,'lxml')  
        divs=soup.find(class_='r-list-container')
        sep=divs.find(class_='r-list-sep')
        if sep!=None:
            divs=sep.find_previous_siblings()
        divs=[x for x in list(divs) if x!='\n']
        date=[x.find(class_='date').text.strip() for x in divs]
        date=[[int(y) for y in x.split('/')] for x in date]  
        date=[datetime.date(startDate.year,x[0],x[1]) for x in date]
        if date[0]<startDate:
            for index in range(1,len(date)):
                if date[index]>=startDate:
                    divs=divs[index:]
                    tempUrls=[host+x.find('a').get('href') for x in divs if x.find('a')!=None]
                    tempUrls.reverse()
                    urls.extend(tempUrls)                
                    break
            break
        else:
            tempUrls=[host+x.find('a').get('href') for x in divs if x.find('a')!=None]
            if page!=pages:
                tempUrls.reverse()
            urls.extend(tempUrls)


#%%

urlGrabByDate()
urlGrabByNum(50)


#%%
  
    
    
    
