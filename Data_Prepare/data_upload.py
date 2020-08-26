<<<<<<< HEAD
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
=======
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
>>>>>>> 07d7c1f9f4000b7ac68be4ab2aa9f2b57ee0cc50
print(cmd)