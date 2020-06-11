from django.db import models


class Query(models.Model):
    vid_num = models.CharField(max_length=5, default='')
    user_id = models.CharField(max_length=20, default='')
    count = models.IntegerField()

    def __str__(self):
        return self.number


class WatchData(models.Model):
    date = models.CharField(max_length=10)
    time = models.CharField(max_length=25)
    speed = models.FloatField()
    timestamp = models.FloatField()
    user_id = models.IntegerField()
    vid_num = models.IntegerField()
