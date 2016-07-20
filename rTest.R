library('httr')
library('rvest')

#example1
url='https://www.ptt.cc/bbs/creditcard/M.1463725283.A.79A.html'
page=read_html(url,encoding='UTF-8')
body=html_text(html_node(page,css='body')) 
iconv(body,from='UTF-8',to='BIG-5') #不可
mainContainer=html_text(html_node(page,css='#main-container')) 
iconv(mainContainer,from='UTF-8',to='BIG-5') #可


#exmple2