from django.db import models


class ResData(models.Model):
    name = models.CharField(max_length=500, blank=True, null=True,
                            db_index=True)
    url = models.CharField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=500, blank=True, null=True)
    review = models.CharField(max_length=5000, blank=True, null=True)
    rating = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Created At',
                                      db_index=True)
    modified_at = models.DateTimeField(auto_now=True,
                                       verbose_name='Last Modified At')

    def __str__(self):
        return '{} - {}'.format(self.name, self.rating)
