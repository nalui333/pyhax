#!/usr/bin/python

#: Title       : scrape_usnews.py
#: Date Created: Tue Sep 9 15:56:34 EDT 2014
#: Author      : "Yemi Olugbuyi" <yemi.olugbuyi@ibx.com>

import os
import time
import requests
from lxml import html
from itertools import izip
from collections import OrderedDict
from lxml.cssselect import CSSSelector


def url_lst(baz_url):
    rezponz_pg = requests.get(baz_url)
    rez_tree = html.fromstring(rezponz_pg.text)
    pattrn2fnd = r'//ul[contains(@class, "specialty-list")]/li/a[contains(@href, "best-hospitals")]/@href'
    patz_lst = rez_tree.xpath(pattrn2fnd)
    catg_url_lst = [ ( baz_url + '/' + patz.rsplit('/', 1)[1] ) for patz in patz_lst ]
    return catg_url_lst


def dump_tbl_dat(tr_tag_elems, td_klazis_2hdgs):
    hosp_rnkg = [] 
    for tr_tag in tr_tag_elems:
        rnkg_ln = [] 
        if not tr_tag.xpath('.//th'):            
            for klass_val, headg in td_klazis_2hdgs.iteritems():
                if klass_val == "ranking-data-national-rank":
                    td_klass_pattrn = r""".//td[contains(@class, "{0}")]/span/span/text()""".format(klass_val)
                    cell_val = ''.join(tr_tag.xpath(td_klass_pattrn)) 
                    cell_dat = ': '.join([headg, cell_val ]) 
                    rnkg_ln.append( cell_dat )
                elif klass_val == "t ranking-data-hospital-info":
                    td_klass_pattrn = r""".//td[contains(@class, "{0}")]/p/strong/a[contains(@href, "http")]/text()""".format(klass_val)
                    cell_val = ''.join(tr_tag.xpath(td_klass_pattrn)) 
                    cell_dat = ': '.join([headg, cell_val ]) 
                    rnkg_ln.append( cell_dat )
                elif klass_val == "data-value grade":
                    td_klass_pattrn = r""".//td[contains(@class, "{0}")]//span/text()""".format(klass_val)
                    cell_val = ''.join(tr_tag.xpath(td_klass_pattrn)) 
                    cell_dat = ': '.join([headg, cell_val ]) 
                    rnkg_ln.append( cell_dat )
                else:
                    td_klass_pattrn = r""".//td[contains(@class, "{0}")]/div/p/text()""".format(klass_val)
                    if len(tr_tag.xpath(td_klass_pattrn)) != 0:
                        cell_val = tr_tag.xpath(td_klass_pattrn)[0].rsplit(':', 1)[1] if 'Score' in tr_tag.xpath(td_klass_pattrn)[0] else tr_tag.xpath(td_klass_pattrn)[0]
                    else:
                        cell_val = "NA"
                    cell_dat = ': '.join([headg, cell_val ]) 
                    rnkg_ln.append( cell_dat )
            row_dat = ' | '.join([klzdat for klzdat in rnkg_ln])
            hosp_rnkg.append(row_dat)
    hosp_rnkg_pg = ( "\n".join([datNrow for datNrow in hosp_rnkg]) + "\n")
    return hosp_rnkg_pg

                    
def dept_info(catg_urler, row_selector, pg_sel, hdg_sel):
    #outfile = r"C:\IBX\IBX_Downloads\ref_docz\usnews_scraped_ranking_" + '_'.join(catg_urler.rsplit('/', 2)[-2:]) + '_' + tm_stamp
    outfile = r"/tmp/usnews_scraped_ranking_" + '_'.join(catg_urler.rsplit('/', 2)[-2:]) + '_' + tm_stamp        
    
    url2uze = ''.join(catg_urler + r'/data')    
    main_pg_rezponz = requests.get(url=url2uze)
    mnpg_domtree = html.fromstring(main_pg_rezponz.text)
    no_of_pages = int( pg_sel(mnpg_domtree)[0].xpath('./a/text()')[-2] )    
    td_klaseez = [ td_elem.get('class') for td_elem in row_selector(mnpg_domtree)[3].xpath('.//td') ]
    headg_vals = [ ''.join(th_elem.xpath('.//text()')) for th_elem in hdg_sel(mnpg_domtree) ]
    klz_2hdg = OrderedDict(izip(td_klaseez, headg_vals))
    #print klz_2hdg
        
    with open(outfile, 'a') as outfl:
        for pgcount in range(1, no_of_pages + 1):
            page_url = ''.join( url2uze + r'?page=' + str(pgcount) )
            pg_rezponz = requests.get(page_url)
            pg_domtree = html.fromstring(pg_rezponz.text)
            tr_elems = row_selector(pg_domtree) #get list of row elements
            page_data = dump_tbl_dat(tr_elems, klz_2hdg)
            #print "Page" + str(pgcount)
            #print page_data
            outfl.write(page_data.encode('utf8'))
            mstrfl.write(page_data.encode('utf8'))
        
        
tm_stamp = time.strftime("%Y_%m_%d__%H_%M_%S")
#all_data_fl = r"C:\IBX\IBX_Downloads\ref_docz\usnews_scraped_ranking_" + '_' + tm_stamp
all_data_fl = r"/tmp/usnews_scraped_ranking_" + '_' + tm_stamp        
baze_urlz = [ r'http://health.usnews.com/best-hospitals/pediatric-rankings', r'http://health.usnews.com/best-hospitals/rankings' ]
rowsel = CSSSelector('html body div div table.data tr' ) #provides a list of rows in table we're interested in
hdgsel = CSSSelector('html body div div table.data tr th' ) #get heading list to use as dict keys for each cell data
psel = CSSSelector('html body div div p#pagination') #get heading list to use as dict keys for each cell data


urlz_by_catg = [ url_lst(new_baze_url) for new_baze_url in baze_urlz ]
with open(all_data_fl, 'a') as mstrfl:
    [ dept_info(catg_url, rowsel, psel, hdgsel) for catg_url in urlz_by_catg ]
