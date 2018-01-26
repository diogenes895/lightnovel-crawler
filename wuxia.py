#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Crawler LNMTL novels and create epub files

[LNMTL](https://lnmtl.com) is a website containing machine translated
novels. This code will convert any given book from this site into epub.
"""
import sys
from os import path, makedirs
import re
import json
from splinter import Browser
from binding import novel_to_kindle

novel_name = 'Unknown'


def get_browser():
    executable_path = path.join('lib', 'chromedriver')
    return Browser('chrome',
                   headless=True,
                   incognito=True,
                   executable_path=executable_path)
# end def

def start():
    try:
        meta_info()
        crawl_pages(start_url)
        novel_to_kindle(output_path)
    finally:
        browser.quit()
    # end try
# end def

def meta_info():
    global novel_name
    print('Visiting:', home_url)
    browser.visit(home_url)
    novel_name = browser.find_by_css('h1.entry-title').first.text
    novel_name = re.sub(r' – Index$', '', novel_name)
# end def

def crawl_pages(url):
    # visit url
    print('Visiting:', url)
    if not url: return
    browser.visit(url)
    next_link = browser.find_link_by_partial_text('Next Chapter')
    if not next_link: return
    # get contents
    articles = browser.find_by_css('div[itemprop="articleBody"] p')
    chapter_title = articles[1].text
    body = [articles[i].text for i in range(len(articles)) if 2 <= i < len(articles) - 4]
    # format contents
    chapter_no = re.search(r'\d+.?$', url).group().strip('/')
    content = {
        'url': url,
        'novel': novel_name,
        'chapter_no': chapter_no,
        'chapter_title': chapter_title,
        'volume_no': str(int(chapter_no) // 100),
        'body': [x.strip() for x in body if x.strip()]
    }
    # save data
    save_chapter(content)
    # move on to next
    if chapter_no != end_chapter:
        crawl_pages(next_link.first['href'])
    # end if
# end def

def save_chapter(content):
    # save to file
    vol = content['volume_no'].rjust(2, '0')
    chap = content['chapter_no'].rjust(5, '0')
    file_name = path.join(output_path, vol, chap + '.json')
    if not path.exists(path.dirname(file_name)):
        makedirs(path.dirname(file_name))
    # end if
    with open(file_name, 'w') as file:
        file.write(json.dumps(content))
    # end with
# end def

if __name__ == '__main__':
    novel_id = sys.argv[1]
    start_chapter = sys.argv[2]
    end_chapter = sys.argv[3] if len(sys.argv) > 3 else ''
    output_path = path.join('_novel', novel_id)

    home_url = 'http://www.wuxiaworld.com/%s-index' % (novel_id)
    start_url = '%s/%s-chapter-%s' % (home_url, novel_id, start_chapter)

    browser = get_browser()
    start()
# end if