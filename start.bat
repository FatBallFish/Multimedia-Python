@echo updating backend code
@cd Multimedia-Python
@git pull origin master
@echo reload backend-server
@start python.exe main.py -c config.ini