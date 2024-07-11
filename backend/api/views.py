import os
from datetime import datetime

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
import boto3
from backend.api import tasks as api_tasks
from celery.result import AsyncResult


from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    OrderingFilterBackend,
    DefaultOrderingFilterBackend,
    SearchFilterBackend,
)

from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet


from .serializer import OrganizationDocumentSerializer
from .documents import OrganizationDocument


class OrganizationDocumentViewSet(DocumentViewSet):
    document = OrganizationDocument
    serializer_class = OrganizationDocumentSerializer
    lookup_field = 'id'
    filter_backends = [
        FilteringFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        SearchFilterBackend,
    ]
    # Define search fields
    search_fields = {
        'name': {'boost': 2},
        'description': {'boost': 1},
    }

    # Define filter fields
    filter_fields = {
        'name': 'name.exact',
        'country': 'country.exact',
        'industry': 'industry.exact',
        'year_founded': 'year_founded',
        'number_of_employees': 'number_of_employees',
    }

    # Define ordering fields
    ordering_fields = {
        'year_founded': 'year_founded',
        'number_of_employees': 'number_of_employees',
    }

    # Specify default ordering
    ordering = ('year_founded',)


class GeneratePresignedUrlView(APIView):
    PRESIGNED_BUCKET = f'{os.getenv("BACKEND_STACK")}-tmp'
    PRESIGNED_KEY_PUT = 'uploads/{timestamp}/{filename}'

    def get(self, request):
        s3_client = boto3.client('s3')

        filename = request.query_params.get('filename')

        # Generate a Presigned URL to avoid overload to our servers

        s3_bucket = self.PRESIGNED_BUCKET
        s3_key = self.PRESIGNED_KEY_PUT.format(timestamp=str(datetime.now().strftime('%Y%m%d%H%M%S')), filename=filename)

        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': s3_bucket,
                'Key': s3_key,
                'ContentType': 'text/csv'
            },
            ExpiresIn=3600  # 1 hour of expiration
        )

        response = {
            'presigned_url': presigned_url,
            's3_bucket': s3_bucket,
            's3_key': s3_key,
        }

        return Response(response, status=status.HTTP_200_OK)


class StartProcessingView(APIView):
    def post(self, request):
        data = request.data
        s3_bucket, s3_key = data.get('s3_bucket'), data.get('s3_key')

        result = api_tasks.start_workflow.apply_async(args=(s3_bucket, s3_key))
        return Response({
            'job_id': result.id,
        }, status=status.HTTP_200_OK)

    def get(self, request, job_id):
        result = AsyncResult(job_id)
        # execution_time = result.date_done - result.date_submitted
        info = result.info

        if result.failed():
            if isinstance(result.info, Exception):
                info = str(result.info)

        response_data = {
            'task_id': job_id,
            'status': result.status,
            'info': info,
            'result': result.result if result.successful() else None,
        }

        return Response(response_data, status=status.HTTP_200_OK)
# Create your views here.
