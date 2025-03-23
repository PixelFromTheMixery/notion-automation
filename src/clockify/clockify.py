from utils.api_tools import make_call_with_retry

class Clockify:
    def __init__(self):
        self.url = "https://api.clockify.me/api/v1/"
    
    def get_user(self):
        self.url += "user"
        user_info = make_call_with_retry("get", self.url)
        print(user_info)