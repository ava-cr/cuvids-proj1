from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
import requests
from .models import Query, WatchData
from django.db.models import F
import fetch
from django_globals import globals

def home(request):

    context = {
        'users': fetch.get_users(),
        'vids': fetch.get_vids(),
    }

    return render(request, 'querysite/home.html', context)

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


def responses(request):

    # query = 'hi'

    path = '/Users/avacrnkovic-rubsamen/Documents/cuvidscos333/watches.txt'

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

    # user_id = request.GET.get('user_id')
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
            #total_watches += 1
            #time_vid = line[0][11: 19] + " | " + video
            #codes.append([time_vid, speed[0: 4]])
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
