# -*- coding: utf-8 -*-
"""
Created on Thu Jul 07 19:44:28 2016

@author: Wu
"""

from collections import Counter
import re
import pandas as pd
import math
#%%

with open('hegel.txt','r') as input:
    content=input.read()
    content=content.decode('utf8')
    content=content.replace('\n',u'。')
#content=re.sub('',content,flags=re.U)
#%%


def rangeGram(chars,max,min):
    rangeGramCounter=Counter()
    for n in range(min,max+1):
        ngramCounter=Counter()
        for i in range(0,len(chars)-n+1):
            charSlice=chars[i:i+n]
            # invalid=len([w for w in skip_word if w in segment])
            # if invalid==0:
                # sentenceCounter[ngramPart]+=1
            if re.match(u"[\u4e00-\u9fa5]",charSlice):
                ngramCounter[charSlice]+=1
        rangeGramCounter=rangeGramCounter+ngramCounter
    return rangeGramCounter

def getNgramCounter(article,max,min):
    delimiter=u'，|：|。|、|/|；|（|）|\(|\)|「|」|」|《|》|／|【|……|）|「|！|‧|\[|\]'
    articleCounter=Counter()
    for sentence in re.split(delimiter,article):
        if sentence is not None and sentence.strip()!='':
            #c=ngram(removeKey(sentence.strip(),keywords),i) #取ngram
            sentenceCounter=rangeGram(sentence.strip(),max,min) #取ngram
            articleCounter=articleCounter+sentenceCounter
    return articleCounter


counter=getNgramCounter(content,5,1)
counterList=zip(counter.keys(),counter.values())
total=float(sum(counter.values()))
pDict=dict(zip(counter.keys(),[x/total for x in counter.values()]))
data=pd.DataFrame(counterList,columns=['word','count'])
data['len']=data['word'].apply(lambda x:len(x))
data=data.sort_values(['count'],ascending=False)



#%%
## filter by frequency and word length

data2=data[(data['len']>1)&(data['count']>5)]

#%%
## filter by breaking-border

def arbCombInd(x,pDict):
    if len(x)==2:
        return pDict[x]/(pDict[x[0]]*pDict[x[1]])
    elif len(x)==3:
        comb1=pDict[x]/(pDict[x[:2]]*pDict[x[2]])
        comb2=pDict[x]/(pDict[x[0]]*pDict[x[1:]])
        return min(comb1, comb2)
    elif len(x)==4:
        comb1=pDict[x]/(pDict[x[:3]]*pDict[x[3]]) #3+1
        comb2=pDict[x]/(pDict[x[0]]*pDict[x[1:]]) #1+3
        comb3=pDict[x]/(pDict[x[:2]]*pDict[x[2]]*pDict[x[3]]) #2+1+1
        comb4=pDict[x]/(pDict[x[0]]*pDict[x[1]]*pDict[x[2:]]) #1+1+2
        comb5=pDict[x]/(pDict[x[0]]*pDict[x[1:3]]*pDict[x[3]]) #1+2+1
        comb6=pDict[x]/(pDict[x[:2]]*pDict[x[2:]])#2+2
        return min(comb1,comb2,comb3,comb4,comb5,comb6)
    else:
        return 0.0

data2['arbCombInd']=data2['word'].apply(arbCombInd,pDict=pDict)

#%%
# filter by stop-within-border

def entropy(counter):
    if len(counter)<=1:
        return 0.0
    result=0.0
    total=float(sum(counter.values()))
    for item in counter:
        p=counter[item]/total
        result += p*math.log(p,2)
    return abs(result)

def entropyCol(x,wordList):
    leftIncList=[]
    rightIncList=[]
    for w in wordList:
        if (x in w) and (len(w)==len(x)+1):
            if re.search(u'.{}'.format(x),w):
                leftIncList.append(w)
        else:
            rightIncList.append(w)
    leftCounter=Counter(leftIncList)
    rightCoutner=Counter(rightIncList)
    return min(entropy(leftCounter),entropy(rightCoutner))

data2['entropy']=data2['word'].apply(entropyCol,wordList=data['word'])

#%%
data3=data2[(data2['arbCombInd']>100)&(data2['entropy']>1)]



