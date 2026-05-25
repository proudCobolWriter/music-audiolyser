from django.db import models


class Student(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class Song(models.Model):
    class Scale(models.TextChoices):
        MINOR = "minor", "Minor"
        MAJOR = "major", "Major"

    youtube_id = models.CharField(max_length=11, unique=True)

    title = models.CharField(max_length=100, default="")
    artist = models.CharField(max_length=100, default="")

    genre = models.TextField(default="")
    bpm = models.IntegerField(default=0)

    danceability = models.FloatField(default=0.0)

    key = models.CharField(max_length=3, default="")
    scale = models.CharField(max_length=5, choices=Scale.choices, default="")
    mood = models.TextField(default="")  # =valence?

    listeners = models.ManyToManyField(Student, related_name="songs")

    def __str__(self):
        return f"{self.title} - {self.artist}"
