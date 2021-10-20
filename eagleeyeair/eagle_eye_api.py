import hashlib
import json
import logging
import urllib.parse
import urllib.request


logger = logging.getLogger(__name__)


class EagleEyeApiError(RuntimeError):
    def __init__(self, e: urllib.error.HTTPError):
        self.status_code = e.code
        self.reason = e.reason
        try:
            data = json.load(e)
            self.error_code = data["errorCode"]
            self.error_message = data["errorMessage"]
        except:
            self.error_code = ""
            self.error_message = "Unknown Error"

    def __str__(self):
        return json.dumps(
            dict(error_code=self.error_code, error_message=self.error_message)
        )


class EagleEyeApi:
    def __init__(self, host, prefix, client_id, secret):
        self.host = host
        self.prefix = prefix
        self.client_id = client_id
        self.secret = secret

    def calculate_hash(self, server_path: str, payload):
        # logger.debug(
        #     f"calculating hash using:\nprefix\n{self.prefix}\nserver_path\n{server_path}\npayload\n{payload}\nsecret\n{self.secret}"
        # )
        data = f"{self.prefix}{server_path}{payload}{self.secret}".encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    def send_request(
        self, method, url_template: str, params={}, query={}, headers={}, data=None
    ):
        server_path = url_template.format(params)
        scheme = "https"
        q_str = urllib.parse.urlencode(query)
        url = urllib.parse.urlunparse(
            (scheme, self.host, f"{self.prefix}{server_path}", None, q_str, None)
        )
        payload = "" if data is None else json.dumps(data)
        req = urllib.request.Request(
            url, payload.encode("utf-8"), headers=headers, method=method
        )
        value = server_path if not q_str else f"{server_path}?{q_str}"
        hash = self.calculate_hash(value, payload)
        req.add_header("X-EES-AUTH-CLIENT-ID", self.client_id)
        req.add_header("X-EES-AUTH-HASH", hash)
        req.add_header("Content-Type", "application/json")
        logger.debug(url)
        logger.debug(urllib.parse.urlsplit(url))
        logger.info(req.headers)
        logger.debug(f"{req.method} {req.full_url}")
        try:
            resp = urllib.request.urlopen(req)
            if resp.status == 204:
                return ''
            if resp.headers.get('content-type', '').find('application/json') >= 0:
                data = json.load(resp)
            else:
                data = resp.read()
        except urllib.error.HTTPError as e:
            raise EagleEyeApiError(e)
        return data

    def get(self, url_template, params={}, query={}, headers={}):
        return self.send_request("GET", url_template, params, query, headers)

    def post(self, url_template, params={}, query={}, headers={}, data=None):
        return self.send_request("POST", url_template, params, query, headers, data)

    def delete(self, url_template, params={}, query={}, headers={}):
        return self.send_request("DELETE", url_template, params, query, headers)

    def put(self, url_template, params={}, query={}, headers={}, data=None):
        return self.send_request("PUT", url_template, params, query, headers, data)

    def patch(self, url_template, params={}, query={}, headers={}, data=None):
        return self.send_request("PATCH", url_template, params, query, headers, data)
