import abc

class BaseAgent:

    def __init__(self):
        pass

    @abc.abstractmethod
    def tell(self, speaker_name, message):
        """Say somthing to this agent"""

    @abc.abstractmethod
    def listen(self):
        """Illicit a response from this agent"""

