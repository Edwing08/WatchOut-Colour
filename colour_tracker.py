from gpiozero.pins.pigpio import PiGPIOFactory
from colour_object_detection import *
from gpiozero import Servo
import numpy as np
import cv2 as cv
import sys


class ColourTracker:
    """
    ColourTracker definition 
    """

    def __init__(self, colour, video):

        # set the properties for each actuator 
        self.x_axis = self.TrackerAxis(-1, 1, -0.05, 0, 18)
        self.y_axis = self.TrackerAxis(-0.8, 0.1, -0.2, 0, 17)

        # set the camera sensor
        self.camera = self.CameraSensor(320, 240, 25, colour = colour, video = video)

    def track_object(self):
        """
        Main method that loops in order to move each axis to keep the object in the centre of the frame 
        """

        # set the limits within which the centre of the object should be located
        window_left = self.camera.cam_width/2 - self.camera.window_frame
        window_right = self.camera.cam_width/2 + self.camera.window_frame

        window_top = self.camera.cam_height/2 - self.camera.window_frame
        window_bot = self.camera.cam_height/2 + self.camera.window_frame
        
        try:

            while True:

                # get the coordinates of the largest object found
                result_obj_centre = self.camera.obtain_obj_centre()
                
                # display the current camera input
                self.camera.show_cam()
                
                # only proceed to track the object if there is indeed a valid object in frame
                if result_obj_centre is None:
                    pass

                else:

                    # track the object by following the x and y coordinates of the centre of the object
                    x_coor, y_coor = result_obj_centre
                    self.move_to_centre(self.x_axis, x_coor, window_right, -0.0125, window_left, 0.0125)
                    self.move_to_centre(self.y_axis, y_coor, window_bot, +0.0125, window_top, -0.0125)
       
        except KeyboardInterrupt:
            self.camera.capture.release()
            cv.destroyAllWindows()


    def move_to_centre(self, tracker_axis, obj_axis_position, window_A, step_A, window_B, step_B):
        """
        Reposition the axis in control if the centre of the object is not within the limits of the window that sets the centre of the image
        """
        if obj_axis_position > window_A:
            tracker_axis.change_position(step_A)

        elif obj_axis_position < window_B:
            tracker_axis.change_position(step_B)


    class TrackerAxis:
        """
        Actuator definition
        """

        def __init__(self, upper_limit, lower_limit, mid, current_position, pin_number):
            # physical limits regarding the servo motor
            self.upper_limit = upper_limit
            self.lower_limit = lower_limit
            self.mid = mid
            self.current_position = current_position

            # set the servo motor
            factory = PiGPIOFactory()
            self.servo = Servo(pin_number, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory)

            # set the tracker to a neutral position
            self.initial_state()


        def initial_state(self):
            """
            Set the servomotor to its middle position
            """
            self.servo.value = self.mid
            self.current_position = self.mid

        def change_position(self, step):
            """
            Move the position of the servomotor according to the step
            """

            # check whether a future position can exceed the physical limits of the servomotor
            future_position = self.current_position + step

            # set the position of the servomotor to its upper limit if reached
            if future_position <= self.upper_limit:
                self.servo.value = self.upper_limit
                self.current_position= self.upper_limit

            # set the position of the servomotor to its lower limit if reached
            elif future_position >= self.lower_limit:
                self.servo.value = self.lower_limit
                self.current_position = self.lower_limit

            # otherwise, set the position according to the step taken
            else:
                new_position = round(future_position, 4)
                self.servo.value = new_position
                self.current_position = new_position


    class CameraSensor:
        """
        Sensor definition
        """

        def __init__(self, width, height, window_frame, **kwargs):
            # camera properties
            self.cam_width = width
            self.cam_height = height
            self.window_frame = window_frame

            self.capture = cv.VideoCapture(0)

            # colour to be tracked
            self.colour = kwargs["colour"]
            
            if not self.capture.isOpened():
                print("Cannot open camera!!")
                exit()

            # reconfigure the camera properties
            self.capture.set(cv.CAP_PROP_FRAME_WIDTH, self.cam_width)
            self.capture.set(cv.CAP_PROP_FRAME_HEIGHT, self.cam_height)

            # video recording configuration
            self.video_output = kwargs["video"]
            if self.video_output != None:
                self.output_video = cv.VideoWriter(self.video_output + '.avi', cv.VideoWriter_fourcc('M','J','P','G'), 20, (320, 240))

            self.final_frame = 0

        def obtain_obj_centre(self):
            """
            Obtain the coordinates of the largest object found, if any
            """

            ret, frame = self.capture.read()
            
            if not ret:
                print("Error")

            else:
                
                # preprocess the image taken by rotating it and applying a Gaussian filter to it
                new_frame = cv.rotate(frame, cv.ROTATE_180)
                img_filtered = cv.GaussianBlur(new_frame, (5,5), 0)

                # filter out all colours other than the one of interest
                colour_mask = colour_filter(img_filtered, self.colour)

                # morphological noise removal
                kernel = np.ones((15, 15), np.uint8)
                morph = cv.morphologyEx(colour_mask, cv.MORPH_CLOSE, kernel)

                # extract the coordinates of the centre and radius of the largest object found
                obj_centre, obj_radio = largest_object(morph)

                # draw a circle around the largest object and write the coordinates of the centre in the image 
                if (obj_centre and obj_radio) is not None:
                    cv.circle(new_frame, (int(obj_centre[0]), int(obj_centre[1])), int(obj_radio), (0,0,255), 3)
                    cv.putText(new_frame, str(obj_centre), (50,50), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 1, cv.LINE_AA)
                                
                # write a video with the name acording to the arguments
                if self.video_output != None:
                    self.output_video.write(new_frame)

                self.final_frame = new_frame

                return obj_centre

  
        def show_cam(self):
            """
            show the current frame from the camera in real time
            """
            cv.imshow("frame", self.final_frame)
            cv.waitKey(1)
                    


if __name__ == "__main__":

    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python colour_tracker.py colour [video_name]")
    
    colour = sys.argv[1]

    if len(sys.argv) == 3:
        video_name = sys.argv[2]
    else:
        video_name = None

    tracker1 = ColourTracker(colour, video_name)
    tracker1.track_object()


