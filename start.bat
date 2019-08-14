@echo updating backend code
@git pull origin master
@echo reload backend-server
@start python.exe main.py -c config.ini