from ngo_scraper.tasks import notify



class Notify:
    """
    send slack notification
    """
    def __init__(self, webhook_url:str):
        self.webhook_url = webhook_url
    
    def alert(self, message:str):
        """
        send message to slack
        """
        notify.delay(message, self.webhook_url)
        return 0
    
    @staticmethod
    def error(message:str):
        """
        wrap message with slack markdown
        """
        return f"ERROR \nReason: \n```{message}```"
    
    @staticmethod
    def info(message:str):
        """
        wrap message with slack markdown
        """
        return f"INFO \nMessage: \n```{message}```"
    
    @staticmethod
    def warn(message:str):
        """
        wrap message with slack markdown
        """
        return f"WARNING \nMessage: \n```{message}````"
    
    def success(self, message:str):
        """
        wrap message with slack markdown
        """
        return f"SUCCESS \nMessage: \n```{message}```"