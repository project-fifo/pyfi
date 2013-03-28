import http.client
import json
from pprint import pprint


class Wiggle:
    def __init__(self, host, user, pw, token):
        self.conn = http.client.HTTPConnection(host);
        self.headers = {"Content-type": "application/json;charset=UTF-8",
                        "Accept": "application/json"}
        if token:
            if not self.set_token(token):
                connect(user, pw)
        else:
            self.connect(user, pw)

    def get_token(self):
        return self._token

    def set_token(self, token):
        self._token = token
        self.headers["X-Snarl-Token"] = self._token
        return self.get("sessions", token)

    def get(self, resource, entity):
        self.conn.request("GET", "/api/0.1.0/" + resource + "/" + entity, "", self.headers)
        response = self.conn.getresponse()
        if (response.status != 200):
            return False
        else:
            return json.loads(str(response.read(), "utf8"))

    def delete(self, resource, entity):
        self.conn.request("DELETE", "/api/0.1.0/" + resource + "/" + entity, "", self.headers)
        response = self.conn.getresponse()
        if (response.status != 200):
            return False
        else:
            return True

    def delete_attr(self, resource, entity, attr):
        self.conn.request("DELETE", "/api/0.1.0/" + resource + "/" + entity + "/" + attr, "", self.headers)
        response = self.conn.getresponse()
        if (response.status != 200):
            return False
        else:
            return True

    def get_attr(self, resource, entity, attr):
        self.conn.request("GET", "/api/0.1.0/" + resource + "/" + entity + "/" + attr, "", self.headers)
        response = self.conn.getresponse()
        if (response.status != 200):
            return False
        else:
            return json.loads(str(response.read(), "utf8"))

    def put(self, resource, entity, body):
        self.conn.request("PUT", "/api/0.1.0/" + resource + "/" + entity, json.dumps(body), self.headers)
        response = self.conn.getresponse()
        if (response.status != 200):
            return False
        else:
            return json.loads(str(response.read(), "utf8"))

    def post(self, resource, body):
        self.conn.request("POST", "/api/0.1.0/" + resource,  json.dumps(body), self.headers)
        response = self.conn.getresponse()
        if (response.status == 303):
            newurl = response.getheader('Location')
            self.conn.request("POST", newurl,  json.dumps(body), self.headers)
            response = self.conn.getresponse()
            if (response.status != 200):
                return False
            else:
                return json.loads(str(response.read(), "utf8"))
        elif (response.status == 200):
            return json.loads(str(response.read(), "utf8"))
        else:
            return False

    def list(self, resource):
        self.conn.request("GET", "/api/0.1.0/" + resource, "", self.headers)
        response = self.conn.getresponse()
        if (response.status != 200):
            return False
        else:
            return json.loads(str(response.read(), "utf8"))

    def connect(self, user, pw):
        self.conn.request("POST", "/api/0.1.0/sessions",  json.dumps({"user":user, "password": pw}), self.headers)
        response = self.conn.getresponse()
        if (response.status == 303):
            self._token = response.getheader("X-Snarl-Token")
            self.headers["X-Snarl-Token"] = self._token
            return self._token
        else:
            return False


class Cloud:
    def __init__(self, wiggle):
        self._wiggle = wiggle
    def status(self):
        return self._wiggle.list("cloud")
    def connection(self):
        return self._wiggle.get("cloud", "connection")

class Entity:
    def __init__(self, wiggle):
        self._resource = "none"
        self._wiggle = wiggle
    def _put(self, uuid, body):
        return self._wiggle.put(self._resource, uuid, body)
    def _post(self, uuid, body):
        return self._wiggle.put(self._resource, uuid, body)
    def _delete_attr(self, uuid, attr):
        return self._wiggle.delete_attr(self._resource, uuid, attr)
    def list(self):
        return self._wiggle.list(self._resource)
    def get(self, uuid):
        return self._wiggle.get(self._resource, uuid)
    def delete(self, uuid):
        return self._wiggle.delete(self._resource, uuid)
    def get_metadata(self, uuid):
        return self._wiggle.get_attr(self._resource, uuid, "metadata")
    def set_metadata(self, uuid, path, k, v):
        return self._wiggle.put(self._resource, uuid, "metadata" + path , {k: v})
    def delete_metadata(self, uuid, path, k):
        return self._wiggle.put(self._resource, uuid, "metadata" + path, {k: v})

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

class Package(Entity):
    def __init__(self, wiggle):
        self._wiggle = wiggle
        self._resource = "packages"
