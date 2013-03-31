from .wiggle import Entity

class VM(Entity):
    def __init__(self, wiggle):
        self._wiggle = wiggle
        self._resource = "vms"
    def start(self, uuid):
        return self._put(uuid, {"action": "start"})
    def stop(self, uuid):
        return self._put(uuid, {"action": "start"})
    def reboot(self, uuid):
        return self._put(uuid, {"action": "reboot"})
    def force_stop(self, uuid):
        return self._put(uuid, {"action": "start", "force": True})
    def force_reboot(self, uuid):
        return self._put(uuid, {"action": "reboot", "force": True})
    def list_snapsots(self, uuid):
        return self._wiggle.get_attr(self._resource, uuid, "snapshots")
    def make_snapsot(self, uuid, comment):
        return self._post(uuid, "snapshots", {"comment": comment})
    def delete_snapsot(self, uuid, snap):
        return self._delete_attr(uuid, "snapshots", snap)
