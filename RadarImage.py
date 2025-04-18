import math

class radarImage:
    def __init__(self, boundary, image, regional = True, ogImage=None):
        self.top = boundary[0]
        self.left = boundary[1]
        self.bottom = boundary[2]
        self.right = boundary[3]
        self.cWidth = abs(self.left - self.right) 
        self.cHeight = abs(self.top - self.bottom)
        self.image = image
        self.width, self.height = image.size
        self.regional = regional
        self.ogImage = ogImage

    def latlon_to_pixel(self, lat, lon, lat_top, lat_bottom, lon_left, lon_right, width, height, regional):
        x = (lon_left - lon) / (lon_left - lon_right) * width
        
        y = 0
        if not regional:
            rads = math.radians(lat)
            yMult = 1 / math.cos(rads)
            rads = math.radians(lat_bottom)
            yMult = (yMult - (1/math.cos(rads)))/2 + 1
            y = (lat - lat_bottom)
            y = y / (lat_top - lat_bottom)
            y = y * height
            y = height - y
            y = y * yMult
        else:
            y = lat - lat_bottom
            y = y / (lat_top - lat_bottom)
            y = y * height
            y = height - y

        return int(x), int(y)

# X IS LONGITUDE, Y IS LATITUDE

    def getCoordPosition(self, coords):
        x = coords[1]
        y = coords[0]

        x, y = self.latlon_to_pixel(y, x, self.top, self.bottom, self.left, self.right, self.width, self.height, self.regional)
        
        return (x, y)
    
    def merge(self):
        self.ogImage.paste(self.image, (0, 23), self.image.convert('RGBA'))
        self.image = self.ogImage
