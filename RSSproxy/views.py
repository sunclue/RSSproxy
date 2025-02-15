from flask import Response
from feedgen.feed import FeedGenerator
from bs4 import BeautifulSoup
import requests
import certifi
from urllib.parse import unquote

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
    entries = Box.find_all('article', class_='Box-row')
    
    # 创建Feed
    fg = FeedGenerator()
    fg.title('Github Trending Repositories')
    fg.link(href=target_url)
    fg.description('Daily trending repositories on GitHub')
    
    for entry in entries:
        title = entry.find('h2').text
        link = entry.find('h2').find('a')['href']
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

    decoded_url=unquote(url)

    if decoded_url.startswith('http:/') and not decoded_url.startswith('http://'):
        decoded_url = decoded_url.replace('http:/', 'http://', 1)
    elif decoded_url.startswith('https:/') and not decoded_url.startswith('https://'):
        decoded_url = decoded_url.replace('https:/', 'https://', 1)

    HEADERS = {
        'User-Agent'        : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept'            : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    }
    try:
        response = requests.get(
            decoded_url,
            headers=HEADERS,
            proxies={
                'http':'',
                'https':''
            },
            verify=certifi.where(),      # 使用certifi的CA证书
            timeout=10
            )
        return Response(response.content, mimetype='application/xml')
    except requests.exceptions.RequestException as e:
        return f"error: {str(e)}", 502

@app.route('/')
def hello():
    return 'hello'