import os
import sys
import math
import time
from datetime import datetime
import simplejson as json
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from geopy import geocoders


address=str(sys.argv[1]) #Location (City name, adress...)
halfradius=float(sys.argv[2]) #Radius in Km of the Bounding Box
outputlocation=str(sys.argv[3])
datereq = datetime.utcnow().strftime("%d%m%Y")



ckey ="Your Consumer Key"
csecret = "Your Consumer Secret"
atoken = "Your API Token"
asecret = "Your API Secret"

class listener(StreamListener):
    def on_data(self, data):
        data = json.loads(data)
        logfile = open(os.path.join(outputlocation, address + "-" + datereq + "-Request-Peter.csv"), "a")
        logfile2 = open(os.path.join(outputlocation, datereq + "-Tweets.csv"), "a")
        tweet_date = unicode(data['created_at']).encode("ascii", "ignore")[:10] + " " + unicode(data['created_at']).encode("ascii", "ignore")[-4:]

        tweet_time = unicode(data['created_at']).encode("ascii", "ignore")[11:-11]
        user_id = unicode(data['user']['id']).encode("ascii", "ignore")
        text_id = unicode(data['id']).encode("ascii", "ignore")
        user_location = unicode(data['user']['location']).encode("ascii", "ignore")
        user_lang = unicode(data['user']['lang']).encode("ascii", "ignore")
        text_msg = unicode(data['text']).encode("utf8", "ignore").replace(',', ' ')

        if data['coordinates'] is None:
            #print "[No geotag for this tweet]"
            longitude = ""
            latitude = ""
        else:
            coord = unicode(data['coordinates']['coordinates']).encode("ascii", "ignore")
            longitude = coord[:coord.rfind(',')].replace("[", "")
            latitude = coord.split(" ")[1].replace("]", "")

            stream_log = latitude + "," + longitude + "," + tweet_date + "," + tweet_time + "," + user_id + "," + user_location + "," + user_lang + "," + text_id + "," + text_msg
            stream_log = stream_log.replace('\n', ' ')

            csv_output = latitude + "," + longitude + "," + text_msg + "," + tweet_date + ":" + tweet_time
            print csv_output
            print >> logfile2, csv_output
            #print stream_log
            print >> logfile, stream_log
            logfile.close()
        return True

    def on_error(self, status):
        print (status)


# degrees to radians
def deg2rad(degrees):
    return math.pi * degrees / 180.0


# radians to degrees
def rad2deg(radians):
    return 180.0*radians/math.pi

# Semi-axes of WGS-84 geoidal reference
WGS84_a = 6378137.0  # Major semiaxis [m]
WGS84_b = 6356752.3  # Minor semiaxis [m]


# Earth radius at a given latitude, according to the WGS-84 ellipsoid [m]
def WGS84EarthRadius(lat):
    # http://en.wikipedia.org/wiki/Earth_radius
    An = WGS84_a*WGS84_a * math.cos(lat)
    Bn = WGS84_b*WGS84_b * math.sin(lat)
    Ad = WGS84_a * math.cos(lat)
    Bd = WGS84_b * math.sin(lat)
    return math.sqrt( (An*An + Bn*Bn)/(Ad*Ad + Bd*Bd) )


# Bounding box surrounding the point at given coordinates,
# assuming local approximation of Earth surface as a sphere
# of radius given by WGS84
def boundingBox(latitudeInDegrees, longitudeInDegrees, halfSideInKm):
    lat = deg2rad(latitudeInDegrees)
    lon = deg2rad(longitudeInDegrees)
    halfSide = 1000 * halfSideInKm

    # Radius of Earth at given latitude
    radius = WGS84EarthRadius(lat)
    # Radius of the parallel at given latitude
    pradius = radius * math.cos(lat)

    latMin = lat - halfSide / radius
    latMax = lat + halfSide / radius
    lonMin = lon - halfSide / pradius
    lonMax = lon + halfSide / pradius

    return (rad2deg(latMin), rad2deg(lonMin), rad2deg(latMax), rad2deg(lonMax))

def main():
    g = geocoders.GoogleV3()
    #place, (lat, lng) = g.geocode(address)
    
    lat = 38.9071923
    lng = -77.0368707

    location = [boundingBox(lng, lat, halfradius)[0], boundingBox(lng, lat, halfradius)[1],
                boundingBox(lng, lat, halfradius)[2], boundingBox(lng, lat, halfradius)[3]]
    #print "Location of " + address + " :", lat, lng
    auth = OAuthHandler(ckey, csecret)
    auth.set_access_token(atoken, asecret)
    twitterStream = Stream(auth, listener())
    twitterStream.filter(locations=location)
main()
