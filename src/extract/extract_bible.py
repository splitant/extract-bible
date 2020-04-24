#!/usr/bin/python

from pyquery import PyQuery as pq
from lxml import etree
import urllib
import json
import os
import time


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
        pattern_value = book + '-' + str(chapter) + '-' + version

        verses = dict()
        try:
            d = pq(url=self._getUrl(pattern_value))
            bibleVerses = d('.list-verses .verse')

            for bibleVerse in bibleVerses.items():
                number = bibleVerse.find('.num').text()
                verse = bibleVerse.find('.content').text()

                verses[number] = verse
        except:
            return False
        finally:
            return verses

class ExtractUtilsAdditional(ExtractUtils):

    URL_BASE_PATTERN = 'https://lire.la-bible.net/lecture/<pattern>'

    def __init__(self, bible_books):
        super(ExtractUtilsAdditional, self).__init__()

        self._bibleVersions['Colombe'] = 'La Colombe'
        self._bibleVersions['PDV'] = 'La Bible Parole de Vie'
        self._bibleVersions['RVR'] = 'Reina-Valera'

        self._bibleBooks = bible_books
    
    def extractBibleVerses(self, version, book, chapter):
        pattern_value = book.replace('-', '+') + '/' + str(chapter) + '/' + version

        verses = dict()
        try:
            d = pq(url=self._getUrl(pattern_value))
            bibleVerses = d('.list-verses .verse')

            for bibleVerse in bibleVerses.items():
                number = bibleVerse.find('.num').text()
                verse = bibleVerse.find('.content').text()

                verses[number] = verse
        except:
            return False
        finally:
            return verses


class ExtractProcess:
    SOURCE_DIRECTORY = 'bible'

    def __init__(self):
        self._extractUtils = ExtractUtils()
        self._extractUtils.extractAndInitBibleVersions()
        self._extractUtils.extractAndInitBibleBooks()

        self._extractUtilsAddtionnal = ExtractUtilsAdditional(
            self._extractUtils.bibleBooks)

    def createBibleDirectory(self):
        try:
            os.makedirs(self.SOURCE_DIRECTORY, exist_ok=True)
        except:
            print("Creation of the directory %s failed" % self.SOURCE_DIRECTORY)
        else:
            print("Directory %s is created" % self.SOURCE_DIRECTORY)

    def createBibleVersionsJSON(self):
        file_path = self.SOURCE_DIRECTORY + '/bible_versions.json'

        full_bible_versions = {
            **(self._extractUtils.bibleVersions), **(self._extractUtilsAddtionnal.bibleVersions)}

        with open(file_path, 'w', encoding='utf8') as json_file:
            json.dump(full_bible_versions, json_file, ensure_ascii=False)
        print('File %s is created' % file_path)

    def createBibleBooksJSON(self):
        file_path = self.SOURCE_DIRECTORY + '/bible_books.json'
        with open(file_path, 'w', encoding='utf8') as json_file:
            json.dump(self._extractUtils.bibleBooks, json_file, ensure_ascii=False)
        print('File %s is created' % file_path)

    def processExtract(self):
        for extract in [self._extractUtils, self._extractUtilsAddtionnal]:
            for key_version, value_version in extract.bibleVersions.items():
                path_directory = self.SOURCE_DIRECTORY + '/' + key_version
                try:
                    os.makedirs(path_directory, exist_ok=True)
                except:
                    print('Creation of the directory %s failed' % path_directory)
                else:
                    for key_book, value_book in extract.bibleBooks.items():
                        book_json_array = dict()

                        book_json_array['name'] = value_book
                        book_json_array['version_book'] = value_version
                        book_json_array['code_version_book'] = key_version

                        chapter_num = 1
                        chapter = extract.extractBibleVerses(key_version, key_book, chapter_num)

                        print("\nProcessing [%s|%s]" %(value_version, value_book))
                        time_begin = time.perf_counter()
                        if (chapter):
                            book_json_array['chapters'] = dict()

                        while (chapter):
                            book_json_array['chapters'][chapter_num] = chapter
                            chapter_num = chapter_num + 1 
                            chapter = extract.extractBibleVerses(key_version, key_book, chapter_num)
                        
                        with open(path_directory + '/' + key_book + '.json', 'w', encoding='utf8') as json_file:
                            json.dump(book_json_array, json_file, ensure_ascii=False)

                        time_end = time.perf_counter()
                        print("[%s|%s] processed" %(value_version, value_book))
                        print(f"Time duration : {time_end - time_begin:0.2f} seconds")
                        
