# -*- coding: utf-8 -*-
"""
Created on Tue May 17 13:11:10 2016

@author: Wu
"""



#%%
import sqlite3
con=sqlite3.connect('test.db')
cur=con.cursor()
cur.execute('DROP TABLE IF EXISTS test')
cur.execute('CREATE TABLE test(name TEXT, date datetime)')
cur.execute('INSERT INTO test VALUES("kimball", "1986-09-27 00:00:00")')
cur.execute('INSERT INTO test VALUES("kimball2", "1986-10-01 00:00:00")')
cur.execute('INSERT INTO test VALUES("kimball3", "1986-11-01 00:00:00")')
cur.execute('INSERT INTO test VALUES(?,?)',[['kimball','2016-01-01 00:00:00'],['kimball','2016-02-02 00:00:00']])
print cur.execute('SELECT * FROM test WHERE date(date)>date("1986-09-30")').fetchall()
con.commit()
con.close()
#%%
rep=cur.execute("SELECT name FROM sqlite_master WHERE TYPE = 'table' AND name= 'test'")
print rep.fetchone()




#%%
#create database
con=sqlite3.connect('test.db')
cur=con.cursor()
cur.execute('DROP TABLE IF EXISTS post')
cur.execute('''create table POST (         
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
            lastUpdate CHAR(20)
            )''')            
#insert article      
temp=[]
articles=articles.reindex_axis(['url','user','ip','time','title','postContent','pushCount','commentCount','booCount','actType'],axis=1)
for index, row in articles.iterrows():
    temp.append(row.tolist())
cur.executemany('INSERT INTO post VALUES(?,?,?,?,?,?,?,?,?)',temp)

cur.execute('DROP TABLE IF EXISTS push')
cur.execute('''create table push (         
            url CHAR(60),
            postTime CHAR(20),
            user CHAR(20),
            time CHAR(20),
            content NVARCHAR,
            actType CHAR(15),
            lastUpdate CHAR(20)
            )''')  
            
temp=[]
pushes=pushes.reindex_axis(['url','user','time','pushContent','actType'],axis=1)
for index, row in pushes.iterrows():
    temp.append(row.tolist())
cur.executemany('INSERT INTO push VALUES(?,?,?,?,?)',temp)                        
con.commit()
con.close()


#%%
