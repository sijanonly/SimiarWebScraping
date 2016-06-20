import scrapy
from scrapy.selector import Selector

from scrapy.spiders.init import InitSpider
from scrapy.http import Request, FormRequest
from scrapy.xlib.pydispatch import dispatcher
from selenium import webdriver
from selenium import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
import time

from SimilarScraper.items import SimilarscraperItem


class SimilarSpider(InitSpider):
    handle_httpstatus_list = [404, 500]
    name = 'selspider'
    allowed_domains = ['www.similarweb.com']
    start_urls = ['https://www.similarweb.com', ]

    def init_request(self):
        """This function is called before crawling starts."""
        self.driver = webdriver.Firefox()
        # self.driver.implicitly_wait(30)
        return Request(url='https://www.similarweb.com', callback=self.parse)

    def parse(self, response):
        sites = ['monster.com']
        all_links = []
        for site in sites:
            full_url = "https://www.similarweb.com/website/" + site
            my_request = scrapy.Request(
                url=full_url,
                # headers=headers,
                callback=self.parse_items,)
            all_links.append(my_request)
        return all_links

    def clean_history(self, sel, domain):
        temp = sel.get_location()
        # for domain in domains:
        sel.open(domain)
        sel.delete_all_visible_cookies()
        sel.open(temp)

    def parse_items(self, response):
        delay = 3
        print "parse items entered"
        # self.driver.implicitly_wait(10)
        scrape_url = response.url
        # self.clean_history(self.driver, self.allowed_domains[0])
        self.driver.get(scrape_url)
        # try:
        elm = ec.presence_of_element_located(
            (By.CSS_SELECTOR, 'h1.stickyHeader-names'))
        WebDriverWait(self.driver, delay).until(elm)
        sel = Selector(response)
        time.sleep(2)
        print ('cookie is', response.headers.getlist('Set-Cookie')[0].split(";")[0].split("=")[1])
        my_file = open('body.html', 'w+b')
        my_file.write(response.body)
        print "response headers up", response.headers
        content = self.driver.find_element_by_class_name('stickyHeader-names').text
        print "content is", content
        result = self.driver.execute_script("return Sw.preloadedData")
        print "result is", result
        # time.sleep(2)
        items = response.xpath(
            '//script/text()').re(r"Sw\.preloadedData = {([^}]*)}")
        print items
        try:
            global_rank = self.driver.find_element_by_xpath(
                '//div[@class="rankingItem--global"]//div[@class="rankingItem-value"]'
            ).text
        except:
            global_rank = None
        print global_rank
        self.driver.execute_script("document.cookie='';")
