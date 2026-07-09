from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    elo_rating = Column(Integer, default=1200)

    games = relationship("Game", back_populates="user")

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    opponent_name = Column(String(50))
    result = Column(String(20)) # e.g., "win", "loss", "draw"
    pgn = Column(String) # Portable Game Notation
    played_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="games")

from pydantic import BaseModel, Field, field_validator
import chess

class MoveRequest(BaseModel):
    fen: str
    difficulty: int = Field(default=50, ge=0, le=100)
    aggression: int = Field(default=50, ge=0, le=100)
    
    @field_validator('fen')
    @classmethod
    def validate_fen(cls, v: str):
        try:
            chess.Board(v)
            return v
        except Exception:
            raise ValueError("Invalid FEN")
