from bs4 import BeautifulSoup
import urllib2
import re
import sys
reload(sys)
sys.setdefaultencoding("utf8")
from urlparse import urlparse
import re
import os

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

def getTitle(soup, separator):
    title = soup.title.string
    title = title.split(separator)[0].strip()
    return title

def getTags(soup, tag, property, propertyValue, content):
    ct = []
    for tag in soup.findAll(tag, {property : propertyValue}):
        content = tag.attrs.get(content).lower()
        contentTag = content.split(",")
        for t in contentTag:
            ct.append(t.strip())

    return ct

def checkAndCreateDataFolder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    else:
        fileList = os.listdir(folder)
        for fileName in fileList:
            os.remove(folder+"/"+fileName)

def bbc_crawler():
    checkAndCreateDataFolder('data/bbc')
    url = 'http://www.bbc.com'
    source_code = urllib2.urlopen(url).read()
    soup = BeautifulSoup(source_code,"html.parser")
    count = 0;
    for link in soup.findAll('a', {'class': 'media__link'}):
        href = link.get('href')
        #This is to ignore video and image galleries
        if 'video-extras' in href or 'in-pictures-' in href or '/live/' in href:
            continue

        #Append the parent url only if the url is not well formed
        if href.startswith( '/' ) == True:
            href = url + href
        count += 1
        bbc_getContent(href,url, count)

def bbc_getContent(item_url,seedUrl,count):
    try:
        source_code = urllib2.urlopen(item_url).read()
        soup = BeautifulSoup(source_code,"html.parser")
        title = getTitle(soup, "-")
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

        ct = getTags(soup, 'meta', 'property', 'og:description', 'content')

        tagList = ",".join(map(str,ct))
        writeIntoFile("data/bbc/"+str(count)+".xml",seedUrl,item_url,title, desc,tagList)

    except Exception as inst:
        pass

def guardian_crawler():
    checkAndCreateDataFolder('data/guardian')
    url = 'http://www.theguardian.com/us'
    source_code = urllib2.urlopen(url).read()
    soup = BeautifulSoup(source_code,"html.parser")
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
        desc = ''
        title = getTitle(soup, "|")

        for para in soup.findAll('p', {'class' : ''}):
            desc += para.text

        ct = getTags(soup, 'meta', 'name', 'keywords', 'content')

        tagList = ",".join(map(str,ct))

        writeIntoFile("data/guardian/"+str(count)+".xml",seedUrl.strip(),item_url.strip(),title.strip(), desc.strip(),tagList)

    except Exception as inst:
        pass

def foxnews_crawler():
    checkAndCreateDataFolder('data/fox')
    url = 'http://www.foxnews.com/'
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = urllib2.Request(url,headers=hdr)
    source_code = urllib2.urlopen(req)
    soup = BeautifulSoup(source_code,"html.parser")
    count = 0
    links = []
    for link in soup.findAll('a'):
        href = link.get('href')
        parsed_uri = urlparse(href)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)

        pattern = re.compile("^http:\/\/www.foxnews.com\/[A-z]{1,}.html$")

        subsribe = re.compile("^http:\/\/www.foxnews.com\/.*\/subscribe.html$")

        index = re.compile("^http:\/\/www.foxnews.com\/.*\/index.html$")

        if url == domain and not (pattern.match(href) or subsribe.match(href) or index.match(href) or '/archive/' in href):
            links.append(href)

    links = set(links)
    #foxnews_getContent(url, 'http://www.foxnews.com/politics/2016/01/09/occam-s-razor-ny-rep-israels-retirement-explanation-smells-like-truth.html?intcmp=latestnews', 3)
    for l in links:
        count += 1
        foxnews_getContent(url, l, count)

def foxnews_getContent(seedUrl, item_url, count):
    #print item_url
    try:
        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = urllib2.Request(item_url,headers=hdr)
        source_code = urllib2.urlopen(req)
        soup = BeautifulSoup(source_code,"html.parser")
        title = getTitle(soup, "|")

        ct = getTags(soup, 'meta', 'name', 'keywords', 'content')
        tagList = ",".join(map(str,ct))
        desc = ''

        for para in soup.findAll('p', {'itemprop' : ''}):
            cls = para.attrs.get("class")
            if type(cls) is list and 'legal' in cls:
                continue
            else:
                followPattern = re.compile("^\+ Follow[A-z]{1,} on Facebook$")
                subscribePattern = re.compile("^Subscribe to the .{1,}\.$")
                twitterfollow =re.compile("^.{1,} follow them on Twitter: @.{1,}$")
                foxnewsContributorPattern = re.compile("^.{1,}, a Fox News contributor, .{1,}$")
                articleWrittenByPattern = re.compile("^This article was written by .{1,}$")
                clickHerePattern = re.compile("^Click here.{0,}$")
                copyright = re.compile("^.[0-9]{4} FOX News Network, LLC.{0,}$")
                paratext = para.text
                if followPattern.match(paratext) or subscribePattern.match(paratext) \
                        or paratext.lower() == 'advertisement' or paratext == 'Sign in to comment!'\
                        or paratext.startswith('Related:') or twitterfollow.match(paratext)\
                        or paratext.startswith('Author\'s note:')\
                        or paratext.startswith('WATCH:')\
                        or paratext == 'Don\'t miss a minute of opinion. Sign up for our newsletter now'\
                        or foxnewsContributorPattern.match(paratext)\
                        or articleWrittenByPattern.match(paratext)\
                        or clickHerePattern.match(paratext)\
                        or 'To explore more, ' in paratext\
                        or copyright.match(paratext):
                    continue

                desc += para.text

        writeIntoFile("data/fox/"+str(count)+".xml",seedUrl.strip(),item_url.strip(),title.strip(), desc.strip(),tagList)
    except:
        pass

def crawl():
    bbc_crawler()
    guardian_crawler()
    foxnews_crawler()

crawl()