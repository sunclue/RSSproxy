from flask import Flask, Response
from feedgen.feed import FeedGenerator
from bs4 import BeautifulSoup
import requests
import os

app=Flask(__name__)

def generate_rss_for_github_trending():
    # 爬取页面
    target_url='https://github.com/trending'
    HEADERS = {
        'User-Agent'        : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
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
    return Response(rss, mimetype='application/rss_xml')

@app.route('/proxy/rss/<path:url>')
def proxy_rss(url):
    response = requests.get(url)
    return Response(response.content, mimetype='application/xml')