import logging
import os

logger = logging.getLogger(__package__)

from celery import chain, group, chord, shared_task
from celery.contrib import rdb

import pandas as pd
from django.db.models.fields import Field
from django.db import connection, transaction
from backend.api.models import Country, Industry, Organization

from backend.helpers.handler_s3 import HandlerS3


@shared_task(bind=True)
def download_file(self, bucket, s3_key):
    s3_uri = f"s3://{bucket}/{s3_key}"
    handler_s3 = HandlerS3()

    localfile = f'/tmp/{s3_key}'

    handler_s3.get_uri_to_file(uri=s3_uri, localfile=localfile)

    return localfile


@shared_task
def read_file(file_path):
    df = pd.read_csv(file_path)
    countries_names = df['Country'].unique().tolist()
    industries_names = df['Industry'].unique().tolist()

    return countries_names, industries_names, file_path


@shared_task
def process_countries(arguments):
    """
    arguments[0] countries
    arguments[1] industries
    arguments[-1] file_path
    """
    columns = ['name']
    df = pd.DataFrame(arguments[0], columns=columns)
    csv_file_path = '/tmp/countries.csv'
    df.to_csv(csv_file_path, index=False, header=False)

    table_name = Country._meta.db_table

    # Unique Query
    additional_query = f"""
                INSERT INTO {table_name} (name)
                SELECT name FROM tmp_{table_name}
                WHERE name NOT IN (SELECT name FROM {table_name});
            """

    run_bulk_import(csv_file_path=csv_file_path, entity=Country, additional_query=additional_query, headers=columns)

    countries = Country.objects.values('id', 'name')

    return {country['name']: country['id'] for country in countries}, arguments[-1]


@shared_task
def process_industries(arguments):
    """
        arguments[0] countries
        arguments[1] industries
        arguments[-1] file_path
    """
    columns = ['name']
    df = pd.DataFrame(arguments[1], columns=columns)
    csv_file_path = '/tmp/industries.csv'
    df.to_csv(csv_file_path, index=False, header=False)

    table_name = Industry._meta.db_table

    # Unique Query
    additional_query = f"""
                    INSERT INTO {table_name} (name)
                    SELECT name FROM tmp_{table_name}
                    WHERE name NOT IN (SELECT name FROM {table_name});
                """

    run_bulk_import(csv_file_path=csv_file_path, entity=Industry, additional_query=additional_query, headers=columns)

    industries = Industry.objects.values('id', 'name')

    return {industry['name']: industry['id'] for industry in industries}, arguments[-1]


@shared_task
def prepare_organization(results):
    countries_dict, csv_path = results[0]
    industries_dict, csv_path2 = results[1]
    custom_column_names = ['index_item', 'organization_id', 'name', 'website', 'country_id', 'description', 'year_founded', 'industry_id', 'number_of_employees']
    df = pd.read_csv(csv_path, names=custom_column_names, header=0)
    df = df.drop(columns=['index_item'])

    df['country_id'] = df['country_id'].map(countries_dict)
    df['industry_id'] = df['industry_id'].map(industries_dict)

    chunk_size = 10000

    column_order = [
        'organization_id', 'name', 'website', 'description', 'year_founded',
        'number_of_employees', 'country_id', 'industry_id'
    ]

    all_chunks = []

    for i, chunk in enumerate(split_dataframe(df, chunk_size)):
        csv_file_path = f'/tmp/organizations_chunk_{i + 1}.csv'
        chunk.to_csv(csv_file_path, index=False, columns=column_order)
        all_chunks.append(csv_file_path)

    return all_chunks, column_order


@shared_task
def process_chunk_organization(csv_file_path, headers):
    run_bulk_import(csv_file_path=csv_file_path, entity=Organization, additional_query=None, headers=headers)

    return 'process_chunk_organization'


@shared_task
def finish_processing(results):
    return 'finalized'


@shared_task
def create_groups(results):
    return group(process_chunk_organization.s(x[0], results[1]) for x in results[0]).apply_async()


def start_workflow(bucket, s3_key):
    final_workflow = chain(
        download_file.s(bucket, s3_key),
        read_file.s(),
        chord(group(process_industries.s(), process_countries.s()), prepare_organization.s()),
        chord(create_groups.s(), finish_processing.s())
    )

    return final_workflow.apply_async()


def bulk_import_entity(csv_file_path, entity, additional_query=None, headers=None):
    table_name = entity._meta.db_table
    with connection.cursor() as cursor:
        query = f"CREATE TEMP TABLE tmp_{table_name} (LIKE {table_name} INCLUDING ALL);"
        print(query)
        cursor.execute(query)

        with open(csv_file_path, 'r') as f:
            query = f"COPY tmp_{table_name}({','.join(headers)}) FROM stdin WITH CSV"
            print(query)
            cursor.copy_expert(query, f)

        if additional_query:
            print(additional_query)
            cursor.execute(additional_query)


@transaction.atomic
def run_bulk_import(csv_file_path, entity, additional_query, headers):
    bulk_import_entity(csv_file_path, entity, additional_query, headers)
    os.remove(csv_file_path)


def split_dataframe(df, chunk_size):
    for i in range(0, df.shape[0], chunk_size):
        yield df.iloc[i:i + chunk_size]
