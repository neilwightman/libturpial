# -*- coding: utf-8 -*-

"""Module to handle custom exceptions for Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Jan 07, 2012


class URLShortenError(Exception):
    """An URL shorten error ocurred"""
    def __init__(self, message):
        self.message = message


class NoURLException(Exception):
    """No URL to short"""
    def __init__(self):
        self.message = 'No URL to short'


class AlreadyShortURLException(Exception):
    """URL already short"""
    def __init__(self):
        self.message = 'URL already short'


class UploadImageError(Exception):
    """An upload image error ocurred"""
    def __init__(self, message):
        self.message = message
