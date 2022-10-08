from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.


class User(AbstractUser):
    role = models.IntegerField(choices=[(1, 'Product Manager'), (2, 'Developer')], default=1)


class Project(models.Model):
    name = models.CharField(max_length=100)
    abbr = models.CharField(max_length=5)
    creator = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='creator_user')
    submit_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)


class Task(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True, default=None)
    creator = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='creator')
    assignee = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='assignee')
    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING)
    submit_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
