from django.forms import ModelForm
from .models import Question


class QuestionForm(ModelForm):
    class Meta:
        model = Question
        fields = ['question', 'option_one', 'option_two',
                  'option_three', 'option_four']
