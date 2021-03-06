# -*- coding: utf-8 -*-

""" Module to represent status entities (URLs, HTs, mentions) """
#
# Author: Wil Alvarez (aka Satanas)
# Dic 07, 2011


class Entity:
    def __init__(self, account_id, url, text, search):
        self.account_id = account_id
        self.url = url
        self.display_text = text
        self.search_for = search
