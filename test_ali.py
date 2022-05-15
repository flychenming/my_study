# code=utf-8
import csv

import os

path = "config"  # 文件夹目录
files = os.listdir(path)  # 得到文件夹下的所有文件名称
s = set()
for file in files:  # 遍历文件夹
    if not os.path.isdir(file):  # 判断是否是文件夹，不是文件夹才打开
        try:
            f = open(path + "/" + file)  # 打开文件
            for line in f.readlines():  # 遍历文件，一行行遍历，读取文本
                # print(line)
                if 'redis' in line and 'port' not in line and 'password' not in line:
                    ss = line.split('=')
                    if len(ss) == 2 and len(ss[1]) > 9:
                        s.add(ss[1].replace('\n', ''))
        except:
            f = open(path + "/" + file, encoding='gb2312')  # 打开文件
            for line in f.readlines():  # 遍历文件，一行行遍历，读取文本
                if 'redis' in line and 'port' not in line and 'password' not in line:
                    ss = line.split('=')
                    if len(ss) == 2 and len(ss[1]) > 9:
                        s.add(ss[1].replace('\n', ''))
print(s)  # 打印结果

file = open('阿里云redis.csv')
csvreader = csv.reader(file)
header = next(csvreader)
# print(header)
header.append('')
header.append('1.0是否使用')
data = []
for row in csvreader:
    print(row)
    fg = False
    for item in row:
        for sss in s:
            if sss in item:
                fg = True
    row.append('是' if fg else '否')
    data.append(row)

filename = '阿里云redis_out.csv'
with open(filename, 'w', newline="") as file:
    csvwriter = csv.writer(file)  # 2. create a csvwriter object
    csvwriter.writerow(header)  # 4. write the header
    csvwriter.writerows(data)  # 5. write the rest of the data
