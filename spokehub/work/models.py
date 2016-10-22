from django.contrib.auth.models import User
from django.db import models


class Project(models.Model):
    title = models.TextField(blank=True, default="")
    slug = models.SlugField()
    subhead = models.TextField(blank=True, default="")
    date = models.TextField(blank=True, default="")
    description = models.TextField(blank=True, default="")
    published = models.BooleanField(default=False)
    thumb_hash = models.TextField(blank=True, null=True)
    thumb_extension = models.TextField(blank=True, null=True)
    cardinality = models.IntegerField(default=1)

    class Meta:
        ordering = ['-cardinality']


class ProjectContributor(models.Model):
    project = models.ForeignKey(Project)
    fullname = models.TextField(blank=True, default="")
    user = models.ForeignKey(User, null=True)

    class Meta:
        order_with_respect_to = 'project'


class ProjectMedia(models.Model):
    project = models.ForeignKey(Project)
    image_hash = models.TextField(blank=True, null=True)
    image_extension = models.TextField(blank=True, null=True)
    youtube_id = models.TextField(default="", blank=True)
    vimeo_id = models.TextField(default="", blank=True)

    class Meta:
        order_with_respect_to = 'project'