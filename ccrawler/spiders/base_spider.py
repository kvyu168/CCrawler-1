import os
import re
import urllib2
import urllib
import time
import logging

from urlparse import urljoin
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http.request import Request
from scrapy.shell import inspect_response
from ccrawler.items import BaseItem

from ccrawler.settings import *
from ccrawler.utils.urls_manager import UrlsManager

class BaseSpider(BaseSpider):
    name = DEFAULT_SPIDER
    start_urls = ()
    allowed_domains = []
    items = []

    
    def __init__(self, rdir="remote_data", urlfile=DEFAULT_URLS_LIST_FILE):

    	# create a remote directory if one does not exists
    	if not os.path.exists("../../"+rdir):
                os.makedirs("../../"+rdir)

        # TODO: replace the root directory with constant or configuratoin value
        urls_list_path = os.path.join(
            os.path.dirname(__file__), "../../", urlfile)

        # Setting start_urls and allowed_domains from the urls.txt file,
        # located in <project>/urls.txt
        start_urls_list = []
        self.urls_manager = UrlsManager()
        
        with open(urls_list_path, "r") as urls:
            for line in urls:
                if re.match("^#", line):
                    continue
                elif re.match("^http://", line):
                    current_visit_url = line.rstrip()
                    # Checking is target file exists based on return code
                    try:
                        pre_crawldb_path = os.path.join(current_visit_url, 'ccdata', CRAWL_FILE_NAME)
                        # CHECKME: If urlopen tries to non-exist url, then it may raise an exception. 
                        ret = urllib2.urlopen(pre_crawldb_path)
                        if ret.getcode() == 200:  # ccrawler file exists. Skip normal crawl...
                            rcopy_local = open("../../"+rdir+'/' + 'remote_crawl_data-' + str(
                                int(time.time())) + '.json', 'w')
                            rcopy_local.write('<crawlRemoteURL>' + current_visit_url + '</crawlRemoteURL>\n')
                            rcopy_local.write(ret.read())
                            rcopy_local.close()
                            print("Crawl data found on target... Skipping crawling...")
                            continue
                    except: # file does not exists. Perform normal crawl... 
                        start_urls_list.append(line.strip())
                            
                else:
                    self.allowed_domains.append(line.strip())

        self.start_urls = tuple(start_urls_list)
        self.urls_manager.add_urls("", start_urls_list, visited=True)
        
    def parse(self, response):
        current_visit_url = response.url
        logging.info ("Vistied: %s" % current_visit_url)
		
        # Just for debugging -------------------------------------------------------------
        # inspect_response(response) # Invoking the shell from spiders to inspect responses
        # ---------------------------------------------------------------------------------
        hxs = HtmlXPathSelector(response)
        next_candidate_urls = hxs.select("//html/body/div[3]/ul/li[3]/a/@href").extract()
        title = hxs.select("//head/title/text()").extract()
        body = "".join(hxs.select('//div[contains(@class, "body")]//text()').extract())

        item = BaseItem()
        item['id'] = current_visit_url
        item['title'] = title[0]
        item['content'] = body
#        item['link' ] = current_visit_url
        self.items.append(item)

        links = hxs.select("//a/@href").extract()
        print("Links in %s" % current_visit_url)
        # for index, link in enumerate(links):
        # print("\t[%02d]: %s" %(index, urljoin(current_visit_url, link)))
        yield item
      
        
        if next_candidate_urls:
            self.urls_manager.add_urls(current_visit_url, next_candidate_urls)

        logging.debug(self.urls_manager.show_current_urls_status())
        
        next_url = self.urls_manager.get_next_url()
        
        if next_url is not None:
            logging.info ("\tnext_url -> %s" % next_url)
            yield Request(next_url, self.parse)          

    
