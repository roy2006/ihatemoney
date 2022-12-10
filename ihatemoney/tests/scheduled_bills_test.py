import time
from unittest.mock import patch

from wtforms.fields import SelectField

from ihatemoney.tests.common.ihatemoney_testcase import IhatemoneyTestCase


def allow_1_sec_schedule():
    choices = [(1, "1-sec"), (3600, "1 Hour")]
    recurring_schedule = SelectField(
        label="Repeat every", choices=choices, coerce=int, default=0
    )
    return recurring_schedule


@patch(
    "ihatemoney.forms.BillForm.recurring_schedule", new_callable=allow_1_sec_schedule
)
class ScheduledBillsTestCase(IhatemoneyTestCase):
    def test_recurring_bill(self, _):
        self.post_project("raclette")
        # add two participants
        self.client.post("/raclette/members/add", data={"name": "zorglub"})
        self.client.post("/raclette/members/add", data={"name": "tata"})

        members_ids = [m.id for m in self.get_project("raclette").members]

        # test balance
        resp = self.client.post(
            "/raclette/add",
            data={
                "date": "2011-08-10",
                "what": "fromage à raclette",
                "payer": members_ids[0],
                "payed_for": members_ids,
                "amount": "100",
                "recurring_schedule": 1,
            },
        )

        assert resp.status_code == 302

        p = self.get_project("raclette")
        assert len(p.get_bills().all()) == 1

        time.sleep(1.5)
        assert len(p.get_bills().all()) > 1

    def test_edit_bill_schedule(self, _):
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
                "recurring_schedule": 1,
            },
        )

        p = self.get_project("raclette")
        assert len(p.get_bills().all()) == 1

        bill_id = p.get_bills().first().id

        self.client.post(
            f"/raclette/edit/{bill_id}",
            data={
                "date": "2011-08-10",
                "what": "fromage à raclette",
                "payer": members_ids[0],
                "payed_for": members_ids,
                "amount": "100",
                "recurring_schedule": 3600,
            },
        )

        # No new bills should be created
        time.sleep(1.5)
        assert len(p.get_bills().all()) == 1

    def test_delete_bill_schedule(self, _):
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
                "recurring_schedule": 1,
            },
        )

        p = self.get_project("raclette")
        assert len(p.get_bills().all()) == 1

        bill_id = p.get_bills().first().id

        self.client.post(f"/raclette/delete/{bill_id}", data={})

        # No new bills should be created
        time.sleep(1.5)
        assert len(p.get_bills().all()) == 0
