import time
import datetime
import os


from celery import chain, group, chord, shared_task
from elasticsearch import Elasticsearch, helpers

import pandas as pd
from django.db import connection, transaction
from backend.api.models import Country, Industry, Organization
from celery.result import AsyncResult, GroupResult

from backend.helpers.handler_s3 import HandlerS3
from django.conf import settings


# Main Workflow
@shared_task(bind=True)
def start_workflow(self, bucket, s3_key):
    start_time = datetime.datetime.now()
    final_workflow = chain(
        download_file.s(bucket, s3_key),
        read_file.s(),
        group(
            chain(
                chord(group(process_industries.s(), process_countries.s()), prepare_organization.s()),
                chord(create_groups.s(), finish_processing.s())
            ),
            chain(
                prepare_data_for_elastic_search.s(),
                create_groups_of_document.s(),
            )
        ),
    )

    result = final_workflow.apply_async()
    all_result_tasks = get_result_tasks_objects(result)

    while not result.ready():
        total_progress = 0
        for res in all_result_tasks:
            total_progress += calculate_progress(res)
            iter_group_result(group_result=res)
        general_progress = total_progress / len(all_result_tasks)
        self.update_state(state='PROGRESS', meta={'progress': general_progress})
        time.sleep(2)

    if result.failed():
        iter_group_result(result)

    general_progress = 100
    self.update_state(state='PROGRESS', meta={'progress': general_progress})

    end_time = datetime.datetime.now()
    execution_time = (end_time - start_time).total_seconds()

    self.update_state(state='SUCCESS', meta={
        'result_task_id': result.id,
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'execution_time': execution_time,
        'general_progress': general_progress
    })

    return {
        'result_task_id': result.id,
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'execution_time': execution_time,
        'general_progress': general_progress
    }


@shared_task(bind=True)
def download_file(self, bucket, s3_key):
    s3_uri = f"s3://{bucket}/{s3_key}"
    handler_s3 = HandlerS3()

    localfile = f'/tmp/{s3_key}'

    self.update_state(state='PROGRESS', meta={'progress': 20})

    handler_s3.get_uri_to_file(uri=s3_uri, localfile=localfile)

    self.update_state(state='PROGRESS', meta={'progress': 100})

    return localfile


@shared_task(bind=True)
def read_file(self, file_path):
    df = pd.read_csv(file_path)
    self.update_state(state='PROGRESS', meta={'progress': 50})
    countries_names = df['Country'].unique().tolist()
    industries_names = df['Industry'].unique().tolist()
    self.update_state(state='PROGRESS', meta={'progress': 100})

    return countries_names, industries_names, file_path


@shared_task(bind=True)
def process_countries(self, arguments):
    """
    arguments[0] countries
    arguments[1] industries
    arguments[-1] file_path
    """
    columns = ['name']
    df = pd.DataFrame(arguments[0], columns=columns)
    csv_file_path = '/tmp/countries.csv'
    df.to_csv(csv_file_path, index=False, header=False)
    self.update_state(state='PROGRESS', meta={'progress': 50})

    table_name = Country._meta.db_table

    # Unique Query
    additional_query = f"""
                INSERT INTO {table_name} (name)
                SELECT name FROM tmp_{table_name}
                WHERE name NOT IN (SELECT name FROM {table_name});
            """

    run_bulk_import(csv_file_path=csv_file_path, entity=Country, additional_query=additional_query, headers=columns)
    self.update_state(state='PROGRESS', meta={'progress': 100})

    countries = Country.objects.values('id', 'name')

    return {country['name']: country['id'] for country in countries}, arguments[-1]


@shared_task(bind=True)
def process_industries(self, arguments):
    """
        arguments[0] countries
        arguments[1] industries
        arguments[-1] file_path
    """
    columns = ['name']
    df = pd.DataFrame(arguments[1], columns=columns)
    csv_file_path = '/tmp/industries.csv'
    df.to_csv(csv_file_path, index=False, header=False)

    self.update_state(state='PROGRESS', meta={'progress': 50})

    table_name = Industry._meta.db_table

    # Unique Query
    additional_query = f"""
                    INSERT INTO {table_name} (name)
                    SELECT name FROM tmp_{table_name}
                    WHERE name NOT IN (SELECT name FROM {table_name});
                """

    run_bulk_import(csv_file_path=csv_file_path, entity=Industry, additional_query=additional_query, headers=columns)

    self.update_state(state='PROGRESS', meta={'progress': 100})

    industries = Industry.objects.values('id', 'name')

    return {industry['name']: industry['id'] for industry in industries}, arguments[-1]


@shared_task(bind=True)
def prepare_organization(self, results):
    industries_dict, csv_path = results[0]
    countries_dict, csv_path2 = results[1]
    custom_column_names = ['index_item', 'organization_id', 'name', 'website', 'country_id', 'description', 'year_founded', 'industry_id', 'number_of_employees']
    df = pd.read_csv(csv_path, names=custom_column_names, header=0)
    self.update_state(state='PROGRESS', meta={'progress': 50})
    df = df.drop(columns=['index_item'])

    df['country_id'] = df['country_id'].map(countries_dict)
    df['industry_id'] = df['industry_id'].map(industries_dict)

    chunk_size = 10_000

    column_order = [
        'organization_id', 'name', 'website', 'description', 'year_founded',
        'number_of_employees', 'country_id', 'industry_id'
    ]

    all_chunks = []

    for i, chunk in enumerate(split_dataframe(df, chunk_size)):
        csv_file_path = f'/tmp/organizations_chunk_{i + 1}.csv'
        chunk.to_csv(csv_file_path, index=False, columns=column_order, header=False)
        all_chunks.append(csv_file_path)
    self.update_state(state='PROGRESS', meta={'progress': 100})
    return all_chunks, column_order


def import_to_elastic(csv_file_path, index):
    df = pd.read_csv(csv_file_path)
    list_of_dicts = df.to_dict('records')
    for doc in list_of_dicts:
        yield {'_index': index,
               '_source': doc}


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 5})
def run_bulk_import_elastic_search(self, csv_path_file, index_name):
    es_client = Elasticsearch(settings.ELASTICSEARCH_DSL['default']['hosts'])

    response_chunks = helpers.streaming_bulk(
            es_client,
            actions=import_to_elastic(
                csv_file_path=csv_path_file,
                index=index_name
            )
    )

    for status_ok, response in response_chunks:
        if not status_ok:
            print(f'status_ok: {status_ok}, response={response}')
            raise Exception(str(response))


@shared_task(bind=True)
def prepare_data_for_elastic_search(self, *args, **kwargs):
    chunk_size = 10_000

    _, _, csv_file_path = args[0]
    # Columns of Document Organization
    columns = ['index_item', 'organization_id', 'name', 'website', 'country', 'description',
                           'year_founded', 'industry', 'number_of_employees']
    df = pd.read_csv(csv_file_path, names=columns, header=0)
    df = df.drop(columns=['index_item'])

    all_chunks = []

    for i, chunk in enumerate(split_dataframe(df, chunk_size)):
        csv_file_path = f'/tmp/organizations_document_chunk_{i + 1}.csv'
        chunk.to_csv(csv_file_path, index=False)
        all_chunks.append(csv_file_path)
    index_name = settings.ELASTICSEARCH_INDEX_NAMES['documents.organization']
    return all_chunks, index_name


@shared_task(bind=True)
def process_chunk_organization(self, csv_file_path, headers):
    self.update_state(state='PROGRESS', meta={'progress': 50})
    table_name = Organization._meta.db_table

    additional_query = f"""
                        INSERT INTO {table_name} ({','.join(headers)})
                        SELECT {','.join(headers)} FROM tmp_{table_name};
                    """
    run_bulk_import(csv_file_path=csv_file_path, entity=Organization, additional_query=additional_query, headers=headers)

    self.update_state(state='PROGRESS', meta={'progress': 100})

    os.remove(csv_file_path)

    return 'process_chunk_organization'


@shared_task(bind=True)
def finish_processing(self, results):
    self.update_state(state='PROGRESS', meta={'progress': 100})
    return 'finalized'


@shared_task(bind=True)
def create_groups(self, results):
    self.update_state(state='PROGRESS', meta={'progress': 100})
    workers = group(process_chunk_organization.s(x, results[1]) for x in results[0])
    results = workers.apply_async().get(disable_sync_subtasks=False)
    return 'success create_groups'


@shared_task
def verify_tasks_status(*args, **kwargs):
    for task_result in args:
        if isinstance(task_result, dict) and task_result.get('status') == 'FAILURE':
            raise Exception(f'Task failed with error: {task_result.get("exc_message")}')
    return 'All tasks completed successfully'


@shared_task(bind=True)
def create_groups_of_document(self, results):
    csv_files = results[0]
    index_name = results[1]
    self.update_state(state='PROGRESS', meta={'progress': 100})
    workers = group(run_bulk_import_elastic_search.s(x, index_name) for x in csv_files)
    results = workers.apply_async().get(disable_sync_subtasks=False)
    return 'success create_groups_of_document'


def iter_group_result(group_result):
    if isinstance(group_result, GroupResult):
        async_results = group_result.results
        for async_result in async_results:
            iter_group_result(async_result)
    elif isinstance(group_result, AsyncResult):
        if group_result.status == 'FAILURE':
            raise Exception(group_result.traceback)


def calculate_progress(group_result):
    total_progress = 0
    if isinstance(group_result, GroupResult):
        async_results = group_result.results
        for async_result in async_results:
            iter_group_result(async_result)
    elif isinstance(group_result, AsyncResult):
        if group_result.status == 'FAILURE':
            raise Exception(group_result.traceback)
        if group_result.state == 'PROGRESS':
            total_progress += group_result.info.get('progress', 0)
        elif group_result.state == 'SUCCESS':
            total_progress += 100

    return total_progress if total_progress <= 100 else 100


def bulk_import_entity(csv_file_path, entity, additional_query=None, headers=None):
    table_name = entity._meta.db_table
    with connection.cursor() as cursor:
        query = f"CREATE TEMP TABLE tmp_{table_name} (LIKE {table_name} INCLUDING ALL);"
        cursor.execute(query)

        with open(csv_file_path, 'r') as f:
            query = f"COPY tmp_{table_name}({','.join(headers)}) FROM stdin WITH CSV"
            cursor.copy_expert(query, f)

        if additional_query:
            cursor.execute(additional_query)


@transaction.atomic
def run_bulk_import(csv_file_path, entity, additional_query, headers):
    bulk_import_entity(csv_file_path, entity, additional_query, headers)


def split_dataframe(df, chunk_size):
    for i in range(0, df.shape[0], chunk_size):
        yield df.iloc[i:i + chunk_size]


def get_result_tasks_objects(result):
    task_ids = []
    def recurse(result):
        task_ids.append(result)
        if hasattr(result, 'parent') and result.parent:
            recurse(result.parent)
    recurse(result)
    return task_ids


@shared_task(bind=True)
def error_handler(self, *args, **kwargs):
    print(f'*ARGS: {args}')
    print(f'*KWARGS: {kwargs}')
    self.update_state(state='FAILURE', meta={'exc_type': str(type(args)), 'exc_message': f'Error on {args}'})
    raise Exception(str('Generic Exception'))
