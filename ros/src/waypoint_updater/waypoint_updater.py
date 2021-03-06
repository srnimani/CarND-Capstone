#!/usr/bin/env python

import rospy
from geometry_msgs.msg import PoseStamped
from styx_msgs.msg import Lane, Waypoint
from std_msgs.msg import Int32

import math
import numpy as np
'''
This node will publish waypoints from the car's current position to some `x` distance ahead.
As mentioned in the doc, you should ideally first implement a version which does not care
about traffic lights or obstacles.
Once you have created dbw_node, you will update this node to use the status of traffic lights too.
Please note that our simulator also provides the exact location of traffic lights and their
current status in `/vehicle/traffic_lights` message. You can use this message to build this node
as well as to verify your TL classifier.
TODO (for Yousuf and Aaron): Stopline location for each traffic light.
'''

LOOKAHEAD_WPS = 200 # Number of waypoints we will publish. You can change this number


class WaypointUpdater(object):
    def __init__(self):
        
        self.pose = None      
        self.waypoints = None # the final waypoints
        self.point = None # Stores the waypoint index the car is closest to
        self.traffic_point = None
        
        rospy.init_node('waypoint_updater')
        rospy.loginfo("Running init")
        rospy.Subscriber('/current_pose', PoseStamped, self.pose_cb)
        rospy.Subscriber('/base_waypoints', Lane, self.waypoints_cb)

        # TODO: Add a subscriber for /traffic_waypoint and /obstacle_waypoint below
        rospy.Subscriber('/traffic_waypoint', Int32, self.traffic_cb)




        self.final_waypoints_pub = rospy.Publisher('final_waypoints', Lane, queue_size=1)

        # TODO: Add other member variables you need below
        
        rospy.spin()

    def pose_cb(self, msg):
        self.pose = msg


        dl = lambda a, b: math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2 )

        d = [] # temporary list to capture distance of waypoints from current position
        # rospy.loginfo(self.pose)

        if self.waypoints:
            for waypoint in self.waypoints.waypoints: 
                d.append(dl(waypoint.pose.pose.position, self.pose.pose.position))
            self.point = np.argmin(d)

            # rospy.loginfo(self.point)


            l = Lane()
            l.header = self.waypoints.header
            l.waypoints = self.waypoints.waypoints[self.point:self.point+1 + LOOKAHEAD_WPS]


            # for i, w in enumerate(l.waypoints):
            #     rospy.loginfo("Pose: %d: %d %d %d", i, w.pose.pose.position.x, w.pose.pose.position.y, w.pose.pose.position.z)
            #     rospy.loginfo("Twist: %d: %d %d %d", i, w.twist.twist.linear.x, w.twist.twist.linear.y, w.twist.twist.linear.z)
            self.final_waypoints_pub.publish(l)

            # i = len(l.waypoints)
            # w = l.waypoints[-1]
            # rospy.loginfo("Pose: %d: %d %d %d", i, w.pose.pose.position.x, w.pose.pose.position.y, w.pose.pose.position.z)


    def waypoints_cb(self, waypoints):
        '''
        Finds the closest base waypoint position from the current car's position as an index
        Publishes the next LOOKAHEAD_WPS points
        '''
        self.waypoints = waypoints


        
    def traffic_cb(self, msg):
     	self.traffic_point = msg
     	rospy.loginfo(self.distance(self.waypoints.waypoints,self.point, self.traffic_point.data))


    def obstacle_cb(self, msg):
        # TODO: Callback for /obstacle_waypoint message. We will implement it later
        pass

    def get_waypoint_velocity(self, waypoint):
        return waypoint.twist.twist.linear.x

    def set_waypoint_velocity(self, waypoints, waypoint, velocity):
        waypoints[waypoint].twist.twist.linear.x = velocity

    def distance(self, waypoints, wp1, wp2):
        dist = 0
        dl = lambda a, b: math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2  + (a.z-b.z)**2)
        for i in range(wp1, wp2+1):
            dist += dl(waypoints[wp1].pose.pose.position, waypoints[i].pose.pose.position)
            wp1 = i
        return dist
    


if __name__ == '__main__':
    try:
        WaypointUpdater()
    except rospy.ROSInterruptException:
        rospy.logerr('Could not start waypoint updater node.')
