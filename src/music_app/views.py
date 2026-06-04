from django.shortcuts import render
from backend.settings import BASE_DIR
from logging import getLogger

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Student, Song

from .services.tf_connection import socket, ee

import json

app_name = "music_app"
logger = getLogger(app_name)

songsFeedback = {
    # key = value
    # ["youtube-id"] = {
    #       ...
    # }
}


@ee.on("packet-received")
def handlePacket(data: str):
    request = "CHECK-SONG"

    if data.startswith(request):
        payload = data[len(request) :]

        if len(payload) == 0:
            return logger.error("No payload detected", exc_info=True)

        data = json.loads(payload)
        key = data["id"]

        songsFeedback[key] = data


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

    socket.send("ADD-VIDEO " + "https://www.youtube.com/watch?v=" + youtube_id)

    return JsonResponse(
        {
            "success": True,
            "student_name": student.name,
            "song_internal_id": song.id,
            "song_youtube_id": youtube_id,
            "created": created,
        }
    )


@csrf_exempt
def checkSong(request):
    if request.method != "POST":
        return Res(400, "POST required")

    data = json.loads(request.body)
    youtube_id = data.get("youtube-id", "")

    matchingSong = next((song for song in songsFeedback.values() if song["id"] == youtube_id), None)
    responseDict = {"success": False}

    if matchingSong:
        responseDict["success"] = True
        responseDict.update(matchingSong)

    return JsonResponse(responseDict)


@csrf_exempt
def index(request):
    return render(request, BASE_DIR / "backend" / "templates" / "base.html")
