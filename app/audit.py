from sqlalchemy import event
from app.models.audit_log import AuditLog
import json
from datetime import datetime, date
def get_model_data(instance):
    def safe_value(val):
        if isinstance(val, (datetime, date)):
            return val.isoformat()
        return val

    return {
        col.name: safe_value(getattr(instance, col.name))
        for col in instance.__table__.columns
    }

def register_auditing_for_model(model_class, Session):
    @event.listens_for(Session, "after_flush")
    def after_flush(session, flush_context):
        for obj in session.new:
            if isinstance(obj, model_class):
                log = AuditLog(
                    table_name=obj.__tablename__,
                    operation="INSERT",
                    old_data=None,
                    new_data=get_model_data(obj),
                    user=getattr(session.info, "user", None)
                )
                session.add(log)

        for obj in session.dirty:
            if isinstance(obj, model_class) and session.is_modified(obj):
                log = AuditLog(
                    table_name=obj.__tablename__,
                    operation="UPDATE",
                    old_data=get_model_data(obj),  # dados antes
                    new_data=get_model_data(obj),                        # dados depois
                    user=getattr(session.info, "user", None)
                )
                session.add(log)

        for obj in session.deleted:
            if isinstance(obj, model_class):
                log = AuditLog(
                    table_name=obj.__tablename__,
                    operation="DELETE",
                    old_data=get_model_data(obj),
                    new_data=None,
                    user=getattr(session.info, "user", None)
                )
                session.add(log)
