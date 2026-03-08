import uuid
from sqlalchemy import Column, Integer, String, Float, Numeric, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base # use defined function to connect to our database

class Property(Base):
    __tablename__ = "properties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False, index=True)
    zip_code = Column(String(20), nullable=False)
    property_type = Column(String(50), nullable=False)
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)
    square_meters = Column(Float)
    year_built = Column(Integer)

   
    listings = relationship("Listing", back_populates="property", cascade="all, delete-orphan")
    audits = relationship("Audit", back_populates="property", cascade="all, delete-orphan")
    anomalies = relationship("Anomaly", back_populates="property", cascade="all, delete-orphan")


class Listing(Base):
    __tablename__ = "listings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    asking_price = Column(Numeric(15, 2), nullable=False)
    status = Column(String(50), nullable=False, index=True)
    listed_date = Column(DateTime(timezone=True), server_default=func.now())

    property = relationship("Property", back_populates="listings")


class Audit(Base):
    __tablename__ = "audits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    estimated_rental_income = Column(Numeric(12, 2))
    estimated_maintenance_costs = Column(Numeric(12, 2))
    gross_yield_percentage = Column(Float)
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())

    property = relationship("Property", back_populates="audits")


class Anomaly(Base):
    __tablename__ = "anomalies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    flag_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False)

    property = relationship("Property", back_populates="anomalies")