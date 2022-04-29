import os
import sqlite3
import urllib.request

import patoolib
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch

index = 'study_v1'
domain = 'https://www.shijuan1.com'
# es = Elasticsearch(
#     hosts=['http://43.154.70.80:9200'],  # 地址
#     request_timeout=3600  # 超时时间
# )
# 可以指定创建数据库的路径，比如可以写成sqlite3.connect(r"E:\DEMO.db")
con = sqlite3.connect("my_study.db")
cur = con.cursor()


def download(url: str, du: str):
    out = du[3:].replace('.html', '')
    # if not os.path.exists(out):
    #     os.makedirs(out)
    # elif os.listdir(out):
    #     return out
    # file_name, headers = urllib.request.urlretrieve(domain + url)
    # patoolib.extract_archive(file_name, outdir=out)
    # if os.path.exists(out + '/第一试卷网.url'):
    #     os.remove(out + '/第一试卷网.url')
    return out


def get_rar(url: str):
    rar_request = urllib.request.urlopen(domain + url)
    rar_html = rar_request.read().decode("gb2312", 'ignore')

    return BeautifulSoup(rar_html, 'html.parser').select_one('.downurllist a').get('href')


def get_page(page_url: str):
    # 建立连接
    print(domain + page_url)
    my_request = urllib.request.urlopen(domain + page_url)
    my_html = my_request.read().decode("gb2312", 'ignore')
    soup = BeautifulSoup(my_html, 'html.parser')
    tag = soup.select('.place a')[2].getText()
    for item in soup.select('.listbox tr')[1:]:
        body = {'type': tag}
        tds = item.select('td')
        detail_url = tds[0].select_one('a').get('href')
        file_url = get_rar(detail_url)
        file_path = download(file_url, detail_url)
        fs = ['name', 'suffix', 'grade', 'source', 'size', 'uploadDate']
        for idx, ii in enumerate(tds):
            body[fs[idx]] = ii.getText()
        body['filePath'] = file_url
        print(body)
        sid = file_path.split('/')[1]
        cur.execute('select id from study where id =%s ' % sid)
        if cur.fetchone():
            # if es.exists(index=index, id=sid):
            print('has in db', sid)
        else:
            body['id'] = sid
            columns = ', '.join(body.keys())
            placeholders = ', '.join('?' * len(body))
            sql = 'INSERT INTO study ({}) VALUES ({})'.format(columns, placeholders)
            values = [int(x) if isinstance(x, bool) else x for x in body.values()]
            cur.execute(sql, values)
            con.commit()
            # es.index(index=index, document=body, id=sid)
    for item in soup.select('.pagelist a'):
        if item.getText() == '下一页':
            return item.get('href')

    return ''


if __name__ == '__main__':

    sql = "CREATE TABLE IF NOT EXISTS study(id INTEGER PRIMARY KEY,type varchar ,name varchar," \
          "suffix varchar,grade varchar,source varchar,size varchar,uploadDate varchar,filePath varchar)"
    cur.execute(sql)
    grade = '1'
    ap = ['/a/sjyw%s/','/a/sjyy%s/','/a/sjsx%s/']
    for bp in ap:
        path = bp % grade
        while path:
            path = bp % grade + get_page(path)

