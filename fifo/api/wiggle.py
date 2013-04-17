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


