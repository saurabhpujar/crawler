import requests
from bs4 import BeautifulSoup
import urllib2
import re
import sys
reload(sys)
sys.setdefaultencoding("utf8")

def bbc_crawler():
    url = 'http://www.bbc.com'
    source_code = urllib2.urlopen(url).read()
    soup = BeautifulSoup(source_code,"html.parser")
    count = 0;
    for link in soup.findAll('a', {'class': 'media__link'}):
        href = link.get('href')
        #This is to ignore video and image galleries
        if 'video-extras' in href or 'in-pictures-' in href:
            continue

        #Append the parent url only if the url is not well formed
        if href.startswith( '/' ) == True:
            href = url + href
        title = link.text.strip()
        count += 1
        bbc_getContent(href,url,title, count)

def bbc_getContent(item_url,seedUrl,title,count):
    try:
        #logging.info('Inside inner method')
        source_code = urllib2.urlopen(item_url).read()
        soup = BeautifulSoup(source_code,"html.parser")
        #resource = NewsData(parent=newsData_key(seedUrl))
        #resource.seedUrl = seedUrl
        #resource.url = item_url
        #resource.title = title
        desc = ''
        for intro in soup.findAll('p', {'class' : 'story-body__introduction'}):
            introText = intro.text
            desc += introText
            desc += '\n'

        for para in soup.findAll('p', {'class' : ''}):
            cls = para.attrs.get("class")
            if not cls:
                paraText = para.text
                desc += paraText
                desc += '\n'

        #logging.info("Description : "+desc)
        #resource.description = desc

        ct = []
        for tag in soup.findAll('meta', {'property' : 'og:description'}):
            content = tag.attrs.get("content").lower()
            contentTag = content.split(" ")
            for t in contentTag:
                ct.append(t.strip())

        #logging.info("Tags : "+ct)
        #resource.tags = ct
        tagList = ",".join(map(str,ct))
        #resource.put()
        writeIntoFile("data/bbc/"+str(count)+".xml",seedUrl,item_url,title, desc,tagList)

    except Exception as inst:
        #logging.info(inst)
        #logging.info('Inside exception')
        pass

def writeIntoFile(loc,seedUrl,item_url,title, desc,tagList):
    print "Making " + loc
    resource = open(loc, "wb")
    resource.write("<seedurl>")
    resource.write("\n\t"+seedUrl)
    resource.write("\n</seedurl>")

    resource.write("\n<url>")
    resource.write("\n\t"+item_url)
    resource.write("\n</url>")

    resource.write("\n<title>")
    resource.write("\n\t"+title)
    resource.write("\n</title>")

    resource.write("\n<description>")
    resource.write("\n\t"+str(desc))
    resource.write("\n</description>")

    resource.write("\n<tags>")
    resource.write("\n\t"+tagList)
    resource.write("\n</tags>")

    resource.close()

def guardian_crawler():
    url = 'http://www.theguardian.com/us'
    source_code = urllib2.urlopen(url).read()
    soup = BeautifulSoup(source_code)
    count = 0
    links = []
    for link in soup.findAll('a', {'data-link-name': 'article'}):
        href = link.get('href')
        #This is to ignore video and image galleries
        if '/thecounted' in href or '/video/' in href:
            continue
        links.append(href)

    links = set(links)

    for l in links:
        count += 1
        guardian_getContent(url, l,count)

def guardian_getContent(seedUrl, item_url, count):
    try:
        #logging.info('Inside inner method')
        source_code = urllib2.urlopen(item_url).read()
        soup = BeautifulSoup(source_code,"html.parser")
        #resource = NewsData(parent=newsData_key(seedUrl))
        #resource.seedUrl = seedUrl
        #resource.url = item_url
        #resource.title = title
        desc = ''
        title = soup.title.string
        title = title.split("|")[0].strip()

        for para in soup.findAll('p', {'class' : ''}):
            desc += para.text

        #logging.info("Description : "+desc)
        #resource.description = desc

        ct = []
        for tag in soup.findAll('meta', {'name' : 'keywords'}):
            content = tag.attrs.get("content").lower()
            contentTag = content.split(",")
            for t in contentTag:
                ct.append(t.strip())

        #logging.info("Tags : "+ct)
        #resource.tags = ct
        tagList = ",".join(map(str,ct))
        #resource.put()

        # print 'Title : '+title
        # print 'Seed : '+ seedUrl
        # print 'Link : '+item_url
        # print 'Title : '+title
        # print 'Desc : '+desc
        # print 'Tag List : '+tagList
        writeIntoFile("data/guardian/"+str(count)+".xml",seedUrl.strip(),item_url.strip(),title.strip(), desc.strip(),tagList)

    except Exception as inst:
        #logging.info(inst)
        #logging.info('Inside exception')
        pass

def crawl():
    bbc_crawler()
    guardian_crawler()

crawl()