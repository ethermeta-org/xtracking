from loguru import logger
from sqlmodel import Field, Session
from app.db import models
from app.xiot_api import schema


def crud_create_tracking_record(db: Session, item: schema.RetraspectsCreate) -> schema.Retraspects:
    rec = schema.Retraspects(jq_sn=item.jq_sn, vendor_sn=item.vendor_sn,
                             product_code="TBD",product_name='TBD',
                             controller_code=item.controller_code, system_code=item.system_code)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec
