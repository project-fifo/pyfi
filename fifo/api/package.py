from wiggle import Entity

class Package(Entity):
    def __init__(self, wiggle):
        self._wiggle = wiggle
        self._resource = "packages"
