from pydantic.v1 import BaseModel, Field
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


# TOXICOLOGICAL INFORMATION
class ToxicologicalEffect(BaseModel):
    status: bool = Field(description="Toxic Status")
    details: str = Field(description="Details or Reason for status (ex - under which regulation or agency a material has a toxic status for an element). Try to provide a valid reason for the status above.")
    source: str = Field(description="Whether the source was the MSDS information or openai options - (MSDS, OPENAI)")


# class SVHC(BaseModel):
#     status: bool = Field(description="SVHC Status (true or false)")
#     reason_of_inclusion: List[str] = Field(description="If SVHC status is true, give reason(s) for inclusion. The "
#                                                        "reasons can only be among - Toxic for reproduction (Article 57c),"
#                                                        "vPvB (Article 57e), PBT (Article 57d), Equivalent level of "
#                                                        "concern having probable serious effects to human health "
#                                                        "(Article 57(f) - human health), Equivalent level of concern "
#                                                        "having probable serious effects to human health (Article 57(f) - environment, Endocrine disrupting properties (Article 57(f) - human health), Endocrine disrupting properties (Article 57(f) - environment), Respiratory sensitising properties (Article 57(f) - human health), Respiratory sensitising properties (Article 57(f) - environment, Specific target organ toxicity after repeated exposure (Article 57(f) - human health), Mutagenic (Article 57b).")
#     source: str = Field(description="Whether the source was the MSDS information or openai options - (MSDS, OPENAI)")


class Toxicity(BaseModel):
    action: str = Field(description="Route of how the chemical affects humans or animal; eg: inhalation, touch, etc.")
    affected: str = Field(description="Affected entity (ex - Human, Rat, Rabbit, etc")
    signs_and_symptoms: List[str] = Field(description="Sign and symptoms which one observes.")
    chemical_carcinogenic: ToxicologicalEffect = Field(description="Carcinogenic status of the chemical")
    chemical_mutagenicity: ToxicologicalEffect = Field(description="Mutagenic status of the chemical")
    chemical_reproductive_toxicity: ToxicologicalEffect = Field(description="Reproductive Toxicity status of the chemical")
    chemical_teratogenicity: ToxicologicalEffect = Field(description="Teratogenicity status of the chemical")
    other_info: List[str] = Field(description="Any other information about the chemical's toxicity which does not "
                                              "conform to action and signs & symptoms")


class ChemicalToxicity(BaseModel):
    name: str = Field(description="name of chemical or component")
    toxicity: Toxicity = Field(description="list of ways or standards a component can be toxic, ex - LD 50 (ORAL-RAT)")
    impacts_on_humans: List[str] = Field(description="list of ways or standards a component can impact humans")


class ToxicologicalInfo(BaseModel):
    material_carcinogenic: ToxicologicalEffect = Field(description="Carcinogenic status of the material")
    material_mutagenicity: ToxicologicalEffect = Field(description="Mutagenic status of the material")
    material_reproductive_toxicity: ToxicologicalEffect = Field(description="Reproductive Toxicity status of the material")
    material_teratogenicity: ToxicologicalEffect = Field(description="Teratogenicity status of the material")
    chemical_level_toxicity: List[ChemicalToxicity] = Field(description="list of ways component can be toxic")
    # svhc: str = Field(description="Whether the component is a Substance of Very High Concern. Make the Decision either based on the context or external knowledge sources like ECHA SVHC list.")
    additional_information: List[str] = Field(description="List of additional points relevant to toxicity")

#
# # ECO-TOXICITY
# class EcoToxicity(BaseModel):
#     name: str = Field(description="name of chemical or component")
#     toxicity: List[str] = Field(description="list of ways or standards a component can be toxic, ex - LD 50 (ORAL-RAT)")
#
#
# class EcoToxicologicalInfo(BaseModel):
#     toxicity: List[ChemicalToxicity] = Field(description="list of ways component can be toxic")
#     other: List[str] = Field(description="List of additional points relevant to ecological toxicity")


# # COMPOSITION INFORMATION
# class ChemicalInformation(BaseModel):
#     name: str = Field(description="Chemical Name")
#     cas_number: str = Field(description="CAS Number")
#     concentration: str = Field(description="Concentration if given in percentage")
#     other_information: str = Field(description="Other Information regarding chemical only from document provided")
#
#
# class MaterialComposition(BaseModel):
#     composition: List[ChemicalInformation] = Field(description="Composition of the material as a list of ChemicalInformations")
#
#
# # STABILITY AND REACTIVITY
# class StabilityReactivity(BaseModel):
#     reactivity: str = Field(description="Reactivity of the material as given in document")
#     stability: str = Field(description="Stability of the material as given in document")
#     avoid: List[str] = Field(description="List of conditions to avoid as given in document")
#     decomp_products: List[str] = Field(description="List of hazardous decomposition products as given in document")
#     hazardous_polymerization: bool = Field(description="Hazardous polymerization as given in document")
#
#
# # REGULATORY INFORMATION
# class Regulatory(BaseModel):
#     countries: List[str] = Field(description="List of countries the material is regulated in according to the document")
#     agency: List[str] = Field(description="List of organizations the material is in accordance with")
# # DECISIONS
# class Decisions(BaseModel):
#     pfas: bool = Field(description="whether the material is PFAS compliant or not")
#     carcinogenic: bool = Field(description="whether the material is carcinogenic or not")
#     svhc: bool = Field(description="whether the material is SVHC compliant or not")
#
#
# # ALL INFO
# class DocumentInformation(BaseModel):
#     identification: Identification = Field(description="information for identifying the material")
#     material_composition: MaterialComposition = Field(description="information about composition of material")
