import hashlib
import json
import urllib.parse
import urllib.request

class EagleEyeApi:
    def __init__(self, host, prefix, client_id, secret):
        self.host = host
        self.prefix = prefix
        self.client_id = client_id
        self.secret = secret
    def calculate_hash(self, server_path: str, payload):
        # print(f'calculating hash using:\nprefix\n{self.prefix}\nserver_path\n{server_path}\npayload\n{payload}\nsecret\n{self.secret}')
        data = f'{self.prefix}{server_path}{payload}{self.secret}'.encode('utf-8')
        return hashlib.sha256(data).hexdigest()
    def send_request(self, method, url_template: str, params={}, query={}, headers={}, data=None):
        server_path = url_template.format(params)
        scheme = 'https'
        q_str = urllib.parse.urlencode(query)
        url = urllib.parse.urlunparse((
            scheme,
            self.host,
            f'{self.prefix}{server_path}',
            None,
            q_str,
            None))
        payload = '' if data is None else json.dumps(data)
        req = urllib.request.Request(url, payload.encode('utf-8'), headers=headers, method=method)
        value = server_path if not q_str else f'{server_path}?{q_str}'
        hash = self.calculate_hash(value, payload)
        req.add_header('X-EES-AUTH-CLIENT-ID', self.client_id)
        req.add_header('X-EES-AUTH-HASH', hash)
        req.add_header('Content-Type', 'application/json')
        print(req)
        print(url), print(urllib.parse.urlsplit(url))
        print(req.headers)
        print(f'{req.method} {req.full_url}')
        print(hash)
        resp = urllib.request.urlopen(req)
        data = json.load(resp)
        return data
    def get(self, url_template, params={}, query={}, headers={}):
        return self.send_request('GET', url_template, params, query, headers)
    def post(self, url_template, params={}, query={}, headers={}, data=None):
        return self.send_request('POST', url_template, params, query, headers, data)
    def delete(self, url_template, params={}, query={}, headers={}):
        return self.send_request('DELETE', url_template, params, query, headers)
    def put(self, url_template, params={}, query={}, headers={}, data={}):
        return self.send_request('PUT', url_template, params, query, headers, data)
    def patch(self, url_template, params={}, query={}, headers={}, data={}):
        return self.send_request('PATCH', url_template, params, query, headers, data)
