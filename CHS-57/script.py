# scrape CHS nonsense:
# the general idea is to import the mapserver into qgis (add layers, add arc-gis mapserver...)
# then create an xyz layer from the extents of that.  This will be mostly empty because qgis doesn't query the mapserver correctly, but gives us the right file structure/names
# once the file structure is in place, we can use it to generate the bbox's to query the mapserver for the actual data

import math
import os
import requests
import shutil

def get_url(dpi=96, transparent='true', format='png24', layers='show:0,1,2,3,4,5,6,7', bboxSR="4326",
            bbox="-63.77192935617817,45.898290276110444,-63.203770112907755,46.11005162288075", imageSR="102100", size="256,256"):
    return f"https://gisp.dfo-mpo.gc.ca/arcgis/rest/services/CHS/ENC_MaritimeChartService/MapServer/exts/MaritimeChartSe" \
      f"rvice/MapServer/export?dpi={dpi}&transparent={transparent}&format={format}&layers={layers}&bbox={bbox}&bboxSR={bboxSR}&imageSR={imageSR}&size={size}&f=image"


def get_latlng(x, y, z):
    n = 2**z
    a = math.pi * (1 - 2 * y/n)
    lat = math.degrees(math.atan(math.sinh(a)))
    long = 360*x/n - 180
    return lat, long

def get_bbox(x, y, z):
    lat, lng = get_latlng(x, y, z)
    lat1, lng1 = get_latlng(x + 1, y + 1, z)
    return f"{lng},{lat1},{lng1},{lat}"

# this is the output from qgis should be:
img_dir = "C:\\Users\\stoyelq\\Desktop\\work\\projects\\andes\\CHS\\test_map_png\\"

out_dir = "C:\\Users\\stoyelq\\Desktop\\work\\projects\\andes\\CHS\\test_scrape_png\\"
for path, subdirs, files in os.walk(img_dir):
    try:
        print(path)
        z = int(path.split("\\")[-2])
        x = int(path.split("\\")[-1])

        x_dir = f"{out_dir}\\{z}\\{x}"
        if not os.path.exists(x_dir):
            os.makedirs(x_dir)

        for name in files:
            y = int(name[:-4])
            out_file_path = f"{x_dir}\\{y}.png"
            bbox = get_bbox(x, y, z)
            url = get_url(bbox=str(bbox))
            response = requests.get(url, stream=True)
            with open(out_file_path, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response
    except ValueError:
        pass
