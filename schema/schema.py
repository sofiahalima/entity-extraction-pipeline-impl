from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class EntityMatch(BaseModel):
    entity_type: str  # e.g., "Person"
    entity_text: str  # raw extracted value
    start_pos: int
    end_pos: int
    score: Optional[float]
    is_matched: bool
    matched_entity_id: Optional[str] = None
    matched_entity_name: Optional[str] = None


class EntityOutput(BaseModel):
    uuid: UUID
    title: str
    content: str
    publication_date: Optional[datetime]
    inserted_at: Optional[datetime]
    url: Optional[str]
    source: Optional[str]
    entities: List[EntityMatch]


class Document(BaseModel):
    uuid: UUID
    title_en: Optional[str]
    title_source_language: Optional[str]
    body_en: str
    body_source_language: Optional[str]
    summary_en: str
    summary_source_language: Optional[str]
    publication_date: Optional[datetime]
    url: Optional[str]
    source: Optional[str]


class EntityAlias(BaseModel):
    id: str
    entity_type: str
    name: str
    aliases: List[str]
