from django.contrib import admin
from .models import Query, WatchData, QuestionData

admin.site.register(Query)
admin.site.register(WatchData)
admin.site.register(QuestionData)
