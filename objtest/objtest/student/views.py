from django.shortcuts import render, redirect
from staff.models import QuestionCredendial, Question, Result, Credentials
from django.views.decorators.csrf import csrf_exempt

from datetime import date, datetime, timedelta
import json
from random import shuffle

@csrf_exempt
def student_test(request):
    if request.method == "POST" and request.POST.get("finishTest"):
        answers_marked = request.session.get("answers_marked")
        question_credential = QuestionCredendial.objects.get(pk = int(request.session.get("question_credential_pk")))
        all_questions_pk = request.session.get("all_questions_pk")

        total = 0
        co1_total = 0
        co2_total = 0
        co3_total = 0
        co4_total = 0
        co5_total = 0
        co6_total = 0
        co7_total = 0

        for idx, question_pk in enumerate(all_questions_pk):
            question = Question.objects.get(pk = question_pk)
            if question.option_one_answer:
                answer = 1
            elif question.option_two_answer:
                answer = 2
            elif question.option_three_answer:
                answer = 3
            else:
                answer = 4
            if answer == answers_marked[idx]:
                total += 1
                if question.question_co == 1:
                    co1_total += 1
                elif question.question_co == 2:
                    co2_total += 1
                elif question.question_co == 3:
                    co3_total += 1
                elif question.question_co == 4:
                    co4_total += 1
                elif question.question_co == 5:
                    co5_total += 1
                elif question.question_co == 6:
                    co6_total += 1
                else:
                    co7_total += 1
        end_time = datetime.now().time()
        start_time = datetime.strptime(request.session.get("start_time"), "%H:%M:%S").time()
        rollnumber = Credentials.objects.get(user = request.user)
        result = Result()
        result.rollnumber = rollnumber
        result.question_credential = question_credential
        result.start_time = start_time
        result.end_time = end_time
        result.total = total
        result.co1_total = co1_total
        result.co2_total = co2_total
        result.co3_total = co3_total
        result.co4_total = co4_total
        result.co5_total = co5_total
        result.co6_total = co6_total
        result.co7_total = co7_total
        result.save()
        # To give a toast on completion
        request.session["completed_successfully"] = True
        return redirect('student_dashboard')

    if request.method == "POST" and request.POST.get("previous"):
        request.session["question_counter"] = int(request.session.get("question_counter")) - 1
        if int(request.session.get("question_counter")) == -1:
            request.session["question_counter"] = int(QuestionCredendial.objects.get(pk = int(request.session.get("question_credential_pk"))).total_questions) - 1
    
    if request.method == "POST" and request.POST.get("next"):
        request.session["question_counter"] = int(request.session.get("question_counter")) + 1
        if int(request.session.get("question_counter")) == int(QuestionCredendial.objects.get(pk = int(request.session.get("question_credential_pk"))).total_questions):
            request.session["question_counter"] = 0
    
    if request.method == "POST" and request.POST.get("go_to_page"):
        go_to_page = int(request.POST.get("go_to_page"))
        request.session["question_counter"] = go_to_page - 1
    
    if request.method == "POST" and request.POST.get("mark_this_page"):
        temp = request.session.get("questions_marked")
        if int(request.session.get("question_counter")) in temp:
            temp.remove(int(request.session.get("question_counter")))
        else:
            temp.append(int(request.session.get("question_counter")))
        request.session["questions_marked"] = temp

    if request.method == "POST" and request.POST.get("save_response"):
        option = int(request.POST.get("option"))
        answers_marked = request.session.get("answers_marked")
        answers_marked[int(request.session.get("question_counter"))] = option
        request.session["answers_marked"] = answers_marked

    all_questions_pk = request.session.get("all_questions_pk")
    question_counter = int(request.session.get("question_counter"))
    question_credential_pk = request.session.get("question_credential_pk")
    questions_marked = request.session.get("questions_marked")
    answers_marked = request.session.get("answers_marked")

    current_question = Question.objects.get(pk = all_questions_pk[question_counter])
    question_credential = QuestionCredendial.objects.get(pk = question_credential_pk)
    constraint_time = request.session.get("constraint_time")
    constraint_hour = constraint_time[0:2]
    constraint_minute = constraint_time[3:5]
    constraint_second = constraint_time[6:8]

    return render(request, 'student/studentTest.html', {
        "subject_code": question_credential.subject_code,
        "subject_name": question_credential.subject_name,
        "total_questions": question_credential.total_questions,
        "questions_marked": questions_marked,
        "test_date": question_credential.test_date,
        "start_time": question_credential.start_time,
        "end_time": question_credential.end_time,
        "question_counter": question_counter,
        "question_number": question_counter + 1,
        "question": current_question.question,
        "option_one": current_question.option_one,
        "option_two": current_question.option_two,
        "option_three": current_question.option_three,
        "option_four": current_question.option_four,
        "answers_marked": answers_marked,
        "answers_marked_count": len(answers_marked) - answers_marked.count(0),
        "constraint_time": constraint_time,
        "constraint_hour": constraint_hour,
        "constraint_minute": constraint_minute,
        "constraint_second": constraint_second,
    })


def student_dashboard(request):
    # Enter into the questions answering zone
    if request.method == "POST" and request.POST.get("attemptQuestionPaper"):
        question_credential = QuestionCredendial.objects.get(
            pk=int(request.POST.get("question_credential_pk")))
        all_questions_queryset = Question.objects.filter(
            question_credential=question_credential).order_by('question_number')
        all_questions_pk = []
        for queryset in all_questions_queryset:
            all_questions_pk.append(queryset.pk)
        shuffle(all_questions_pk)
        request.session["all_questions_pk"] = all_questions_pk
        request.session["question_credential_pk"] = question_credential.pk
        request.session["question_counter"] = 0
        request.session["questions_marked"] = []
        request.session["answers_marked"] = [0] * int(QuestionCredendial.objects.get(pk = int(request.session.get("question_credential_pk"))).total_questions)
        now = datetime.now()
        request.session["start_time"] = now.time().strftime("%H:%M:%S")
        # after = now + timedelta(minutes = int(1) )   
        after = now + timedelta(minutes = int(question_credential.duration_in_minutes))        
        request.session["constraint_time"] = after.time().strftime("%H:%M:%S")

        students_allowed = json.decoder.JSONDecoder().decode(question_credential.students_allowed)
        students_allowed.remove(int(request.user.username))
        question_credential.students_allowed = json.dumps(students_allowed)
        question_credential.save()
        return redirect('student_test')

    current_question_papers = []
    allocated_question_papers = []
    question_papers = []
    username = request.user.username

    question_credentials = QuestionCredendial.objects.all()
    for question_credential in question_credentials:
        students_allowed = json.decoder.JSONDecoder().decode(
            question_credential.students_allowed)
        if int(username) in students_allowed and int(question_credential.total_questions) == int(question_credential.questions_added):
            question_papers.append(question_credential)
    current_date, current_time = date.today(), datetime.now().time()
    for question_credential in question_papers:
        if current_date == datetime.strptime(str(question_credential.test_date), '%Y-%m-%d').date() and datetime.strptime(str(question_credential.start_time), "%H:%M:%S").time() <= current_time <= datetime.strptime(str(question_credential.end_time), "%H:%M:%S").time():
            current_question_papers.append(question_credential)
        else:
            allocated_question_papers.append(question_credential)
    if request.session.get("completed_successfully"):
        completed_successfully = True
        request.session["completed_successfully"] = False
    else:
        completed_successfully = False
    return render(request, "student/studentDashboard.html", {
        "username": username,
        "question_papers": question_papers,
        "current_question_papers": current_question_papers,
        "allocated_question_papers": allocated_question_papers,
        "question_papers_length": len(question_papers),
        "current_question_papers_length": len(current_question_papers),
        "allocated_question_papers_length": len(allocated_question_papers),
        "completed_successfully": completed_successfully
    })
