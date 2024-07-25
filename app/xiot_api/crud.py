from loguru import logger
from sqlalchemy.orm import Session
from app.db import models
from app.service_api import schemas


def crud_create_tracking_recodr(db: Session, service: schemas.OMESServiceDefItemCreate) -> models.OeMesService:
    db_service = models.OeMesService(customer_code=service.customer_code, version=service.version, node=service.node,
                                     service_port=service.service_port, is_demo=service.is_demo)
    db_service.service_url = f'https://{service.customer_code}.{SAAS_DOMAIN_NAME}'
    db.add(db_service)
    return db_service