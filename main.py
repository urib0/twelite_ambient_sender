#!/usr/bin/env python3
# python3.7で動作確認済み

import ambient
import time
import json
import datetime as dt
import random
import requests

REPETITIONS = 3

def conv(data):
    if data[0] in {"tm", "hu"}:
        return int(data[1]) / 100.0
    elif data[0] in {"ba"}:
        return int(data[1]) / 1000.0
    else:
        return int(data[1])

# 設定値読み込み
f = open("/home/pi/work/twelite_ambient_sender/config.json", "r")
conf = json.loads(f.read())
f.close()

am = ambient.Ambient(conf["ambient_channel"], conf["ambient_key_write"])

for device in conf["devices"]:
    filename = conf["logdir"] + "/" + device["sensor_name"] + "/" + device["sensor_name"] + "_" + dt.datetime.now().strftime("%Y-%m-%d") + ".csv"

    device = conf["devices"][0]

    f = open(filename,"r")
    # ログの末尾1行をとってくる
    lines = f.readlines()[-1:][0][:-1]
    f.close

    data_list = lines.split(",")[1].split(":")
    data_num = len(data_list)
    data_dic={}
    if len(device["sensors"]) == data_num - 10:
        for i in range(data_num):
            # センサ名と数字のペアができる ex) ["temp","2657"]
            data_pair = data_list[i].split("=")

            if data_pair[0] in device["sensors"]:
                # 送信すべきambientのデータ番号が存在することを確認 ex) d1~d8
                data_dic[device["sensors"][data_pair[0]]] = conv(data_pair)
    else:
        break

# ambient送信処理
for i in range(REPETITIONS):
    try:
        res = am.send(data_dic, timeout=3)
        print('sent to Ambient (ret = %d)' % res.status_code)
        if res.status_code == 200:
            break
        time.sleep(random.randint(1,10))
    except requests.exceptions.RequestException as e:
        print('request failed: ', e)

