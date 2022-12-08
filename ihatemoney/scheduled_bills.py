from apscheduler.triggers.interval import IntervalTrigger
from flask import current_app
from ihatemoney.models import Bill, db


def billing_job_id(bill_id):
    return f"recurring-bill-{bill_id}"

def sched_duplicate_bill(scheduler, bill_id):
    # To use the database, we need to set a context. We can get the context from the scheduler. 
    with scheduler.app.app_context():
        
        bill = Bill.query.filter_by(id = bill_id).first() 
        if not bill:
            raise Exception("Can't find bill to duplicate")

        duplicate_bill = bill.duplicate("(on schedule)")
        duplicate_bill.recurrence = None
        db.session.add(duplicate_bill)
        db.session.commit()

def remove_scheduled_job(bill_id):
    job_name = billing_job_id(bill_id)
    if current_app.scheduler.get_job(job_name):
        current_app.scheduler.remove_job(job_name)

def create_scheduled_job(bill_id, num_seconds):
    if not num_seconds: 
        return 
    job_name = billing_job_id(bill_id)
        
    trigger = IntervalTrigger(seconds = num_seconds)
    current_app.scheduler.add_job(job_name, sched_duplicate_bill, args = [current_app.scheduler, bill_id], 
        trigger = trigger)
