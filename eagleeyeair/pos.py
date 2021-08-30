from .eagle_eye_api import EagleEyeApi


class EagleEyePos(EagleEyeApi):
    def open_wallet(self, data):
        return self.post(f"/connect/wallet/open", data=data)

    def settle_transaction(self, data):
        return self.post(f"/connect/wallet/settle", data=data)

    def amend_wallet_transaction(self, transaction_id, data):
        return self.patch(
            f"/connect/wallet/transaction",
            headers={"X-EES-TRANSACTION-ID": transaction_id},
            data=data,
        )

    def get_wallet_transaction(self, transaction_id):
        return self.get(
            f"/connect/wallet/transaction",
            headers={"X-EES-TRANSACTION-ID": transaction_id},
        )

    def refund_wallet_transaction(self, data):
        return self.post(f"/connect/wallet/refund", data=data)

    def unlock_wallet(self, data):
        return self.post(f"/connect/wallet/unlock", data=data)

    def spend_calculate(self, data):
        return self.post(f"/connect/wallet/spend/calculate", data=data)

    def spend(self, data):
        return self.post(f"/connect/wallet/spend", data=data)

    def spend_void(self, data):
        return self.post(f"/connect/wallet/spend/void", data=data)

    def create_account(self, data):
        return self.post(f"/connect/account", data=data)

    def verify_account(self, data):
        return self.post(f"/connect/account/verify", data=data)

    def activate_account(self, data):
        return self.post(f"/connect/account/activate", data=data)

    def load_account(self, data):
        return self.post(f"/connect/account/load", data=data)

    def unlock_account(self, data):
        return self.post(f"/connect/account/unlock", data=data)

    def lock_account(self, data):
        return self.post(f"/connect/account/lock", data=data)

    def redeem_account(self, data):
        return self.post(f"/connect/account/redeem", data=data)

    def debit_account(self, data):
        return self.post(f"/connect/account/debit", data=data)

    def credit_account(self, data):
        return self.post(f"/connect/account/credit", data=data)

    def earn_points(self, data):
        return self.post(f"/connect/account/earn", data=data)

    def spend_points(self, data):
        return self.post(f"/connect/account/spend", data=data)

    def stamp_account(self, data):
        return self.post(f"/connect/account/stamp", data=data)

    def unredeem_account_transaction(self, data):
        return self.patch(f"/connect/account/unredeem", data=data)

    def refund_account_transaction(self, data):
        return self.patch(f"/connect/account/refund", data=data)

    def void_account_transaction(self, data):
        return self.patch(f"/connect/account/void", data=data)
