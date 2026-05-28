"""SQLAlchemy models for auctions and bids."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class Auction(Base):
    __tablename__ = "auctions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    group_id = Column(String(36), nullable=False)
    month_number = Column(Integer, nullable=False)
    scheduled_at = Column(DateTime)
    opened_at = Column(DateTime)
    closed_at = Column(DateTime)
    status = Column(Enum("SCHEDULED", "OPEN", "CLOSED", "CANCELLED"), default="SCHEDULED")
    winner_id = Column(String(36))
    winning_bid_amount = Column(Numeric(12, 2))
    disbursement_amount = Column(Numeric(12, 2))
    created_at = Column(DateTime, default=datetime.utcnow)

    bids = relationship("Bid", back_populates="auction", cascade="all, delete-orphan")


class Bid(Base):
    __tablename__ = "bids"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    auction_id = Column(String(36), ForeignKey("auctions.id"), nullable=False)
    member_id = Column(String(36), nullable=False)
    bid_amount = Column(Numeric(12, 2), nullable=False)
    placed_at = Column(DateTime, default=datetime.utcnow)

    auction = relationship("Auction", back_populates="bids")
