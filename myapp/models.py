from django.db import models


class User(models.Model):
    userid = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)  # Hashed password storage

    def __str__(self):
        return self.username


class DatabaseCredential(models.Model):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    db_name = models.CharField(max_length=255)
    port = models.IntegerField()
    db_type = models.CharField(max_length=50)
    host = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.db_name} ({self.db_type})"
