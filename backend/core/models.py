from django.db import models
import uuid

class Book(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=200, default="Unknown Author")
    description = models.TextField(blank=True)
    rating = models.FloatField(default=0.0)
    price = models.CharField(max_length=20, blank=True)
    book_url = models.URLField(blank=True)
    summary = models.TextField(blank=True)
    genre = models.CharField(max_length=100, blank=True)
    recommendations = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

class ChatHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.TextField()
    answer = models.TextField()
    sources = models.TextField(blank=True)  # Store sources as string
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Q: {self.question[:50]}..."
