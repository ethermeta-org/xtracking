import sqlalchemy
from sqlmodel import Session, select, or_

from app.xiot_api import schema


def crud_create_tracking_record(db: Session, item: schema.RetraspectsCreate) -> schema.Retraspects:
    rec = schema.Retraspects(jq_sn=item.jq_sn, vendor_sn=item.vendor_sn,
                             product_code="TBD", product_name='TBD',
                             controller_code=item.controller_code, system_code=item.system_code)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


def crud_existed_records(db: Session, item: schema.RetraspectsCreate) -> schema.Retraspects:
    statement = select(schema.Retraspects).where(schema.Retraspects.jq_sn == item.jq_sn,
                                                 schema.Retraspects.system_code == item.system_code,
                                                 schema.Retraspects.controller_code == item.controller_code,
                                                 )
    result = db.exec(statement).one_or_none()
    return result


def crud_conflict_records_existed(db: Session, item: schema.RetraspectsCreate) -> schema.Retraspects:
    statement = select(schema.Retraspects).where(or_(schema.Retraspects.jq_sn == item.jq_sn,
                                                     schema.Retraspects.system_code == item.system_code,
                                                     schema.Retraspects.controller_code == item.controller_code,
                                                     ))
    result = db.exec(statement).one_or_none()
    return result


def crud_update_existed_records_vendor_sn(db: Session, rec: sqlalchemy.engine.result,
                                          vendor_sn: str) -> schema.Retraspects:
    rec.vendor_sn = vendor_sn
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec
