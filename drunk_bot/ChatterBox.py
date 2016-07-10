from cleverbot.cleverbot import Cleverbot


class Chatty(Cleverbot):
    def __init__(self):
        self.name = "Drunk Bot"
        super().__init__()

    def chat(self, convoy: str):
        if "your" in convoy and "name" in convoy and "what" in convoy:
            return "My name is %s" % self.name
        return self.ask(convoy)
