import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import SimmonsItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class SimmonsSpider(scrapy.Spider):
	name = 'simmons'
	start_urls = ['https://www.simmonsbank.com/about-us/news-releases']

	def parse(self, response):
		articles = response.xpath('//h3/a')
		for index in range(len(articles)):
			date = response.xpath(f'(//div[@class="get-faded"])[{index+1}]/text()').get().split()[2]
			post_links = response.xpath(f'(//h3/a)[{index+1}]/@href').get()
			yield response.follow(post_links, self.parse_post, cb_kwargs=dict(date=date))

	def parse_post(self, response, date):
		title = response.xpath('//h1/text()').get().strip()
		content = response.xpath('//div[@class="page-bodytext"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=SimmonsItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
