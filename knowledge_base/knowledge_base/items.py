# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class QuestionAnswer(scrapy.Item):
    """
    Model for super user question / answer
    """
    question_title = scrapy.Field()
    question_body = scrapy.Field()
    question_tags = scrapy.Field()
    question_upvotes = scrapy.Field()
    question_view_count = scrapy.Field()
    question_author = scrapy.Field()
    question_date = scrapy.Field()

    answer_body = scrapy.Field()
    answer_accepted = scrapy.Field()
    answer_upvotes = scrapy.Field()




