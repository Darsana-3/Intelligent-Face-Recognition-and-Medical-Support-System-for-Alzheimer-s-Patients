import os
import base64
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.conf import settings
from core.helpers import login_required_role, log_activity
from .models import KnownFace, FaceImage, RecognitionLog
from . import utils


@login_required_role('patient')
def known_faces_list(request):
    patient = request.user_obj
    faces = KnownFace.objects.filter(patient=patient)
    return render(request, 'face_recognition_app/known_faces_list.html', {'faces': faces})


@login_required_role('patient')
def enroll_face_view(request):
    """Enroll a new known face: upload primary + extra images."""
    patient = request.user_obj
    if request.method == 'POST':
        person_name = request.POST.get('person_name', '').strip()
        relationship = request.POST.get('relationship', '').strip()
        notes = request.POST.get('notes', '')
        primary = request.FILES.get('primary_image')
        extras = request.FILES.getlist('extra_images')

        if not all([person_name, relationship, primary]):
            messages.error(request, "Name, relationship and a primary photo are required.")
            return render(request, 'face_recognition_app/enroll_face.html')

        kf = KnownFace.objects.create(
            patient=patient,
            person_name=person_name,
            relationship=relationship,
            primary_image=primary,
            notes=notes,
        )
        # save extra images
        image_paths = [os.path.join(settings.MEDIA_ROOT, kf.primary_image.name)]
        for img in extras:
            fi = FaceImage.objects.create(known_face=kf, image=img)
            image_paths.append(os.path.join(settings.MEDIA_ROOT, fi.image.name))

        # Extract embeddings
        success, count = utils.enroll_face(
            patient.id, kf.id, person_name, relationship, image_paths
        )

        if success:
            kf.embedding_count = count
            kf.save()
            log_activity('patient', patient.id, patient.name, f"Enrolled face: {person_name}", request)
            messages.success(request, f"{person_name} enrolled successfully from {count} image(s).")
            return redirect('known_faces_list')
        else:
            kf.delete()
            messages.error(request, "Could not detect a face in the uploaded images. Please use clear, front-facing photos.")
    return render(request, 'face_recognition_app/enroll_face.html')


@login_required_role('patient')
def delete_known_face(request, fid):
    patient = request.user_obj
    kf = get_object_or_404(KnownFace, id=fid, patient=patient)
    name = kf.person_name
    utils.remove_face(patient.id, kf.id)
    kf.delete()
    messages.success(request, f"{name} removed from known faces.")
    return redirect('known_faces_list')


@login_required_role('patient')
def recognize_view(request):
    """Real-time recognition page (webcam capture)."""
    return render(request, 'face_recognition_app/recognize.html', {'patient': request.user_obj})


@login_required_role('patient')
def recognize_api(request):
    """AJAX endpoint: receive captured image, run recognition, return JSON."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    patient = request.user_obj
    image_data = request.POST.get('image_data', '')
    if not image_data:
        return JsonResponse({'error': 'No image data'}, status=400)

    # decode base64 image from webcam
    try:
        if ',' in image_data:
            image_data = image_data.split(',', 1)[1]
        img_bytes = base64.b64decode(image_data)
    except Exception as e:
        return JsonResponse({'error': f'Invalid image: {e}'}, status=400)

    # save temporary file
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'recognition_logs')
    os.makedirs(temp_dir, exist_ok=True)
    from django.utils import timezone
    fname = f"capture_{patient.id}_{int(timezone.now().timestamp())}.jpg"
    fpath = os.path.join(temp_dir, fname)
    with open(fpath, 'wb') as f:
        f.write(img_bytes)

    # run recognition
    result = utils.recognize_face(patient.id, fpath)

    # log it
    rel_path = os.path.join('recognition_logs', fname)
    log = RecognitionLog.objects.create(
        patient=patient,
        recognized_person=result.get('person_name', 'Unknown'),
        relationship=result.get('relationship', ''),
        confidence=result.get('confidence', 0.0),
        is_match=result.get('match', False),
        captured_image=rel_path,
    )
    result['log_id'] = log.id
    result['voice_enabled'] = patient.voice_announcement_enabled
    return JsonResponse(result)


@login_required_role('patient')
def recognition_logs_view(request):
    patient = request.user_obj
    logs = RecognitionLog.objects.filter(patient=patient)[:50]
    return render(request, 'face_recognition_app/recognition_logs.html', {'logs': logs})
