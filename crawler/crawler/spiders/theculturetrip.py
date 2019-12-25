import scrapy
import json
import re
from requests.models import PreparedRequest
from crawler.items import CrawlerItem


class CultureTripSpider(scrapy.Spider):
    name = "theculturetrip"

    scrolled_article = []

    base_url = ''
    api_url = ''
    counter = 0
    total = 0
    i = 1

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'scrolled_article': ''
    }

    params = {
        'queryType': 'location_page',
        'kgID': '',
        'offset': 0,
        'limit': 15,
    }

    def start_requests(self):
        urls = ['https://theculturetrip.com/asia/malaysia']

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        jres = re.findall(
            "\{\".*\:\{.*\:.*\}", response.body.decode("utf-8"))
        jres = json.loads(jres[0])

        for url in jres['props']['pageProps']['locationStoreState']['spotlightPicks']:
            self.base_url = jres['props']['pageProps']['env']['WP_BASE']
            next_url = self.base_url + url['url']
            self.scrolled_article.append(
                jres['props']['pageProps']['locationStoreState']['spotlightPicks'][self.counter]['id'])
            self.counter = self.counter + 1
            yield scrapy.Request(url=next_url, callback=self.parse_details)

        self.total = jres['props']['pageProps']['locationStoreState']['locationData']['locationResources'][0]['articleCounter']
        self.headers.update({'scrolled_article': (
            str(self.scrolled_article)[1:-1]).replace(" ", "")})
        self.params['kgID'] = jres['props']['pageProps']['locationStoreState']['locationData']['locationResources'][0]['kgID']

        self.api_url = jres['props']['pageProps']['env']['APP_API_CLIENT'] + \
            '/v2/articles'
        preq = PreparedRequest()
        preq.prepare_url(self.api_url, self.params)
        # self.params['offset'] = self.params['offset'] + 15

        yield scrapy.Request(url=preq.url, headers=self.headers, dont_filter=True, callback=self.parse_article)

    def parse_article(self, response):
        jres = json.loads(response.body.decode("utf-8"))
        for url in jres['data']:
            self.scrolled_article.append(url['postID'])
            self.counter = self.counter + 1
            for href in url['links']:
                if (href['rel'] == 'web_self'):
                    yield scrapy.Request(url=(self.base_url + href['href']), callback=self.parse_details)

        if(self.counter < self.total):
            self.headers.update({'scrolled_article': (
                str(self.scrolled_article)[1:-1]).replace(" ", "")})
            self.params['offset'] = self.params['offset'] + 15
            preq = PreparedRequest()
            preq.prepare_url(self.api_url, self.params)
            yield scrapy.Request(url=preq.url, headers=self.headers, dont_filter=True, callback=self.parse_article)

    def parse_json(self, response):
        for url in response.body['data']:
            self.scrolled_article.append(url['postID'])
            yield scrapy.Request(url=url['links'], callback=self.parse_details)

    def parse_details(self, response):
        jres = re.findall(
            "\{\".*\:\{.*\:.*\}", response.body.decode("utf-8"))
        jres = json.dumps(jres[0])
        # print('')
        # print(jres)
        # self.i = self.i + 1
        # print('')
        item = CrawlerItem()
        item['topic'] = "theculturetrip"
        item['data'] = jres
        yield item
        # with open('test.json', 'w') as outfile:
        #     json.dump(jres, outfile, sort_keys=True, indent=4)
