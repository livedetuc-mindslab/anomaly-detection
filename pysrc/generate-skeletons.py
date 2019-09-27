# -*-coding: utf-8 -*-
import xml.etree.ElementTree as elemTree
from datetime import datetime
import datetime as dt
import json
import os
import uuid

# ## action labeling map
action_map = {}
# #공항
action_map['2-person'] = 1001
action_map['rush'] = 1011
action_map['reverse-dash'] = 1021
action_map['abandon'] = 1031

# #공공사업
# 폭행 assult
action_map['walking'] = 2011
action_map['running'] = 2021
action_map['standing'] = 2031
action_map['punching'] = 2041
action_map['kicking'] = 2051
action_map['pushing'] = 2061
action_map['throwing'] = 2071
action_map['falldown'] = 2081
action_map['threaten'] = 2091
action_map['piercing'] = 2101

## data rsc root setting
anomaly_data_root = os.getenv('ANOMALY_DATA_ROOT')
anomaly_skeleton_path = os.getenv('ANOMALY_SKELETON_PATH')
if anomaly_data_root is None:
    anomaly_data_root = os.getcwd()


# a -> b
def map_point(a, b):
    mapped_score.insert(b, score[a])
    mapped_pose.insert(2 * b, pose[2 * a])
    mapped_pose.insert(2 * b + 1, pose[2 * a + 1])


def map_point_sets():
    # 'nose',            # 1  ( 0) ==>  0
    map_point(0, 0)
    # 'neck',            #         ==>  1
    mapped_score.insert(1, 0)
    mapped_pose.insert(2, round((pose[10] + pose[12]) / 2, 1))
    mapped_pose.insert(3, round((pose[11] + pose[13]) / 2, 1))
    # 'right_shoulder',  # 7  ( 6) ==>  2
    map_point(6, 2)
    # 'right_elbow',     # 9  ( 8) ==>  3
    map_point(8, 3)
    # 'right_wrist',     # 11 (10) ==>  4
    map_point(10, 4)
    # 'left_shoulder',   # 6  ( 5) ==>  5
    map_point(5, 5)
    # 'left_elbow',      # 8  ( 7) ==>  6
    map_point(7, 6)
    # 'left_wrist',      # 10 ( 9) ==>  7
    map_point(9, 7)
    # 'right_hip',       # 13 (12) ==>  8
    map_point(12, 8)
    # 'right_knee',      # 15 (14) ==>  9
    map_point(14, 9)
    # 'right_ankle',     # 17 (16) ==> 10
    map_point(16, 10)
    # 'left_hip',        # 12 (11) ==> 11
    map_point(11, 11)
    # 'left_knee',       # 14 (13) ==> 12
    map_point(13, 12)
    # 'left_ankle',      # 16 (15) ==> 13
    map_point(15, 13)
    # 'right_eye',       # 3  ( 2) ==> 14
    map_point(2, 14)
    # 'left_eye',        # 2  ( 1) ==> 15
    map_point(1, 15)
    # 'right_ear',       # 5  ( 4) ==> 16
    map_point(4, 16)
    # 'left_ear',        # 4  ( 3) ==> 17
    map_point(3, 17)


xml_file_list = []
for root, dirs, files in os.walk(anomaly_data_root):
    # 비효율. 1 depth만 훓도록 바꾼다.
    for file in files:
        f_name, f_extension = os.path.splitext(file)
        if f_extension == '.xml':
            xml_file_list.append(os.path.join(root, file))

kinetics_label_json = {}

for xml_file in xml_file_list:
    # # xml parsing
    tree = elemTree.parse(xml_file)

    # 'file name' parsing
    file_name = tree.find('./filename').text  # LeeDaeWoong.mp4
    title = file_name[0:-4]  # LeeDaeWoong (mp4라 가정)

    # 'event' parsing (일단은 무용지물)
    event = tree.find('./event')
    event_name = event.find('./eventname').text
    event_start_time = datetime.strptime(event.find('./starttime').text, '%M:%S.%f')
    duration_datetime = datetime.strptime(event.find('./duration').text, '%M:%S.%f')
    event_duration = dt.timedelta(minutes=duration_datetime.minute, seconds=duration_datetime.second,
                                  microseconds=duration_datetime.microsecond)
    event_end_time = event_start_time + event_duration
    print("event : ", event_name)

    # 'action' parsing
    # {"rush" :[ [101, 202], [209, 411]]} 구조
    action_frame_list = {}
    # for object in tree.find('object'):
    object = tree.findall('object')[0]  # 1명으로 가정

    for action in object.findall('action'):
        action_name = action.find('actionname').text
        for frame in action.findall('frame'):
            start_frame = int(frame.find('start').text)
            end_frame = int(frame.find('end').text)
            if action_name in action_frame_list.keys():
                action_frame_list[action_name].append([start_frame, end_frame])
            else:
                action_frame_list[action_name] = [[start_frame, end_frame]]

    # sample input
    # openpifpaf_json_list = [
    #     {
    #     "keypoints": [467.2, 74.3, 1.0, 468.8, 71.4, 0.9, 464.2, 71.3, 1.0, 0.0, 0.0, 0.0, 455.6, 71.5, 0.9, 470.9, 86.2, 0.9, 443.6, 86.8, 0.9, 465.3, 108.5, 0.9, 442.9, 110.6, 0.9, 467.7, 117.9, 0.7, 462.9, 108.8, 0.9, 465.8, 132.6, 0.9, 448.4, 133.1, 0.9, 471.0, 167.0, 0.9, 443.4, 165.7, 0.9, 472.1, 205.1, 0.9, 431.3, 189.9, 1.0],
    #         "bbox": [431.3, 71.3, 40.7, 133.8],
    #         "score": 0.785
    #     },
    #     {
    #         "keypoints": [510.0, 43.8, 0.8, 512.1, 41.8, 0.8, 508.1, 41.5, 0.8, 514.3, 41.8, 0.5, 504.1, 40.3, 0.8, 517.2, 53.5, 0.9, 498.9, 49.7, 1.0, 521.2, 69.7, 0.9, 492.3, 61.8, 0.8, 522.3, 85.9, 0.9, 493.0, 72.9, 0.6, 508.5, 81.8, 0.9, 496.6, 80.2, 0.9, 507.1, 107.1, 0.9, 496.1, 105.8, 0.9, 508.7, 134.3, 0.8, 498.0, 130.3, 0.9],
    #         "bbox": [492.3, 40.3, 30.1, 94.0],
    #         "score": 0.738
    #     },
    #     {
    #         "keypoints": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 592.3, 102.6, 0.9, 0.0, 0.0, 0.0, 585.5, 113.1, 0.9, 607.2, 115.1, 0.9, 584.3, 132.1, 0.9, 607.9, 133.7, 0.6, 587.5, 143.4, 0.5, 0.0, 0.0, 0.0, 591.3, 156.0, 0.9, 606.3, 155.4, 0.9, 571.0, 150.5, 0.8, 591.7, 156.3, 0.3, 571.4, 180.1, 0.8, 0.0, 0.0, 0.0],
    #         "bbox": [571.0, 102.6, 36.9, 77.5],
    #         "score": 0.452
    #     }
    # ]

    for action in action_frame_list:
        for frame in action_frame_list[action]:
            openpifpaf_json_list = []
            start_frame = frame[0]
            end_frame = frame[1]

            # ouput param 관련
            kinetics_json = {}
            data_list = []

            for i in range(start_frame, end_frame):
                # [FRAME].jpg.pifpaf.json 에 1개 원소 가진 배열이 있는 것으로 관찰됨.
                frame_num = str(i).zfill(5)
                json_file = open(anomaly_data_root + title + '.images/' + frame_num + '.jpg.pifpaf.json', 'r')
                openpifpaf_json = json.loads(json_file.readline())[0]
                json_file.close()
                # BEFORE
                # print(openpifpaf_json)
                # openpifpaf_json_list.append(openpifpaf_json)

                j = 0
                pose = []
                score = []
                mapped_pose = []
                mapped_score = []
                data = {"frame_index": i, "skeleton": [{"pose": [], "score": []}]}

                for key_point in openpifpaf_json['keypoints']:
                    key = j % 3

                    if key == 0:
                        pose.append(key_point)
                    elif key == 1:
                        pose.append(key_point)
                    elif key == 2:
                        score.append(key_point)

                    j += 1

                # point 셋 매핑
                map_point_sets()
                data['skeleton'][0]['pose'] = mapped_pose
                data['skeleton'][0]['score'] = mapped_score
                data_list.append(data)

            kinetics_json['data'] = data_list
            kinetics_json['label'] = action
            kinetics_json['label_index'] = action_map[action]
            # output
            # print(kinetics_json)

            output_file_name = action + '-' + str(uuid.uuid4())
            kinetics_json_file = open(anomaly_skeleton_path + 'kinetics_val/' + output_file_name + '.json', 'w')
            kinetics_json_file.write(json.dumps(kinetics_json))
            kinetics_json_file.close()

            kinetics_label_json[output_file_name] = {"has_skeleton": True,
                                                     "label": action,
                                                     "label_index": action_map[action]}
            kinetics_label_file = open(anomaly_skeleton_path + 'kinetics_val_label.json', 'w')
            kinetics_label_file.write(json.dumps(kinetics_label_json))
            kinetics_label_file.close()
