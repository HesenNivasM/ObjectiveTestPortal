from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from ckeditor_uploader.fields import RichTextUploadingField


class Credentials(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    attended = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user.username)


class QuestionCredendial(models.Model):
    staff_id = models.CharField(max_length=30)
    subject_code = models.CharField(max_length=1000)
    subject_name = models.CharField(max_length=1000)
    total_questions = models.IntegerField()
    questions_added = models.IntegerField(default=0)
    test_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_in_minutes = models.IntegerField()
    students_allowed = models.CharField(max_length=10000)
    total_allowed_students = models.IntegerField()

    def __str__(self):
        return str(self.subject_code + " - " + self.subject_name + " on " + str(self.test_date))


class Question(models.Model):
    question_credential = models.ForeignKey(
        QuestionCredendial, on_delete=models.CASCADE)
    question_number = models.IntegerField()
    question_co = models.IntegerField()
    question = RichTextUploadingField()
    option_one = RichTextUploadingField()
    option_two = RichTextUploadingField()
    option_three = RichTextUploadingField()
    option_four = RichTextUploadingField()
    option_one_answer = models.BooleanField(default=False)
    option_two_answer = models.BooleanField(default=False)
    option_three_answer = models.BooleanField(default=False)
    option_four_answer = models.BooleanField(default=False)

    def __str__(self):
        return str(self.question_credential.subject_code + " - " + self.question_credential.subject_name + " on " + str(self.question_credential.test_date) + " - " + str(self.question_number))


class Result(models.Model):
    rollnumber = models.ForeignKey(Credentials, on_delete=models.CASCADE)
    question_credential = models.ForeignKey(
        QuestionCredendial, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    total = models.IntegerField()
    co1_total = models.IntegerField()
    co2_total = models.IntegerField()
    co3_total = models.IntegerField()
    co4_total = models.IntegerField()
    co5_total = models.IntegerField()
    co6_total = models.IntegerField()
    co7_total = models.IntegerField()

    def __str__(self):
        return str(self.question_credential.subject_code + " - " + self.question_credential.subject_name + " by " + self.rollnumber.user.username)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Credentials.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.credentials.save()
