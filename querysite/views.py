from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
import requests
from .models import Query
from django.db.models import F


def home(request):
    return render(request, 'querysite/home.html')

def clear(request):  # 'Clear Database' navbar button

    messages.success(request, f'Database cleared!')
    Query.objects.all().delete()
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

    video_num = request.GET.get('video_num')
    codes = [0, 0, 0, 0]
    total_watches = 0

    if video_num:
        if Query.objects.filter(vid_num=video_num):  # if in database already
            Query.objects.filter(vid_num=video_num).update(
                count=F('count') + 1)
        else:
            Query.objects.create(vid_num=video_num, count=1)

    user_id = request.GET.get('user_id')

    if user_id:
        codes = []
        if Query.objects.filter(user_id=user_id):  # if in database already
            Query.objects.filter(user_id=user_id).update(
                count=F('count') + 1)
        else:
            Query.objects.create(user_id=user_id, count=1)

    data_file = open(path, 'r')
    allLines = data_file.readlines()
    all = []
    for line in allLines:
        all.append(line.split('|'))

    for line in all:
        if(line[6] == video_num and line[5] == user_id):    # both
            total_watches += 1
            time_vid = line[0][11: 19] + " | " + line[6]
            codes.append([time_vid, line[2][0: 4]])
        elif(not user_id and line[6] == video_num):         # just video
            total_watches += 1
            if(line[2] == '1.000000'):
                codes[0] += 1
            elif (line[2] == '1.250000'):
                codes[1] += 1
            elif (line[2] == '2.000000'):
                codes[2] += 1
            else:
                codes[3] += 1
        elif(not video_num and line[5] == user_id):         # just user
            total_watches += 1
            time_vid = line[0][11: 19] + " | " + line[6]
            codes.append([time_vid, line[2][0: 4]])

    if video_num and not user_id and total_watches != 0:
        codes = [['1.00', codes[0]], ['1.25', codes[1]],
                 ['2.00', codes[2]], ['Other', codes[3]]]

    context = {
        'video_num': video_num,
        'codes': codes,
        'total_watches': total_watches,
        'user_id': user_id,
    }

    return render(request, 'querysite/responses.html', context)

    '''

    query = request.GET.get('query')

    codes = []
    for dictionary in all['term'][0]['subjects']:
        if (dictionary['code'] == query):
            for course in dictionary['courses']:
                codes.append(
                    query + ' ' + course['catalog_number'] + ' ' + course['title'])
        # codes.append(dictionary['subjects'][0]['code'] + ' ' + dictionary['subjects'][0]
        #   ['courses'][0]['catalog_number'])

    context = {
        'codes': codes,
        'number': len(all['term'][0]['subjects']),
    }

    return render(request, 'querysite/responses.html', context)


all = []


def get_OIT(url):
    r = requests.get(url)
    if r.status_code != 200:
        return ["bad json"]
    return r.json()


def main():
    global all
    # Read OIT feed before starting the server.
    oit = 'http://etcweb.princeton.edu/webfeeds/courseofferings/?fmt=json&term=current&subject=all'
    all = get_OIT(oit)


main()

'''
