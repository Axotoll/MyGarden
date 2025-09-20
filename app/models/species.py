from pydantic import BaseModel
from typing import List, Optional

class Species(BaseModel):
    name: str
    scientific_name: Optional[str] = None
    family: Optional[str] = None
    origin: Optional[str] = None
    description: Optional[str] = None
    care_tips: Optional[str] = None
    light_requirements: Optional[str] = None
    water_requirements: Optional[str] = None
    fertilization: Optional[str] = None
    growth_rate: Optional[str] = None
    mature_size: Optional[str] = None
    common_pests: Optional[List[str]] = []
    common_diseases: Optional[List[str]] = []
    base_photos: Optional[List[str]] = []