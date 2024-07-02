from pydantic.v1 import BaseModel, Field
import datetime
from typing import List


# IDENTIFICATION INFORMATION
class ManufacturerInfo(BaseModel):
    name: str = Field(description="Manufacturer Name")
    address: str = Field(description="Address of manufacturer")
    contact: str = Field(description="Contact number")
    emergency_contact: str = Field(description="Emergency contact number")


class Identification(BaseModel):
    material_name: str = Field(description="Material Name")
    manufacturer_info: ManufacturerInfo = Field(description="Manufacturer Information")
    created_by: str = Field(description="Created By")
    created_on: str = Field(description="Creation Date")
    revision_date: str = Field(description="Revision Date")


# COMPOSITION INFORMATION
class ChemicalInformation(BaseModel):
    name: str = Field(description="Chemical Name")
    cas_number: str = Field(description="CAS Number")
    concentration: str = Field(description="Concentration if given in percentage")
    other_information: str = Field(description="Other Information regarding chemical only from document provided")


class MaterialComposition(BaseModel):
    composition: List[ChemicalInformation] = Field(description="Composition of the material as a list of ChemicalInformations")


# STABILITY AND REACTIVITY
class StabilityReactivity(BaseModel):
    reactivity: str = Field(description="Reactivity of the material as given in document")
    stability: str = Field(description="Stability of the material as given in document")
    avoid: List[str] = Field(description="List of conditions to avoid as given in document")
    decomp_products: List[str] = Field(description="List of hazardous decomposition products as given in document")
    hazardous_polymerization: bool = Field(description="Hazardous polymerization as given in document")


# REGULATORY INFORMATION
class Regulatory(BaseModel):
    countries: List[str] = Field(description="List of countries the material is regulated in according to the document")
    agency: List[str] = Field(description="List of organizations the material is in accordance with")


# TOXICOLOGICAL INFORMATION
class ChemicalToxicity(BaseModel):
    name: str = Field(description="name of chemical or component")
    toxicity: List[str] = Field(description="list of ways or standards a component can be toxic, ex - LD 50 (ORAL-RAT)")


class ToxicologicalInfo(BaseModel):
    toxicity: List[ChemicalToxicity] = Field(description="list of ways component can be toxic")
    other: List[str] = Field(description="List of additional points relevant to toxicity")


# ECO-TOXICITY
class EcoToxicity(BaseModel):
    name: str = Field(description="name of chemical or component")
    toxicity: List[str] = Field(description="list of ways or standards a component can be toxic, ex - LD 50 (ORAL-RAT)")


class EcoToxicologicalInfo(BaseModel):
    toxicity: List[ChemicalToxicity] = Field(description="list of ways component can be toxic")
    other: List[str] = Field(description="List of additional points relevant to ecological toxicity")


# DECISIONS
class Decisions(BaseModel):
    pfas: bool = Field(description="whether the material is PFAS compliant or not")
    carcinogenic: bool = Field(description="whether the material is carcinogenic or not")
    svhc: bool = Field(description="whether the material is SVHC compliant or not")


# ALL INFO
class DocumentInformation(BaseModel):
    identification: Identification = Field(description="information for identifying the material")
    material_composition: MaterialComposition = Field(description="information about composition of material")
