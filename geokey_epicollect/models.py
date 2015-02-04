from django.db import models


class EpiCollectProject(models.Model):
    enabled = models.BooleanField(default=False)
    project = models.OneToOneField(
        'projects.Project',
        primary_key=True,
        related_name='epicollect'
    )

    objects = models.Manager()
