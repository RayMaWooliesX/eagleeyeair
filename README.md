# Eagle Eye Air

This package provides Python SDK for accessing APIs provided by [the eagleeye platform](https://status.eagleeye.com).

## Setup environment

To use the package, we need to first configure os with following variables:

* `EES_AUTH_CLIENT_ID`: this is your `eagleeye` client id
* `EES_AUTH_CLIENT_SECRET`: your `eagleeye` secret, will be used for payload encryption
* `EES_API_PREFIX`: api version to use, default to `/2.0`
* `EES_POS_API_HOST`: hostname of the POS API server
* `EES_WALLET_API_HOST`: hostname of the Wallet API server
* `EES_RESOURCES_API_HOST`: hostname of the Resources API server

## Invoke API

With environment setup, you can invoke the APIs as shown below:

```python
import json
from eagleeyeair import resources

print(json.dumps(resources.list_campaigns(limit=5), indent=2))
```
