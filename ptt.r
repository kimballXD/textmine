library('httr')
library('rvest')
library('lubridate')

toBig5<-function(x){
  return(iconv(x,'UTF-8','big-5'))
}

inlineIpv4='((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'

ptt='https://www.ptt.cc/bbs/creditcard/index.html'
indexPage=httr::GET(ptt)
indexPpage=httr::content(indexPage,as='text')
pageXml=xml2::read_html(indexPpage)
title=html_nodes(pageXml,css='.r-ent a')
urls=html_attr(title,'href')
urls=sapply(urls,function(x){paste0('https://www.ptt.cc',x)})
urls=as.character(urls)
urls=urls[1:3] 
rowList=list()
for(i in seq_along(urls)){
  page=content(GET(urls[i]),as='text')
  pageXml=read_html(page)
  #tags=toBig5(html_text(html_nodes(pageXml,css='.article-meta-tag')))
  values=toBig5(html_text(html_nodes(pageXml,css='.article-meta-value')))
  author=strsplit(values[1],' ')[[1]][1]
  title=values[3]
  time=unlist(strsplit(values[4],' '))
  time=paste(time[5],match(time[2],month.abb),time[3],time[4],sep=' ')
  time=lubridate::ymd_hms(time, tz='Asia/Taipei') #timezone info:see OlsonNames()
  url=urls[i]
  ip=regmatches(pageXml,regexpr(inlineIpv4,pageXml))
  temp=data.frame(url,author,title,time,ip,stringsAsFactors = F)
  rowList[1+length(rowList)]<-list(temp)
}
data=do.call(rbind, rowList)

author=html_nodes(pageXml,css='.author')
author=toBig5(html_text(author))


title=toBig5(html_text(title))
postDate=html_nodes(pageXml,css='.date')
postDate=toBig5(html_text(postDate))
data=data.frame(title,author,postDate)

page2=read_html(ptt)
title2=rvest::html_nodes(pageXml,css='.r-ent a')
b=rvest::html_text(title2[14])


substr(a,as.numeric(regexpr('\n',a))+1,nchar(a))
