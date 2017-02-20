# -*- coding: utf-8 -*-
import scrapy


class SuperuserSpider(scrapy.Spider):
    name = "superuser"
    allowed_domains = ["superuser.com"]
    start_urls = ['http://superuser.com/']

    def parse(self, response):
        pass
