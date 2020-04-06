from pyquery import PyQuery as pq
from lxml import etree
import urllib

if __name__ == "__main__":
    d = pq(url='https://emcitv.com/bible/genese-segond_21.html')
    p = d("#book-selector")
    print(p.text())
