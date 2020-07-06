from django.db import models


class Query(models.Model):
    vid_num = models.CharField(max_length=5, default='')
    user_id = models.CharField(max_length=20, default='')
    count = models.IntegerField()

    def __str__(self):
        return self.number


class WatchData(models.Model):
    vid_num = models.IntegerField()
    vid_name = models.CharField(max_length=100, default='NaN')
    user_id = models.IntegerField()
    username = models.CharField(max_length=25, default='NaN')
    email = models.CharField(max_length=25, default='NaN')
    date = models.CharField(max_length=10)
    time = models.CharField(max_length=25)
    speed = models.FloatField()
    timestamp = models.FloatField()


class QuestionData(models.Model):
    user_id = models.IntegerField()
    email = models.CharField(max_length=25, default='NaN')
    username = models.CharField(max_length=25, default='NaN')
    video_id = models.IntegerField()
    video_location = models.IntegerField()
    question_id = models.IntegerField()
    answer_id = models.IntegerField()
    is_correct = models.BooleanField()


'''
class WatchData(models.Model):
    date = models.CharField(max_length=10)
    time = models.CharField(max_length=25)
    speed = models.FloatField()
    timestamp = models.FloatField()
    user_id = models.IntegerField()
    vid_num = models.IntegerField()
'''
