#!/usr/bin/env python2

import json
from PIL import Image, ImageFilter

# ROS
import rospy
import rospkg
from std_srvs.srv import Empty
from kuka_cv.srv import *
from kuka_cv.msg import *
import time

__autor__ = 'Valerii Chernov'

debugModeOn = True

makeSampleConf = False

""" Some general stuff goes here """

rospack = rospkg.RosPack()
packagePath = rospack.get_path('Picture-PreProcessing') + "/"
imagePalette = Palette()

colors = []
canvas = []
size = []
dictToParse = {}
start = False;      # Bool variable for starting the work of node

corner = 5; # outside corner constant (https://stackoverflow.com/questions/42278777/image-index-out-of-range-pil)

def myRange(start, end, step):
    while start <= end:
        yield start
        start += step

def create_sample_conf():
    color_palette = {
                            "description": 42,
                            "version": 0.1,
                            "file": 'jake.jpg',
                            "colors": [
                                    {
                                        "color": "red",
                                        "ID": 0,
                                        "R": 255,
                                        "G": 0,
                                        "B": 0
                                    },
                                    {
                                        "color": "green",
                                        "ID": 1,
                                        "R": 0,
                                        "G": 255,
                                        "B": 0
                                    },{
                                        "color": "blue",
                                        "ID": 2,
                                        "R": 0,
                                        "G": 0,
                                        "B": 255
                                    },{
                                        "color": "yellow",
                                        "ID": 3,
                                        "R": 255,
                                        "G": 255,
                                        "B": 0
                                    },{
                                        "color": "cyan",
                                        "ID": 4,
                                        "R": 0,
                                        "G": 255,
                                        "B": 255
                                    },{
                                        "color": "magenta",
                                        "ID": 5,
                                        "R": 255,
                                        "G": 0,
                                        "B": 255
                                    },{
                                        "color": "black",
                                        "ID": 6,
                                        "R": 0,
                                        "G": 0,
                                        "B": 0
                                    }

                                ],
                            'height': 4,
                            'width': 2,
                            'brush': 0.02
                        }

    json.dump(color_palette, open(packagePath + 'sample_conf.json', 'w')) # save .json file

def load_sample_conf():
    with open(packagePath + 'sample_conf.json', 'r') as myfile: # open .json file
        raw_data=myfile.read().replace('\n', '')

    data = json.loads(raw_data) # load raw data from .json

    if (debugModeOn):
        print(raw_data) # debug stuff
        print(data["version"])

    palette = [] # color palette parsing
    for color in range( len(data["colors"]) ):
        palette += [[ data["colors"][color]['R'], data["colors"][color]['G'], data["colors"][color]['B'] ]]

    canvasDimentions = [data["width"], data["height"]] # get canvas Dimentions

    brush = data["brush"] # get brush size

    f = packagePath + data["file"] # get name of file with the picture to be drawed

    return brush, f

def choseColor(r, g, b, colors):

    marker = [] # create list of parameter that we want to minimize

    for i in range( len(colors) ): # calculating distances in color space from the point (r, g, b) to a points from color palette
        marker += [(r - colors[i][0]) ** 2 + (g - colors[i][1]) ** 2 + (b - colors[i][2]) ** 2]

    print(marker);
    id = marker.index(min(marker), 0, len(marker)) # choose ID of the most simular color from our palette

    return id

def compose(d,l,canvas):
    alpha, beta = float (d/l), round(canvas[0] / canvas[1], 3)

    print(alpha, beta)

    print("Canvas size: " + str([l, d]))
    if (alpha == beta):
        return 1
    elif(alpha < beta):
        return round(l/canvas[1])
    else:
        return round(d/canvas[0])

def pixelatingPicture(img, pixelSize):
    # print("Size: " + str([img.size[0], img.size[1]]))
    img = img.resize((int(round(img.size[0] / pixelSize)), int(round(img.size[1] / pixelSize))), Image.NEAREST)
    img = img.resize((img.size[0] * pixelSize, img.size[1] * pixelSize), Image.NEAREST)

    return img

def exportData(step, w, h, pixels, colors, canvas):
    dictToParse = {}

    dictToParse['test'] = 'is done'
    dictToParse['paintingPoints'] = []

    for i in range(len(colors)):
        for x in myRange(0, w - corner, step):
            for y in range(0, h - corner, step):
                # Create message with position of pixel center and BGR colour
                colourMsg = Colour()
                colourMsg.position = [round((2*x + step)/2 * canvas[0]/w, 3), round((2*y + step)/2 * canvas[0]/w, 3), 0]
                colourMsg.bgr = [pixels[x, y][2], pixels[x, y][1], pixels[x, y][0]]
                imagePalette.colours.append(colourMsg)

                dictToParse['paintingPoints'].append({
                                                            'x': round((2*x + step)/2 * canvas[0]/w, 3), # convertation to m
                                                            'y': round((2*y + step)/2 * canvas[0]/w, 3), # convertation to m
                                                            'R': pixels[x, y][0],
                                                            'G': pixels[x, y][1],
                                                            'B': pixels[x, y][2]
                                                     })

    if (debugModeOn):
        # print(dictToParse) #debug stuff
        print(imagePalette)

    json.dump(dictToParse, open(packagePath + 'out.json', 'w')) # json dump

    print('Done')

# --------------------------------------- #

# TODO organize Action Server
""" Service Server for communication with LTP """
def startPreprocessing(data):

    print("READ palette and canvas message")
    colors = []
    canvas = []
    try:
        # Get information about colours
        clrResp = paletteClient()
        for clr in clrResp.colours:
            colors += [[ int(clr.bgr[2]), int(clr.bgr[1]), int(clr.bgr[0]) ]]

        # Get information about canvas dimensions
        cnvsResp = canvasCient()
        canvas = [cnvsResp.width, cnvsResp.height]
    except rospy.ServiceException, e:
        print "Service call failed: %s"%e

    print("Palette COLORS: " + str(colors))
    print("Canvas DIM: " + str(canvas))
    print("==========================================")

    # Start main image processing
    main(colors, canvas)

def sendImagePalette(data):
    while (len(imagePalette.colours) == 0 and not rospy.is_shutdown()):
        time.sleep(1)

    if rospy.is_shutdown():
        return False

    resp = RequestPaletteResponse()
    resp.colours = imagePalette.colours
    return resp

def main(colors, canvas):
    if (makeSampleConf):
        create_sample_conf() #debug stuff

    """ Load environment data """
    brushSize, file = load_sample_conf()

    """ Load picture to be drawed """
    picture = Image.open(file)
    picSize = picture.size
    pixels = picture.load()

    if (debugModeOn):
        picture.show() #debug stuff
        print()

    """ Pixelating """
    pixelSize = compose(picture.size[0]*brushSize, picture.size[1]*brushSize, canvas) # compose() function checks if
                                                                                      # picture needs to be resized

    if (pixelSize != 0):
        picture = pixelatingPicture(picture, int(pixelSize))

    if (debugModeOn):
        picture.show() #debug stuff

    """ Change colors of picture  """

    for x in range(picture.size[0] - corner):
        for y in range(picture.size[1] - corner):
            i = choseColor(pixels[x, y][0], pixels[x, y][1], pixels[x, y][2], colors)
            pixels[x, y] = (colors[i][0], colors[i][1], colors[i][2])

    """ Export JSON file """

    exportData(int(pixelSize), picture.size[0], picture.size[1], pixels, colors, canvas)

if __name__ == '__main__':
    rospy.init_node('image_preprocessor')

    """ Start Servers and Clients """

    imagePeprocessingService = rospy.Service("/start_image_preprocessing", Empty, startPreprocessing)
    sendImagePaletteService = rospy.Service("/request_image_palette", RequestPalette, sendImagePalette)
    paletteClient = rospy.ServiceProxy('/request_palette', RequestPalette)
    canvasCient = rospy.ServiceProxy('/request_canvas', RequestCanvas)
    print("Waiting for Service.")
    while not rospy.is_shutdown():
        rospy.spin();