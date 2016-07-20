# -*- coding: utf-8 -*-
"""
Created on Tue May 24 18:09:59 2016

@author: Wu
"""

signaturePattern=u'(--\n((.+?)\n){,6}\n)--\n※'
signature=''
if re.search(signaturePattern,mainContent)!=None:
    signature=re.search(signaturePattern,mainContent).group(1)
    mainContent=mainContent.replace(signature,'')
    
    
citationLog=u'<span class="f2">※ 引述.+?</span>'