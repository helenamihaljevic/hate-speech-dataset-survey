import requests
import json
import argparse
import os
from os.path import join

BASE_URL = "https://api.openalex.org/works"
QUERY = """(offensive OR hateful OR toxic OR abusive OR profanity OR "hate speech" OR hatespeech)
AND (corpus OR "data set" OR dataset OR collection)"""
# id for primary topic "Automated Detection of Hate Speech and Offensive Language"
TOPIC = "t12262"  # https://explore.openalex.org/works?page=1&filter=primary_topic.id%3At12262
TYPE = "dataset"
DATA_PATH = join(os.getcwd(), 'data')


def build_title_query(query):
    return f'title.search:{query}'


def build_title_abstract_query(query):
    return f'title_and_abstract.search:{query}'


def build_topic_type_query(topic, work_type):  # primary_topic.id%3At12262
    return f'primary_topic.id:{topic},type:{work_type}'


def fetch_works(query, per_page=25):
    all_works = []
    cursor = '*'

    while cursor:
        params = {
            'filter': query,
            'per_page': per_page,
            'cursor': cursor
        }

        response = requests.get(BASE_URL, params=params)

        if response.status_code == 200:
            results = response.json()
            works = results.get('results', [])
            all_works.extend(works)

            # Update cursor for the next page
            cursor = results['meta'].get('next_cursor')
            if not cursor:
                break
        else:
            print(f"Failed to fetch data. HTTP Status code: {response.status_code}")
            break

    return all_works


def export_to_json(f_out, data):
    with open(f_out, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch data from OpenAlex based on query type.")
    parser.add_argument("--query-type", choices=['title', 'title_abstract', 'topic_type'], required=True,
                        help="Specify the type of query to execute: 'title', 'title_abstract', or 'topic_type'")

    args = parser.parse_args()

    if args.query_type == 'title':
        query = build_title_query(QUERY)
    elif args.query_type == 'title_abstract':
        query = build_title_abstract_query(QUERY)
    elif args.query_type == 'topic_type':
        query = build_topic_type_query(TOPIC, TYPE)
    else:
        query = None
        print("No query built. Stopping script")

    if query:
        results = fetch_works(query)
        output_file = join(DATA_PATH, f"openalex_{args.query_type}_export.json")

        if results:
            export_to_json(output_file, results)
        else:
            print(f"No results for {args.query_type} query found.")
