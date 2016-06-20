import scrapy, json
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
        sites = ['monster.com', 'meroanswer.com', 'upwork.com', 'canva.com', 'twitter.com']
        all_links = []
        for site in sites:
            full_url = "https://www.similarweb.com/website/" + site
            my_request = scrapy.Request(
                url=full_url,
                # headers=headers,
                callback=self.parse_items,)
            my_request.meta['domain'] = {
                "domain": site

            }
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
        # sel = Selector(response)
        # time.sleep(2)
        # my_file = open('body.html', 'w+b')
        # my_file.write(response.body)
        content = self.driver.find_element_by_class_name('stickyHeader-names').text
        print "content is", content
        result = self.driver.execute_script("return Sw.preloadedData")
        print "result is", result, type(result)
        # time.sleep(2)
        description = self.driver.find_element_by_class_name(
            'analysis-descriptionText').text
        print "description is", description
        try:
            global_rank = self.driver.find_element_by_xpath(
                '//div[@class="rankingItem--global"]//div[@class="rankingItem-value"]'
            ).text
        except:
            global_rank = None
        print global_rank
        data = {}
        data['SimilarWebURL'] = self.driver.current_url
        data['Domain'] = response.meta['domain']['domain']
        # data['Ranks'] = {}
        rank_dict = {}
        global_rank = {}
        global_rank['Rank'] = result['overview']['GlobalRank'][0]
        rank_dict['Global_Rank'] = global_rank
        # data['Ranks'] = global_rank_dict

        # country_rank_dict = {}
        country_rank = {}
        country_rank['Rank'] = result['overview']['CountryRanks'].values()[0][0]
        rank_dict['Country_Rank'] = country_rank
        # data['Ranks'] = country_rank_dict

        # category_rank_dict = {}
        category_rank = {}
        category_rank['Rank'] = result['overview']['CategoryRank']
        rank_dict['Category_Rank'] = category_rank
        data['Ranks'] = rank_dict

        engagement = {}
        engagement['Date'] = result['overview']['Engagements']['LastEngagementYear']
        engagement['Total_Visits'] = result['overview']['Engagements']['TotalLastMonthVisits']
        engagement['Avg_Time_On_Page'] = result['overview']['Engagements']['TimeOnSite']
        engagement['Avg_Page_Views'] = result['overview']['Engagements']['PageViews']
        engagement['Bounce_Rate'] = result['overview']['Engagements']['BounceRate']
        visits = []
        if result['overview']['Engagements']['WeeklyTrafficNumbers']:
            traffic = result['overview']['Engagements']['WeeklyTrafficNumbers']
            for key, value in traffic.iteritems():
                visit = {}
                visit[key] = value
                visits.append(visit)
        engagement['Visits'] = visits
        data['Engagements'] = engagement

        traffic = {}
        direct_percentage = {}
        direct_percentage['Percent'] = result['overview']['TrafficSources']['Direct']
        traffic['Direct'] = direct_percentage

        referral = {}
        top_reffering = {}
        top_destination = {}
        referral['Percent'] = result['overview']['TrafficSources']['Referrals']
        if result['overview']['Referrals']:
            domains = []
            destinations = result['overview']['Referrals']['destination']
            if destinations:
                # top_destination = {}
                for dest in destinations:
                    dest_dict = {}
                    dest_dict['Domain'] = dest['Site']
                    dest_dict['Percent'] = dest['Value']
                    domains.append(dest_dict)
                top_destination['Domains'] = domains
            destinations = result['overview']['Referrals']['referrals']
            if destinations:
                # top_reffering = {}
                for dest in destinations:
                    dest_dict = {}
                    dest_dict['Domain'] = dest['Site']
                    dest_dict['Percent'] = dest['Value']
                    domains.append(dest_dict)
                top_reffering['Domains'] = domains
        referral['Top_Refering'] = top_reffering
        referral['Top_Destination'] = top_destination
        traffic['Referrals'] = referral

        data['Traffic_Sources'] = traffic

        # print 'data is', data
        # my_file = open('data.json', 'w+b')
        # my_file.write(data)
        with open('data.txt', 'a') as outfile:
            json.dump(data, outfile)

        self.driver.execute_script("document.cookie='';")
