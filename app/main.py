#!/usr/bin/python

from extract import extract_bible

if __name__ == "__main__":
    extract = extract_bible.ExtractProcess()
    extract.createBibleDirectory()
    extract.createBibleVersionsJSON()
    extract.createBibleBooksJSON()
    extract.processExtract()
