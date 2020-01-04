import scrapy
from crawler.items import AttractionLocationItem, AttractionActivityItem, AttractionReviewItem
import json
import re
# from scrapy_splash import SplashRequest
# from requests.models import PreparedRequest

script = """
-- Arguments:
-- * url - URL to render;

-- main script
function main(splash)
    assert(splash:go(splash.args.url))
  	assert(splash:wait(0.5))
  	assert(splash:runjs('document.getElementsByClassName("ui_button nav next primary")[0].click()'))
    splash:wait(0.5)
    return {
      html = splash:html(),
    }
end
"""


class AttractionDetailSpider(scrapy.Spider):
    # scrapy crawl tripadvisor_attr_detail
    # dependency files - datasets/tripadvisor_dataset/tripadvisor-graphql-query.json, datasets/tripadvisor_dataset/attractions/tripadvisor_attr_href_cat.json
    name = "tripadvisor_attr_detail"

    # start_urls = ['']
    base_url = "https://www.tripadvisor.com.my"
    api_location_url = "/data/1.0/location/"  # required location_id
    api_prod_activity_url = "/data/1.0/attractions/products/activity/"  # required activityId
    api_query_url = "/data/graphql/batched/"  # required request payload and variables

    allowed_domains = ["tripadvisor.com"]

    custom_settings = {
        'JOBDIR': 'crawls/tripadvisor_attr_detail',
        'LOG_FILE': 'tripadvisor_attr_detail.log',
        'LOG_LEVEL': 'INFO',
        'DOWNLOAD_DELAY': 3,
        'ITEM_PIPELINES': {
            'crawler.pipelines.KafkaPipeline': 300,
        },
    }

    headers = {
        "Content-Type": "application/json",
        "cookie": "TAUnique=%1%enc%3AB0bnoop86pbZSQ%2BkBPmnRh%2FSUiJxjhQHfYWoRZ0Eg8xpMN00eOgflw%3D%3D; ServerPool=X; TASSK=enc%3AAOq4BGtvG8uu32y8nIchqJDSRLo67jlGnymi9b9mKFteDq%2FEHYdd4bkqhONwQo0473lfMww%2FUS6fkYN%2BVVhT3CrWIfPQ7XuvGFcPk%2F4st5cxnXT4y33BJDqnjUOO3vkjWA%3D%3D; TAPD=tripadvisor.com.my; fbm_162729813767876=base_domain=.tripadvisor.com.my; TADCID=6ez55FCLQ6Tfc0u4ABQC5UI2n8iqRdCoS-RMXjJFU1o-TM4XdW_AVlgjX8w7tSFskd56Z25cUCc10yZ0NtGILL0ddGgOy3YJ5Fw; TART=%1%enc%3A2UkPpAT5p0aBsu79S6iUAVmfbtOEN1nzuk%2BMumHOTQrNMST5tAR5s%2BI5a%2F5NJW3bOXGJvKEzqtI%3D; PMC=V2*MS.22*MD.20191125*LD.20191223; CM=%1%PremiumMobSess%2C%2C-1%7Ct4b-pc%2C%2C-1%7CRestAds%2FRPers%2C%2C-1%7CRCPers%2C%2C-1%7CWShadeSeen%2C%2C-1%7Cpv%2C5%2C-1%7CTheForkMCCPers%2C%2C-1%7CHomeASess%2C8%2C-1%7CPremiumSURPers%2C%2C-1%7CPremiumMCSess%2C%2C-1%7CUVOwnersSess%2C%2C-1%7CRestPremRSess%2C%2C-1%7CCCSess%2C8%2C-1%7CCYLSess%2C%2C-1%7CPremRetPers%2C%2C-1%7CViatorMCPers%2C%2C-1%7Csesssticker%2C%2C-1%7C%24%2C%2C-1%7CPremiumORSess%2C%2C-1%7Ct4b-sc%2C%2C-1%7CRestAdsPers%2C%2C-1%7CMC_IB_UPSELL_IB_LOGOS2%2C%2C-1%7Cb2bmcpers%2C%2C-1%7CPremMCBtmSess%2C%2C-1%7CPremiumSURSess%2C%2C-1%7CMC_IB_UPSELL_IB_LOGOS%2C%2C-1%7CLaFourchette+Banners%2C%2C-1%7Csess_rev%2C%2C-1%7Csessamex%2C%2C-1%7CPremiumRRSess%2C%2C-1%7CTADORSess%2C%2C-1%7CAdsRetPers%2C%2C-1%7CTARSWBPers%2C%2C-1%7CSPMCSess%2C%2C-1%7CTheForkORSess%2C%2C-1%7CTheForkRRSess%2C%2C-1%7Cpers_rev%2C%2C-1%7Cmdpers%2C%2C-1%7Cmds%2C1577082482262%2C1577168882%7CSPMCWBPers%2C%2C-1%7CRBAPers%2C%2C-1%7CRestAds%2FRSess%2C%2C-1%7CHomeAPers%2C%2C-1%7CPremiumMobPers%2C%2C-1%7CRCSess%2C%2C-1%7CLaFourchette+MC+Banners%2C%2C-1%7CRestAdsCCSess%2C%2C-1%7CRestPremRPers%2C%2C-1%7CUVOwnersPers%2C%2C-1%7CRevHubRMPers%2C%2C-1%7Csh%2C%2C-1%7Cpssamex%2C%2C-1%7CTheForkMCCSess%2C%2C-1%7CCYLPers%2C%2C-1%7CCCPers%2C%2C-1%7Cb2bmcsess%2C%2C-1%7CSPMCPers%2C%2C-1%7CPremRetSess%2C%2C-1%7CViatorMCSess%2C%2C-1%7CRevHubRMSess%2C%2C-1%7CPremiumMCPers%2C%2C-1%7CAdsRetSess%2C%2C-1%7CPremiumRRPers%2C%2C-1%7CRestAdsCCPers%2C%2C-1%7CTADORPers%2C%2C-1%7CTheForkORPers%2C%2C-1%7CPremMCBtmPers%2C%2C-1%7CTheForkRRPers%2C%2C-1%7CTARSWBSess%2C%2C-1%7CPremiumORPers%2C%2C-1%7CRestAdsSess%2C%2C-1%7CRBASess%2C%2C-1%7CSPORPers%2C%2C-1%7Cperssticker%2C%2C-1%7CSPMCWBSess%2C%2C-1%7Cmdsess%2C-1%2C-1%7C; TATravelInfo=V2*AC.KUL*DA.DAC*AY.2020*AM.1*AD.5*DY.2020*DM.1*DD.6*A.2*MG.-1*HP.2*FL.3*DSM.1577086574199*RS.1; mp_tripadvisor_mixpanel=%7B%22distinct_id%22%3A%20%2216ea34b97904cd-0456083c9f896d-14291003-1fa400-16ea34b979180d%22%2C%22bc_persist_updated%22%3A%201574697670546%7D; PAC=APUGkA0U8qSFqIVAXlf0U99iScnPVhyfb16TAZldcDBfJvXkF4pA7aA8Fs1bqQzA_RmNg_aOf3d0gts4BtjLcEeLFunFCSTgggcRi-oiceCs-tohBcAhN0qQfKnHt1hvu0XQDJ-QzlatZEFJd1kWDe4IT4eI3vqergOmlba_so5872InXz7-dwaLbYVP4l4mpj8nlSOYoKNQ6ffwAzOsqK12JMrxmS5HYUUmJWJJyCqwpJzZ7MWdJVed6pMpOov6s0UwhMHi3n9YRKhuLOrYGoVOuPgdSf9jllZPAEoMsUly; VRMCID=%1%V1*id.12082*llp.%2FShowTopic-g1-i12105-k8592085-Trip_Advisor_API_v2_0_changes-TripAdvisor_Support-m12082*e.1577695656916; fbsr_162729813767876=KEzwTYcFd6vIkstJ-6AKYTNGkinzTdtoipW_xMIwNUY.eyJ1c2VyX2lkIjoiMTAwMDAyMjQxNjUzNTA2IiwiY29kZSI6IkFRRDhmV2Jzb3F6YWdhNDA4b2s2VHNNWlppeUttaXhTNXh4MEJLY1dhVDRZaTNBZWNTME91dnNCTXhQSkRicTBjRzdIU1lvLWdRXzcwUldPam1vNmp3WXdYN3ZLSVBrNmJSZlpkY0g5eXhtNWQ4YkpYSmhJckRNWktwN2NxbGNLMjV4R29CSnNWb3NrT01iNlpMRUc1eUI4c2R2TnZwVUhReW41YTZnWW1qMS1RV1BhWW44WWVlODZjYl9LMkNxU3lkLVNMdnd1Q3RZU2g1VVA2eEJPVHp5bjhSVGFxVWF4MVZNMW5OOGEwZ0hWa3hOTzVBdnN6MHcxZTRreWVPR19ScHdwRGF2R1AzRXd1aGRsMmR1aDRSbU9EVUtaNFplajEydnd1eHVwbUVDc0ZFTGlMNmdab3FvZkNyMHRNeU9GZEMxclUtREYtdXQyNXZhWUZ1UXhlc3dJIiwib2F1dGhfdG9rZW4iOiJFQUFDVUFIeVpCZHNRQkFBalZxekNBYW5qMUlNWkJiN3VtYW9aQ3NMazk2bHhOY3BnMDJKckNCRlpCRm1NdmwwWkJWWkNDWkF6UnJwVXN2V2xXYzVmcEtKMEJENDRvUk9UM252ZVpBam9xeVdqY1pCQkNtbG9SZnBVQkdLVDVUdHlTVExReUd4ZXB3WkJzT3VKZ3ZtNUxVVnRiQlpDMEtJdDEya1JrYnFiYjJBblBSTFJDWkNtOElVTzJFbDI2dW1BSTVtRENGbUJ1SW1GNmU0WkFlbnRtQURIUVFhRGMiLCJhbGdvcml0aG0iOiJITUFDLVNIQTI1NiIsImlzc3VlZF9hdCI6MTU3NzA5MDg3OX0; __vt=BddzmZK7pR1TpkY9ABQCKh0bQ-d8T96qptG7UVr_ZQoqoYPs0tF2W_7_o5yifdAIUGfD_UD5JS58ETamCn8q_PXfEahOdqvuIrDvbirX51hpHYEJNnvlzV0UT5cNqY1JjutzF0vli0qpcHLpMeZW2H_0; TAReturnTo=%1%%2FAttractionProductReview-g298570-d12962337-Malaysia_Countryside_and_Batu_Caves_Tour_from_Kuala_Lumpur-Kuala_Lumpur_Wilayah_Pe.html; roybatty=TNI1625!AOMA9nYJknnS5W0sNIJsQOICTe0Q9koR8cHBA1nIRMsAibbGmCB5GSGwAHtDuVkfg6aoveDXHCUKVHNblQNo5NrdOepZT7vYcsBfgBuds29HKQAqLC5NK5vqVqQWORNxFkBnzxvpZh8wmCoC94eSrbDEJyYYMJJ1inSRZdfS4I3A%2C1; SRT=%1%enc%3A2UkPpAT5p0aBsu79S6iUAVmfbtOEN1nzuk%2BMumHOTQrNMST5tAR5s%2BI5a%2F5NJW3bOXGJvKEzqtI%3D; TASession=V2ID.87B4EFE3329350FEAFD94C6750960108*SQ.687*LS.PageMoniker*GR.50*TCPAR.10*TBR.85*EXEX.65*ABTR.63*PHTB.26*FS.99*CPU.13*HS.recommended*ES.popularity*DS.5*SAS.popularity*FPS.oldFirst*LF.en*FA.1*DF.0*IR.1*OD.null*FLO.1770798*TRA.false*LD.12962337; TAUD=LA-1574697655926-1*RDD-2-2019_11_25*HC-2387881594*HDD-2388917705-2020_01_05.2020_01_06*LD-2393524421-2020.1.5.2020.1.6*LG-2393524423-2.1.F.",
        "x-requested-by": "TNI1625!AObtWs7+WBUcGGl3nYadc7+VtOuZWqN0FP2DocM82UA8efGHjAnpvxF3SxGefK1Vxqwijl6NoBm9GdDf3PBCcO61s40COv6y/wLrJvI6SiXh+VmFIAqKGlpcvLyfxApCQddrXOcRyEepTAJDkaVFKy6y5ZPR9RSBrZs4BRiKq0UM",
    }

    unwantedLocationKey = ["awards", "doubleclick_zone", "preferred_map_engine", "is_jfy_enabled",
                           "nearest_metro_station", "has_restaurant_coverpage", "has_attraction_coverpage", "has_curated_shopping_list", ""]
    unwantedActivityKey = ["highlights", "obfuscatedViatorCommerceLink"]

    with open('datasets/tripadvisor_dataset/tripadvisor-graphql-query.json', 'r') as f:
        query = json.load(f)
    reviewListQuery = query[1]

    def start_requests(self):
        with open('datasets/tripadvisor_dataset/attractions/tripadvisor_attr_href_cat.json', 'r') as f:
            attractionHrefList = json.load(f)

        locationIdList = re.findall(r'g(\d+)', json.dumps(attractionHrefList))
        locationIdList = list(dict.fromkeys(locationIdList))  # remove duplicate locationId
        # locationIdList = [self.base_url + self.api_location_url + i for i in locationIdList]

        activityIdList = re.findall(r'd(\d+)', json.dumps(attractionHrefList))
        activityIdList = list(dict.fromkeys(activityIdList))
        # activityIdList = [self.base_url + self.api_prod_activity_url + i for i in activityIdList]

        for locationId in locationIdList:
            print("[Loading] Requesting Location of locationId: " + str(locationId))
            self.logger.info("[Loading] Requesting Location of locationId: " + str(locationId))

            url = self.base_url + self.api_location_url + str(locationId)
            yield scrapy.Request(url=url, meta={'locationId': locationId}, dont_filter=True, callback=self.parseLocation)

        for activityId in activityIdList:
            print("[Loading] Requesting Activity of activityId: " + str(activityId))
            self.logger.info("[Loading] Requesting Activity of activityId: " + str(activityId))

            url = self.base_url + self.api_prod_activity_url + str(activityId)
            yield scrapy.Request(url=url, meta={'activityId': activityId}, dont_filter=True, callback=self.parseActivity)

            print("[Loading] Requesting Review of activityId: " + str(activityId))
            self.logger.info("[Loading] Requesting Review of activityId: " + str(activityId))

            self.reviewListQuery[0]['variables']['locationId'] = activityId  # activityId
            self.reviewListQuery[0]["variables"]["limit"] = -1
            yield scrapy.Request(url=self.base_url + self.api_query_url, meta={'activityId': activityId}, method="POST", dont_filter=True, body=json.dumps(self.reviewListQuery), headers=self.headers, callback=self.parseReview)

    def parseLocation(self, response):
        data = json.loads(response.body.decode("utf-8"))
        for key in self.unwantedLocationKey:
            data.pop(key, None)

        item = AttractionLocationItem()
        item['topic'] = "tripad_attr_location"
        item['data'] = json.dumps(data).encode("utf-8")
        yield item

        print("[Success] Get Location of locationId: " + str(response.meta['locationId']))
        self.logger.info("[Success] Get Location of locationId: " + str(response.meta['locationId']))

    def parseActivity(self, response):
        data = json.loads(response.body.decode("utf-8"))
        for key in self.unwantedActivityKey:
            data.pop(key, None)

        item = AttractionActivityItem()
        item['topic'] = "tripad_attr_activity"
        item['data'] = json.dumps(data).encode("utf-8")
        yield item

        print("[Success] Get Activity of activityId: " + str(response.meta['activityId']))
        self.logger.info("[Success] Get Activity of activityId: " + str(response.meta['activityId']))

    def parseReview(self, response):
        attemp = 0
        data = json.loads(response.body.decode("utf-8"))
        activityId = data[0].get("data").get("locations")[0].get("locationId")

        if data[0]["data"]["locations"][0]["reviewListPage"] is not None:
            data[0].pop("errors", None)

            print("[Success] Get Review of activityId: " + str(activityId))
            self.logger.info("[Success] Get Review of activityId: " + str(activityId))

            item = AttractionReviewItem()
            item['topic'] = "tripad_attr_review"
            item['data'] = json.dumps(data).encode("utf-8")
            yield item
        else:
            print("[Error] Retry retrieving review list of activityId: " + str(response.meta['activityId']))
            self.logger.info("[Error] Retry retrieving review list of activityId: " + str(response.meta['activityId']))

            self.reviewListQuery[0]["variables"]["locationId"] = response.meta['activityId']
            self.reviewListQuery[0]["variables"]["limit"] = -1

            attemp += 1
            if attemp < 3:
                yield scrapy.Request(url=self.base_url + self.api_query_url, method="POST", meta={'activityId': response.meta['activityId']}, dont_filter=True, body=json.dumps(self.reviewListQuery), headers=self.headers, callback=self.parseReview)
            else:
                print("[Error] Retrieving review list of activityId: " + str(response.meta['activityId']))
                self.logger.info("[Error] Retrieving review list of activityId: " + str(response.meta['activityId']))

        # yield SplashRequest(url=response.url, dont_filter=True, callback=self.parse, endpoint='execute', args={'lua_source': script, 'wait': 0.5, 'body': json.dumps(query)})


# location_id = re.search(r'g(\d+)', url["attraction_url"]).group(1)
# activityId = re.search(r'd(\d+)', url["attraction_url"]).group(1)

# i = response.xpath(
#     '//div[contains(@data-test-target,"reviews-tab")]/div/div')
# print(i.xpath('div/div/div/span/a/text()').extract())

# print("text "+response.xpath(
#     './/div[contains(@class,"ui_pagination")]/a/@href').extract_first())

# query[0]['variables']['offset'] += 5


# Tripadvisor Attractions API

# https://www.tripadvisor.com.my/data/1.0/location/293951
# https://www.tripadvisor.com.my/data/1.0/attractions/products/activity/12962337
