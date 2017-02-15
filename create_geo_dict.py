# -*- coding: utf-8 -*-
# File: create_geo_dict.py (python3)
# Author: Bowen LU <Bowen.Lu@mail.com>
# Date: 15.01.2017

import re
from collections import OrderedDict


city_skipwords = ['市辖区', '市', '县', '省直辖行政单位', '省直辖县级行政单位']
area_skipwords = ['市辖区']

# load province, city and area information
province_dict = OrderedDict()
with open('./db_dump_provinces.txt') as f:
    items = f.readlines()
    for item in items:
        item = item.replace(u'\u3000', '').rstrip('\n')
        # key: provinceId, value: provinceName
        province_dict[item.split()[0]] = item.split()[1]

city_dict = OrderedDict()
with open('./db_dump_cities.txt') as f:
    items = f.readlines()
    for item in items:
        item = item.replace(u'\u3000', '').rstrip('\n')
        # key: cityId, value: [cityName, provinceId]
        city_dict[item.split()[0]] = [item.split()[1], item.split()[2]]

area_dict = OrderedDict()
with open('./db_dump_areas.txt') as f:
    items = f.readlines()
    for item in items:
        item = item.replace(u'\u3000', '').rstrip('\n')
        # key: areaId, value: [areaName, cityId]
        area_dict[item.split()[0]] = [item.split()[1], item.split()[2]]

geo_dict = OrderedDict()

# insert provinces to geo_dict
for provinceId in province_dict:
    provinceName = province_dict[provinceId]
    geo_dict[provinceName] = OrderedDict()

# insert cities to geo_dict[province]
for cityId in city_dict:
    cityName = city_dict[cityId][0]
    provinceId = city_dict[cityId][1]
    provinceName = province_dict[provinceId]
    if cityName in city_skipwords:
        cityName = provinceName
    geo_dict[provinceName][cityName] = []

# insert areas to geo_dict[province][city]
for areaId in area_dict:
    areaName = area_dict[areaId][0]
    cityId = area_dict[areaId][1]
    cityName = city_dict[cityId][0]
    provinceId = city_dict[cityId][1]
    provinceName = province_dict[provinceId]
    if cityName in city_skipwords:
        cityName = provinceName
    if areaName in area_skipwords:
        areaName = cityName
    geo_dict[provinceName][cityName].append(areaName)

with open('./geo_dict.txt', 'w') as f:
    f.write(repr(geo_dict))
print('>> ./geo_dict.txt generated.')

# geo_dict_short
geo_dict_short = OrderedDict()



# shorten functions
def short(name, level):
    if level == 'province':
        keywords = ['自治区', '特别行政区', '省', '市']
        for keyword in keywords:
            name = name.replace('壮族', '')
            name = name.replace('回族', '')
            name = name.replace('维吾尔', '')
            name = name.replace(keyword, '')
    elif level == 'city':
        keywords = ['自治州', '地区', '市', '盟']
        for keyword in keywords:
            if name not in city_skipwords and len(name) >= 3:
                if re.compile('.*'+keyword+'$').match(name):
                    name = name.replace(keyword, '')
        with open('./ethnic_dict.txt', 'r') as f:
            for item in f:
                item = item.rstrip('\n')
                name = name.replace(item, '')
                if len(item) >= 3:
                    name = name.replace(item.rstrip('族\n'), '')
    elif level == 'area':
        keywords = ['自治县', '矿区', '区', '县', '市']
        for keyword in keywords:
            if name not in area_skipwords and len(name) >= 3:
                if re.compile('.*'+keyword+'$').match(name):
                    name = name.replace(keyword, '')
        with open('./ethnic_dict.txt', 'r') as f:
            for item in f:
                item = item.rstrip('\n')
                name = name.replace(item, '')
                if len(item) >= 3 and name.replace(item.rstrip('族\n'), '') != '':
                    name = name.replace(item.rstrip('族\n'), '')
    return name


# filter: province
# remove keywords from province names
for province in geo_dict:
    geo_dict_short[short(province, 'province')] = OrderedDict()
# filter: city
for province in geo_dict:
    for city in geo_dict[province]:
        geo_dict_short[short(province, 'province')][short(city, 'city')] = []
# filter: area
for province in geo_dict:
    for city in geo_dict[province]:
        for area in geo_dict[province][city]:
            if short(area, 'area') != '':
                geo_dict_short[short(province, 'province')][short(city, 'city')].append(short(area, 'area'))
            else:
                geo_dict_short[short(province, 'province')][short(city, 'city')].append(area)

with open('./geo_dict_short.txt', 'w') as f:
    # f.write('exec("from collections import OrderedDict"),')
    f.write(repr(geo_dict_short))
print('>> ./geo_dict_short.txt generated.')

# generate list file for jieba segmentation.
with open('./geo_dict_short_jieba.txt', 'w') as f:
    for province in geo_dict_short:
        f.write('%s 250 Loc\n' % province)
        for city in geo_dict_short[province]:
            if city not in city_skipwords:
                f.write('%s 250 Loc\n' % city)
            for area in geo_dict_short[province][city]:
                if area not in area_skipwords:
                    f.write('%s 250 Loc\n' % area)
print('>> ./geo_dict_short_jieba.txt generated.')

# print
# for province in geo_dict_short:
    # print('*'*10)
    # print(province)
    # for city in geo_dict_short[province]:
        # print(' '*5 + city)
        # for area in geo_dict_short[province][city]:
            # print(' '*10 + area)
