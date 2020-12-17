from flask import Flask, render_template, request
import logging, urllib.request, urllib.error, urllib.parse, json, webbrowser, datetime, requests

app = Flask(__name__)

@app.route("/")
def main_handler():
    app.logger.info("In MainHandler")
    return render_template('search.html',page_title="News search")
@app.route("/oldnews")
def search_handler():
    app.logger.info(request.args.get('key'))
    key = request.args.get('key')
    if not key:
        return render_template('search.html',
        page_title="News search",
        prompt="Please enter a keyword")
    app.logger.info(request.args.get('language'))
    language = request.args.get('language')
    if not language:
        language = 'en'
    app.logger.info(request.args.get('size'))
    size = request.args.get('size')
    if not size:
        size = 20
    size = int(size)
    if size<1 or size>100:
        return render_template('search.html',
        page_title="News search",
        prompt="Incorrect page size, please check.")
    app.logger.info(request.args.get('sort'))
    sort = request.args.get('sort')
    if not sort:
        sort='publishedAt'
    if sort not in ['relevancy', 'popularity', 'publishedAt']:
        return render_template('search.html',
        page_title="News search",
        prompt="Incorrect sort method, please check.")
    newslist=getnews(key=key, language=language, sortby=sort, pageSize=size)
    if newslist != []:
        return render_template('Newsresponse.html',
        page_title="Old News",
        mynews=newslist)
    return render_template('search.html',
        page_title="News search",
        prompt="Sorry, we don't support this language or the language code is incorrect, please check.")

def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

def safe_get(url):
    try:
        return urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        print("The server couldn't fulfill the request." )
        print("Error code: ", e.code)
    except urllib.error.URLError as e:
        print("We failed to reach a server")
        print("Reason: ", e.reason)
    return None

def newsREST(baseurl = 'http://newsapi.org/v2/everything',
    apiKey = '89ce22a41f8d49a0951c7100c88f6eaa',
    params={},
    printurl = False
    ):
    params['apiKey'] = apiKey
    if format == "json": params["nojsoncallback"]=True
    url = baseurl + "?" + urllib.parse.urlencode(params)
    if printurl:
        print(url)
    return safe_get(url)

def getinfo(news):
    infolist={}
    for new in news['articles']:
        infolist[new['title']] = {'description': new['description'],'url': new['url'], 'date': new['publishedAt']}
    return infolist

def printinfo(infolist):
    count = 1
    string =[] #add string to a list, then [% for word in list] - <br>{{word}}?
    for x in infolist:
        string.append('News[{count}]:'.format(count=count))
        string.append("Title: {x}".format(x=x))
        string.append("Description: {desc}".format(desc=infolist[x]['description']))
        string.append("Url: {url}".format(url=infolist[x]['url']))
        string.append("Published: {date}".format(date=infolist[x]['date']))
        string.append("---------------------------------------------------")
        count = count + 1
    return string

#language: language code. Default: en.
#start: A date and optional time for the oldest article allowed. This should be in ISO 8601 format (e.g. 2020-12-08 or 2020-12-08T09:46:24) Default: today's time.
#end: A date and optional time for the newest article allowed. Default: today's time.
#sortby: The order to sort the articles in. Possible options: relevancy, popularity, publishedAt.
         #relevancy = articles more closely related to q come first.
         #popularity = articles from popular sources and publishers come first.
         #publishedAt = newest articles come first.
         #Default: publishedAt
#pageSize: The number of results to return per page. 20 is the default, 100 is the maximum.
def getnews(key, language='en', sortby='publishedAt',pageSize=20):
    todaytime = datetime.date.today() - datetime.timedelta(days=30)
    result = newsREST(printurl=True, params={"qInTitle": key, "language": language, "from": todaytime,"to": todaytime, "sortBy": sortby, "pageSize": pageSize}).read()
    jsonresult = json.loads(result)
    newslist = getinfo(jsonresult)
    return printinfo(newslist)
