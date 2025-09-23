from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from pydantic import Field

class GrowthEntry(BaseModel):
    _id_growth: Optional[str] = None
    date: Optional[datetime] = Field(default_factory=datetime.utcnow)
    height: Optional[float]
    photo_url: Optional[str]
    notes: Optional[str] = None


class Plant(BaseModel):
    species_id: Optional[str] = None
    date_planted: Optional[datetime] = Field(default_factory=datetime.utcnow)
    last_watered: Optional[datetime] = Field(default_factory=datetime.utcnow)
    last_fertilized: Optional[datetime] = None
    growth_log: List[GrowthEntry] = []
    care_tips: Optional[str] = None
    user_id: str

class PlantCreate(BaseModel):
    species_id: Optional[str] = None
    date_planted: Optional[datetime] = Field(default_factory=datetime.utcnow)
    last_watered: Optional[datetime] = Field(default_factory=datetime.utcnow)
    last_fertilized: Optional[datetime] = None
    growth_log: List[GrowthEntry] = []
    care_tips: Optional[str] = None