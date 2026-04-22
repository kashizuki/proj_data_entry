from django.conf import settings
from django.db import models
from django.urls import reverse


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    nim = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.user.username} ({self.nim})"


class Project(models.Model):
    STATUS_CHOICES = [
        ("Aktif", "Aktif"),
        ("Selesai", "Selesai"),
        ("Tertunda", "Tertunda"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="projects"
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    executor = models.CharField(max_length=200)
    supervisor = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Aktif")
    is_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("data_entry:project_detail", kwargs={"project_id": self.id})


class Work(models.Model):
    CATEGORY_CHOICES = [
        ("engineering", "Intelligence Engineering"),
        ("creation", "Intelligence Creation"),
        ("implementation", "Implementation"),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="works")
    name = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    executor = models.CharField(max_length=200)
    supervisor = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Activity(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name="activities")
    name = models.CharField(max_length=200)
    execution_time = models.CharField(max_length=100)
    executor = models.CharField(max_length=200)
    done = models.BooleanField(default=False)
    evaluation = models.TextField(blank=True)
    additional_plan = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class ActivityPhoto(models.Model):
    activity = models.ForeignKey(
        Activity, on_delete=models.CASCADE, related_name="photos"
    )
    image = models.FileField(upload_to="activity_photos/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
