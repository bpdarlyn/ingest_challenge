import os
import time
import traceback
import sys
from urllib.parse import urlparse
import random
from pathlib import Path
import logging
import threading

from backend.helpers.handler_file import HandlerFile

import boto3
import botocore
from botocore.config import Config


threading_lock = threading.Lock()
logger = logging.getLogger(__package__)


class HandlerS3(object):

    def __init__(self):
        try:
            self.client = self._get_s3_client()
            self.conn_s3 = self._get_s3_connection()
            self.__local_filehandler__ = HandlerFile("/")
        except Exception:
            print("problem with HandlerS3 connection (missing credentials?)")
            traceback.print_exc(file=sys.stdout)
            traceback.print_exc(file=sys.stderr)
            raise

    @staticmethod
    def _get_s3_connection():
        wait_seconds = 1

        while True:
            try:
                res = boto3.resource('s3')
                #print(traceback.print_stack())
                return res
            except botocore.exceptions.ClientError as eee:
                print("problem getting boto3 s3 connection (B)")
                wait_time = wait_seconds + random.random()
                print("waiting {second} seconds".format(second=wait_time))
                time.sleep(wait_time)
                wait_seconds *= 2

    @staticmethod
    def _get_s3_client():
        wait_seconds = 1

        while True:
            try:
                config = Config(retries=dict(max_attempts=250))
                res = boto3.client('s3', config=config)
                return res
            except botocore.exceptions.ClientError as eee:
                print("problem getting boto3 s3 client (D)")
                wait_time = wait_seconds + random.random()
                print("waiting {second} seconds".format(second=wait_time))
                time.sleep(wait_time)
                wait_seconds *= 2

    def get_uri_to_file(self, uri, localfile, force_cache=True):
        if force_cache and self.__local_filehandler__.isfile(path=localfile):
            logger.info(f'Cache hit {localfile}, skipping downloading')
            return

        parsed_uri = urlparse(uri)
        key_name = parsed_uri.path[1:]
        bucket_name = parsed_uri.hostname
        bucket = self.conn_s3.Bucket(bucket_name)

        self.__local_filehandler__.mkdir_p(path=localfile)

        logger.info("{uri} => {local} (H)".format(uri=uri, local=localfile))

        tmp_localfile = localfile + ".%s.tmp" % time.time()

        bucket.download_file(Key=key_name, Filename=tmp_localfile)

        self.__local_filehandler__.move(tmp_localfile, localfile)
