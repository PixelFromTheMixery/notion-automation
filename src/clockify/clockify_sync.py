from clockify.clockify_utils import ClockifyUtils
from utils.api_tools import make_call_with_retry
from utils.config import Config
from utils.files import read_yaml, write_yaml

class ClockifySync:
    def __init__(self):
        self.url = Config().clockify_url
    
    def setup(self):
        clockify_info = ClockifyUtils.get_workspace()
        user_info = make_call_with_retry("get", self.url)
        print(user_info)