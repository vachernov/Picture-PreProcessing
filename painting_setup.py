import json
from PIL import Image, ImageFilter

__autor__ = 'Valerii Chernov'

debugModeOn = False

""" Some general stuff goes here """

colors = []
canvas = []
size = []
dictToParse = {}

pixelSize = 5

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
                            'height': 400,
                            'width': 200,
                            'brush': 20
                        }

    json.dump(color_palette, open('sample_conf.json', 'w'))

def load_sample_conf():
    with open('sample_conf.json', 'r') as myfile:
        raw_data=myfile.read().replace('\n', '')

    data = json.loads(raw_data)

    print(raw_data)
    print(data["version"])

    palette = []
    for color in range( len(data["colors"]) ):
        palette += [[ data["colors"][color]['R'], data["colors"][color]['G'], data["colors"][color]['B'] ]]

    canvasDimentions = [data["width"], data["height"]]

    f = data["file"]

    return palette, canvasDimentions, f

def choseColor(r: int, g: int, b: int) -> int:

    marker = []

    for i in range( len(colors) ):
        marker += [(r - colors[i][0]) ** 2 + (g - colors[i][1]) ** 2 + (b - colors[i][2]) ** 2]

    id = marker.index(min(marker), 0, len(marker))

    return id

def pixelatingPicture(img, pixelSize):
    img = img.resize((round(img.size[0] / pixelSize), round(img.size[1] / pixelSize)), Image.NEAREST)
    img = img.resize((img.size[0] * pixelSize, img.size[1] * pixelSize), Image.NEAREST)

    return img

def addPoint(x: int, y: int, i: int) -> str:
    #bullshit goes here

    return "{ 'x': %(x)i, 'y': %(y)i, 'colorID': %(i)i }," % {"x": x, "y": y, "i": i}

def exportData(step: int, w: int, h: int, pixels):
    dictToParse = {}

    dictToParse['test'] = 'is done'
    dictToParse['paintingPoints'] = []

    for i in range(len(colors)):
        for x in myRange(0, w, step):
            for y in range(0, h, step):
                #print(i, x, y)
                #print(colors[i][0], colors[i][1], colors[i][2])
                if pixels[x, y] == (colors[i][0], colors[i][1], colors[i][2]):
                    dictToParse['paintingPoints'].append({
                                                            'x':       x / w * canvas[0] + step/2, # convertation to Cm
                                                            'y':       y / h * canvas[1] + step/2, # convertation to Cm
                                                            'colorID': i
                                                         })

    if (debugModeOn):
        print(dictToParse) #debug stuff

    json.dump(dictToParse, open('out.json', 'w')) # json dump


# --------------------------------------- #

create_sample_conf() #debug stuff

""" Load environment data """
colors, canvas, file = load_sample_conf()

""" Load picture to be drawed """
picture = Image.open(file)
picSize = picture.size
pixels = picture.load()
#print(picture._getexif()) #debug stuff

if (debugModeOn):
    picture.show() #debug stuff
    print()

""" Pixelating """

picture = pixelatingPicture(picture, pixelSize)

print(picture.size)

if (debugModeOn):
    picture.show() #debug stuff

""" Change colors of picture  """

for x in range(picture.size[0]):
    for y in range(picture.size[1]):
        i = choseColor(pixels[x, y][0], pixels[x, y][1], pixels[x, y][2])
        pixels[x, y] = (0, 0, 0) # (colors[i][0], colors[i][1], colors[i][2])

if (debugModeOn):
    picture.show() #debug stuff

""" Export JSON file """

exportData(pixelSize, picture.size[0], picture.size[1], pixels)