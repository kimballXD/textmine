# -*- coding: utf-8 -*-
"""
Created on Tue May 24 15:40:10 2016
    to do list
        fix@1: accidental crossing year happened when not using --spraseMode
        fix: request sleep
        powerUp@1: refactoring date logic
        powerUp: errorlog
        powerUP: make pttCrawler importable (have to refactoring argument check and error message part)
        powerUp: enable json save(retrun) type (ie: json object design)
@author: Wu
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
import re    
import time, datetime
import calendar
import os, argparse
import sys,traceback
import sqlite3


#%%
def urlCrawl(urls):    
    #tool preparation, storing 
    pttIp=u'※.+?(((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))'
    pushTypeTrans={u'→':'comment',u'推':'push',u'噓':'boo'}

    articleList=[]
    articleUrl=[]
    articlePostTime=[]
    pushTypeList=[]
    pushUser=[]
    pushContent=[]
    pushDateTime=[]
    errorLog=[]
    for url in urls:
        try:
            page=requests.get(url)
            page.encoding='utf8'
            soup=bs(page.text,'lxml')
            lastUpdate=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            #article content
            headers=soup.select('.article-meta-value')    
            rawTime=headers[3].text
            postTime=time.strftime('%Y-%m-%d %H:%M:%S',time.strptime(rawTime))
            year=postTime[0:4]
            ipLog=soup.select('.f2') # green sys log
            ipLog=[re.search(pttIp,x.text) for x in ipLog] 
            ip=[x.group(1) for x in ipLog if x!=None]  
            mainPattern=re.compile(rawTime+'</span></div>'+u'\n(.+?)<span class="f2">※ (發信站|編輯)',flags=re.DOTALL) # 預設 . 不認 \n，要開flag
            mainContent=re.search(mainPattern,unicode(soup)).group(1)
        
            #push content
            pushType=[x.text.strip() for x in soup.select('.push-tag')]
            pushTypeDict=pd.Series(pushType).value_counts().to_dict()
            totalPush=sum(pushTypeDict.values())
            articleUrl.extend([url]*totalPush)
            articlePostTime.extend([postTime]*totalPush)
            pushTypeList.extend([pushTypeTrans[x] for x in pushType])
            pushContent.extend([x.text[2:] for x in soup.select('.push-content')])
            pushUser.extend([x.text for x in soup.select('.push-userid')])
            pushTimeList=[year+'/'+x.text.strip() for x in soup.select('.push-ipdatetime')]
            pushTimeList=[time.strftime('%Y-%m-%d %H:%M:%S',time.strptime(x,'%Y/%m/%d %H:%M')) for x in pushTimeList]
            pushDateTime.extend(pushTimeList)
        except:
            a,b,c=sys.exc_info()
            tb=traceback.format_tb(c)[-1].split(',')
            tempLog=u'Error at {}. Exception:{}-{}.Found at {} {}'.format(url,a,b,tb[1],tb[2].replace('\n','-'))
            errorLog.append(tempLog)
            continue
        
        #storing articles
        articleDict={
            'user':headers[0].text.split(' ')[0],
            'title':headers[2].text,
            'time':postTime,
            'ip':ip[0],
            'postContent':mainContent,
            'pushCount':pushTypeDict.get(u'推',0),
            'commentCount':pushTypeDict.get(u'→',0),
            'booCount':pushTypeDict.get(u'噓',0),
            'actType':'post',
            'url':url, 
            'lastUpdate':lastUpdate}            
        articleList.append(articleDict)                    
            
    # data arrange and output    
    articles=pd.DataFrame(articleList)
    pushes=pd.DataFrame({'url':articleUrl, 
                         'postTime':articlePostTime,
                         'pushContent':pushContent,
                         'actType':pushTypeList,
                         'user':pushUser,
                         'time':pushDateTime,
                         'lastUpdate':lastUpdate})
    articles=articles.reindex_axis(['url','user','ip','time','title','postContent','pushCount','commentCount','booCount','actType','lastUpdate'],axis=1)
    pushes=pushes.reindex_axis(['url','postTime','user','time','pushContent','actType','lastUpdate'],axis=1)
#    print len(articles.columns), articles.columns
#    print len(pushes.columns), pushes.columns
    return (articles,pushes,errorLog)
#%%
def urlGrab(board, startDate, endDate, sparseMode):  
    #tool preparation  
    pageTemplate='https://www.ptt.cc/bbs/{}/index{}.html'
    host='https://www.ptt.cc'
    reDay="({}) ({}) (3[0-1]|[0-2][0-9])".format('|'.join(list(calendar.day_abbr)), '|'.join(list(calendar.month_abbr)[1:]))
    reTime="(2[0-3]|[0-1][0-9]):[0-5][0-9]:[0-5][0-9]"
    reYear="\d{4}"
    reDate='{} {} {}'.format(reDay,reTime,reYear)    
            
    def getDate(div,sleep=0,host=host,reDate=reDate):
        if div.find('a')==None:
            return None
        else:
            url=host+div.find('a').get('href')
            rep=requests.get(url)
            rep.encoding='utf8'
            time.sleep(sleep)
            date=re.search(reDate,rep.text)
            if date==None:
                return None
            else:
                date=time.strptime(date.group(0))
                return datetime.date(date[0],date[1],date[2])
    
    
    ##get total page number
    indexPage=pageTemplate.format(board,'')
    rep=requests.get(indexPage)
    rep.encoding='utf8'
    soup=bs(rep.text,'lxml')
    indexPattern=u'<a class="btn wide" href=\"/bbs/'+board+u'/index(\d+).html\">&lsaquo; 上頁</a>'
    pages=int(re.search(indexPattern,rep.text).group(1))+1    

    #saving and confiquration    
    urls=[]
    crossYear=True if startDate.year<endDate.year else False 
    realDate=True  if (crossYear or sparseMode) else False    
    endDateFound=False
    #grab url
    for page in range(pages,1,-1):
        rep=requests.get(pageTemplate.format(board,page))
        rep.encoding='utf8'
        soup=bs(rep.text,'lxml')  

        ##get and filter divs by sepration line
        divs=soup.find(class_='r-list-container')
        sep=divs.find(class_='r-list-sep')
        if sep!=None:
            divs=sep.find_previous_siblings()
            divs.reverse()
        divs=[x for x in list(divs) if x!='\n']
               
        ## filter divs by date relationship #powerUp@1
        startIndex=0
        offset=0
        if not realDate:
            date=[x.find(class_='date').text.strip() for x in divs]
            date=[[int(y) for y in x.split('/')] for x in date]  
            date=[datetime.date(endDate.year,x[0],x[1]) for x in date]
            firstPostDate=date[0]        
            if firstPostDate<startDate: 
                while startIndex<len(date) and date[startIndex]<startDate:
                    startIndex+=1
            if not endDateFound:
                endIndex=startIndex
                while endIndex<len(date) and date[endIndex]<=endDate:
                    endIndex+=1
                if endIndex!=0:
                    endDateFound=True
            else:
                endIndex=len(date)
            divs=divs[startIndex:endIndex] 
    
        else: ### realDate flag
            ### get firstPostDate and defense for 404-not found
            for div in divs:
                firstPostDate=getDate(div)
                if firstPostDate!=None:
                    break
                else:
                    offset+=1
                    continue               
            
            dateTrans=False            
            if firstPostDate<startDate: 
                date=[getDate(x) for x in divs]
                print date
                dateTrans=True
                while offset+startIndex<len(date):
                    if date[offset+startIndex]==None:
                        startIndex+=1
                    else:
                         if date[offset+startIndex]<startDate:
                             startIndex+=1
                         else:
                             break
            if not endDateFound:  
                if not dateTrans:
                    date=[getDate(x) for x in divs]
                    print date
                divsIndex=[]
                for index in range(offset+startIndex,len(date)):
                    if date[index]==None:
                        offset+=1
                        continue
                    else:
                        if date[index]<=endDate:
                            divsIndex.append(index)
                        else:
                            break
                if len(divsIndex)!=0:
                    endDateFound=True
                divs=[divs[index] for index in divsIndex]
            else:
                divs=[x for x in divs[startIndex:] if x!=None] #避免 not found 
                            
        ## get url from cleaned divs and decide if whether crawling will going on or not
        if len(divs)>0:
            tempUrls=[host+x.find('a').get('href') for x in divs if x.find('a')!=None] #避免「本文已經刪除」 if not realDate
            if len(urls)==0:
                tempUrls.reverse()
            urls.extend(tempUrls)
            if startIndex!=0:
                return urls
            else:
                continue ###for page in pages
        else: 
            if len(urls)>0:
                return urls
            else:
                if not endDateFound and not startIndex+offset==len(date): #fix@1
                    continue
                else:
                    raise RuntimeError('No article post in the date range you assigned')

#%%

#def createTable(cur,dataType):
def dbSave(connection,startDate,endDate,mode='update',**kwargs):
        startDate=startDate.strftime('%Y-%m-%d')
        endDate=endDate.strftime('%Y-%m-%d')
        dataType='post' if kwargs.has_key('post') else 'push'        
        cur=connection.cursor()
        
        #table preparation
        tableExist=cur.execute("SELECT name FROM sqlite_master WHERE TYPE = 'table' AND name= '{}'".format(dataType))
        tableExist=tableExist.fetchone()
        #print mode, tableExist, tableExist==None
        if tableExist==None:
            if dataType=='post':
                cur.execute('''CREATE TABLE post (
                url CHAR(60),
                user CHAR(20),
                ip CHAR(15),
                time CHAR(20),
                title NVARCHAR,
                content NVARCHAR,
                pushCount INT,
                commentCount INT,
                booCount INT,
                actType CHAR(15),
                lastUpdate CHAR(20))''')
            else:
                cur.execute('''CREATE TABLE push (         
                url CHAR(60),
                postTime CHAR(20),
                user CHAR(20),
                time CHAR(20),
                content NVARCHAR,
                actType CHAR(15),
                lastUpdate CHAR(20))''')                  
        elif tableExist!=None and mode=='update':
            timeColumn='time' if dataType=='post' else 'postTime'
            cur.execute("DELETE FROM {a} WHERE date({b})>=date('{c}') and date({b})<=date('{d}')".format(a=dataType, b=timeColumn, c=startDate, d=endDate))
            connection.commit()
        #insert data
        dataList=[]
        for index, row in kwargs.get(dataType).iterrows():
            dataList.append(row.tolist())
        columnNum= 11 if dataType=='post' else 7
        cur.executemany("INSERT INTO {} VALUES({})".format(dataType,','.join(['?']*columnNum)), dataList)
#%%

def pttCrawler(board,startDate,endDate,sparseMode=False,**kwargs):
    urls=urlGrab(board,startDate,endDate,sparseMode)
    articles,pushes,errorLog=urlCrawl(urls)
    if not kwargs.has_key('notSave'): ## import only argument. Must saving when commandline using 
        if kwargs.has_key('filePath'):
            filePath=kwargs.get('filePath')
            startDate=startDate.strftime('%Y%m%d')
            endDate=startDate.strftime('%Y%m%d')
            articlePath='{}/{}_articles_{}-{}.xls'.format(filePath,board,startDate,endDate)
            pushesPath='{}/{}_pushes_{}-{}.xls'.format(filePath,board,startDate,endDate)
            errorLogPath='{}/{}_errorLog_{}-{}.csv'.format(filePath,board,startDate,endDate)        
            articles.to_excel(articlePath,index=False,encoding='utf8')
            pushes.to_excel(pushesPath,index=False,encoding='utf8')
            with open(errorLogPath,'w') as errorLogFile:
                [errorLogFile.write(x.encode('utf8')+'\n') for x in errorLog]
        elif kwargs.has_key('dbPath'):
            dbPath=kwargs.get('dbPath')
            dbMode=kwargs.get('dbMode')
            dbPath=os.getcwd()+'/'+dbPath if ':' not in dbPath else dbPath
            con=sqlite3.connect(dbPath)
            try:
                dbSave(con,startDate,endDate,mode=dbMode,post=articles)
                dbSave(con,startDate,endDate,mode=dbMode,push=pushes)
            except Exception:
                con.close()
                if dbMode=='create':
                    os.remove(dbPath)
                raise
            con.commit()
            con.close()
            errorLogPath='{}/{}_errorLog_{}-{}.csv'.format(os.path.dirname(dbPath),board,startDate,endDate)
    return(articles,pushes,errorLog)


#%%:

if __name__ =='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('board')
    parser.add_argument('--backDays',type=int, default=0)
    parser.add_argument('--startDate',help='the date start grabbing. YYYY/MM/DD')
    parser.add_argument('--endDate',default=datetime.date.today())
    parser.add_argument('--saveType',default='file', choices=['file','sqlite'])
    parser.add_argument('--filePath',default=os.getcwd())
    parser.add_argument('--dbMode',choices=['create','update','append'])
    parser.add_argument('--dbPath')
    parser.add_argument('--sparseMode',action='store_true')
    #parser.add_argument('--notSaved',action='store_true')
    args=parser.parse_args()
    #print parser.parse_args()
    
    #check and define startDate (and backDays)
    if args.startDate!=None:
        try:
            date=[int(x) for x in args.startDate.split('/')]
            startDate=datetime.date(date[0],date[1],date[2])
        except:
            raise argparse.ArgumentTypeError('--startDate [startDate]: {} is not a valid date format. Assign date with YYYY/MM/DD'.format(args.startDate)) 
    else:
        if args.backDays<0:
            raise argparse.ArgumentTypeError('--backDays [backDays]: {} is not a valid backDay. Only positive integer is allowed'.format(args.backDays)) 
        startDate=datetime.date.today()-datetime.timedelta(days=args.backDays)
        
    #check and define endDate
    if not isinstance(args.endDate,datetime.date):
        try:
            date=[int(x) for x in args.endDate.split('/')]
            endDate=datetime.date(date[0],date[1],date[2])
        except:
            raise argparse.ArgumentTypeError('--endDate [endDate]: {} is not a valid date format. Assign date with YYYY/MM/DD'.format(args.endDate))         
    else:
        endDate=args.endDate
        
    #check relationship bewtween startDate,endDate,and Today
    if startDate>endDate:
        raise argparse.ArgumentTypeError('--startDate [startDate] --endDate [endDate]: endDate must same or after startDate')         
    if endDate>datetime.date.today():
        raise argparse.ArgumentTypeError('--endDate [endDate]: endDate must same or before today.')         
        
    #check and define argumentList of saveType
    saveType=args.saveType
    if saveType=='file':
        filePath=args.filePath
        if not os.path.isdir(filePath):
            raise argparse.ArgumentTypeError('--saveType file [filePath]: Folder {} dose not exist'.format(filePath))
        result=pttCrawler(args.board,startDate,endDate,args.sparseMode,filePath=filePath)
    elif saveType=='sqlite':
        dbPath=args.dbPath        
        dbMode=args.dbMode
        tempList=['dbMode', 'dbPath']
        for i in range(2):            
            if eval(tempList[i])==None:
                raise argparse.ArgumentTypeError('--saveType sqlite: Must explicitly assign --{} when using saveType sqlite'.format(tempList[i]))
        if dbMode in ['update','append'] and not os.path.exists(dbPath):
            raise argparse.ArgumentTypeError('--dbMode {} --dbPath [dbPath]: Databese {} not exist'.format(dbMode,dbPath))
        elif dbMode=='create' and os.path.exists(dbPath):
            raise argparse.ArgumentTypeError('--dbMode {} --dbPath [dbPath]: Databese {} already existed'.format(dbMode,dbPath))     
        result=pttCrawler(args.board,startDate,endDate,args.sparseMode, dbPath=dbPath, dbMode=dbMode)
        
#%%
#test case with ipython
        
## function test        
#backDays, db create %run pttCrawler Soft_Job --backDays 2 --saveType sqlite --dbMode create  --dbPath Soft_Job.db
#backDays, db update %run pttCrawler Soft_Job --backDays 1 --saveType sqlite --dbMode update  --dbPath Soft_Job.db
#startDay, endDate %run pttCrawler Soft_Job --startDate 2016/05/20  --endDate 2016/05/23 --saveType sqlite --dbMode update  --dbPath Soft_Job.db        
#startDay, endDate sparseMode %run pttCrawler Soft_Job --startDate 2016/05/20  --endDate 2016/05/23 --saveType sqlite --dbMode update  --dbPath Soft_Job.db  --sparseMode              

## date
#%run pttCrawler B97310XXX --startDate 2016/05/20  --endDate 2016/05/23  --sparseMode

##input test
#%run pttCrawler Soft_Job --startDate 150030 --saveType sqlite --dbMode create  --dbPath Soft_Job.db
#%run pttCrawler Soft_Job --startDate 2016/12/30 --endDate 2015/01/01 --saveType sqlite --dbMode create  --dbPath Soft_Job.db