import os


os.environ["EES_AUTH_CLIENT_ID"] = "u2v2hsh07xvju1eex8eh"
os.environ["EES_AUTH_CLIENT_SECRET"] = "tplzi3t8v6okghbrrhts0644dep5ns"
os.environ["EES_API_PREFIX"] = "/2.0"
os.environ["EES_POS_API_HOST"] = "pos.sandbox.uk.eagleeye.com"
os.environ["EES_RESOURCES_API_HOST"] = "resources.sandbox.uk.eagleeye.com"
os.environ["EES_WALLET_API_HOST"] = "wallet.sandbox.uk.eagleeye.com"
os.environ[
    "MONGO_API_LOGGING_URL"
] = "https://apigee-test.api-wr.com/wx/v2/member/preferences/mongo"

os.environ["MONGO_API_LOGGING_CLIENT_ID"] = "hrANvT98mnUo2fPXIZlAXEEO9u9VNihA"

import logging
from unittest.mock import patch
import unittest
import loyalty_util


def test_logging():
    r = loyalty_util.mongodb_logging(
        "update",
        True,
        200,
        "message",
        "5cffdbe0-1912-42eb-8a60-c12b34ded5c6",
    )

    assert r == 200


@patch(
    "loyalty_util.ee.wallet.get_wallet_by_identity_value",
    return_value=(
        {
            "walletId": "128875740",
            "friendlyName": "Wallet 1 of household 1",
            "status": "ACTIVE",
            "type": "MEMBER",
            "state": "EARNBURN",
            "meta": {"sample": "metadata", "key": "value"},
            "dateCreated": "2022-03-09T04:10:05+00:00",
            "lastUpdated": "2022-03-09T04:10:26+00:00",
            "relationships": {
                "parent": [],
                "child": ["128875739"],
                "associate": [],
                "donor": [],
            },
        }
    ),
)
def test_is_in_household(fake_wallet):
    is_in_household, wallet = loyalty_util.is_in_household("true_card_number")
    assert is_in_household == True


@patch(
    "loyalty_util.ee.wallet.get_wallet_by_identity_value",
    return_value=(
        {
            "walletId": "128875740",
            "friendlyName": "Wallet 1 of household 1",
            "status": "ACTIVE",
            "type": "MEMBER",
            "state": "EARNBURN",
            "meta": {"sample": "metadata", "key": "value"},
            "dateCreated": "2022-03-09T04:10:05+00:00",
            "lastUpdated": "2022-03-09T04:10:26+00:00",
            "relationships": {
                "parent": [],
                "child": [],
                "associate": [],
                "donor": [],
            },
        }
    ),
)
def test_is_in_household_false(fake_wallet):
    is_in_household, wallet = loyalty_util.is_in_household("false_card_number")
    assert is_in_household == False


@patch(
    "loyalty_util.is_in_household",
    return_value=(True, {"relationships": {"child": [123]}}),
)
@patch(
    "loyalty_util.ee.wallet.get_wallet_by_wallet_id",
    return_value=(
        {
            "walletId": "128875756",
            "friendlyName": "HOUSEHOLD WALLET of holder 666082022140258367737",
            "status": "ACTIVE",
            "type": "HOUSEHOLD",
            "state": "EARNBURN",
            "meta": {"primary lcn": "666082022140258367737"},
            "dateCreated": "2022-03-09T04:27:12+00:00",
            "lastUpdated": "2022-03-09T04:27:13+00:00",
            "relationships": {
                "parent": ["128193334", "128193338"],
                "child": [],
                "associate": [],
                "donor": [],
            },
        }
    ),
)
@patch(
    "loyalty_util.ee.wallet.get_wallet_by_identity_value",
    return_value=(
        {
            "walletId": "128875740",
            "friendlyName": "Wallet 1 of household 1",
            "status": "ACTIVE",
            "type": "MEMBER",
            "state": "EARNBURN",
            "meta": {"sample": "metadata", "key": "value"},
            "dateCreated": "2022-03-09T04:10:05+00:00",
            "lastUpdated": "2022-03-09T04:10:26+00:00",
            "relationships": {
                "parent": [],
                "child": ["128875739"],
                "associate": [],
                "donor": [],
            },
        }
    ),
)
def test_is_household_primary_card(fake_is_household, h_wallet, p_wallet):
    (
        is_household_primary_card,
        p_wallet,
        h_wallet,
    ) = loyalty_util.is_household_primary_card("666082022140258367737")
    assert is_household_primary_card == "PRIMARY"


@patch(
    "loyalty_util.is_in_household",
    return_value=(True, {"relationships": {"child": [123]}}),
)
@patch(
    "loyalty_util.ee.wallet.get_wallet_by_wallet_id",
    return_value=(
        {
            "walletId": "128875756",
            "friendlyName": "HOUSEHOLD WALLET of holder 666082022140258367737",
            "status": "ACTIVE",
            "type": "HOUSEHOLD",
            "state": "EARNBURN",
            "meta": {"primary lcn": "666082022140258367737"},
            "dateCreated": "2022-03-09T04:27:12+00:00",
            "lastUpdated": "2022-03-09T04:27:13+00:00",
            "relationships": {
                "parent": ["128193334", "128193338"],
                "child": [],
                "associate": [],
                "donor": [],
            },
        }
    ),
)
@patch(
    "loyalty_util.ee.wallet.get_wallet_by_identity_value",
    return_value=(
        {
            "walletId": "128875740",
            "friendlyName": "Wallet 1 of household 1",
            "status": "ACTIVE",
            "type": "MEMBER",
            "state": "EARNBURN",
            "meta": {"sample": "metadata", "key": "value"},
            "dateCreated": "2022-03-09T04:10:05+00:00",
            "lastUpdated": "2022-03-09T04:10:26+00:00",
            "relationships": {
                "parent": [],
                "child": ["128875739"],
                "associate": [],
                "donor": [],
            },
        }
    ),
)
def test_is_household_primary_card_secondary(fake_is_household, h_wallet, p_wallet):
    (
        is_household_primary_card,
        p_wallet,
        h_wallet,
    ) = loyalty_util.is_household_primary_card("secondary card number")
    assert is_household_primary_card == "SECONDARY"


@patch("loyalty_util.is_in_household", return_value=(False, {}))
@patch(
    "loyalty_util.ee.wallet.get_wallet_by_wallet_id",
    return_value=(
        {
            "walletId": "128875756",
            "friendlyName": "HOUSEHOLD WALLET of holder 666082022140258367737",
            "status": "ACTIVE",
            "type": "HOUSEHOLD",
            "state": "EARNBURN",
            "meta": {"primary lcn": "666082022140258367737"},
            "dateCreated": "2022-03-09T04:27:12+00:00",
            "lastUpdated": "2022-03-09T04:27:13+00:00",
            "relationships": {
                "parent": ["128193334", "128193338"],
                "child": [],
                "associate": [],
                "donor": [],
            },
        }
    ),
)
@patch(
    "loyalty_util.ee.wallet.get_wallet_by_identity_value",
    return_value=(
        {
            "walletId": "128875740",
            "friendlyName": "Wallet 1 of household 1",
            "status": "ACTIVE",
            "type": "MEMBER",
            "state": "EARNBURN",
            "meta": {"sample": "metadata", "key": "value"},
            "dateCreated": "2022-03-09T04:10:05+00:00",
            "lastUpdated": "2022-03-09T04:10:26+00:00",
            "relationships": {
                "parent": [],
                "child": ["128875739"],
                "associate": [],
                "donor": [],
            },
        }
    ),
)
def test_is_household_primary_card_not_in_household(
    fake_is_household, h_wallet, p_wallet
):
    (
        is_household_primary_card,
        p_wallet,
        h_wallet,
    ) = loyalty_util.is_household_primary_card("Not in a house hold")
    assert is_household_primary_card == "NO_IN_HOUSEHOLD"


class test_link_cards(unittest.TestCase):
    @patch("loyalty_util.is_in_household", return_value=(True, {"walletId": 123456}))
    def test_link_card_primary_already_in_household(self, is_secondary_in_household):
        with self.assertRaises(ValueError) as exc:
            loyalty_util.link_cards("primary_card", "secondary_card")

        self.assertEqual(
            str(exc.exception),
            "card secondary_card is already member of a household",
        )

    @patch("loyalty_util.is_in_household", return_value=(False, {"walletId": 123456}))
    @patch("loyalty_util.is_household_primary_card", return_value=("SECONDARY", {}, {}))
    def test_link_card_primary_card_is_secondary(self, is_secondary, is_primary):
        with self.assertRaises(ValueError) as exc:
            loyalty_util.link_cards("primary_card", "secondary_card")

        self.assertEqual(
            str(exc.exception),
            "primary_card is not a primary card but a secondary card of a household",
        )

    @patch("loyalty_util.is_in_household", return_value=(False, {"walletId": 123456}))
    @patch(
        "loyalty_util.is_household_primary_card",
        return_value=("NO_IN_HOUSEHOLD", {"walletId": 123456}, {}),
    )
    @patch("loyalty_util.create_house_hold_wallet", return_value={"walletId": 123456})
    @patch(
        "loyalty_util.ee.wallet.create_wallet_child_relation",
        return_value={},
    )
    def test_link_card_primary_card_not_in_household(
        self, is_secondary, is_primary, p, p2
    ):
        with self.assertLogs(level="INFO") as log:
            loyalty_util.link_cards("primary_card", "secondary_card")
            self.assertEqual(len(log.output), 2)
            self.assertEqual(len(log.records), 2)
            self.assertIn(
                "Primary card is not in any household wallet. New household wallet is created.",
                log.output[0],
            )

    @patch("loyalty_util.is_in_household", return_value=(False, {"walletId": 123456}))
    @patch(
        "loyalty_util.is_household_primary_card",
        return_value=("NO_IN_HOUSEHOLD", {"walletId": 123456}, {}),
    )
    @patch("loyalty_util.create_house_hold_wallet", return_value={"walletId": 123456})
    @patch(
        "loyalty_util.ee.wallet.create_wallet_child_relation",
        return_value={},
    )
    def test_link_card_primary_card_not_in_household(
        self, is_secondary, is_primary, p, p2
    ):
        with self.assertLogs(level="INFO") as log:
            loyalty_util.link_cards("primary_card", "secondary_card")
            self.assertEqual(len(log.output), 2)
            self.assertEqual(len(log.records), 2)
            self.assertIn(
                "Primary card is not in any household wallet. New household wallet is created.",
                log.output[0],
            )

    @patch("loyalty_util.is_in_household", return_value=(False, {"walletId": 123456}))
    def test_unlink_card_secondary_card_not_in_household(
        self,
        p1,
    ):
        with self.assertRaises(ValueError) as exc:
            loyalty_util.unlink_cards("primary_card", "secondary_card")
        self.assertEqual(
            str(exc.exception),
            "card secondary_card does not belong to any household wallet.",
        )

    @patch("loyalty_util.is_in_household", return_value=(True, {"walletId": 123456}))
    @patch(
        "loyalty_util.is_household_primary_card",
        return_value=("SECONDARY", {"walletId": 123456}, {}),
    )
    def test_unlink_card_primary_card_is_secondary(self, p1, p2):
        with self.assertRaises(ValueError) as exc:
            loyalty_util.unlink_cards("primary_card", "secondary_card")
        self.assertEqual(
            str(exc.exception),
            "primary_card is not a primary card but a secondary card of a household",
        )

    @patch("loyalty_util.is_in_household", return_value=(True, {"walletId": 123456}))
    @patch(
        "loyalty_util.is_household_primary_card",
        return_value=("NO_IN_HOUSEHOLD", {"walletId": 123456}, {}),
    )
    def test_unlink_card_primary_card_not_in_household(self, p1, p2):
        with self.assertRaises(ValueError) as exc:
            loyalty_util.unlink_cards("primary_card", "secondary_card")
        self.assertEqual(
            str(exc.exception),
            "card secondary_card does not belong to any household wallet.",
        )

    @patch(
        "loyalty_util.is_in_household",
        return_value=(True, {"walletId": 123456, "relationships": {"child": [123]}}),
    )
    @patch(
        "loyalty_util.is_household_primary_card",
        return_value=(
            "PRIMARY",
            {"walletId": 123456, "relationships": {"child": [234]}},
            {"walletId": 111},
        ),
    )
    def test_unlink_cards_not_in_same_household(self, p1, p2):
        with self.assertRaises(ValueError) as exc:
            loyalty_util.unlink_cards("primary_card", "secondary_card")
        self.assertEqual(
            str(exc.exception),
            "card primary_card and secondary_card are not in the same household wallet.",
        )

    @patch(
        "loyalty_util.is_in_household",
        return_value=(True, {"walletId": 222, "relationships": {"child": [111]}}),
    )
    @patch(
        "loyalty_util.is_household_primary_card",
        return_value=(
            "PRIMARY",
            {"walletId": 333, "relationships": {"child": [111]}},
            {"walletId": 111, "relationships": {"parent": [222, 333, 444]}},
        ),
    )
    @patch("loyalty_util.ee.wallet.split_wallet_relation", return_value={})
    def test_unlink_cards_positive(self, p1, p2, p3):
        with self.assertLogs(level="INFO") as log:
            loyalty_util.unlink_cards("primary_card", "secondary_card")
            self.assertEqual(len(log.output), 1)
            self.assertEqual(len(log.records), 1)
            self.assertIn(
                "Completed unlinking card.",
                log.output[0],
            )

    @patch(
        "loyalty_util.is_in_household",
        return_value=(True, {"walletId": 222, "relationships": {"child": [111]}}),
    )
    @patch(
        "loyalty_util.is_household_primary_card",
        return_value=(
            "PRIMARY",
            {"walletId": 333, "relationships": {"child": [111]}},
            {"walletId": 111, "relationships": {"parent": [222, 333]}},
        ),
    )
    @patch("loyalty_util.ee.wallet.split_wallet_relation", return_value={})
    @patch("loyalty_util.ee.wallet.delete_wallet", return_value={})
    def test_unlink_cards_(self, p1, p2, p3, p4):
        with self.assertLogs(level="INFO") as log:
            loyalty_util.unlink_cards("primary_card", "secondary_card")
            self.assertEqual(len(log.output), 2)
            self.assertEqual(len(log.records), 2)
            self.assertIn(
                "Deleted household wallet, since it only has one child left.",
                log.output[0],
            )
            self.assertIn(
                "Completed unlinking card.",
                log.output[1],
            )


@patch("loyalty_util.ee.wallet.split_wallet_relation", return_value={})
@patch("loyalty_util.ee.wallet.delete_wallet", return_value={})
@patch(
    "loyalty_util.ee.wallet.get_wallet_accounts_by_identity_value",
    return_value={"walletId": 111},
)
def test_dismantle_household_wallet(fake_split, fake_delete, p1):
    h_wallet = {"walletId": 111, "relationships": {"parent": [222, 333]}}
    loyalty_util.dismantle_household_wallet(h_wallet)
