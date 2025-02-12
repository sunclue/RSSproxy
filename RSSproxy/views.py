from flask import Response
from feedgen.feed import FeedGenerator
from bs4 import BeautifulSoup
import requests

from RSSproxy import app

def generate_rss_for_github_trending():
    # 爬取页面
    target_url='https://github.com/trending'
    HEADERS = {
        'User-Agent'        : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept'            : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding'    : 'gzip,deflate,sdch',
        'Accept-Language'    : 'zh-CN,zh;q=0.8'
    }
    response = requests.get(target_url,headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    Box = soup.find('div', class_='Box')
    entries = Box.find_all('div', class_='Box-row')
    
    # 创建Feed
    fg = FeedGenerator()
    fg.title('Github Trending Repositories')
    fg.link(href=target_url)
    fg.description('Daily trending repositories on GitHub')
    
    for entry in entries:
        title = entry.find('h2').text
        link = entry.find('a')['href']
        content = entry.find('p').text
        
        fe = fg.add_entry()
        fe.title(title)
        fe.link(href='https://github.com/'+link)
        fe.description(content)
    
    return fg.rss_str()

@app.route('/proxy/githubtrending')
def proxy_github_trending():
    rss = generate_rss_for_github_trending()
    return Response(rss, mimetype='application/xml')

@app.route('/proxy/rss/<path:url>')
def proxy_rss(url):
    response = requests.get(url)
    return Response(response.content, mimetype='application/xml')

@app.route('/')
def hello():
    return 'hello'