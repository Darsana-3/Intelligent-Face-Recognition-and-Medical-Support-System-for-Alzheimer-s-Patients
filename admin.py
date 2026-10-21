from django.contrib import admin
from .models import KnownFace, FaceImage, RecognitionLog

admin.site.register(KnownFace)
admin.site.register(FaceImage)
admin.site.register(RecognitionLog)
