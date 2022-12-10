from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.base import BaseScheduler
from apscheduler.triggers.interval import IntervalTrigger

from ihatemoney.models import Bill, db


class SchduledBills(object):

    _app = None  # Stores the flask application.
    _scheduler: Optional[BaseScheduler] = None

    @staticmethod
    def _billing_job_id(bill_id):
        return f"recurring-bill-{bill_id}"

    @staticmethod
    def _sched_duplicate_bill(bill_id):
        # To use the database, we need to set a context. We can get the context from the scheduler.
        with SchduledBills._app.app_context():

            bill = Bill.query.filter_by(id=bill_id).first()
            if not bill:
                raise Exception("Can't find bill to duplicate")

            duplicate_bill = bill.duplicate("(on schedule)")
            duplicate_bill.recurrence = None
            db.session.add(duplicate_bill)
            db.session.commit()

    @staticmethod
    def remove_scheduled_job(bill_id):
        job_name = SchduledBills._billing_job_id(bill_id)
        if SchduledBills._scheduler.get_job(job_name):
            SchduledBills._scheduler.remove_job(job_name)

    @staticmethod
    def create_scheduled_job(bill_id, num_seconds):
        if not num_seconds:
            return
        job_name = SchduledBills._billing_job_id(bill_id)

        trigger = IntervalTrigger(seconds=num_seconds)
        SchduledBills._scheduler.add_job(
            SchduledBills._sched_duplicate_bill,
            args=[bill_id],
            trigger=trigger,
            id=job_name,
        )

    @staticmethod
    def start(app):
        scheduler = BackgroundScheduler()
        SchduledBills._app = app
        SchduledBills._scheduler = scheduler
        scheduler.start()
