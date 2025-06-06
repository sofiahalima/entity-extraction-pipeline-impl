import pandera as pa
from pandera import Column, DataFrameSchema, Check


entity_schema = DataFrameSchema({
    "uuid": Column(pa.String),
    "start": Column(pa.Int, checks=Check.ge(0)),
    "end": Column(pa.Int, checks=Check.ge(0)),
    "text": Column(pa.String),
    "label": Column(pa.String, checks=Check.isin(["Person", "Company", "Location"])),
    "score": Column(pa.Float, nullable=True),
    "title_en": Column(pa.String),
    "title_source_language": Column(pa.String),
    "body_en": Column(pa.String),
    "body_source_language": Column(pa.String),
    "summary_en": Column(pa.String),
    "summary_source_language": Column(pa.String),
    "publication_date": Column(pa.String, nullable=True),
    "url": Column(pa.String),
    "source": Column(pa.String),
    "matched_entity_id": Column(pa.String, nullable=True),
    "matched_entity_name": Column(pa.String, nullable=True),
    "is_matched": Column(pa.Bool)
})
