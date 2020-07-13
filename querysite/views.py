from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
import requests
from datetime import datetime
import re
import fetch
from .models import Query, WatchData, QuestionData
from django.db.models import F
from django.http import HttpResponse
import csv

def home(request):

    context = {
        'users': fetch.get_users(),
        'vids': fetch.get_vids(),
    }

    return render(request, 'querysite/home.html', context)


def redash(request):
    return render(request, 'querysite/redash.html')

def clear(request):  # 'Clear Database' navbar button

    messages.success(request, f'Database cleared!')
    Query.objects.all().delete()
    # WatchData.objects.all().delete()
    return redirect('querysite-home')


def count(request):  # 'Query Count' navbar button

    query_data = []

    for query in Query.objects.all():
        query_data.append(query)

    context = {
        'query_data': query_data
    }

    return render(request, 'querysite/count.html', context)

# https://app.redash.io/ava-crnkovic/public/dashboards/WfFFHHuiLXVfhhwG6rL2PsdazRkQ24SJ0ZeK6C6E

def generate_csv(request):

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="report_table.csv"'
    writer = csv.writer(response)

    # determine type of report
    csv_type = request.GET['dropdown_report']

    # column headers
    if csv_type == 'user':
        writer.writerow(['Student Emails',
                         'Total Time', 'Video Ids'])
    elif csv_type == 'video':
        writer.writerow(['Video Id', 'Total Time',
                         'Student Emails'])
    elif csv_type == 'user_video':
        last_vid = fetch.get_vids()[-1]
        header = ['']
        for i in range(1, last_vid + 1):
            header.append(i)
        writer.writerow(header)
    else:
        header = ['User Ids']
        for i in range(1, 95):
            header.append(i)
        writer.writerow(header)

    # get date and email info
    emaildomain = request.GET['emaildomain']
    reg = re.compile(rf'.{emaildomain}')
    sdate = request.GET['startdate']
    edate = request.GET['enddate']

    if 'emailbool' in request.GET and 'datebool' in request.GET:    # filter by email & date
        start = datetime.strptime(sdate, "%m/%d/%Y")
        end = datetime.strptime(edate, "%m/%d/%Y")

        if csv_type == 'user':
            for user in fetch.get_users():
                watches = WatchData.objects.all().filter(user_id=user)
                email = watches.first().email
                if reg.search(email):
                    count = 0
                    for watch in watches:
                        date = datetime.strptime(watch.date, "%Y-%m-%d")
                        if date >= start and date <= end:
                            count += 1
                    writer.writerow([user, email, (count / 360),
                                     fetch.get_vids_for_user(user)])

        elif csv_type == 'video':
            for video in fetch.get_vids():
                watches = WatchData.objects.all().filter(vid_num=video)
                emails = []
                count = 0
                for watch in watches:
                    date = datetime.strptime(watch.date, "%Y-%m-%d")
                    if reg.search(watch.email) and date >= start and date <= end:
                        emails.append(watch.email)
                        count += 1
                if count != 0:
                    writer.writerow([video, (count / 360), set(emails)])

        else:
            print(f'else with both filters!')

    # filter by email only
    elif 'emailbool' in request.GET:

        if csv_type == 'user':
            print(f'here')
            for user in fetch.get_users():
                objects = WatchData.objects.all().filter(user_id=user)
                email = objects.first().email
                if not email:
                    email = objects.first().username
                count = len(objects)
                if reg.search(email):
                    writer.writerow([email, (count / 360),
                                     fetch.get_vids_for_user(user)])
        elif csv_type == 'video':
            for video in fetch.get_vids():
                watches = WatchData.objects.all().filter(vid_num=video)
                emails = []
                count = 0
                for watch in watches:
                    email = watch.email
                    if not email:
                        email = watch.username
                    if reg.search(email):
                        emails.append(email)
                        count += 1
                if count != 0:
                    writer.writerow([video, (count / 360), set(emails)])
        elif csv_type == 'user_video':
            print(f'else in just email')

        else:
            question_count = 95
            user_count = len(fetch.get_users_qdata()) + 1
            print(
                f'construct matrix size { question_count } by { user_count }')
            matrix = [[0 for col in range(question_count)]
                      for row in range(user_count)]
            print(f'done with matrix')

            row = 1
            for user in fetch.get_users_qdata():
                print(f'USER {user}!!!')
                # watches = WatchData.objects.all().filter(user_id=user)
                email = QuestionData.objects.all().filter(
                    user_id=user).first().email
                if not email:
                    email = QuestionData.objects.all().filter(
                        user_id=user).first().username
                if reg.search(email):
                    matrix[row][0] = email
                else:
                    continue
                for question in fetch.get_incorrect_for_user(user):
                    print(f'question {question}')
                    if question < 95:
                        matrix[row][question] = '-1'
                for question in fetch.get_correct_for_user(user):
                    print(f'question {question}')
                    if question < 95:
                        matrix[row][question] = '1'
                row += 1

            writer.writerows(matrix)

    # filter by date only
    elif 'datebool' in request.GET:
        start = datetime.strptime(sdate, "%m/%d/%Y")
        end = datetime.strptime(edate, "%m/%d/%Y")
        if csv_type == 'user':
            for user in fetch.get_users():
                watches = WatchData.objects.all().filter(user_id=user)
                count = 0
                for watch in watches:
                    date = datetime.strptime(watch.date, "%Y-%m-%d")
                    if date >= start and date <= end:
                        count += 1
                if count != 0:
                    writer.writerow([user, watches.first().email, count / 360,
                                     fetch.get_vids_for_user(user)])
        elif csv_type == 'video':
            for video in fetch.get_vids():
                watches = WatchData.objects.all().filter(vid_num=video)
                emails = []
                count = 0
                for watch in watches:
                    date = datetime.strptime(watch.date, "%Y-%m-%d")
                    if date >= start and date <= end:
                        emails.append(watch.email)
                        count += 1
                if count != 0:
                    writer.writerow(
                        [video, (count / 360), set(emails), fetch.get_users_for_vid(video)])
        else:
            print(f'else in just date')

    # no filter
    else:
        if csv_type == 'user':
            for user in fetch.get_users():
                objects = WatchData.objects.all().filter(user_id=user)
                writer.writerow([user, objects.first().email,
                                 len(objects) / 360, fetch.get_vids_for_user(user)])
        elif csv_type == 'video':
            for video in fetch.get_vids():
                emails = WatchData.objects.all().filter(
                    vid_num=video).values_list('email', flat=True)
            writer.writerow([video, (len(emails) / 360),
                             set(emails), fetch.get_users_for_vid(video)])
        elif csv_type == 'user_video':
            vid_count = fetch.get_vids()[-1] + 1
            user_count = len(fetch.get_users()) + 1
            print(f'construct matrix size { vid_count} by {user_count}')
            matrix = [[0 for col in range(vid_count)]
                      for row in range(user_count)]
            print(f'done with matrix')

            row = 1
            for user in fetch.get_users():
                print(f'USER {user}!!!')
                # watches = WatchData.objects.all().filter(user_id=user)
                matrix[row][0] = user
                for video in fetch.get_vids_for_user(user):
                    print(f'video {video}')
                    count = WatchData.objects.all().filter(user_id=user).filter(
                        vid_num=video).count() / 360
                    matrix[row][video] = count
                row += 1

            writer.writerows(matrix)

        else:
            question_count = 95
            user_count = len(fetch.get_users_qdata()) + 1
            print(
                f'construct matrix size { question_count } by { user_count }')
            matrix = [[0 for col in range(question_count)]
                      for row in range(user_count)]
            print(f'done with matrix')

            row = 1
            for user in fetch.get_users_qdata():
                print(f'USER {user}!!!')
                # watches = WatchData.objects.all().filter(user_id=user)
                email = QuestionData.objects.all().filter(
                    user_id=user).first().email
                if not email:
                    email = QuestionData.objects.all().filter(
                        user_id=user).first().username
                matrix[row][0] = email
                for question in fetch.get_correct_for_user(user):
                    print(f'question {question}')
                    if question < 95:
                        matrix[row][question] = '1'
                for question in fetch.get_incorrect_for_user(user):
                    print(f'question {question}')
                    if question < 95:
                        matrix[row][question] = '-1'
                row += 1

            writer.writerows(matrix)

    return response


def responses(request):

    # video_num = request.GET.get('video_num')
    video_num = request.GET['dropdown_vid']
    codes = [0, 0, 0, 0, 0]
    total_watches = 0

    # updating query counts
    if video_num:
        if Query.objects.filter(vid_num=video_num):         # if in database already
            Query.objects.filter(vid_num=video_num).update(
                count=F('count') + 1)
        else:
            Query.objects.create(vid_num=video_num, count=1)

    user_id = request.GET['dropdown_user']

    if user_id:
        codes = []
        if Query.objects.filter(user_id=user_id):           # if in database already
            Query.objects.filter(user_id=user_id).update(
                count=F('count') + 1)
        else:
            Query.objects.create(user_id=user_id, count=1)

    if(video_num and user_id):  # both - adding
        for obj in WatchData.objects.filter(user_id=user_id).filter(vid_num=video_num):
            total_watches += 1

        # check that the vid_num exists for that user
        img_path = fetch.get_watch_patten_graph(user_id, video_num)
        context = {
            'img_path': img_path,
            'user_id': user_id,
            'video_num': video_num,
            'total_watches': total_watches,
        }
        if not img_path:
            messages.warning(
                request, f"Invalid user id and video combination!")
            return redirect('querysite-home')

        # display the graph
        # messages.success(
            # request, f"User and video found! Displaying watch pattern graph...")
        return render(request, 'querysite/responses.html', context)

        # time_vid = f'{obj.time} | {video_num}'
        # codes.append([time_vid, obj.speed])
    elif(not user_id):
        for obj in WatchData.objects.filter(vid_num=video_num):
            speed = obj.speed
            total_watches += 1
            if(speed == 1.000000):
                codes[0] += 1
            elif (speed == 1.250000):
                codes[1] += 1
            elif (speed == 1.500000):
                codes[2] += 1
            elif (speed == 1.750000):
                codes[3] += 1
            else:
                codes[4] += 1

    else:
        for obj in WatchData.objects.filter(user_id=user_id):
            total_watches += 1
            time_vid = f'{obj.time} | {obj.vid_num}'
            codes.append([time_vid, obj.speed])

    '''
    data_file = open(path, 'r')
    allLines = data_file.readlines()
    all = []
    if(all == []):
        for line in allLines:
            all.append(line.split('|'))

    for line in all:
        video = line[6]
        user = line[5]
        speed = line[2]
        if(video == video_num and user == user_id):    # both
            # total_watches += 1
            # time_vid = line[0][11: 19] + " | " + video
            # codes.append([time_vid, speed[0: 4]])
        elif(not user_id and video == video_num):         # just video
            total_watches += 1
            if(speed == '1.000000'):
                codes[0] += 1
            elif (speed == '1.250000'):
                codes[1] += 1
            elif (speed == '1.500000'):
                codes[2] += 1
            elif (speed == '1.7500000'):
                codes[3] += 1
            else:
                codes[4] += 1
        elif(not video_num and user == user_id):         # just user
            total_watches += 1
            time_vid = line[0][11: 19] + " | " + video
            codes.append([time_vid, speed[0: 4]])
    '''
    if video_num and not user_id and total_watches != 0:
        codes = [['1.0x ', codes[0]], ['1.25x', codes[1]],
                 ['1.50x', codes[2]], ['1.75x', codes[3]],
                 ['2.0x ', codes[4]]]
    ''''
    context = {
        'video_num': video_num,
        'codes': codes,
        'total_watches': total_watches,
        'user_id': user_id,
        'user_choice': user_choice
    }
    '''
    context = {
        'video_num': video_num,
        'codes': codes,
        'total_watches': total_watches,
        'user_id': user_id,
    }

    return render(request, 'querysite/responses.html', context)
