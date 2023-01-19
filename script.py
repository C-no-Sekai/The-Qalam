import os
count = 0
for file_name in os.listdir('.'):
	if file_name[-2:] == 'js' or file_name[-3:] == 'css' or file_name[-4:] == 'html':
		with open(file_name, 'r') as f:
			count += len(f.read().split('\n'))
print(count)
