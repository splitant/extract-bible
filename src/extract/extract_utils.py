from pyquery import PyQuery as pq
from lxml import etree
import urllib

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

    def extractAndInitBibleVersions(self):
        d = pq(url=self._getUrl('genese'))
        bibleVersionsLinksHTML = d('#nav-versions a')

        for linkHTML in bibleVersionsLinksHTML.items():
            version_name = linkHTML.text()

            link_parts = linkHTML.attr['href'].split('-')
            last_part_link = link_parts[-1]
            version_key = last_part_link[:last_part_link.index('.html')]

            self._bibleVersions[version_key] = version_name

    def extractAndInitBibleBooks(self):
        d = pq(url=self._getUrl('genese'))
        bibleBooksLinksHTML = d(
            '#modal-book-selector .modal-body .list-group a[data-book-id]')
        
        for linkHTML in bibleBooksLinksHTML.items():
            version_name = linkHTML.text()

            link_parts = linkHTML.attr['href'].split('/')
            last_part_link = link_parts[-1]
            version_key = last_part_link[:last_part_link.index('.html')]

            self._bibleBooks[version_key] = version_name

    def extractBibleVerses(self, version, book, chapter):
        pattern_value = book + '-' + chapter + '-' + version

        try:
            d = pq(url=self._getUrl(pattern_value))

            verses = dict()
            bibleVerses = d('.list-verses .verse')

            for bibleVerse in bibleVerses:
                number = bibleVerse.find('.num').text()
                verse = bibleVerse.find('.content').text()

                verses[number] = verse

            return verses
        except:
            return None
