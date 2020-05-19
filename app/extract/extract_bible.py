#!/usr/bin/python

from pyquery import PyQuery as pq
from lxml import etree
import urllib
import json
import os
import time


class ExtractBible:

    URL_BASE_PATTERN = 'https://emcitv.com/bible/<pattern>.html'
    INDEX_CODE_BOOK = 'code_book'
    INDEX_LABEL_BOOK = 'label_book'
    INDEX_ID_BOOK_WEBSITE = 'id_book_emci'

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

        for index, linkHTML in enumerate(bibleBooksLinksHTML.items()):
            book_name = linkHTML.text()

            link_parts = linkHTML.attr['href'].split('/')
            last_part_link = link_parts[-1]
            book_key = last_part_link[:last_part_link.index('.html')]

            index_str = str(index)
            self._bibleBooks[index_str] = dict()
            self._bibleBooks[index_str][self.INDEX_CODE_BOOK] = book_key
            self._bibleBooks[index_str][self.INDEX_LABEL_BOOK] = book_name
            self._bibleBooks[index_str][self.INDEX_ID_BOOK_WEBSITE] = book_key

    def extractBibleVerses(self, version, book, chapter):
        pattern_value = book + '-' + str(chapter) + '-' + version

        verses = dict()
        try:
            d = pq(url=self._getUrl(pattern_value))
            bible_verses = d('.list-verses .verse')

            for bible_verse in bible_verses.items():
                number = bible_verse.find('.num').text()
                verse = bible_verse.find('.content').text()

                verses[number] = verse
        except:
            return False
        finally:
            return verses

class ExtractBibleTopBible(ExtractBible):

    URL_BASE_PATTERN = 'https://topbible.topchretien.com/genese/<pattern>/'
    INDEX_ID_BOOK_WEBSITE = 'id_book_topbible'

    def __init__(self, bible_books):
        super(ExtractBibleTopBible, self).__init__()

        self._bibleVersions['COL'] = 'La Colombe'
        self._bibleVersions['PDV'] = 'Parole de Vie'
        self._bibleVersions['PVI'] = 'Parole Vivante'
        self._bibleVersions['BFC'] = 'La Bible en français courant'

        self._bibleBooks = bible_books
        self.extractAndInitBibleBooks()

        self._pqBibleVersions = dict()
    
    def extractAndInitBibleBooks(self):
        for index, book in enumerate(self._bibleBooks):
            self._bibleBooks[str(index)][self.INDEX_ID_BOOK_WEBSITE] = str(index + 1) 

    def extractBibleVerses(self, version, book, chapter):
        if (book == 'habakuk'):
            book = 'habacuc'

        verses = dict()
        try:
            if not version in self._pqBibleVersions:
                self._pqBibleVersions[version] = pq(url=self._getUrl(version))

            verses_element_html = self._pqBibleVersions[version]('div[data-bookorder="' + book + '"][data-chapter="' + str(chapter) + '"]')

            if (len(verses_element_html)):
                verses_url = pq(verses_element_html).attr('data-loadurl')
                d = pq(url=verses_url)
                lines = d('div.bible-verse')
                for line in lines.items():
                    number = line.find('.number-verse').text()
                    verse = line.find('.bible-verse-text').text()
                    verses[number] = verse
        except:
            return False
        finally:
            return verses

class ExtractBibleBibleCom(ExtractBible):

    URL_BASE_PATTERN = 'https://www.bible.com/bible/<pattern>'
    INDEX_ID_BOOK_WEBSITE = 'id_book_biblecom'
    
    URL_JSON_VERSION = 'https://www.bible.com/json/bible/versions/fra'
    URL_JSON_BOOK = 'https://www.bible.com/json/bible/books/62'

    def __init__(self, bible_books):
        super(ExtractBibleBibleCom, self).__init__()

        self._bibleVersions['NBS'] = 'Nouvelle Bible Segond'
        self._bibleVersions['NFC'] = 'Nouvelle Français courant'
        self._bibleVersions['BCC1923'] = 'Bible catholique Crampon 1923'
        self.extractAndInitBibleVersions()

        self._bibleBooks = bible_books
        self.extractAndInitBibleBooks()

        self._pqBibleVersions = dict()
    
    def extractAndInitBibleVersions(self):
        d = pq(url=self.URL_JSON_VERSION)
        list_versions = json.loads(d.text())
        self.__bibleVersionsIDBibleCom = dict()
        self.__chapterRedirected = dict()

        for version in list_versions['items']:
            if version['local_abbreviation'] in self._bibleVersions:
                self.__bibleVersionsIDBibleCom[version['local_abbreviation']] = version['id']
                self.__chapterRedirected['GEN.1.' + version['local_abbreviation']] = False

    def extractAndInitBibleBooks(self):
        d = pq(url=self.URL_JSON_BOOK)
        list_books = json.loads(d.text())

        for index, book in enumerate(list_books['items']):
            self._bibleBooks[str(index)][self.INDEX_ID_BOOK_WEBSITE] = book['usfm']

    def extractBibleVerses(self, version, book, chapter):
        pattern_value = str(self.__bibleVersionsIDBibleCom[version]) + '/' + book + '.' + str(chapter) + '.' + version

        verses = dict()
        try:
            d = pq(url=self._getUrl(pattern_value))
            chapter_element = d('.yv-bible-text .version .book .chapter')
            chapter_code = chapter_element.attr('data-usfm') + '.' + version

            if (chapter_code in self.__chapterRedirected):
                if (self.__chapterRedirected[chapter_code]):
                    return
                else:
                    self.__chapterRedirected[chapter_code] = True

            num_verse = 1
            bible_verse = chapter_element.find('.v' + str(num_verse))
            while (bible_verse):
                number = bible_verse.children('.label').text()
                verse = bible_verse.find('.content').text()
                verse = verse.strip()
                verse = verse.replace('S eigneur', 'Seigneur')
                verses[number] = verse

                num_verse = num_verse + 1
                bible_verse = chapter_element.find('.v' + str(num_verse))
        except:
            return False
        finally:
            return verses

class ExtractProcess:
    SOURCE_DIRECTORY = 'bible'

    def __init__(self):
        self._extractBible = ExtractBible()
        self._extractBible.extractAndInitBibleVersions()
        self._extractBible.extractAndInitBibleBooks()

        self._extractBibleTopBible = ExtractBibleTopBible(
            self._extractBible.bibleBooks)
        
        self._extractBibleBibleCom = ExtractBibleBibleCom(
            self._extractBibleTopBible.bibleBooks)

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
            **(self._extractBible.bibleVersions), 
            **(self._extractBibleTopBible.bibleVersions),
            **(self._extractBibleBibleCom.bibleVersions),
        }

        with open(file_path, 'w', encoding='utf8') as json_file:
            json.dump(full_bible_versions, json_file, ensure_ascii=False)
        print('File %s is created' % file_path)

    def createBibleBooksJSON(self):
        file_path = self.SOURCE_DIRECTORY + '/bible_books.json'
        with open(file_path, 'w', encoding='utf8') as json_file:
            json.dump(self._extractBible.bibleBooks, json_file, ensure_ascii=False)
        print('File %s is created' % file_path)

    def processExtract(self):
        for extract in [self._extractBible, self._extractBibleTopBible, self._extractBibleBibleCom]:
            for key_version, value_version in extract.bibleVersions.items():
                path_directory = self.SOURCE_DIRECTORY + '/' + key_version
                try:
                    os.makedirs(path_directory, exist_ok=True)
                except:
                    print('Creation of the directory %s failed' % path_directory)
                else:
                    for key_book, value_book in extract.bibleBooks.items():
                        book_json_array = dict()

                        book_json_array['version_book'] = value_version
                        book_json_array['code_version_book'] = key_version
                        book_json_array['name'] = value_book[extract.INDEX_LABEL_BOOK]
                        id_book_website = value_book[extract.INDEX_ID_BOOK_WEBSITE]
                        code_book = value_book[extract.INDEX_CODE_BOOK]

                        chapter_num = 1
                        chapter = extract.extractBibleVerses(key_version, id_book_website, chapter_num)

                        print("\nProcessing [%s|%s]" %(value_version, book_json_array['name']))
                        time_begin = time.perf_counter()
                        if (chapter):
                            book_json_array['chapters'] = dict()

                        while (chapter):
                            book_json_array['chapters'][chapter_num] = chapter
                            chapter_num = chapter_num + 1 
                            chapter = extract.extractBibleVerses(key_version, id_book_website, chapter_num)
                        
                        with open(path_directory + '/' + code_book + '.json', 'w', encoding='utf8') as json_file:
                            json.dump(book_json_array, json_file, ensure_ascii=False)

                        time_end = time.perf_counter()
                        print("[%s|%s] processed" %(value_version, book_json_array['name']))
                        print(f"Time duration : {time_end - time_begin:0.2f} seconds")
                        
