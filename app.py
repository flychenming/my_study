import os
import sqlite3

import patoolib
from cachetools import TTLCache
from flask import Flask, render_template, request, send_file
from flask_paginate import Pagination, get_page_args
import urllib.request
from tempfile import TemporaryDirectory

app = Flask(__name__)

domain = 'https://nginx.mytestray.cf:10003'

cache = TTLCache(maxsize=10, ttl=360)


@app.route('/download/<path:filename>')
def download_file(filename: str):
    print(filename)
    td = 'https://www.shijuan1.com/'
    print(td + filename)
    file_name, headers = urllib.request.urlretrieve(td + filename)
    with TemporaryDirectory() as out:
        print('dirname is:', out)
        patoolib.extract_archive(file_name, outdir=out)
        if os.path.exists(out + '/第一试卷网.url'):
            os.remove(out + '/第一试卷网.url')
        listdir = os.listdir(out)
        if listdir:
            return send_file(out + '/' + listdir[0], as_attachment=True)


@app.route('/')
def index():
    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    params = request.args.to_dict()
    print(params)
    con = sqlite3.connect("my_study.db")
    con.row_factory = sqlite3.Row

    cur = con.cursor()

    sql = 'select * from study where 1=1'
    csql = 'select count(*) as total from study where 1=1'
    if 'keyword' in params and params['keyword']:
        sql += " and name like '%" + params['keyword'] + "%'"
        csql += " and name like '%" + params['keyword'] + "%'"

    if 'grade' in params and params['grade']:
        sql += " and grade='%s' " % params['grade']
        csql += " and grade='%s' " % params['grade']
    if 'type' in params and params['type']:
        sql += " and type='%s' " % params['type']
        csql += " and type='%s' " % params['type']
    if 'source' in params and params['source']:
        sql += " and source='%s' " % params['source']
        csql += " and source='%s' " % params['source']
    cur.execute(csql)
    total = cur.fetchone()['total']
    sql += ' limit %d offset %d' % (per_page, offset)
    print(sql)
    cur.execute(sql)
    data = cur.fetchall()
    # print(data)

    if 'grade' in cache:
        grade = cache['grade']
    else:
        cur.execute('select grade key,count(grade) doc_count from study group by grade')
        grade = cur.fetchall()
        cache['grade'] = grade
    if 'type' in cache:
        _type = cache['type']
    else:
        cur.execute('select type key,count(type) doc_count from study group by type')
        _type = cur.fetchall()
        cache['type'] = _type
    if 'source' in cache:
        source = cache['source']
    else:
        cur.execute('select source key,count(source) doc_count from study group by source')
        source = cur.fetchall()
        cache['source'] = source
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    return render_template('index.html',
                           data=data,
                           page=page,
                           per_page=per_page,
                           pagination=pagination, domain=domain, grade=grade,
                           type=_type, source=source, params=params
                           )


if __name__ == '__main__':
    app.run(debug=False)
