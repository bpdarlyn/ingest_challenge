import os
from datetime import datetime

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Company
from .serializer import CompanySerializer
from django.conf import settings
import boto3


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class GeneratePresignedUrlView(APIView):
    PRESIGNED_BUCKET = f'{os.getenv("BACKEND_STACK")}-tmp'
    PRESIGNED_KEY_PUT = 'uploads/{timestamp}/{filename}'

    def get(self, request):
        s3_client = boto3.client('s3')

        filename = request.query_params.get('filename')

        # Generate a Presigned URL to avoid overload to our servers

        s3_bucket = self.PRESIGNED_BUCKET
        s3_key = self.PRESIGNED_KEY_PUT.format(timestamp=datetime.now, filename=filename)

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



# Create your views here.
