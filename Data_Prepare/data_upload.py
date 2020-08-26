import os

path = "E:/video_list_2/video_list_2"
file_list = os.listdir(path)

cmd = """cd D:
/cd /Program Files/MongoDB/bin
"""
fp = os.popen(cmd)
res = fp.read()

for i in range(len(file_list)):
    cmd = "mongofiles -d video_data put E:/video_list_2/video_list_2/{0}".format(file_list[i])
    fp = os.popen(cmd)
    res = fp.read()
    stat = fp.close()
print(cmd)