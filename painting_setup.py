import json
from PIL import Image, ImageFilter

__autor__ = 'Valerii Chernov'

debugModeOn = True

makeSampleConf = True

""" Some general stuff goes here """

colors = []
canvas = []
size = []
dictToParse = {}

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

    json.dump(color_palette, open('sample_conf.json', 'w')) # save .json file

def load_sample_conf():
    with open('sample_conf.json', 'r') as myfile: # open .json file
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

    f = data["file"] # get name of file with the picture to be drawed

    return palette, canvasDimentions, brush, f

def choseColor(r: int, g: int, b: int) -> int:

    marker = [] # create list of parameter that we want to minimize

    for i in range( len(colors) ): # calculating distances in color space from the point (r, g, b) to a points from color palette
        marker += [(r - colors[i][0]) ** 2 + (g - colors[i][1]) ** 2 + (b - colors[i][2]) ** 2]

    id = marker.index(min(marker), 0, len(marker)) # choose ID of the most simular color from our palette

    return id

def compose(d: int,l: int,canvas: int) -> int:
    alpha, beta = float (d/l), float(canvas[0] / canvas[1])

    print(alpha, beta)

    if (alpha == beta):
        return 1
    elif(alpha < beta):
        return round(l/canvas[1])
    else:
        return round(d/canvas[0])

def pixelatingPicture(img, pixelSize):

    img = img.resize((round(img.size[0] / pixelSize), round(img.size[1] / pixelSize)), Image.NEAREST)
    img = img.resize((img.size[0] * pixelSize, img.size[1] * pixelSize), Image.NEAREST)

    return img

def exportData(step: int, w: int, h: int, pixels):
    dictToParse = {}

    dictToParse['test'] = 'is done'
    dictToParse['paintingPoints'] = []

    for i in range(len(colors)):
        for x in myRange(0, w - corner, step):
            for y in range(0, h - corner, step):
                dictToParse['paintingPoints'].append({
                                                            'x': round(x / w * canvas[0] + step/2, 3), # convertation to m
                                                            'y': round(y / h * canvas[1] + step/2, 3), # convertation to m
                                                            'R': pixels[x, y][0],
                                                            'G': pixels[x, y][1],
                                                            'B': pixels[x, y][2]
                                                     })

    if (debugModeOn):
        print(dictToParse) #debug stuff

    json.dump(dictToParse, open('out.json', 'w')) # json dump

    print('Done')


# --------------------------------------- #


if (makeSampleConf):
    create_sample_conf() #debug stuff

""" Load environment data """
colors, canvas, brushSize, file = load_sample_conf()

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
    picture = pixelatingPicture(picture, pixelSize)

if (debugModeOn):
    picture.show() #debug stuff

""" Change colors of picture  """

for x in range(picture.size[0] - corner):
    for y in range(picture.size[1] - corner):
        i = choseColor(pixels[x, y][0], pixels[x, y][1], pixels[x, y][2])
        pixels[x, y] = (colors[i][0], colors[i][1], colors[i][2])

""" Export JSON file """

exportData(pixelSize, picture.size[0], picture.size[1], pixels)