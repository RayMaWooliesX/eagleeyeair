import os

from .pos import EagleEyePos
from .resources import EagleEyeResources
from .wallet import EagleEyeWallet

client_id = os.environ.get("EES_AUTH_CLIENT_ID", "")
secret = os.environ.get("EES_AUTH_CLIENT_SECRET", "")
prefix = os.environ.get("EES_API_PREFIX", "")
pos_host = os.environ.get("EES_POS_API_HOST", "")
resources_host = os.environ.get("EES_RESOURCES_API_HOST", "")
wallet_host = os.environ.get("EES_WALLET_API_HOST", "")

pos = EagleEyePos(pos_host, prefix, client_id, secret)
resources = EagleEyeResources(resources_host, prefix, client_id, secret)
wallet = EagleEyeWallet(wallet_host, prefix, client_id, secret)

__all__ = [
    EagleEyePos,
    EagleEyeResources,
    EagleEyeWallet,
    pos,
    resources,
    wallet,
]
