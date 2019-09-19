import time
import logging
log_lock = logging.getLogger(__name__)
class Lock():
    Lock = False
    lock_def = None
    lock_text = ""
    timeout = -1
    timeout_def = None
    def __init__(self,timeout:int=-1,timeout_def:object=None):
        self.timeout = timeout
        self.timeout_def = timeout_def
    def __repr__(self):
        return "<{} : {}>".format(self.lock_text,self.lock_def)
    def acquire(self,lock_def:object=None,lock_text:str="")->bool:
        time_js = 0
        while self.Lock:
            print("Locking:{}".format(self.lock_text))
            log_lock.info("Locking:{}".format(self.lock_text))
            if self.timeout != -1:
                if time_js >= self.timeout:
                    if self.timeout_def != None:
                        self.timeout_def()
                    else:
                        return False
                time_js += 1
            time.sleep(1)

        self.Lock = True
        self.lock_def = lock_def
        self.lock_text = lock_text
        return True

    def release(self)->bool:
        self.Lock = False
        self.lock_def = None
        self.lock_text = ""
        return True