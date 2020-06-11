# load the data into a database
# (for now, will clear and readd all the data)
import os
from django_globals import globals
from querysite.models import WatchData

# the Agg needs to be used to prevent 'outside main thread error' with the 'get_watch_patten_graph()' function
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import datetime

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# where static files stored
STATIC_DIR = os.path.join(BASE_DIR, 'cuvidscos333/querysite/static/')


path = '/Users/avacrnkovic-rubsamen/Documents/cuvidscos333/real_watches.txt'
boolean_path = '/Users/avacrnkovic-rubsamen/Documents/cuvidscos333/boolean.txt'
boolean_file = open(boolean_path, 'r')

# cache the unique users and videos for quicker performance
users = []
videos = []

if boolean_file.readlines():

    print(f'resetting database')

    WatchData.objects.all().delete()

    file = open(path, 'r')
    lines = file.readlines()
    data_objects = []
    redundant_users = []
    redundant_vids = []
    for line in lines:
        line_entries = line.split('|')
        date = line_entries[0][0:10]
        time = line_entries[0][11: 26]
        timestamp = float(line_entries[1])
        speed = float(line_entries[2])
        user_id = int(line_entries[5])
        vid_num = int(line_entries[6])
        data_objects.append(WatchData(date=date,
                                      time=time,
                                      timestamp=timestamp,
                                      speed=speed, user_id=user_id,
                                      vid_num=vid_num))
        redundant_users.append(user_id)
        redundant_vids.append(vid_num)
    print('all objects created, saving to database')
    WatchData.objects.bulk_create(data_objects)
    print('objects saved, clearing the reload_file')
    boolean_file.close()
    boolean_file = open(boolean_path, 'w')
    boolean_file.write('')
    boolean_file.close()

    # store only unique users and videos
    users = list(set(redundant_users))
    videos = list(set(redundant_vids))

else:  # need to recache the unique users and videos upon a rerun of this script
    redundant_users = []
    redundant_vids = []
    print("getting all the objects from the database")
    all_watches = WatchData.objects.all()
    print(f'scanning through {len(all_watches)} objects in the database')
    for watch in all_watches:
        redundant_users.append(watch.user_id)
        redundant_vids.append(watch.vid_num)
    users = sorted(list(set(redundant_users)))
    videos = sorted(list(set(redundant_vids)))

# script finished, close up everything
boolean_file.close()
print('fetch.py was run again, boolean_file closed')


def get_users():
    return users


def get_vids():
    return videos


def get_vids_for_user(user_id):
    all_watches = WatchData.objects.all().filter(user_id=user_id)
    redundant_vid_nums = []
    for watch in all_watches:
        redundant_vid_nums.append(watch.vid_num)
    return list(set(redundant_vid_nums))


def get_objects_by_user_vid(user_id, vid_num):
    return WatchData.objects.all().filter(user_id=user_id, vid_num=vid_num)


# GRAPH CODE:
def get_watch_patten_graph(user_id, vid_num):
    gap_duration = 8  # watch is considered to be another session if gap exceeds this in seconds

    # color for speeds - red will be scaled by speed
    blue = 198 / 255.0
    green = 168 / 255.0
    alpha = 1
    max_speed = 1  # speed scaled relative to this - will be found below

    objs = WatchData.objects.all().filter(
        user_id=user_id, vid_num=vid_num).order_by('date', 'time')
    if len(objs) == 0:
        return None

    dates = []
    times = []
    timestamps = []
    speeds = []
    colors = []

    for obj in objs:
        dates.append(obj.date)
        times.append(obj.time)
        timestamps.append(obj.timestamp)
        speeds.append(obj.speed)

        if obj.speed > max_speed:
            max_speed = obj.speed

    rel_times = []
    avg_speeds = []
    avg_colors = []

    for i in range(len(dates)):
        rel_times.append(get_time_sec_difference(
            (dates[0], times[0]), (dates[i], times[i])))
        colors.append((speeds[i] / max_speed, green, blue, alpha))
    for i in range(len(dates) - 1):
        avg_speeds.append((speeds[i] + speeds[i + 1]) / 2.0)
        avg_colors.append((avg_speeds[i] / max_speed, green, blue, alpha))

    # plot the data
    plt.figure()
    plt.scatter(timestamps, rel_times, color=colors)
    # plt.title(f'Watch Pattern for Video: {vid_num} by User: {user_id}')
    plt.xlabel('Video Timestamp [sec]')
    plt.ylabel('Real-World Time [sec]')

    # create the color map and bar
    colordict = {
        'red': [(0, 0, 0, alpha), (1, 1, 1, alpha)],
        'green': [(0, green, green, alpha), (1, green, green, alpha)],
        'blue': [(0, blue, blue, alpha), (1, blue, blue, alpha)]
    }
    colormap = LinearSegmentedColormap('colormap', segmentdata=colordict)
    norm = matplotlib.colors.Normalize(vmin=0, vmax=max_speed)
    plt.colorbar(matplotlib.cm.ScalarMappable(
        norm=norm, cmap=matplotlib.cm.cool), label='Video Speed')

    # save the graph as a png
    GRAPH_PATH_REL_STATIC = f'images/{user_id}_{vid_num}.png'
    SAVE_GRAPH_DIR = os.path.join(STATIC_DIR, GRAPH_PATH_REL_STATIC)
    plt.savefig(SAVE_GRAPH_DIR)
    return GRAPH_PATH_REL_STATIC


# positive difference means time2 is in the future
# helper function to be used above
def get_time_sec_difference(datetime1, datetime2):
    date1, time1 = datetime1
    date2, time2 = datetime2

    # datetime(year, month, day, hour, minute, second)
    datetimeObj1 = datetime.datetime(int(date1[:4]), int(date1[5:7]), int(
        date1[8:10]), int(time1[:2]), int(time1[3:5]), int(time1[6:8]))
    datetimeObj2 = datetime.datetime(int(date2[:4]), int(date2[5:7]), int(
        date2[8:10]), int(time2[:2]), int(time2[3:5]), int(time2[6:8]))
    difference = datetimeObj2 - datetimeObj1
    return difference.total_seconds()
