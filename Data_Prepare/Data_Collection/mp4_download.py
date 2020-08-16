#-*- coding: utf-8 -*-
import os
import wget

def createFolder(directory):
	try:
		if not os.path.exists(directory): # 폴더 존재하지 않으면 
			os.makedirs(directory)	# 폴더 생성
	except OSError:
		print("Error: While Creating Directory" + directory)

file_count = 0 # 파일 갯수
folder_num = 0 # 폴더 번호
with open("sign_language.txt", encoding='CP949') as f:
	while True:
		# sign_language.txt에서 한 줄씩 읽어오기
	    line = f.readline().strip().split('\t')

	    # 파일 100개마다 폴더 생성
	    if file_count%100 == 0:

	    	# 파일 100개당 폴더 번호 1씩 증가 
	    	folder_num += 1

	    	# 새로운 폴더 경로 만들기 & 생성
	    	output_directory = '/Users/krrap/Desktop/nothing/korean_' + str(folder_num)
	    	createFolder(output_directory)
	    else:
	    	# 100개 안채워졌으면 그대로(아마 없어도 될듯..?)
	    	output_directory = '/Users/krrap/Desktop/nothing/korean_' + str(folder_num)

	    file_count += 1

	    # 끝까지 왔으면
	    if not line:
	    	break
	    
	    url = line[0]
	    # title = line[1]
	    # mp4_title = line[2] # wget 자체가 /로 split해서 제일 마지막거를 이름으로 저장. mp4_title 필요 없어짐.
	    # view = line[3]

	    wget.download(url, out=output_directory)

