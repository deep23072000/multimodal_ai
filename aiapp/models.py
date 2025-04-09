from django.db import models

class SearchHistory(models.Model):
    query = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.query} at {self.timestamp}"
