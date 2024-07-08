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
    def get(self, request):
        # s3_client = boto3.client(
        #     's3',
        #     region_name=settings.AWS_S3_REGION_NAME,
        #     aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        #     aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        # )

        # Generar una URL pre-firmada para la carga de un archivo
        # presigned_url = s3_client.generate_presigned_url(
        #     'put_object',
        #     Params={
        #         'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
        #         'Key': 'uploads/your_filename.ext',  # Cambia el nombre del archivo según sea necesario
        #         'ContentType': 'application/octet-stream'  # Opcional: especifica el tipo de contenido
        #     },
        #     ExpiresIn=3600  # La URL expira en 1 hora
        # )
        presigned_url = "here the s3 url presigned ready to upload"

        return Response({'url': presigned_url}, status=status.HTTP_200_OK)



# Create your views here.
