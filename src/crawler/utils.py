import re

patterns = {
    "https://us.forums.blizzard.com/en/wow/c/": "category",
    "https://us.forums.blizzard.com/en/wow/t/": "topic",
}

http_pattern = "https://"

class ForumPage:
    def __init__(self, url, main_class = None, sub_class = None):
        self.url = url
        self.type = "other"
        self.main_class = main_class
        self.sub_class = sub_class
        self._set_attributes()

    def _set_attributes(self):
        
        for key in patterns.keys():
            if re.match(key, self.url):
                self.type = patterns[key]

        if self.is_category():
            split_url = self.url.split("/")
            self.main_class = split_url[-3]
            self.sub_class = split_url[-2]

    def is_topic(self):
        return self.type == "topic"
    
    def is_category(self):
        return self.type == "category"
    
    def is_just_category(self):
        return self.type == "category" and self.url.split("/") == 8
    
def is_absolute_path(url:str):
    return re.match(http_pattern, url)