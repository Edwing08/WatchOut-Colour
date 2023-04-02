# **WatchOut-Colour**

#### Video Demo: [WatchOut-Colour](https://www.youtube.com/watch?v=kSkUyFp7Bf0)

![GIF demo](img/demo-gif.gif)

`WatchOut-Colour` is a device based on a Pan-Tilt camera (consisting of a camera and a pan-tilt mount driven by two servomotors) that follows the largest object in the frame according to the color of interest indicated by the user.

Once the program starts, the device moves to its initial state reaching a neutral position in which the camera points straight ahead. Shortly thereafter, the object with the largest surface area colored according to the color selected by the user will be tracked. If the object moves, the camera will follow its trajectory keeping the object in the frame at all times until finally the object disappears from view, either by moving quickly out of the frame or by leaving the working area. In this case, the device will remain stationary in its last position until any object that has the color of interest appears.

## Explanation

`WatchOut-Color` has been created taking advantage of the object oriented programming offered by python. In the script `colour_tracker.py` the object and method to be used to track a color object is defined. The `ColourTracker()` class represents the device itself, as can be seen in the definition of this class, it consists of two actuators (one for each axis) and the camera module. Both were built using classes as well. `TrackerAxis()` is the class that contains the properties and methods used by the servomotors and `CameraSensor()` is the class that comprises all aspects related to the camera.

the `ColourTracker()` class contains a method in which the whole object tracking process is solidified, namely track_object(). This method performs an infinite loop collecting data from the camera module. If there is an object of interest, its coordinates (provided by the method obtain_obj_centre()) within the camera frame are processed so that the object is tracked. The main idea is to move the actuators (using the method move_to_centre()) so that the center of the object matches the center of the camera frame. In each iteration, each axis moves one step trying to reach that goal. There is a window frame that behaves as a safe area, if the center of the object is positioned within this range, the object is considered to be in the center and therefore no action needs to be taken by the actuators.

Regarding the camera module, the CameraSensor() class defines its main properties, configures the camera and starts recording so that obtain_obj_centre() method can do its job of obtaining the center of the object in frame, if any. This method relies on the OpenCV library, which provides many functions for image processing. The whole process in this method is descripbed as follows. First, the image read is rotated 180 degrees due to how the physical camera was attached to the Pan-Tilt mount. After that, a image filtering was done using a Gaussian blur to reduce posible noise in the input image as well as to smooth the detail that every pixel has and to interprete the image in a bigger scale. Then the image goes through a method called colour_filter(), which takes an image and a colour and as a result it outputs a mask, which is a binary image hidding every pixel that is not related to the colour of interest and revealing the ones that are. The HSV colour model (Hue, Saturation, Value) is used instead of any other model due to its strong response to light changes, which is import for this type of application. The HSV values used to threshold the image were picked by eye from a HSV colour scale.

the next step of the process consists in filtering the mask by applying a morphological transformation, so that some of the false negatives values (noise) coming from the thresholding process are removed. At this point, the image containing the mask is ready to continue with object detection. Using the largest_object() method, it returns the largest object found based on the contours. This method uses a Canny edges detector and then a contours detector. The features (center coordinates and radius) from each contour found are stored in a list that will be used to extract the largest object found based on the radius of the contour.

When it comes to the actuators, `TrackerAxis` is a class that defines them by configuring them and establishing a method that allows optimal movement conditions especially for this type of application. The task of using a servomotor with a Raspberry Pi was facilitated by relying on the "Servo" and "PiGPIOFactory" libraries. In the initialization, physical limit are set, which means that the control signal feeding the servomotor would not surpace that value. As a brief description, this type of servomotor moves only in the range of 0 to 180 degrees, this library controls the position of the servomotor proportionally rotate based on the value asigned, going from -1 to one end and 1 to the other end.

The main method of this class is change_position(), which rotates the servomotor a small amount called step. The step adds up with the current value to conform the final value of the servomotor control, once the step value and the current value exceed the limits, it is capped at that limit by not letting the servomotor assign itself a value beyong that limit.











WatchOut Colour core is defined in the script colour_tracker.py. This script uses the class ColourTracker() 
stick together all the pieces 
mechanical - servomotors
detection - camera

1 CameraSensor

2 TrackerAxis



The script colour_tracker.py is the main script python colour_tracker.py colour [video_name]
WatchOut colour is defined as an object comprised of two classes. 

The tracker consists of two modules, the first one is the object detection and the other one is where the actual tracking happens by moving the mechanism to follow the object. Taking advantange of python's feature as an object oriented programming language, a class with two inner classes was created in order to represent the gadget obtimally thinking always in avoid redundancy. the main class gathers the class that defines the servomotors that moves the camera and the class that defines the camera that captures the images.

Colour object detection

when it comes to extractring valuable information out of the images captured by the camera, some image processing had to be done, therefore the framework OpenCV was used to perform this task. 

Firstly, image pre-processing was necessarily before the actual processing. In this step the image read was rotated 180 degrees due to how the physical camera was attached to the module and a small image filtering using a Gaussian blur to reduce posible noice in the input image as well as to smooth the detail that every pixel has and to interprete the image in a bigger scale. After that the image goes through a function called "colour_filter", this function takes an image and a colour, as a result it outputs a mask, which is a binary image hidding every pixel that is not related to the colour of interest and revealing the ones that are. the HSV colour model (Hue, Saturation, Value) was used instead of any other model due to its strong response to light changes, which is import for this type of application. The HSV values used to threshold the image were picked by eye from a HSV colour scale.

the next step of the process is to filter the mask applying a morphological transformation so that some of the false negatives values (noice) coming from the thresholding process are eliminated. At this point, the image containing the mask is ready to continue with object detection. Using the function "largest_object", it returns the largest object found based on the contours, if any. This function uses a Canny edges detector and then a contours detector. the features (center coordinates and radius) from each contours found are stored in a list that will be used to extract the biggest object found based on the radius of the contour.

the last step in this module aims to provide a way to show to the user, what is happening by drawing the biggest contour and displaying it in real time.

Tracker axis

TrackerAxis is a class that defines the actuator by setting it up and stablishing a method that would allow a optimal movement conditions particularly for this type of application.

The actual task of using a servomotor with a raspberry pi was made easier by relying on the "Servo" and "PiGPIOFactory" libraries. In the initialization physical limit were established, meaning that the control signal feeding the servomotor would not surpace that value. As a brief description, this type of servomotor move only in the range of 0 to 180 degrees, this library controls the position of the servomotor proportionally rotate based on the value asigned, going from -1 to one end and 1 to the other end.

The main method from this class is "change_position", which rotates the axis from the servomotor a small amount called the step. The step adds up with the current value to conform the final value for the control signal of the servomotor, once the step value and the current value surpass the limits, it caps to that limit not letting the servomotor get assign a value beyong that limit.

Colour tracker

conforming all together, the main class make use of its two inner classes to conform what is call the colour tracker. the "track_object" method works on a infinite loop moving the actuators based on the information regarding the position of the object sensed obtained by the camera. in every iteration the system will ensure that the center of the object is inside a window frame marking the center of the image. Take a look at the following picture.


each axis will move respectibely in the correct direction until the center of the object reachs the window frame in the centre meaning that the object is within frame due to the actuators moving correctly





