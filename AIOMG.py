# A.I.O.M.G
# Alert Image Or Map Generator

# This script will take an image or generate a map from an CAP alert.

# first, look for an image, it could be encoded in base64 or have a link (i haven't seen an image with a link though...)
# then, if no image could be found, generate a polygon, output image in 1:1 ratio.
# if any of the generation processes fails, just use the fallback image.

import re, base64, requests, os, subprocess, shutil

import matplotlib
matplotlib.use('Agg') 

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Polygon
from matplotlib.lines import Line2D

# Requirments: matplotlib, basemap

ImageOutput = "./images/alertImage.png"

def overlay_polygon(map_object, lats, lons, label='', color='red'):
    x, y = map_object(lons, lats)
    map_object.plot(x, y, marker=None, color=color, linewidth=2, linestyle='-', label=label)

def fill_polygon(map_object, lats, lons, color='red', alpha=0.5):
    x, y = map_object(lons, lats)
    polygon = Polygon(list(zip(x, y)), facecolor=color, alpha=alpha)
    map_object.ax.add_patch(polygon)

def calculate_bounding_box(coordinates):
    min_lat = min(lat for lat, _ in coordinates)
    max_lat = max(lat for lat, _ in coordinates)
    min_lon = min(lon for _, lon in coordinates)
    max_lon = max(lon for _, lon in coordinates)
    return min_lat, max_lat, min_lon, max_lon

def GenerateMapImage(InfoXML, PolyColor="#FF0000"):
    print("[AIOMG]: Generating map image...")
    if "#" not in PolyColor: PolyColor = "#" + PolyColor
    if len(PolyColor) > 7: PolyColor = "#FF0000"
    for char in PolyColor:
        if 'G' <= char <= 'Z' or 'g' <= char <= 'z': PolyColor = "#FF0000"

    
    # Get alert title TODO
    #HEADLINE = "Test alert"
    HEADLINE = re.search(r'<headline>\s*(.*?)\s*</headline>', InfoXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)

    # Get all polygons TODO
    
    #Areas = re.findall(r'<area>\s*(.*?)\s*</area>', InfoXML, re.MULTILINE | re.IGNORECASE | re.DOTALL)
    AllCoords = re.findall(r'<polygon>\s*(.*?)\s*</polygon>', InfoXML, re.MULTILINE | re.IGNORECASE | re.DOTALL)
    
    #for SingleArea in Areas:
    #    Polygon = re.search(r'<polygon>\s*(.*?)\s*</polygon>', SingleArea, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
    #    print(Polygon)

    # Generate map
    coordinates_string = ""
    for i in AllCoords:
        coordinates_string = coordinates_string + f" {i}"
    polygon_coordinates = [list(map(float, item.split(','))) for item in coordinates_string.split()]
    min_lat, max_lat, min_lon, max_lon = calculate_bounding_box(polygon_coordinates)
    lat_center = (min_lat + max_lat) / 2
    lon_center = (min_lon + max_lon) / 2
    lat_range = max_lat - min_lat
    lon_range = max_lon - min_lon

    if lat_range > lon_range: lon_range = lat_range
    else: lat_range = lon_range

    fig = plt.figure(figsize=(10, 10))
    # For outlined polygon
    #world_map = Basemap(projection='mill', lat_1=-60, lat_2=90, lon_0=lon_center, llcrnrlat=lat_center - 1.1 * lat_range, urcrnrlat=lat_center + 1.1 * lat_range, llcrnrlon=lon_center - 1.1 * lon_range, urcrnrlon=lon_center + 1.1 * lon_range, resolution='i')
    ax = fig.add_subplot(111)
    
    #world_map = Basemap(ax=ax, projection='mill', lat_1=-60, lat_2=90, lon_0=lon_center, llcrnrlat=lat_center - 1.1 * lat_range, urcrnrlat=lat_center + 1.1 * lat_range, llcrnrlon=lon_center - 1.1 * lon_range, urcrnrlon=lon_center + 1.1 * lon_range, resolution='i')
    
    world_map = Basemap(
        ax=ax, 
        projection='cyl',  # Using cylindrical projection to minimize distortion
        lon_0=lon_center,
        llcrnrlat=lat_center - 1.1 * lat_range, 
        urcrnrlat=lat_center + 1.1 * lat_range, 
        llcrnrlon=lon_center - 1.1 * lon_range, 
        urcrnrlon=lon_center + 1.1 * lon_range, 
        resolution='i'
    )
    
    world_map.drawcoastlines()
    world_map.drawcountries()
    world_map.drawcounties()
    world_map.drawstates()
    world_map.fillcontinents(color='#00AA44', lake_color='#002255')
    world_map.drawmapboundary(fill_color='#002255')
    for i in AllCoords:
        i = [list(map(float, item.split(','))) for item in i.split()]
        lats, lons = zip(*i)
        fill_polygon(world_map, lats, lons, color=PolyColor, alpha=0.5)
        overlay_polygon(world_map, lats, lons, label=HEADLINE, color=PolyColor) # For outlined polygon
    
    ax.set_aspect('equal')
    
    legend_patch = Line2D([0], [0], marker='o', color='w', markerfacecolor=PolyColor, markersize=10, label=HEADLINE)
    plt.legend(handles=[legend_patch], loc='upper right')
    #plt.legend(loc='upper right') # For outlined polygon
    #plt.show() #For testing, to show the map in a window
    fig.savefig(ImageOutput, bbox_inches='tight', pad_inches=0.0, dpi=70)

def ConvertImageFormat(inputAudio, outputAudio):
        result = subprocess.run(["ffmpeg", "-y", "-i", inputAudio, "-vf", "scale=-1:450", outputAudio], capture_output=True, text=True)
        if result.returncode == 0: print(f"[AIOMG]: {inputAudio} --> {outputAudio} ... Conversion successful!")
        else: print(f"[AIOMG]: {inputAudio} --> {outputAudio} ... Conversion failed: {result.stderr}")

# ffmpeg -i input_image.png -vf "scale=-1:600" output_image.png

def ResizeImage():
    pass

def GetImage(imagelink, Output, DecodeType):
    if DecodeType == 1:
        print("Decoding image from BASE64...")
        with open(Output, "wb") as fh: fh.write(base64.decodebytes(imagelink))
    elif DecodeType == 0:
        print("Downloading image...")
        r = requests.get(imagelink)
        with open(Output, 'wb') as f: f.write(r.content)

def GrabImage(InfoXML):
    resources = re.findall(r'<resource>\s*(.*?)\s*</resource>', InfoXML, re.MULTILINE | re.IGNORECASE | re.DOTALL)
    if "image/jpeg" in str(resources): pass
    elif "image/png" in str(resources): pass
    else: return False
    print("[AIOMG]: Grabbing image from CAP...")

    try:
        for ImageResource in resources:
            if "<derefUri>" in ImageResource:
                ImageLink = bytes(re.search(r'<derefUri>\s*(.*?)\s*</derefUri>', ImageResource, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1), 'utf-8')
                ImageType = re.search(r'<mimeType>\s*(.*?)\s*</mimeType>', ImageResource, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                Decode = 1
            else:
                ImageLink = re.search(r'<uri>\s*(.*?)\s*</uri>', ImageResource, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                ImageType = re.search(r'<mimeType>\s*(.*?)\s*</mimeType>', ImageResource, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                Decode = 0
            
            if ImageType == "image/jpeg":
                GetImage(ImageLink,"./Audio/tmp/PreImage.jpg",Decode)
                ConvertImageFormat("./Audio/tmp/PreImage.jpg", ImageOutput)
                os.remove("./Audio/tmp/PreImage.jpg")
            elif ImageType == "image/png":
                GetImage(ImageLink,ImageOutput,Decode)

        return True
    except: return False

def OutputAlertImage(InfoXML=None, InputColor="#FF0000", Fallback=False):
    if Fallback is True:
        print("[AIOMG]: Using fallback image...")
        shutil.copy("./images/fallbackImage.png", ImageOutput)
    else:
        try:
            if GrabImage(InfoXML) is True: pass
            else: GenerateMapImage(InfoXML, InputColor)  
            print("[AIOMG]: Image generation finished")
        except Exception as e:
            print("[AIOMG]: Image generation failure: ", e)
            print("[AIOMG]: Using fallback image...")
            shutil.copy("./images/fallbackImage.png", ImageOutput)

# for testing...
if __name__ == "__main__":
    with open("testerX.xml", "r") as file: XML = file.read()
    INFOXML = re.search(r'<info>\s*(.*?)\s*</info>', XML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
    INFOXML = f"<info>{INFOXML}</info>"
    OutputAlertImage(INFOXML) # this is the main one to run