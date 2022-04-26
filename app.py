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
    params = request.args.to_dict()
    print(params)
    _index = 'study_v1'
    es = Elasticsearch(
        hosts=['http://43.154.70.80:9200'],  # 地址
        request_timeout=3600  # 超时时间
    )

    query = {
        "bool": {
        }
    }
    if 'keyword' in params and params['keyword']:
        query['bool']['must'] = [{'match': {
            "name": {
                "query": params['keyword'],
                "boost": 1.0
            }
        }}]
    if 'grade' in params and params['grade']:
        if 'filter' not in query['bool']:
            query['bool']['filter'] = []
        query['bool']['filter'].append({'term': {
            "grade": {
                "value": params['grade'],
                "boost": 1.0
            }
        }})

    if 'type' in params and params['type']:
        if 'filter' not in query['bool']:
            query['bool']['filter'] = []
        query['bool']['filter'].append({'term': {
            "type": {
                "value": params['type'],
                "boost": 1.0
            }
        }})
    if 'source' in params and params['source']:
        if 'filter' not in query['bool']:
            query['bool']['filter'] = []
        query['bool']['filter'].append({'term': {
            "source": {
                "value": params['source'],
                "boost": 1.0
            }
        }})
    aggregations = {
        "grade": {
            "terms": {
                "field": "grade"
            }
        },
        "type": {
            "terms": {
                "field": "type"
            }
        },
        "source": {
            "terms": {
                "field": "source"
            }
        }
    }
    print(query)
    agg = es.search(index=_index, query={
        "match_all": {}
    }, from_=0, size=0, aggregations=aggregations)

    data = es.search(index=_index, query=query if query['bool'] else {
        "match_all": {}
    }, from_=offset, size=per_page)
    # print(data)
    total = data['hits']['total']['value']
    grade = agg['aggregations']['grade']['buckets']
    _type = agg['aggregations']['type']['buckets']
    source = agg['aggregations']['source']['buckets']
    list_data = data['hits']['hits']
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    return render_template('index.html',
                           data=list_data,
                           page=page,
                           per_page=per_page,
                           pagination=pagination, domain=domain, grade=grade,
                           type=_type, source=source, params=params
                           )


if __name__ == '__main__':
    app.run(debug=False)
