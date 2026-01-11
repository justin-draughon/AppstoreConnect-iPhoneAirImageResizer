# AppstoreConnect-iPhoneAirImageResizer
This script takes the iPhone Air screenshots from the simulator and converts them slightly into the dimensions Apple requires for Appstore Connect. 
Note: The v2 script relies only on native OS fucntions on MacOS and Windows to edit the screenshots. It does not require third party Python packages to be installed such as Pillows through PIP. 

To Run: Copy the script into the directory with your screenshots. Open a terminal in that folder and run "python image_resizer.py" 

The script will take all images in the folder and resize them to 1284 x 2778, which is the dimensions Apple requires. The output files will be placed in the same folder, but with "RESIZE - " appended to the beginning of the file name. 
