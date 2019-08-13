from django.contrib import admin
from .models import Credentials, QuestionCredendial, Question, Result

admin.site.register(Credentials)
admin.site.register(QuestionCredendial)
admin.site.register(Question)
admin.site.register(Result)
