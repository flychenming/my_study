import os

from elasticsearch import Elasticsearch
from flask import Flask, render_template, request, send_file
from flask_paginate import Pagination, get_page_args

app = Flask(__name__)

domain = 'https://nginx.mytestray.cf:10002'


@app.route('/download/<path:filename>')
def download_file(filename: str):
    print(filename)
    listdir = os.listdir('/root/' + filename)
    if listdir:
        return send_file('/root/' + filename + '/' + listdir[0], as_attachment=True)


@app.route('/')
def index():
    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    args = request.args
    print(args)
    index = 'study_v1'
    es = Elasticsearch(
        hosts=['http://43.154.70.80:9200'],  # 地址
        request_timeout=3600  # 超时时间
    )
    query = {
        "query": {
            "match_all": {}
        },
        "from": offset,
        "size": per_page
    }

    data = es.search(index=index, query={
        "match_all": {}
    }, from_=offset, size=per_page)
    # print(data)
    total = data['hits']['total']['value']
    list_data = data['hits']['hits']
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    return render_template('index.html',
                           data=list_data,
                           page=page,
                           per_page=per_page,
                           pagination=pagination, domain=domain
                           )


if __name__ == '__main__':
    app.run(debug=False)
