from .eagle_eye_api import EagleEyeApi

class EagleEyeWallet(EagleEyeApi):
    def get_wallet_by_identity_value(self, lcn: str):
        '''Get wallet by lcn'''
        return self.get(f'/wallet', query={'identity-value': lcn})
    def create_wallet(self, data):
        return self.post(f'/wallet', data=data)
    def get_wallet_by_wallet_id(self, wallet_id):
        return self.get(f'/wallet/{wallet_id}')
    def update_wallet_main_properties(self, wallet_id, data):
        return self.patch(f'/wallet/{wallet_id}', data=data)
    def delete_wallet(self, wallet_id):
        return self.delete(f'/wallet/{wallet_id}')
    def get_wallet_stats(self, wallet_id):
        return self.get(f'/wallet/{wallet_id}/stats')
    def activate_wallet(self, wallet_id):
        return self.patch(f'/wallet/{wallet_id}/activate')
    def suspend_wallet(self, wallet_id):
        return self.patch(f'/wallet/{wallet_id}/suspend')
    def update_wallet_state(self, wallet_id, data):
        return self.patch(f'/wallet/{wallet_id}/state', data=data)
    def create_wallet_child_relation(self, wallet_id, relationship_wallet_id):
        return self.patch(f'/wallet/{wallet_id}/join/{relationship_wallet_id}/child')
    def create_wallet_associate_relation(self, wallet_id, relationship_wallet_id):
        return self.patch(f'/wallet/{wallet_id}/join/{relationship_wallet_id}/associate')
    def create_wallet_donor_relation(self, wallet_id, relationship_wallet_id):
        return self.patch(f'/wallet/{wallet_id}/join/{relationship_wallet_id}/donor')
    def split_wallet_relation(self, wallet_id, relationship_wallet_id):
        return self.patch(f'/wallet/{wallet_id}/split/{relationship_wallet_id}/')
    def move_wallet_relations(self, wallet_id, old_relationship_wallet_id, new_relationship_wallet_id):
        return self.patch(f'/wallet/{wallet_id}/move/from/{old_relationship_wallet_id}/to/{new_relationship_wallet_id}')
    def get_wallet_bank_reward_links(self, wallet_id):
        return self.get(f'/wallet/{wallet_id}/bank/pointsreward/links')
    def create_wallet_bank_reward_link(self, wallet_id, points_reward_bank_id, data):
        return self.post(f'/wallet/{wallet_id}/link/bank/pointsreward/{points_reward_bank_id}', data=data)
    def delete_wallet_bank_reward_link(self, wallet_id, points_reward_bank_id):
        return self.delete(f'/wallet/{wallet_id}/link/bank/pointsreward/{points_reward_bank_id}')
    def amend_wallet_bank_reward_link(self, wallet_id, points_reward_bank_wallet_link_id, data):
        return self.patch(f'/wallet/{wallet_id}/link/bank/pointsreward/link/{points_reward_bank_wallet_link_id}', data=data)
    def delete_wallet_bank_reward_link2(self, wallet_id, points_reward_bank_wallet_link_id):
        return self.delete(f'/wallet/{wallet_id}/link/bank/pointsreward/link/{points_reward_bank_wallet_link_id}')
    def get_wallet_invite(self):
        return self.get(f'/wallet/invite')
    def get_wallet_invites_by_wallet_id(self, wallet_id,):
        return self.get(f'/wallet/{wallet_id}/invites')
    def get_wallet_invites(self):
        return self.get(f'/wallet/invites')
    def create_wallet_invite(self, wallet_id, data):
        return self.post(f'/wallet/{wallet_id}/invite', data=data)
    def get_wallet_id_by_invite_id(self, wallet_id, walletInviteId: str):
        return self.get(f'/wallet/{wallet_id}/invite/{walletInviteId}')
    def update_wallet_invite(self, wallet_id, walletInviteId: str, data):
        return self.patch(f'/wallet/{wallet_id}/invite/{walletInviteId}', data=data)
    def verify_wallet_invite(self):
        return self.get(f'/wallet/invite/verify')
    def accept_wallet_invite(self, wallet_id, walletInviteId: str, data):
        return self.patch(f'/wallet/{wallet_id}/invite/{walletInviteId}/accept', data=data)
    def cancel_wallet_invite(self, wallet_id, walletInviteId: str, data):
        return self.patch(f'/wallet/{wallet_id}/invite/{walletInviteId}/cancel', data=data)
    def reject_wallet_invite(self, wallet_id, walletInviteId: str, data):
        return self.patch(f'/wallet/{wallet_id}/invite/{walletInviteId}/reject', data=data)
    def update_wallet_invite_state(self, wallet_id, walletInviteId: str, data):
        return self.patch(f'/wallet/{wallet_id}/invite/{walletInviteId}/state', data=data)
    def get_wallet_identity_by_identity_value(self):
        return self.get(f'/wallet/identity')
    def get_wallet_identities_by_wallet_id(self, wallet_id,):
        return self.get(f'/wallet/{wallet_id}/identities')
    def create_wallet_identity(self, wallet_id, data):
        return self.post(f'/wallet/{wallet_id}/identity', data=data)
    def get_wallet_identity_by_identity_id(self, wallet_id, identity_id):
        return self.get(f'/wallet/{wallet_id}/identity/{identity_id}')
    def update_wallet_identity(self, wallet_id, identity_id, data):
        return self.patch(f'/wallet/{wallet_id}/identity/{identity_id}', data=data)
    def delete_wallet_identity(self, wallet_id, identity_id):
        return self.delete(f'/wallet/{wallet_id}/identity/{identity_id}')
    def update_wallet_identity_status_suspended(self, wallet_id, identity_id):
        return self.patch(f'/wallet/{wallet_id}/identity/{identity_id}/suspend')
    def update_wallet_identity_status_active(self, wallet_id, identity_id):
        return self.patch(f'/wallet/{wallet_id}/identity/{identity_id}/activate')
    def update_wallet_identity_status_lost(self, wallet_id, identity_id):
        return self.patch(f'/wallet/{wallet_id}/identity/{identity_id}/lost')
    def update_wallet_identity_status_stolen(self, wallet_id, identity_id):
        return self.patch(f'/wallet/{wallet_id}/identity/{identity_id}/stolen')
    def update_wallet_identity_state(self, wallet_id, identity_id, data):
        return self.patch(f'/wallet/{wallet_id}/identity/{identity_id}/state', data=data)
    def move_wallet_identity(self, wallet_id, identity_id, data):
        return self.patch(f'/wallet/{wallet_id}/identity/{identity_id}/move', data=data)
    def create_wallet_consumer(self, wallet_id, data):
        return self.post(f'/wallet/{wallet_id}/consumer', data=data)
    def get_wallet_consumer(self, wallet_id):
        '''Return wallet which id is given'''
        return self.get(f'/wallet/{wallet_id}/consumer')
    def get_wallet_consumer_by_consumer_id(self, wallet_id, consumer_id):
        return self.get(f'/wallet/{wallet_id}/consumer/{consumer_id}')
    def update_wallet_consumer(self, wallet_id, consumer_id, data):
        '''Update wallet consumer specified by given ids using payload'''
        return self.patch(f'/wallet/{wallet_id}/consumer/{consumer_id}', data=data)
    def delete_wallet_consumer(self, wallet_id, consumer_id):
        return self.delete(f'/wallet/{wallet_id}/consumer/{consumer_id}')
    def update_wallet_consumer_data_operation(self, wallet_id, consumer_id, data):
        return self.patch(f'/wallet/{wallet_id}/consumer/{consumer_id}/data', data=data)
    def update_wallet_consumer_state(self, wallet_id, consumer_id, data):
        return self.patch(f'/wallet/{wallet_id}/consumer/{consumer_id}/state', data=data)
    def get_wallet_transactions(self, wallet_id):
        return self.get(f'/wallet/{wallet_id}/transactions')
    def create_wallet_transaction(self, wallet_id):
        return self.post(f'/wallet/{wallet_id}/transaction')
    def get_wallet_transaction_by_reference(self, referenceId: str):
        return self.get(f'/wallet/transaction', query={'reference': referenceId})
    def get_wallet_transaction_by_id(self, wallet_id, wallet_transaction_id):
        return self.get(f'/wallet/{wallet_id}/transaction/{wallet_transaction_id}')
    def update_wallet_transaction(self, wallet_id, transaction_id, data):
        return self.patch(f'/wallet/{wallet_id}/transaction/{transaction_id}', data=data)
    def delete_wallet_transaction(self, wallet_id, transaction_id):
        return self.delete(f'/wallet/{wallet_id}/transaction/{transaction_id}')
    def update_wallet_transaction_state(self, wallet_id, transaction_id, data):
        return self.patch(f'/wallet/{wallet_id}/transaction/{transaction_id}/state', data=data)
    def update_wallet_transaction_settle(self, wallet_id, transaction_id):
        return self.patch(f'/wallet/{wallet_id}/transaction/{transaction_id}/settle')
    def cancel_wallet_transaction(self, wallet_id, transaction_id):
        return self.patch(f'/wallet/{wallet_id}/transaction/{transaction_id}/cancel')
    def update_wallet_transaction_expire(self, wallet_id, transaction_id):
        return self.patch(f'/wallet/{wallet_id}/transaction/{transaction_id}/expire')
    def update_wallet_transaction_service_by_id(self, wallet_id, transaction_id, data):
        return self.put(f'/services/wallet/{wallet_id}/transaction/{transaction_id}', data=data)
    def create_wallet_and_wallet_identities(self, data):
        return self.post(f'/services/wallet', data=data)
    def delete_services_wallet(self, wallet_id):
        return self.delete(f'/services/wallet/{wallet_id}')
    def update_wallet_transaction_service_by_reference(self, data):
        return self.put(f'/services/wallet/transaction', data=data)
    def create_wallet_transaction_service(self, wallet_id, data):
        return self.post(f'/services/wallet/{wallet_id}/transaction', data=data)
    def settle_wallet_transaction_service_by_transaction_id(self, wallet_id, transaction_id, data):
        return self.patch(f'/services/wallet/{wallet_id}/transaction/{transaction_id}/settle', data=data)
    def settle_wallet_transaction_service_by_transaction_reference(self, data):
        return self.patch(f'/services/wallet/transaction/settle', data=data)
    def release_wallet_transaction_service_by_transaction_id(self, wallet_id, transaction_id, data):
        return self.patch(f'/services/wallet/{wallet_id}/transaction/{transaction_id}/release', data=data)
    def release_wallet_transaction_service_by_transaction_reference(self, data):
        return self.patch(f'/services/wallet/transaction/release', data=data)
    def cancel_wallet_transaction_service_by_transaction_id(self, wallet_id, transaction_id, data):
        return self.patch(f'/services/wallet/{wallet_id}/transaction/{transaction_id}/cancel', data=data)
    def cancel_wallet_transaction_service_by_transaction_reference(self, data):
        return self.patch(f'/services/wallet/transaction/cancel', data=data)
    def inactivate_wallet_account(self, wallet_id, account_id):
        return self.patch(f'/wallet/{wallet_id}/account/{account_id}/inactivate')
    def create_wallet_campaign_account(self, wallet_id, campaign_id, data):
        return self.post(f'/wallet/{wallet_id}/campaign/{campaign_id}/account', data=data)
    def create_wallet_programme_account(self, wallet_id, programme_id, data):
        return self.post(f'/wallet/{wallet_id}/programme/{programme_id}/account', data=data)
    def create_wallet_scheme_account(self, wallet_id, schemeId: str, data):
        return self.post(f'/wallet/{wallet_id}/scheme/{schemeId}/account', data=data)
    def create_wallet_plan_account(self, wallet_id, planId: str, data):
        return self.post(f'/wallet/{wallet_id}/plan/{planId}/account', data=data)
    def create_wallet_entitlement_coupon_account(self, wallet_id, parent_account_id, campaign_id, data):
        return self.post(f'/wallet/{wallet_id}/account/{parent_account_id}/campaign/{campaign_id}/account', data=data)
    def get_wallet_accounts_by_wallet_id(self, wallet_id):
        return self.get(f'/wallet/{wallet_id}/accounts')
    def get_wallet_accounts_by_identity_value(self):
        return self.get(f'/wallet/accounts')
    def get_wallet_account(self, wallet_id, account_id):
        return self.get(f'/wallet/{wallet_id}/account/{account_id}')
    def update_wallet_account(self, wallet_id, account_id, data):
        return self.patch(f'/wallet/{wallet_id}/account/{account_id}', data=data)
    def credit_wallet_account(self, wallet_id, account_id, data):
        return self.patch(f'/wallet/{wallet_id}/account/{account_id}/credit', data=data)
    def earn_points(self, wallet_id, account_id, data):
        return self.patch(f'/wallet/{wallet_id}/account/{account_id}/earn', data=data)
    def debit_wallet_account(self, wallet_id, account_id, data):
        return self.patch(f'/wallet/{wallet_id}/account/{account_id}/debit', data=data)
    def load_wallet_account(self, wallet_id, account_id, data):
        return self.patch(f'/wallet/{wallet_id}/account/{account_id}/load', data=data)
    def redeem_wallet_account(self, wallet_id, account_id):
        return self.patch(f'/wallet/{wallet_id}/account/{account_id}/redeem')
    def top_up_wallet_account(self, wallet_id, account_id):
        return self.patch(f'/wallet/{wallet_id}/account/{account_id}/topup')
    def unredeem_wallet_account(self, wallet_id, account_id):
        return self.patch(f'/wallet/{wallet_id}/account/{account_id}/unredeem')
    def refund_wallet_account(self, wallet_id, account_id):
        return self.patch(f'/wallet/{wallet_id}/account/{account_id}/refund')
    def void_wallet_account_transaction(self, wallet_id, account_id, accountTransactionId: str, data):
        return self.patch(f'/wallet/{wallet_id}/account/{account_id}/transaction/{accountTransactionId}/void', data=data)
    def activate_wallet_account(self, wallet_id, account_id):
        return self.patch(f'/wallet/{wallet_id}/account/{account_id}/activate')
    def cancel_wallet_account(self, wallet_id, account_id):
        return self.patch(f'/wallet/{wallet_id}/account/{account_id}/cancel')
    def get_wallet_account_transactions(self, wallet_id, account_id):
        return self.get(f'/wallet/{wallet_id}/account/{account_id}/transactions')
    def block_wallet_account(self, wallet_id, account_id):
        return self.patch(f'/wallet/{wallet_id}/account/{account_id}/block')
    def unblock_wallet_account(self, wallet_id, account_id):
        return self.patch(f'/wallet/{wallet_id}/account/{account_id}/unblock')
    def verify_wallet_account_transaction(self, wallet_id, account_id):
        return self.post(f'/wallet/{wallet_id}/account/{account_id}/verify')
    def spend_accumulated_points(self, wallet_id, account_id):
        return self.patch(f'/wallet/{wallet_id}/account/{account_id}/spend')
    def change_wallet_account_state(self, wallet_id, account_id):
        return self.patch(f'/wallet/{wallet_id}/account/{account_id}/state')
    def credit_goodwill_points(self, wallet_id, account_id):
        return self.patch(f'/wallet/{wallet_id}/account/{account_id}/goodwill')
    def calculate_points_to_be_earned(self, schemeId: str):
        return self.get(f'/scheme/{schemeId}/earn/calculate')
    def refresh_wallet_account(self, wallet_id, account_id, data):
        return self.patch(f'/wallet/{wallet_id}/account/{account_id}/refresh', data=data)
    def exchange(self, wallet_id, data):
        return self.post(f'/services/wallet/{wallet_id}/transaction/exchange/pointsreward', data=data)
    def donate(self, wallet_id, data):
        return self.post(f'/services/wallet/{wallet_id}/transaction/donate', data=data)
    def create_credit_wallet_transaction_service(self, wallet_id, data):
        return self.post(f'/services/wallet/{wallet_id}/transaction/credit', data=data)
    def create_redeem_credit_wallet_transaction_service(self, wallet_id, data):
        return self.post(f'/services/wallet/{wallet_id}/transaction/redeemCredit', data=data)
    def create_goodwill_wallet_transaction_service(self, wallet_id, data):
        return self.post(f'/services/wallet/{wallet_id}/transaction/goodwill', data=data)
    def create_debit_wallet_transaction_service(self, wallet_id, data):
        return self.post(f'/services/wallet/{wallet_id}/transaction/debit', data=data)
    def unredeem_wallet_transaction_service(self, wallet_id, data):
        return self.post(f'/services/wallet/{wallet_id}/transaction/unredeem', data=data)
    def merge_two_wallets(self, victim_wallet_id, survivor_wallet_id):
        return self.patch(f'/services/wallet/{victim_wallet_id}/merge/{survivor_wallet_id}')
    def move_account_to_wallet(self, account_id, wallet_id, data):
        return self.patch(f'/account/{account_id}/move/to/wallet/{wallet_id}', data=data)
    def get_wallet_recommendations_by_wallet_id(self, wallet_id):
        return self.get(f'/wallet/{wallet_id}/recommendations')
    def get_wallet_recommendations_by_identity_value(self):
        return self.get(f'/wallet/recommendations')
    def change_recommendation_status_to_active(self, wallet_id, catalogue_guid, recommendation_guid):
        return self.patch(f'/wallet/{wallet_id}/catalogue/{catalogue_guid}/recommendation/{recommendation_guid}/status/activate')
    def change_recommendation_status_to_accepted(self, wallet_id, catalogue_guid, recommendation_guid):
        return self.patch(f'/wallet/{wallet_id}/catalogue/{catalogue_guid}/recommendation/{recommendation_guid}/status/accept')
    def change_recommendation_status_to_rejected(self, wallet_id, catalogue_guid, recommendation_guid):
        return self.patch(f'/wallet/{wallet_id}/catalogue/{catalogue_guid}/recommendation/{recommendation_guid}/status/reject')
    def change_recommendation_status_to_deleted(self, wallet_id, catalogue_guid, recommendation_guid):
        return self.delete(f'/wallet/{wallet_id}/catalogue/{catalogue_guid}/recommendation/{recommendation_guid}/status/delete')
    def accept_recommendation(self, wallet_id, catalogue_guid, recommendation_guid):
        return self.post(f'/services/wallet/{wallet_id}/catalogue/{catalogue_guid}/recommendation/{recommendation_guid}/accept')
