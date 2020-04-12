#!/usr/bin/python

from extract.extract_bible import *

if __name__ == "__main__":
    extract = ExtractProcess()
    extract.createBibleDirectory()
    extract.createBibleVersionsJSON()
    extract.createBibleBooksJSON()
    extract.processExtract()
