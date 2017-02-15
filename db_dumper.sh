#!/bin/bash

# dump geo information from db to text files
mysql -u root -p -N -e 'select provinceid, province from ChinaToponyms.provinces;' > ./db_dump_provinces.txt
mysql -u root -p -N -e 'select cityid, city, provinceid from ChinaToponyms.cities;' > ./db_dump_cities.txt
mysql -u root -p -N -e 'select areaid, area, cityid from ChinaToponyms.areas;' > ./db_dump_areas.txt
