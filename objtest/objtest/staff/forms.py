from django.forms import ModelForm
from .models import Question


class QuestionForm(ModelForm):
    class Meta:
        model = Question
        fields = ['question', 'option_one', 'option_two',
                  'option_three', 'option_four', 'question_co', 'option_one_answer', 'option_two_answer', 'option_three_answer', 'option_four_answer']
