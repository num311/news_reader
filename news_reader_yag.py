#!/usr/bin/python3

from datetime import datetime, timedelta
from time import mktime
import logging
import feedparser
import yagmail



port = 465
#password = input("type your password: ")
password = "en un lugar de la mancha 1234"

yag = yagmail.SMTP(user='senderbender18@gmail.com',password='en un lugar de la mancha 1234', smtp_set_debuglevel=4)

receipt = "pmgiral@pm.me"

logging.basicConfig(level=logging.INFO)

now = datetime.now()
two_hour = timedelta(hours = 2)
two_hours_ago = now -two_hour

pwned = feedparser.parse('https://www.reddit.com/r/pwned/.rss')
meneame = feedparser.parse('https://www.meneame.net/rss')




def list_interesting(feed,cadena):
    result=""
    for i in range(0,len(feed.entries)):
        dt = datetime.fromtimestamp(mktime(meneame.entries[i]['updated_parsed']))
        if ( (cadena in feed.entries[i]['title'].lower()) or (cadena in feed.entries[i]['summary'].lower()) ) and (dt > two_hours_ago) :
            #result = result+"Title: %s\n\n author: %s\n\n Link: %s\n\n" % (  feed.entries[i]['title'] ,  feed.entries[i]['author'] , feed.entries[i]['link'])

            title =  feed.entries[i]['title']
            author = feed.entries[i]['author']
            url = feed.entries[i]['link']

            result = 'Titulo : '+title+  '\n\nAutor : '+ author + '\n\nEnlace : <a href='+url+'>'+url+'</a>'
    return result





#print('result='+list_interesting(meneame,'vuln'))

#if list_interesting(meneame,'vuln')!="":
if list_interesting(meneame, 'tronos') != "":
    logging.debug("noticia encontrada")
    subj = "Meneame : tronos "+datetime.now().strftime("%Y-%m-%d %H:%M")
    cont = list_interesting(meneame,'tronos')

    yag.send(
        to = receipt,
        subject = subj,
        contents = cont
    )




# if list_interesting(meneame,'bbva')!="":
#     subject = "Meneame : BBVA "+datetime.now().strftime("%Y-%m-%d %H:%M")
#     content = Content("text/plain", list_interesting(meneame,'bbva'))
#
#     message = f"""
#        Subject: {subject}
#
#
#        {content}
#        """
#
#     with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
#         server.login("senderbender18@gmail.com", password)
#
#         server.sendmail(sender, receipt, message)
#
#         logging.debug("email sent")
#


#else:
#    print("Sin noticias relevantes que mostrar")
