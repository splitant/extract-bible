from pyquery import PyQuery as pq
from lxml import etree
import urllib
import re

class ExtractUtils:

    URL_BASE_PATTERN = 'https://emcitv.com/bible/<pattern>.html'

    def __init__(self):
        self._bibleVersions = dict()
        self._bibleBooks = dict()

    @property
    def bibleVersions(self):
        return self._bibleVersions

    @bibleVersions.setter
    def bibleVersions(self, bibleVersions):
        self._bibleVersions = bibleVersions

    @property
    def bibleBooks(self):
        return self._bibleBooks

    @bibleBooks.setter
    def bibleBooks(self, bibleBooks):
        self._bibleBooks = bibleBooks

    def _getUrl(self, str_subject):
        return self.URL_BASE_PATTERN.replace('<pattern>', str_subject)

    def extractBibleVersions(self):
        d = pq(url=self._getUrl('genese'))
        bibleVersionsLinksHTML = d('#nav-versions a')

        for linkHTML in bibleVersionsLinksHTML.items():
            version_name = linkHTML.text()

            last_part_link = linkHTML.attr['href'].split('-')
            """ TODO : split link + last part split '.html' """
            version_key = 
            self.bibleVersions[linkHTML.attr['href']] = linkHTML.text()

        bibleVersionsLinksHTML.each(lambda e: self.bibleVersions[e.attr['href']] = e.text())
        result = re.search('asdf=5;(.*)123jasd', s)
print(result.group(1))