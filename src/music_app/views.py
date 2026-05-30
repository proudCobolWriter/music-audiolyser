from django.shortcuts import render
from backend.settings import BASE_DIR

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Student, Song

from music_app.services.downloader_process import command_queue

import json


def Res(status: int, message: str):
    return JsonResponse({"error": message}, status=status)


@csrf_exempt  # don't leave that for production, it leaves room for CSRF attacks
def sendName(request):
    if request.method != "POST":
        return Res(400, "POST required")

    data = json.loads(request.body)
    name = data.get("name", "").strip()

    if not name:
        return Res(400, "Missing name")

    student, created = Student.objects.get_or_create(name=name)

    return JsonResponse(
        {
            "success": True,
            "name": student.name,
            "student_id": student.id,
            "created": created,
        }
    )


@csrf_exempt
def sendSong(request):
    if request.method != "POST":
        return Res(400, "POST required")

    data = json.loads(request.body)
    youtube_id = data.get("youtube-id", "")
    student_id = data.get("id", -1)

    if not isinstance(student_id, int) or student_id == -1:
        return Res(400, "Incorrect id")

    student = Student.objects.filter(id=student_id).first()

    if student is None:
        return Res(400, "Student doesn't exist")

    if not youtube_id:
        return Res(400, "Incorrect YTB content ID")

    song, created = Song.objects.get_or_create(youtube_id=youtube_id)
    song.listeners.add(student)

    # get_downloader() += "https://www.youtube.com/watch?v=" + youtube_id

    command_queue.put("https://www.youtube.com/watch?v=" + youtube_id)

    return JsonResponse(
        {
            "success": True,
            "student_name": student.name,
            "song_id": song.id,
            "song_name": song.youtube_id,
            "created": created,
        }
    )


def index(request):
    return render(request, BASE_DIR / "backend" / "templates" / "base.html")
