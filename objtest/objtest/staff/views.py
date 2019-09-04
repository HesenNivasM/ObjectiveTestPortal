from django.shortcuts import render, redirect
from .models import Credentials

from django.contrib.auth.models import User
from .models import Credentials, QuestionCredendial, Question, Result
from .forms import QuestionForm

import json

def staff_results(request):
    result_question_credential_pk = request.session.get("result_question_credential_pk")
    question_credential = QuestionCredendial.objects.get(pk = result_question_credential_pk)
    results = Result.objects.filter(question_credential = question_credential).order_by('rollnumber')
    # Check if repetition is not found
    temp_for_rollnumbers = []
    refined_results = []
    for result in results:
        if int(result.rollnumber.user.username) not in temp_for_rollnumbers:
            temp_for_rollnumbers.append(int(result.rollnumber.user.username))
            refined_results.append(result)        
    max_total = 0
    max_co1 = 0
    max_co2 = 0
    max_co3 = 0
    max_co4 = 0
    max_co5 = 0
    max_co6 = 0
    max_co7 = 0
    questions = Question.objects.filter(question_credential = question_credential)
    for question in questions:
        max_total += 1
        if int(question.question_co) == 1:
            max_co1+= 1
        elif int(question.question_co) == 2:
            max_co2+= 1
        elif int(question.question_co) == 3:
            max_co3+= 1
        elif int(question.question_co) == 4:
            max_co4+= 1
        elif int(question.question_co) == 5:
            max_co5+= 1
        elif int(question.question_co) == 6:
            max_co6+= 1
        elif int(question.question_co) == 7:
            max_co7+= 1
    print(max_total, max_co1, max_co2, max_co3, max_co4, max_co5, max_co6, max_co7)
    return render(request, 'staff/staffResults.html', {
        "result_question_credential_pk": result_question_credential_pk,
        "question_credential": question_credential,
        "results": refined_results,
        "max_total": max_total,
        "max_co1": max_co1,
        "max_co2": max_co2,
        "max_co3": max_co3,
        "max_co4": max_co4,
        "max_co5": max_co5,
        "max_co6": max_co6,
        "max_co7": max_co7
    })
                                                    
def staff_dashboard(request):                                                               
    # Receive the pk of the question_credential and redirect with the results
    if request.method == "POST" and request.POST.get("select_result_credential"):
        result_question_credential_pk = request.POST.get("result_credential")
        request.session["result_question_credential_pk"] = result_question_credential_pk
        return redirect('staff_results')

    # To create new roll numbers with modifications in User and Credentials models
    if request.method == "POST" and request.POST.get("addStudentsRollNumbers"):
        toast = "User created successfully!"
        if request.POST.get("singleInput"):
            rollnumber = request.POST.get("singleInput")
            try:
                user = User.objects.get(username=str(rollnumber))
                toast = "User already exists"
            except:
                user = User.objects.create_user(
                    username=str(rollnumber), password="srec@123")
        else:
            start_rollnumber = request.POST.get("multipleInputStart")
            end_rollnumber = request.POST.get("multipleInputEnd")
            for loop in range(int(start_rollnumber), int(end_rollnumber) + 1):
                try:
                    user = User.objects.get(username=str(loop))
                    toast = "Some users already exists"
                except:
                    user = User.objects.create_user(
                        username=str(loop), password="srec@123")
        return render(request, 'staff/staffDashboard.html', {"toast": toast})
    # To clear or block students from attending the test by modifying the Credentials model
    # if request.method == "POST" and request.POST.get("clearStudentsRollNumbers"):
        choice = False if request.POST.get(
            "choiceOfCategory") == "clear" else True
        toast = "Action performed successfully"
        if request.POST.get("singleClearInput"):
            rollnumber = request.POST.get("singleClearInput")
            try:
                user = User.objects.get(username=str(rollnumber))
                credential = Credentials.objects.get(user=user)
                credential.attended = choice
                credential.save()
            except:
                toast = "User doesn't exist"
        else:
            start_rollnumber = request.POST.get("multipleClearInputStart")
            end_rollnumber = request.POST.get("multipleClearInputEnd")
            for loop in range(int(start_rollnumber), int(end_rollnumber) + 1):
                try:
                    user = User.objects.get(username=str(loop))
                    credential = Credentials.objects.get(user=user)
                    credential.attended = choice
                    credential.save()
                except:
                    toast = "Some users doesn't exist"
        return render(request, 'staff/staffDashboard.html', {"toast": toast})
    # Add the credential data about the new test that is being assigned
    if request.method == "POST" and request.POST.get("addCredentials"):
        credential = QuestionCredendial()
        staff_id = str(request.user.username)
        subject_code = str(request.POST.get("subjectCode"))
        subject_name = str(request.POST.get("subjectName"))
        total_questions = request.POST.get("noOfQuestions")
        credential.staff_id = staff_id
        credential.subject_code = subject_code
        credential.subject_name = subject_name
        credential.total_questions = total_questions
        credential.test_date = request.POST.get("testDate")
        credential.start_time = request.POST.get("startTime")
        credential.end_time = request.POST.get("endTime")
        credential.duration_in_minutes = request.POST.get("duration")
        assignedRollnumbers = str(request.POST.get("assignedRollnumbers"))
        rollnumbers_list = []
        rollnumbers = assignedRollnumbers.split(",")
        for rollnumber in rollnumbers:
            if "-" in str(rollnumber):
                start_rollnumber, end_rollnumber = list(map(int, rollnumber.split("-")))
                for i in range(start_rollnumber, end_rollnumber + 1):
                    rollnumbers_list.append(i)
            else:
                rollnumbers_list.append(int(rollnumber))
        credential.students_allowed = json.dumps(rollnumbers_list)
        credential.total_allowed_students = len(rollnumbers_list)
        credential.save()
        question_credential = QuestionCredendial.objects.get(staff_id = staff_id, subject_code = subject_code, test_date = request.POST.get("testDate"), students_allowed = json.dumps(rollnumbers_list))
        request.session["question_credential_pk"] = int(question_credential.pk)
        request.session["staff_id"] = staff_id
        request.session["subject_code"] = subject_code
        request.session["subject_name"] = subject_name
        request.session["total_questions"] = total_questions
        request.session["add_questions"] = True
        request.session["current_question_number"] = 1
        return redirect('staff_questions')
    # Modify the time allocated for the question credential
    if request.method == "POST" and request.POST.get("modifyTime"):
        question_credential = QuestionCredendial.objects.get(pk = int(request.POST.get("hiddenField")))
        question_credential.start_time = request.POST.get("startTime")
        question_credential.end_time = request.POST.get("endTime")
        question_credential.test_date = request.POST.get("testDate")
        question_credential.save()
        return render(request, 'staff/modifyAllowedStudents.html', {
            "question_credential": question_credential,
        })
    # Modify the allowed allowed student credential
    if request.method == "POST" and request.POST.get("modifyStudents"):
        question_credential = QuestionCredendial.objects.get(pk = int(request.POST.get("hiddenField")))
        students_allowed = json.decoder.JSONDecoder().decode(question_credential.students_allowed)
        if request.POST.get("removeStudents"):
            remove_students = []
            rollnumbers = str(request.POST.get("removeStudents")).split(",")
            for rollnumber in rollnumbers:
                if "-" in rollnumber:
                    start_rollnumber, end_rollnumber = list(map(int, rollnumber.split("-")))
                    for i in range(start_rollnumber, end_rollnumber + 1):
                        remove_students.append(i)
                else:
                    remove_students.append(int(rollnumber))
            for student in remove_students:
                if student in students_allowed:
                    students_allowed.remove(student)
        if request.POST.get("appendStudents"):
            append_students = []
            rollnumbers = str(request.POST.get("appendStudents")).split(",")
            for rollnumber in rollnumbers:
                if "-" in rollnumber:
                    start_rollnumber, end_rollnumber = list(map(int, rollnumber.split("-")))
                    for i in range(start_rollnumber, end_rollnumber + 1):
                        append_students.append(i)
                else:
                    append_students.append(int(rollnumber))
            for student in append_students:
                if student not in students_allowed:
                    students_allowed.append(student)
        question_credential.students_allowed = json.dumps(students_allowed)
        question_credential.total_allowed_students = len(students_allowed)
        question_credential.save()
        return render(request, 'staff/modifyAllowedStudents.html', {
            "question_credential": question_credential,
        })
    # Redirect to the Modify the allowed student credential from the dashboard table
    if request.method == "POST" and request.POST.get("modifyAllowedStudents"):
        question_credential = QuestionCredendial.objects.get(pk = int(request.POST.get("changeAllowedStudents")))
        return render(request, 'staff/modifyAllowedStudents.html', {
            "question_credential": question_credential,
        })
    # Complete the incomplete questions from the dashboard table
    if request.method == "POST" and request.POST.get("completeQuestions"):
        question_credential = QuestionCredendial.objects.get(pk = int(request.POST.get("questionCredential")))
        request.session["question_credential_pk"] = int(question_credential.pk)
        request.session["staff_id"] = question_credential.staff_id
        request.session["subject_code"] = question_credential.subject_code
        request.session["subject_name"] = question_credential.subject_name
        request.session["total_questions"] = question_credential.total_questions
        request.session["add_questions"] = True
        request.session["current_question_number"] = question_credential.questions_added + 1
        return redirect('staff_questions')
    # View the questions entered
    if request.method == "POST" and request.POST.get("clickViewQuestions"):
        question_credential = QuestionCredendial.objects.get(pk = int(request.POST.get("viewQuestions")))
        # Remember the pk of the quesiton credential for edit
        request.session["question_credential_pk"] = int(request.POST.get("viewQuestions"))
        questions = Question.objects.filter(question_credential = question_credential)
        subject_code = question_credential.subject_code
        subject_name = question_credential.subject_name
        return render(request, "staff/viewQuestions.html", {
            "questions" : questions,
            "subject_code" : subject_code,
            "subject_name" : subject_name,
        })
    # Return data for dashboard
    staff_question_credentials = QuestionCredendial.objects.filter(staff_id = str(request.user.username))
    incomplete_question_credentials = []
    complete_question_credentials = []
    for staff_question_credential in staff_question_credentials:
        if staff_question_credential.questions_added < staff_question_credential.total_questions:
            incomplete_question_credentials.append(staff_question_credential)
        else:
            complete_question_credentials.append(staff_question_credential)
    if request.session.get("questions_completed"):
        toast = "Questions Added Successfully"
        request.session["questions_completed"] = False
    else:
        toast = None
    credential_with_results = []
    for staff_question_credential in staff_question_credentials:
        temp = Result.objects.filter(question_credential = staff_question_credential)
        if len(temp) > 0:
            credential_with_results.append(staff_question_credential)
    return render(request, 'staff/staffDashboard.html', {
        "incomplete_question_credentials": incomplete_question_credentials,
        "complete_question_credentials": complete_question_credentials,
        "incomplete_question_credentials_length": len(incomplete_question_credentials),
        "complete_question_credentials_length": len(complete_question_credentials),
        "question_credentials_length": len(incomplete_question_credentials) + len(complete_question_credentials),
        "toast": toast,
        "credential_with_results": credential_with_results
    })


def staff_questions(request):
    questions_completed = False
    if request.method == "POST" and request.POST.get("submitQuestion"):
        question = request.POST.get("question")
        option_one = request.POST.get("option_one")
        option_two = request.POST.get("option_two")
        option_three = request.POST.get("option_three")
        option_four = request.POST.get("option_four")
        question_co = request.POST.get("question_co")
        answer = request.POST.get("answer")
        current_question_number = request.session.get("current_question_number")
        question_data = Question()
        question_data.question_credential = QuestionCredendial.objects.get(pk = int(request.session.get("question_credential_pk")))
        question_data.question_number = current_question_number
        question_data.question_co = question_co
        question_data.question = question
        question_data.option_one = option_one
        question_data.option_two = option_two
        question_data.option_three = option_three
        question_data.option_four = option_four
        if int(answer) == 1:
            question_data.option_one_answer = True
        if int(answer) == 2:
            question_data.option_two_answer = True
        if int(answer) == 3:
            question_data.option_three_answer = True
        if int(answer) == 4:
            question_data.option_four_answer = True
        question_data.save()
        request.session["current_question_number"] = int(current_question_number) + 1
        curr_question_credential = QuestionCredendial.objects.get(pk = int(request.session.get("question_credential_pk")))
        curr_question_credential.questions_added += 1
        curr_question_credential.save()
        if int(current_question_number) + 1 > int(request.session.get("total_questions")):
            questions_completed = True
            request.session["questions_completed"] = True
            return redirect('staff_dashboard')
        # print(question,option_one,option_two,option_three,option_four,question_co,answer)
    if request.session.get("add_questions") and not questions_completed:
        current_question_number = request.session.get("current_question_number")
        staff_id = request.session.get("staff_id")
        subject_code = request.session.get("subject_code")
        subject_name = request.session.get("subject_name")
        total_questions = request.session.get("total_questions")
        question_form = QuestionForm()
        return render(request, 'staff/addQuestions.html', {
            "staff_id" : staff_id,
            "subject_code" : subject_code,
            "subject_name" : subject_name,
            "total_questions" : total_questions,
            "question_form": question_form,
            "current_question_number": current_question_number,
        })
    return render(request, 'staff/staffDashboard.html', {
        "toast": "Questions Added Successfully"
    })

# Help Edit the questions
def staff_edit(request, id):
    question_credential = QuestionCredendial.objects.get(pk = int(request.session.get("question_credential_pk")))
    question = Question.objects.get(question_credential = question_credential, question_number = id)    
    form = QuestionForm(request.POST or None, instance = question)
    if form.is_valid():
        form.save()
        return redirect("staff_dashboard")
    return render(request, "staff/editQuestions.html", {
        "staff_id" : request.session.get("staff_id"),
        "subject_code" : request.session.get("subject_code"),
        "subject_name" : request.session.get("subject_name"),        
        "question_form": form,
        "current_question_number": id,
    })