from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Annotated, Literal, Any

class SDO(BaseModel):
    id: str
    type: str
    name: str

class SCO(BaseModel):
    id: str
    type: str
    value: str

class SRO(BaseModel):
    id: str
    type: str
    relationship_type: str
    source_ref: str
    target_ref: str
    description: Optional[str] = None

class Relationship(SRO):
    pass

class DomainName(SCO):
    pass

class Hostname(SCO):
    pass

class URL(SCO):
    pass

class EmailAddress(SCO):
    pass

class Ipv4Address(SCO):
    pass

class CryptocurrencyWallet(SCO):
    pass

class Indicator(SDO):
    description: Optional[str] = None
    indicator_types: Optional[list] = None
    pattern: str
    pattern_type: str
    pattern_type: Literal["stix", "snort", "yara"]

class File(SDO):
    name: Optional[str] = None
    hashes: dict
    size: Optional[Any] = None
    mime_type: Optional[Any] = None

class AttackPattern(SDO):
    description: Optional[str] = None
    aliases: Optional[Any] = None

class Identity(SDO):
    description: Optional[str]=None

class MarkingDefinition(SDO):
    definition: Optional[dict] = None

class Malware(SDO):
    description: Optional[str] = None
    malware_types: Optional[Any] = None
    is_family: Optional[Any] = None
    aliases: Optional[Any] = None
    os_execution_envs: Optional[Any] = None
    architecture_execution_envs: Optional[Any] = None
    implementation_languages: Optional[Any] = None

class Report(SDO):
    description: str
    labels: list
    report_types: Optional[list] = None
    created: datetime
    object_refs: list

class Location(SDO):
    country: str
    description: Optional[str] = None
    latitude: Optional[Any] = None
    longtitude: Optional[Any] = None
    city: Optional[str] = None

class Vulnerability(SDO):
    description: Optional[str] = None

class IntrusionSet(SDO):
    description: Optional[str] = None
    aliases: Optional[Any] = None
    goals: Optional[Any] = None
    resource_level: Optional[Any] = None
    primary_motivation: Optional[Any] = None
    secondary_motivation: Optional[Any] = None

class StixToPydanticMap:
    def __init__(self):
        self.type_to_class = {
            "relationship":Relationship,
            "domain-name":DomainName,
            "hostname":Hostname,
            "url":URL,
            "email-addr":EmailAddress,
            "ipv4-addr":Ipv4Address,
            "cryptocurrency-wallet":CryptocurrencyWallet,
            "indicator":Indicator, 
            "file":File, 
            "attack-pattern":AttackPattern, 
            "identity":Identity, 
            "marking-definition":MarkingDefinition,
            "malware":Malware, 
            "report":Report, 
            "location":Location, 
            "vulnerability":Vulnerability, 
            "intrusion-set":IntrusionSet
        }

    def to_pydantic(self, x):
        object_type = x["type"]
        pydantic_object = self.type_to_class[object_type]
        return pydantic_object(**x)
    
    def __call__(self, x):
        return self.to_pydantic(x)