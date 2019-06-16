#!/usr/bin/env python3

import rospy
import visualization_msgs.msg as vmsgs
import main

def callback(marker_array):
	data = [(marker.text, marker.pose.position.x, marker.pose.position.y) for marker in marker_array.markers]
	data.sort(key = lambda x: (x[2], x[1]))
	roi_objects = [obj for obj in data if (obj[2] > 1.0 and obj[2] < 1.7)]
	events = [main.o[obj[0]].PRESENT for obj in roi_objects]
	for A2SN in main.A2SN_pool.values():
                A2SN.update_events(list(events))
	print('\t'.join([str(x[0]) for x in roi_objects]))
	print('\t'.join([str(ev) for ev in events]))

def start_listener():
	rospy.init_node('ActionRecognitionBridge')
	rospy.Subscriber("/dispatcher/output_objects_data/", vmsgs.MarkerArray, callback)


start_listener()
rospy.spin()
