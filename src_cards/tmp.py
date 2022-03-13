import os

os.environ["EES_AUTH_CLIENT_ID"] = "u2v2hsh07xvju1eex8eh"
os.environ["EES_AUTH_CLIENT_SECRET"] = "tplzi3t8v6okghbrrhts0644dep5ns"
os.environ["EES_API_PREFIX"] = "/2.0"
os.environ["EES_POS_API_HOST"] = "pos.sandbox.uk.eagleeye.com"
os.environ["EES_RESOURCES_API_HOST"] = "resources.sandbox.uk.eagleeye.com"
os.environ["EES_WALLET_API_HOST"] = "wallet.sandbox.uk.eagleeye.com"


import eagleeyeair as ee


print("before")
print(ee.wallet.get_wallet_identities_by_wallet_id(115205616))
ee.wallet.update_wallet_identity_status_active("115205616", "88682691")
print("after")
print(ee.wallet.get_wallet_identities_by_wallet_id(115205616))
