# -*- coding: utf-8 -*-
import json
import urllib
from urllib import request, parse
import numpy as np
from math import *

def crd2gridtuple(point):
    return tuple([round(i,3) for i in point])

def crd2gridstr(point):
    return "%.3f-%.3f" %tuple(point)



def gps_dist(lng1, lat1, lng2, lat2):
    lng1, lat1, lng2, lat2 = map(float, [lng1, lat1, lng2, lat2])
    lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])
    d1 = fabs(lat1 - lat2)
    d2 = fabs(lng1 - lng2)
    p = pow(sin(d1 / 2), 2) + cos(lat1) * cos(lat2) * pow(sin(d2 / 2), 2)
    return 6378137.0 * 2 * asin(sqrt(p))

def gps_dist_point(pnt1, pnt2):
    lng1, lat1 = pnt1
    lng2, lat2 = pnt2
    return gps_dist(lng1, lat1, lng2, lat2)

def gps_dist_list(line, lng, lat):
    line = np.array(line) if type(line) is not np.ndarray else line
    lng = float(lng); lat = float(lat)
    lng = radians(lng)
    lat = radians(lat)
    line = np.radians(line)

    d1 = np.abs(line[:,0] - lng)
    d2 = np.abs(line[:,1] - lat)
    p = np.sin(d1/2) ** 2 + np.cos(lat) * np.cos(line[:,1]) * np.sin(d2/2) **2
    return 6378137.0 * 2 * np.arcsin(np.sqrt(p))

def gps_dist_l2l(line1, line2):
    line1 = np.array(line1).astype(float)
    line2 = np.array(line2).astype(float)
    line1 = np.radians(line1)
    line2 = np.radians(line2)
    d1 = np.abs(line1[:,0] - line2[:,0])
    d2 = np.abs(line1[:,1] - line2[:,1])
    p = np.sin(d1/2) ** 2 + np.cos(line1[:,1]) * np.cos(line2[:,1]) * np.sin(d2/2)**2
    return 6378137.0 * 2 * np.arcsin(np.sqrt(p))

def gps_dist_list_thresh(line, lng, lat, thresh=1000):
    line = np.array(line) if type(line) is not np.ndarray else line
    dists = np.zeros(len(line)) + np.inf
    in_square = ((line - [lng, lat]) < [0.000016 * thresh, 0.00001 * thresh]).all(1)

    line = line[in_square]
    if len(line) == 0:
        return dists
    in_square_dists = gps_dist_list(line, lng, lat)
    in_square_dists[in_square_dists>1000] = np.inf
    dists[in_square] = in_square_dists
    return dists


def gps_dist_matrix(line):
    n = len(line)
    dists = np.zeros([n, n])
    for i, point in enumerate(line):
        print(i)
        dists[i] = gps_dist_list_thresh(line, point[0], point[1])
    return dists


x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 扁率


class Geocoding:
    def __init__(self, api_key):
        self.api_key = api_key

    def geocode(self, address):
        """
        利用高德geocoding服务解析地址获取位置坐标
        :param address:需要解析的地址
        :return:
        """
        geocoding = {'s': 'rsv3',
                     'key': self.api_key,
                     'city': '全国',
                     'address': address}
        geocoding = urllib.parse.urlencode(geocoding)
        ret = urllib.request.urlopen("%s?%s" % ("http://restapi.amap.com/v3/geocode/geo", geocoding))

        if ret.getcode() == 200:
            res = ret.read()
            json_obj = json.loads(res)
            if json_obj['status'] == '1' and int(json_obj['count']) >= 1:
                geocodes = json_obj['geocodes'][0]
                lng = float(geocodes.get('location').split(',')[0])
                lat = float(geocodes.get('location').split(',')[1])
                return [lng, lat]
            else:
                return None
        else:
            return None


def gcj2bd(lng, lat):
    """
    火星坐标系(GCJ-02)转百度坐标系(BD-09)
    谷歌、高德——>百度
    :param lng:火星坐标经度
    :param lat:火星坐标纬度
    :return:
    """
    z = sqrt(lng * lng + lat * lat) + 0.00002 * sin(lat * x_pi)
    theta = atan2(lat, lng) + 0.000003 * cos(lng * x_pi)
    bd_lng = z * cos(theta) + 0.0065
    bd_lat = z * sin(theta) + 0.006
    return [bd_lng, bd_lat]


def bd2gcj(bd_lon, bd_lat):
    """
    百度坐标系(BD-09)转火星坐标系(GCJ-02)
    百度——>谷歌、高德
    :param bd_lat:百度坐标纬度
    :param bd_lon:百度坐标经度
    :return:转换后的坐标列表形式
    """
    x = bd_lon - 0.0065
    y = bd_lat - 0.006
    z = sqrt(x * x + y * y) - 0.00002 * sin(y * x_pi)
    theta = atan2(y, x) - 0.000003 * cos(x * x_pi)
    gg_lng = z * cos(theta)
    gg_lat = z * sin(theta)
    return [gg_lng, gg_lat]


def wgs2gcj(lng, lat):
    """
    WGS84转GCJ02(火星坐标系)
    :param lng:WGS84坐标系的经度
    :param lat:WGS84坐标系的纬度
    :return:
    """
    if out_of_china(lng, lat):  # 判断是否在国内
        return lng, lat
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [mglng, mglat]


def gcj2wgs(lng, lat):
    """
    GCJ02(火星坐标系)转GPS84
    :param lng:火星坐标系的经度
    :param lat:火星坐标系纬度
    :return:
    """
    if out_of_china(lng, lat):
        return lng, lat
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng, lat * 2 - mglat]


def bd2wgs(bd_lon, bd_lat):
    lon, lat = bd2gcj(bd_lon, bd_lat)
    return gcj2wgs(lon, lat)


def wgs2bd(lon, lat):
    lon, lat = wgs2gcj(lon, lat)
    return gcj2bd(lon, lat)


def _transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * sqrt(fabs(lng))
    ret += (20.0 * sin(6.0 * lng * pi) + 20.0 *
            sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * sin(lat * pi) + 40.0 *
            sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * sin(lat / 12.0 * pi) + 320 *
            sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret


def _transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * sqrt(fabs(lng))
    ret += (20.0 * sin(6.0 * lng * pi) + 20.0 *
            sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * sin(lng * pi) + 40.0 *
            sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * sin(lng / 12.0 * pi) + 300.0 *
            sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret


def out_of_china(lng, lat):
    """
    判断是否在国内，不在国内不做偏移
    :param lng:
    :param lat:
    :return:
    """
    return not (lng > 73.66 and lng < 135.05 and lat > 3.86 and lat < 53.55)

