from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from uploader.models import Files
from uploader.serializers import FilesSerializer
from rest_framework.parsers import MultiPartParser, FormParser

@api_view(['GET','POST'])
def upload_form(request):
	if request.method == 'POST':
		instance = Files(docfile=request.FILES['docfile'], title=request.DATA['title'])
		instance.save()
		return Response('uploaded')
		
	elif request.method == 'GET':
		files = Files.objects.all()
		serializer = FilesSerializer(files)
		return Response(serializer.data)

@api_view(['POST','GET'])
def upload_serializers(request):
	if request.method == 'POST':
		serializer = FilesSerializer(data=request.DATA, files=request.FILES)
		if serializer.is_valid():
			serializer.save()
			return Response(data=request.DATA, status=status.HTTP_201_CREATED)
		else:
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
			
	elif request.method == 'GET':
		files = Files.objects.all()
		serializer = FilesSerializer(files)
		return Response(serializer.data)
