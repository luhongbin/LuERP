import pymssql  as pymssql
import time,os,datetime
import cx_Oracle

conn2 = pymssql.connect(host='192.168.0.2', user='sa', password='yh***microsoft***', database='trade',charset='utf8')
cur2 = conn2.cursor();

if not cur2:
    raise Exception('数据库连接失败！')

import ipaddress
import sys
def private_ip(ip):
    try:
    #判断 python 版本
        if sys.version_info[0] == 2:
            return ipaddress.ip_address(ip.strip().decode("utf-8")).is_private
        elif sys.version_info[0] == 3:
            return ipaddress.ip_address(bytes(ip.strip().encode("utf-8"))).is_private
    except Exception:
        return False

def getip(request):
    try:
        ip = request.META['HTTP_X_REAL_IP']
        if ip == '127.0.0.1':
            if request.META.has_key('HTTP_X_FORWARDED_FOR'):
                ip = request.META['HTTP_X_FORWARDED_FOR']
    except KeyError:
        ip = request.META.get('REMOTE_ADDR', None)
    try:
        if private_ip(ip) == True: #'127.0.0.1' or ip == '192.168.0.2':
            return ip,'中国','浙江省','公司内部'
        else:
            print(ip)
            import geoip2.database
            # response = geoip2.database.Reader('./GeoLite2-Country.mmdb')  # mmdb文件路径
            # reader= response.country(ip)
            # country=reader.country.names['zh-CN']

            response = geoip2.database.Reader('./GeoLite2-City.mmdb')  # mmdb文件路径
            reader= response.city(ip)
            country=reader.country.names['zh-CN']
            City=reader.city.names['zh-CN']
            subdivision=reader.subdivisions.most_specific.names['zh-CN']

            return ip,country,subdivision,City
    except Exception:
        return ip,'中国','浙江省','地址不详'

def maxinterid(table1):
    sql = "select id from [tablemaxid] where tablename=%s"
    cur2.execute(sql, (table1))
    row = cur2.fetchone()
    try:
        row0 = row[0]
    except Exception:
        row0 = 1
    today=datetime.datetime.now()
    maxid=today.year*1000000+today.month*10000
    if maxid<=row0:
        row0 += 1
    else:
        row0 = maxid + 1
    # sql = "UPDATE tablemaxid Set id=%d  WHERE tablename=%s" % (maxid,table1)
    #
    # cur2.execute(sql)
    # conn2.commit()  # 执行插入
    cur2.close
    return row0

def get_cursor():
    conn2 = pymssql.connect(host='192.168.0.2', user='sa', password='yh***microsoft***', database='trade',
                            charset='utf8')
    return conn2