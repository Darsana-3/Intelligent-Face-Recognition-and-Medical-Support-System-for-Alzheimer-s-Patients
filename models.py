from django.db import models
from core.models import Patient


class KnownFace(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='known_faces')
    person_name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50, help_text="e.g., Son, Daughter, Caregiver")
    primary_image = models.ImageField(upload_to='known_faces/')
    embedding_count = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['person_name']

    def __str__(self):
        return f"{self.person_name} ({self.relationship}) - {self.patient.name}"


class FaceImage(models.Model):
    """Additional reference images for a known face."""
    known_face = models.ForeignKey(KnownFace, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='known_faces/extras/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class RecognitionLog(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='recognition_logs')
    recognized_person = models.CharField(max_length=100, default='Unknown')
    relationship = models.CharField(max_length=50, blank=True, null=True)
    confidence = models.FloatField(default=0.0)
    is_match = models.BooleanField(default=False)
    captured_image = models.ImageField(upload_to='recognition_logs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recognized_person} -> {self.patient.name} @ {self.created_at}"
