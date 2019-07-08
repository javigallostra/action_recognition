#!/usr/bin/env python3

import rospy
import visualization_msgs.msg as vmsgs
import main
from math import sqrt

objects = []
i = 0

def callback(marker_array):
	data = [(marker.text, marker.pose.position.x, marker.pose.position.y) for marker in marker_array.markers]
	data.sort(key = lambda x: (x[2], x[1]))
	roi_objects = [obj for obj in data if (obj[2] > 1.0 and obj[2] < 1.7)]
	#events = [main.o[obj[0]].PRESENT for obj in roi_objects]
	events = event_parser(roi_objects)
	for A2SN in main.A2SN_pool.values():
                A2SN.update_events(list(events))
	#print('\t'.join([str(x[0]) for x in roi_objects]))
	#print('\t'.join([str(ev) for ev in events]))

def start_listener():
	rospy.init_node('ActionRecognitionBridge')
	rospy.Subscriber("/dispatcher/output_objects_data/", vmsgs.MarkerArray, callback)

def event_parser(data):
	global i
	global objects
	dist_th = 0.03
	i += 1
	for obj in data:
		pos = False
		if len(objects) == 0:
			objects.append([i, obj[1],obj[2],{obj[0]:1},0,""])
		for o in objects:
			if sqrt((obj[1]-o[1])**2 + (obj[2]-o[2])**2) <= dist_th:
				#same position
				o[0] = i
				if obj[0] in list(o[3].keys()):
					o[3][obj[0]] += 1
				else:
					o[3][obj[0]] = 1
				pos = True
		# check position
		if not pos:
			objects.append([i,obj[1],obj[2],{obj[0]:1},0,""])
	#DEcide which objects exist and if they are moving
	detect = 4
	for obj in objects:
		c_max = 0
		name = ""
		for o_name in list(obj[3].keys()):
			if obj[3][o_name] > c_max:
				c_max = obj[3][o_name]
				name = o_name
		if c_max > detect:
			obj[5] = name
			if obj[0] == i:
				obj[4] = 1 #present
			else:
				obj[4] = 2 #moving
		else:
			obj[4] = 0 #nothing
	events = []
	for obj in objects:
		if obj[4] == 1:
			ev = main.o[obj[5]].PRESENT
			events.append(ev)
		elif obj[4] == 2:
			ev = main.o[obj[5]].MOVING
			events.append(ev)
	return events
start_listener()
rospy.spin()
