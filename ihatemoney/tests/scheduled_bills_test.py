from collections import defaultdict
import time
from time import sleep
from urllib.parse import urlparse, urlunparse

from flask import session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from ihatemoney import models
from ihatemoney.currency_convertor import CurrencyConverter
from ihatemoney.tests.common.help_functions import extract_link
from ihatemoney.tests.common.ihatemoney_testcase import IhatemoneyTestCase
from ihatemoney.forms import get_billform_for

from wtforms.fields import SelectField
 
from unittest.mock import patch

def allow_1_sec_schedule():
    choices = [(1, "1-sec"), (3600, "1 Hour")]
    recurring_schedule = SelectField(label="Repeat every", choices=choices, coerce=int, default = 0)
    return recurring_schedule

class ScheduledBillsTestCase(IhatemoneyTestCase):

    @patch("ihatemoney.forms.BillForm.recurring_schedule", new_callable=allow_1_sec_schedule)
    def test_recurring_bill(self, recurring_schedule_mock):
        self.post_project("raclette")
        # add two participants
        self.client.post("/raclette/members/add", data={"name": "zorglub"})
        self.client.post("/raclette/members/add", data={"name": "tata"})

        members_ids = [m.id for m in self.get_project("raclette").members]

        # test balance
        self.client.post(
            "/raclette/add",
            data={
                "date": "2011-08-10",
                "what": "fromage à raclette",
                "payer": members_ids[0],
                "payed_for": members_ids,
                "amount": "100",
                "recurring_schedule": 1
            },
        )

        p = self.get_project("raclette")
        assert len(p.get_bills().all()) == 1

        time.sleep(1.5) 
        assert len(p.get_bills().all()) > 1

    @patch("ihatemoney.forms.BillForm.recurring_schedule", new_callable=allow_1_sec_schedule)
    def test_edit_bill_schedule(self, recurring_schedule_mock):
        self.post_project("raclette")
        # add two participants
        self.client.post("/raclette/members/add", data={"name": "zorglub"})
        self.client.post("/raclette/members/add", data={"name": "tata"})

        members_ids = [m.id for m in self.get_project("raclette").members]

        # test balance
        self.client.post(
            "/raclette/add",
            data={
                "date": "2011-08-10",
                "what": "fromage à raclette",
                "payer": members_ids[0],
                "payed_for": members_ids,
                "amount": "100",
                "recurring_schedule": 1
            },
        )

        p = self.get_project("raclette")
        assert len(p.get_bills().all()) == 1

        bill_id = p.get_bills().first().id

        resp = self.client.post(
            f"/raclette/edit/{bill_id}",
            data={
                "date": "2011-08-10",
                "what": "fromage à raclette",
                "payer": members_ids[0],
                "payed_for": members_ids,
                "amount": "100",
                "recurring_schedule": 3600
            },
        )
        
        # No new bills should be created
        time.sleep(1.5) 
        assert len(p.get_bills().all()) == 1

    @patch("ihatemoney.forms.BillForm.recurring_schedule", new_callable=allow_1_sec_schedule)
    def test_delete_bill_schedule(self, recurring_schedule_mock):
        self.post_project("raclette")
        # add two participants
        self.client.post("/raclette/members/add", data={"name": "zorglub"})
        self.client.post("/raclette/members/add", data={"name": "tata"})

        members_ids = [m.id for m in self.get_project("raclette").members]

        # test balance
        self.client.post(
            "/raclette/add",
            data={
                "date": "2011-08-10",
                "what": "fromage à raclette",
                "payer": members_ids[0],
                "payed_for": members_ids,
                "amount": "100",
                "recurring_schedule": 1
            },
        )

        p = self.get_project("raclette")
        assert len(p.get_bills().all()) == 1

        bill_id = p.get_bills().first().id

        resp = self.client.post(
            f"/raclette/delete/{bill_id}",
            data={ } 
        )
        
        # No new bills should be created
        time.sleep(1.5) 
        assert len(p.get_bills().all()) == 0


