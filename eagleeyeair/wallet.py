from .eagle_eye_api import EagleEyeApi


class EagleEyeWallet(EagleEyeApi):
    def get_wallet_by_identity_value(self, identity_value: str):
        """Get a wallet by an identity value"""
        query = {"identity-value": identity_value}
        return self.get(f"/wallet", query=query)

    def create_wallet(self, data):
        return self.post(f"/wallet", data=data)

    def get_wallet_by_wallet_id(self, wallet_id):
        """Get wallet details by wallet id"""
        return self.get(f"/wallet/{wallet_id}")

    def update_wallet_main_properties(self, wallet_id, data):
        return self.patch(f"/wallet/{wallet_id}", data=data)

    def delete_wallet(self, wallet_id):
        return self.delete(f"/wallet/{wallet_id}")

    def get_wallet_stats(self, wallet_id, date_from="", date_to=""):
        """Get wallet's statistics"""
        query = {}
        if date_from != "":
            query["dateFrom"] = date_from
        if date_to != "":
            query["dateTo"] = date_to
        return self.get(f"/wallet/{wallet_id}/stats", query=query)

    def activate_wallet(self, wallet_id):
        return self.patch(f"/wallet/{wallet_id}/activate")

    def suspend_wallet(self, wallet_id):
        return self.patch(f"/wallet/{wallet_id}/suspend")

    def terminate_wallet(self, wallet_id):
        return self.patch(f"/wallet/{wallet_id}/terminate")

    def update_wallet_state(self, wallet_id, data):
        return self.patch(f"/wallet/{wallet_id}/state", data=data)

    def create_wallet_child_relation(self, wallet_id, relationship_wallet_id):
        return self.patch(f"/wallet/{wallet_id}/join/{relationship_wallet_id}/child")

    def create_wallet_associate_relation(self, wallet_id, relationship_wallet_id):
        return self.patch(
            f"/wallet/{wallet_id}/join/{relationship_wallet_id}/associate"
        )

    def create_wallet_donor_relation(self, wallet_id, relationship_wallet_id):
        return self.patch(f"/wallet/{wallet_id}/join/{relationship_wallet_id}/donor")

    def split_wallet_relation(self, wallet_id, relationship_wallet_id):
        return self.patch(f"/wallet/{wallet_id}/split/{relationship_wallet_id}/")

    def move_wallet_relations(
        self, wallet_id, old_relationship_wallet_id, new_relationship_wallet_id
    ):
        return self.patch(
            f"/wallet/{wallet_id}/move/from/{old_relationship_wallet_id}/to/{new_relationship_wallet_id}"
        )

    def get_wallet_bank_reward_links(
        self, wallet_id, status="", state="", valid_from="", valid_to=""
    ):
        """Retrieve wallet's links to a private points reward banks"""
        query = {}
        if status != "":
            query["status"] = status
        if state != "":
            query["state"] = state
        if valid_from != "":
            query["validFrom"] = valid_from
        if valid_to != "":
            query["validTo"] = valid_to
        return self.get(f"/wallet/{wallet_id}/bank/pointsreward/links", query=query)

    def create_wallet_bank_reward_link(self, wallet_id, points_reward_bank_id, data):
        return self.post(
            f"/wallet/{wallet_id}/link/bank/pointsreward/{points_reward_bank_id}",
            data=data,
        )

    def delete_wallet_bank_reward_link(self, wallet_id, points_reward_bank_id):
        return self.delete(
            f"/wallet/{wallet_id}/link/bank/pointsreward/{points_reward_bank_id}"
        )

    def amend_wallet_bank_reward_link(
        self, wallet_id, points_reward_bank_wallet_link_id, data
    ):
        return self.patch(
            f"/wallet/{wallet_id}/link/bank/pointsreward/link/{points_reward_bank_wallet_link_id}",
            data=data,
        )

    def delete_wallet_bank_reward_link2(
        self, wallet_id, points_reward_bank_wallet_link_id
    ):
        return self.delete(
            f"/wallet/{wallet_id}/link/bank/pointsreward/link/{points_reward_bank_wallet_link_id}"
        )

    def get_wallet_invite(self, guid: str, reference=""):
        """Get a wallet invite"""
        query = {"guid": guid}
        if reference != "":
            query["reference"] = reference
        return self.get(f"/wallet/invite", query=query)

    def get_wallet_invites_by_wallet_id(
        self, wallet_id, state=[], status=[], type=[], limit=20, offset=0
    ):
        """Get invites of specified wallet"""
        query = {}
        if state != []:
            query["state"] = state
        if status != []:
            query["status"] = status
        if type != []:
            query["type"] = type
        if limit != 20:
            query["limit"] = limit
        if offset != 0:
            query["offset"] = offset
        return self.get(f"/wallet/{wallet_id}/invites", query=query)

    def get_wallet_invites(
        self, reference: str, guid="", state=[], status=[], type=[], limit=20, offset=0
    ):
        """Get wallet invites"""
        query = {"reference": reference}
        if guid != "":
            query["guid"] = guid
        if state != []:
            query["state"] = state
        if status != []:
            query["status"] = status
        if type != []:
            query["type"] = type
        if limit != 20:
            query["limit"] = limit
        if offset != 0:
            query["offset"] = offset
        return self.get(f"/wallet/invites", query=query)

    def create_wallet_invite(self, wallet_id, data):
        return self.post(f"/wallet/{wallet_id}/invite", data=data)

    def get_wallet_id_by_invite_id(self, wallet_id, wallet_invite_id: str):
        return self.get(f"/wallet/{wallet_id}/invite/{wallet_invite_id}")

    def update_wallet_invite(self, wallet_id, wallet_invite_id: str, data):
        return self.patch(f"/wallet/{wallet_id}/invite/{wallet_invite_id}", data=data)

    def verify_wallet_invite(self):
        return self.get(f"/wallet/invite/verify")

    def accept_wallet_invite(self, wallet_id, wallet_invite_id: str, data):
        return self.patch(
            f"/wallet/{wallet_id}/invite/{wallet_invite_id}/accept", data=data
        )

    def cancel_wallet_invite(self, wallet_id, wallet_invite_id: str, data):
        return self.patch(
            f"/wallet/{wallet_id}/invite/{wallet_invite_id}/cancel", data=data
        )

    def reject_wallet_invite(self, wallet_id, wallet_invite_id: str, data):
        return self.patch(
            f"/wallet/{wallet_id}/invite/{wallet_invite_id}/reject", data=data
        )

    def update_wallet_invite_state(self, wallet_id, wallet_invite_id: str, data):
        return self.patch(
            f"/wallet/{wallet_id}/invite/{wallet_invite_id}/state", data=data
        )

    def get_wallet_identity_by_identity_value(self, name="", safe_value=""):
        query = {}
        if name != "":
            query["name"] = name
        if safe_value != "":
            query["safeValue"] = safe_value
        return self.get(f"/wallet/identity", query=query)

    def get_wallet_identities_by_wallet_id(
        self,
        wallet_id,
        state=[],
        status=[],
        type=[],
        safe_value="",
        limit=100,
        offset=0,
    ):
        query = {}
        if state != []:
            query["state"] = state
        if status != []:
            query["status"] = status
        if type != []:
            query["type"] = type
        if safe_value != "":
            query["safeValue"] = safe_value
        if limit != 100:
            query["limit"] = limit
        if offset != 0:
            query["offset"] = offset
        return self.get(f"/wallet/{wallet_id}/identities", query=query)

    def create_wallet_identity(self, wallet_id, data):
        return self.post(f"/wallet/{wallet_id}/identity", data=data)

    def get_wallet_identity_by_identity_id(self, wallet_id, identity_id):
        return self.get(f"/wallet/{wallet_id}/identity/{identity_id}")

    def update_wallet_identity(self, wallet_id, identity_id, data):
        return self.patch(f"/wallet/{wallet_id}/identity/{identity_id}", data=data)

    def delete_wallet_identity(self, wallet_id, identity_id):
        return self.delete(f"/wallet/{wallet_id}/identity/{identity_id}")

    def update_wallet_identity_status_suspended(self, wallet_id, identity_id):
        return self.patch(f"/wallet/{wallet_id}/identity/{identity_id}/suspend")

    def update_wallet_identity_status_active(self, wallet_id, identity_id):
        return self.patch(f"/wallet/{wallet_id}/identity/{identity_id}/activate")

    def update_wallet_identity_status_lost(self, wallet_id, identity_id):
        return self.patch(f"/wallet/{wallet_id}/identity/{identity_id}/lost")

    def update_wallet_identity_status_stolen(self, wallet_id, identity_id):
        return self.patch(f"/wallet/{wallet_id}/identity/{identity_id}/stolen")

    def update_wallet_identity_status_terminated(self, wallet_id, identity_id):
        return self.patch(f"/wallet/{wallet_id}/identity/{identity_id}/terminate")

    def update_wallet_identity_state(self, wallet_id, identity_id, data):
        return self.patch(
            f"/wallet/{wallet_id}/identity/{identity_id}/state", data=data
        )

    def move_wallet_identity(self, wallet_id, identity_id, data):
        return self.patch(f"/wallet/{wallet_id}/identity/{identity_id}/move", data=data)

    def create_wallet_consumer(self, wallet_id, data):
        return self.post(f"/wallet/{wallet_id}/consumer", data=data)

    def get_wallet_consumer(self, wallet_id):
        """Get wallet consumer details"""
        return self.get(f"/wallet/{wallet_id}/consumer")

    def get_wallet_consumer_by_consumer_id(self, wallet_id, consumer_id):
        """Get wallet consumer details for a specific wallet"""
        return self.get(f"/wallet/{wallet_id}/consumer/{consumer_id}")

    def update_wallet_consumer(self, wallet_id, consumer_id, data):
        """Update wallet consumer specified by given ids using payload"""
        return self.patch(f"/wallet/{wallet_id}/consumer/{consumer_id}", data=data)

    def delete_wallet_consumer(self, wallet_id, consumer_id):
        return self.delete(f"/wallet/{wallet_id}/consumer/{consumer_id}")

    def update_wallet_consumer_data_operation(self, wallet_id, consumer_id, data):
        return self.patch(f"/wallet/{wallet_id}/consumer/{consumer_id}/data", data=data)

    def update_wallet_consumer_state(self, wallet_id, consumer_id, data):
        return self.patch(
            f"/wallet/{wallet_id}/consumer/{consumer_id}/state", data=data
        )

    def get_wallet_transactions(
        self,
        wallet_id,
        wallet_transaction_ids=[],
        type=[],
        status=[],
        state=[],
        reference=[],
        transaction_date_time="",
        date_created="",
        last_updated="",
        include_children="",
        order_by="",
        limit=20,
        offset=0,
    ):
        query = {}
        if wallet_transaction_ids != []:
            query["walletTransactionId"] = wallet_transaction_ids
        if type != []:
            query["type"] = type
        if status != []:
            query["status"] = status
        if state != []:
            query["state"] = state
        if reference != []:
            query["type"] = reference
        if transaction_date_time != "":
            query["transactionDateTime"] = transaction_date_time
        if date_created != "":
            query["dateCreated"] = date_created
        if last_updated != "":
            query["lastUpdated"] = last_updated
        if include_children != "":
            query["includeChildren"] = include_children
        if order_by != "":
            query["orderBy"] = order_by
        if limit != 20:
            query["limit"] = limit
        if offset != 0:
            query["offset"] = offset
        return self.get(f"/wallet/{wallet_id}/transactions", query=query)

    def create_wallet_transaction(self, wallet_id):
        return self.post(f"/wallet/{wallet_id}/transaction")

    def get_wallet_transaction_by_reference(self, reference_id: str):
        query = {"reference": reference_id}
        return self.get(f"/wallet/transaction", query=query)

    def get_wallet_transaction_by_id(self, wallet_id, wallet_transaction_id):
        return self.get(f"/wallet/{wallet_id}/transaction/{wallet_transaction_id}")

    def update_wallet_transaction(self, wallet_id, transaction_id, data):
        return self.patch(
            f"/wallet/{wallet_id}/transaction/{transaction_id}", data=data
        )

    def delete_wallet_transaction(self, wallet_id, transaction_id):
        return self.delete(f"/wallet/{wallet_id}/transaction/{transaction_id}")

    def update_wallet_transaction_state(self, wallet_id, transaction_id, data):
        return self.patch(
            f"/wallet/{wallet_id}/transaction/{transaction_id}/state", data=data
        )

    def update_wallet_transaction_settle(self, wallet_id, transaction_id):
        return self.patch(f"/wallet/{wallet_id}/transaction/{transaction_id}/settle")

    def cancel_wallet_transaction(self, wallet_id, transaction_id):
        return self.patch(f"/wallet/{wallet_id}/transaction/{transaction_id}/cancel")

    def update_wallet_transaction_expire(self, wallet_id, transaction_id):
        return self.patch(f"/wallet/{wallet_id}/transaction/{transaction_id}/expire")

    def update_wallet_transaction_service_by_id(self, wallet_id, transaction_id, data):
        return self.put(
            f"/services/wallet/{wallet_id}/transaction/{transaction_id}", data=data
        )

    def create_wallet_and_wallet_identities(self, data):
        return self.post(f"/services/wallet", data=data)

    def delete_services_wallet(self, wallet_id):
        return self.delete(f"/services/wallet/{wallet_id}")

    def update_wallet_transaction_service_by_reference(self, data):
        return self.put(f"/services/wallet/transaction", data=data)

    def create_wallet_transaction_service(self, wallet_id, data):
        return self.post(f"/services/wallet/{wallet_id}/transaction", data=data)

    def settle_wallet_transaction_service_by_transaction_id(
        self, wallet_id, transaction_id, data
    ):
        return self.patch(
            f"/services/wallet/{wallet_id}/transaction/{transaction_id}/settle",
            data=data,
        )

    def settle_wallet_transaction_service_by_transaction_reference(self, data):
        return self.patch(f"/services/wallet/transaction/settle", data=data)

    def release_wallet_transaction_service_by_transaction_id(
        self, wallet_id, transaction_id, data
    ):
        return self.patch(
            f"/services/wallet/{wallet_id}/transaction/{transaction_id}/release",
            data=data,
        )

    def release_wallet_transaction_service_by_transaction_reference(self, data):
        return self.patch(f"/services/wallet/transaction/release", data=data)

    def cancel_wallet_transaction_service_by_transaction_id(
        self, wallet_id, transaction_id, data
    ):
        return self.patch(
            f"/services/wallet/{wallet_id}/transaction/{transaction_id}/cancel",
            data=data,
        )

    def cancel_wallet_transaction_service_by_transaction_reference(self, data):
        return self.patch(f"/services/wallet/transaction/cancel", data=data)

    def inactivate_wallet_account(self, wallet_id, account_id):
        return self.patch(f"/wallet/{wallet_id}/account/{account_id}/inactivate")

    def create_wallet_campaign_account(self, wallet_id, campaign_id, data):
        return self.post(
            f"/wallet/{wallet_id}/campaign/{campaign_id}/account", data=data
        )

    def create_wallet_programme_account(self, wallet_id, programme_id, data):
        return self.post(
            f"/wallet/{wallet_id}/programme/{programme_id}/account", data=data
        )

    def create_wallet_scheme_account(self, wallet_id, scheme_id: str, data):
        return self.post(f"/wallet/{wallet_id}/scheme/{scheme_id}/account", data=data)

    def create_wallet_plan_account(self, wallet_id, plan_id: str, data):
        return self.post(f"/wallet/{wallet_id}/plan/{plan_id}/account", data=data)

    def create_wallet_entitlement_coupon_account(
        self, wallet_id, parent_account_id, campaign_id, data
    ):
        return self.post(
            f"/wallet/{wallet_id}/account/{parent_account_id}/campaign/{campaign_id}/account",
            data=data,
        )

    def get_wallet_accounts_by_wallet_id(
        self,
        wallet_id,
        state=[],
        status=[],
        type=[],
        client_type=[],
        account_id=[],
        parent_account_id="",
        valid_to="",
        valid_from="",
        date_created="",
        last_updated="",
        campaign_status="",
        tokens="",
        limit=20,
        offset=0,
        order_by="",
    ):
        query = {}
        if state != []:
            query["state"] = state
        if status != []:
            query["status"] = status
        if type != []:
            type["type"] = type
        if client_type != []:
            type["clientType"] = client_type
        if account_id != []:
            query["accountId"] = account_id
        if parent_account_id != "":
            query["parentAccountId"] = parent_account_id
        if valid_to != "":
            query["validTo"] = valid_to
        if valid_from != "":
            query["validFrom"] = valid_from
        if date_created != "":
            query["dateCreated"] = date_created
        if last_updated != "":
            query["lastUpdated"] = last_updated
        if campaign_status != 1:
            query["campaign-status"] = campaign_status
        if tokens != "":
            query["tokens"] = tokens
        if limit != 20:
            query["limit"] = limit
        if offset != 0:
            query["offset"] = offset
        if order_by != "":
            query["orderBy"] = order_by
        return self.get(f"/wallet/{wallet_id}/accounts", query=query)

    def get_wallet_accounts_by_identity_value(
        self,
        identity_value="",
        state=[],
        status=[],
        type=[],
        client_type=[],
        account_id=[],
        parent_account_id="",
        valid_to="",
        valid_from="",
        date_created="",
        last_updated="",
        campaign_status="",
        tokens="",
        limit=20,
        offset=0,
        order_by="",
    ):
        query = {}
        if identity_value != "":
            query["identity-value"] = identity_value
        if state != []:
            query["state"] = state
        if status != []:
            query["status"] = status
        if type != []:
            type["type"] = type
        if client_type != []:
            type["clientType"] = client_type
        if account_id != []:
            query["accountId"] = account_id
        if parent_account_id != "":
            query["parentAccountId"] = parent_account_id
        if valid_to != "":
            query["validTo"] = valid_to
        if valid_from != "":
            query["validFrom"] = valid_from
        if date_created != "":
            query["dateCreated"] = date_created
        if last_updated != "":
            query["lastUpdated"] = last_updated
        if campaign_status != "":
            query["campaign-status"] = campaign_status
        if tokens != "":
            query["tokens"] = tokens
        if limit != 20:
            query["limit"] = limit
        if offset != 0:
            query["offset"] = offset
        if order_by != "":
            query["orderBy"] = order_by
        return self.get(f"/wallet/accounts", query=query)

    def get_wallet_account(self, wallet_id, account_id, tokens=""):
        query = {}
        if tokens != "":
            query["tokens"] = tokens
        return self.get(f"/wallet/{wallet_id}/account/{account_id}", query=query)

    def update_wallet_account(self, wallet_id, account_id, data):
        return self.patch(f"/wallet/{wallet_id}/account/{account_id}", data=data)

    def credit_wallet_account(self, wallet_id, account_id, data):
        return self.patch(f"/wallet/{wallet_id}/account/{account_id}/credit", data=data)

    def earn_points(self, wallet_id, account_id, data):
        return self.patch(f"/wallet/{wallet_id}/account/{account_id}/earn", data=data)

    def debit_wallet_account(self, wallet_id, account_id, include, data):
        query = {}
        if include != "":
            query["include"] = include
        return self.patch(
            f"/wallet/{wallet_id}/account/{account_id}/debit", query=query, data=data
        )

    def load_wallet_account(self, wallet_id, account_id, data):
        return self.patch(f"/wallet/{wallet_id}/account/{account_id}/load", data=data)

    def redeem_wallet_account(self, wallet_id, account_id):
        return self.patch(f"/wallet/{wallet_id}/account/{account_id}/redeem")

    def top_up_wallet_account(self, wallet_id, account_id):
        return self.patch(f"/wallet/{wallet_id}/account/{account_id}/topup")

    def unredeem_wallet_account(self, wallet_id, account_id):
        return self.patch(f"/wallet/{wallet_id}/account/{account_id}/unredeem")

    def refund_wallet_account(self, wallet_id, account_id):
        return self.patch(f"/wallet/{wallet_id}/account/{account_id}/refund")

    def void_wallet_account_transaction(
        self, wallet_id, account_id, account_transaction_id: str, data
    ):
        return self.patch(
            f"/wallet/{wallet_id}/account/{account_id}/transaction/{account_transaction_id}/void",
            data=data,
        )

    def activate_wallet_account(self, wallet_id, account_id):
        return self.patch(f"/wallet/{wallet_id}/account/{account_id}/activate")

    def cancel_wallet_account(self, wallet_id, account_id):
        return self.patch(f"/wallet/{wallet_id}/account/{account_id}/cancel")

    def get_wallet_account_transactions(
        self,
        wallet_id,
        account_id,
        event="",
        date_created="",
        last_updated="",
        parent_account_transaction_id="",
        account_transaction_id="",
        source="",
        value="",
        order_by="",
        limit=20,
        offset=0,
    ):
        query = {}
        if event != "":
            query["event"] = ""
        if date_created != "":
            query["dateCreated"] = date_created
        if last_updated != "":
            query["lastUpdated"] = last_updated
        if parent_account_transaction_id != "":
            query["parentAccountTransactionId"] = parent_account_transaction_id
        if account_transaction_id != "":
            query["accountTransactionId"] = account_transaction_id
        if source != "":
            query["source"] = source
        if value != "":
            query["value"] = value
        if order_by != "":
            query["orderBy"] = order_by
        if limit != 20:
            query["limit"] = limit
        if offset != 0:
            query["offset"] = offset
        return self.get(
            f"/wallet/{wallet_id}/account/{account_id}/transactions", query=query
        )

    def block_wallet_account(self, wallet_id, account_id):
        return self.patch(f"/wallet/{wallet_id}/account/{account_id}/block")

    def unblock_wallet_account(self, wallet_id, account_id):
        return self.patch(f"/wallet/{wallet_id}/account/{account_id}/unblock")

    def verify_wallet_account_transaction(self, wallet_id, account_id):
        return self.post(f"/wallet/{wallet_id}/account/{account_id}/verify")

    def spend_accumulated_points(self, wallet_id, account_id):
        return self.patch(f"/wallet/{wallet_id}/account/{account_id}/spend")

    def change_wallet_account_state(self, wallet_id, account_id):
        return self.patch(f"/wallet/{wallet_id}/account/{account_id}/state")

    def credit_goodwill_points(self, wallet_id, account_id):
        return self.patch(f"/wallet/{wallet_id}/account/{account_id}/goodwill")

    def calculate_points_to_be_earned(
        self,
        scheme_id: str,
        total_transaction_value,
        store_id="",
        store_parent_id="",
        rate_name="",
    ):
        query = {"totalTransactionValue": total_transaction_value}
        if store_id != "":
            query["location[storeId]"] = store_id
        if store_parent_id != "":
            query["location[storeParentId"] + store_parent_id
        if rate_name != "":
            query["rateName"] = rate_name
        return self.get(f"/scheme/{scheme_id}/earn/calculate", query=query)

    def refresh_wallet_account(self, wallet_id, account_id, data):
        return self.patch(
            f"/wallet/{wallet_id}/account/{account_id}/refresh", data=data
        )

    def exchange(self, wallet_id, data):
        return self.post(
            f"/services/wallet/{wallet_id}/transaction/exchange/pointsreward", data=data
        )

    def donate(self, wallet_id, data):
        return self.post(f"/services/wallet/{wallet_id}/transaction/donate", data=data)

    def create_credit_wallet_transaction_service(self, wallet_id, data):
        return self.post(f"/services/wallet/{wallet_id}/transaction/credit", data=data)

    def create_redeem_credit_wallet_transaction_service(self, wallet_id, data):
        return self.post(
            f"/services/wallet/{wallet_id}/transaction/redeemCredit", data=data
        )

    def create_goodwill_wallet_transaction_service(self, wallet_id, data):
        return self.post(
            f"/services/wallet/{wallet_id}/transaction/goodwill", data=data
        )

    def create_debit_wallet_transaction_service(self, wallet_id, data):
        return self.post(f"/services/wallet/{wallet_id}/transaction/debit", data=data)

    def unredeem_wallet_transaction_service(self, wallet_id, data):
        return self.post(
            f"/services/wallet/{wallet_id}/transaction/unredeem", data=data
        )

    def merge_two_wallets(self, victim_wallet_id, survivor_wallet_id):
        return self.patch(
            f"/services/wallet/{victim_wallet_id}/merge/{survivor_wallet_id}"
        )

    def move_account_to_wallet(self, account_id, wallet_id, data):
        return self.patch(
            f"/account/{account_id}/move/to/wallet/{wallet_id}", data=data
        )

    def get_wallet_recommendations_by_wallet_id(self, wallet_id, status, channel):
        query = {"status": status, "channel": channel}
        return self.get(f"/wallet/{wallet_id}/recommendations", query=query)

    def get_wallet_recommendations_by_identity_value(
        self, identity_value, status, channel
    ):
        query = {"identity-value": identity_value, "status": status, "channel": channel}
        return self.get(f"/wallet/recommendations", query=query)

    def change_recommendation_status_to_active(
        self, wallet_id, catalogue_guid, recommendation_guid
    ):
        return self.patch(
            f"/wallet/{wallet_id}/catalogue/{catalogue_guid}/recommendation/{recommendation_guid}/status/activate"
        )

    def change_recommendation_status_to_accepted(
        self, wallet_id, catalogue_guid, recommendation_guid
    ):
        return self.patch(
            f"/wallet/{wallet_id}/catalogue/{catalogue_guid}/recommendation/{recommendation_guid}/status/accept"
        )

    def change_recommendation_status_to_rejected(
        self, wallet_id, catalogue_guid, recommendation_guid
    ):
        return self.patch(
            f"/wallet/{wallet_id}/catalogue/{catalogue_guid}/recommendation/{recommendation_guid}/status/reject"
        )

    def change_recommendation_status_to_deleted(
        self, wallet_id, catalogue_guid, recommendation_guid
    ):
        return self.delete(
            f"/wallet/{wallet_id}/catalogue/{catalogue_guid}/recommendation/{recommendation_guid}/status/delete"
        )

    def accept_recommendation(self, wallet_id, catalogue_guid, recommendation_guid):
        return self.post(
            f"/services/wallet/{wallet_id}/catalogue/{catalogue_guid}/recommendation/{recommendation_guid}/accept"
        )
