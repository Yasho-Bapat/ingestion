import os
import dotenv

dotenv.load_dotenv()


class DotAccessDict(dict):
    def __getattr__(self, attr):
        if attr in self:
            return self[attr]
        else:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{attr}'"
            )


class Constants(DotAccessDict):
    # Environment Variables
    embedding_deployment = os.getenv("EMBEDDING_DEPLOYMENT")
    llm_deployment = os.getenv("LLM_DEPLOYMENT")
    endpoint = os.getenv("ENDPOINT")
    openai_api_version = os.getenv("OPENAI_API_VERSION")
    azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")

    # Output Example
    example = {
        "document_name": "40.1 SDS NORTON NORPOR 6 X 14 X 1-14 69078671488.pdf",
        "identification": {
            "material_name": "Vitrified Bonded Product",
            "manufacturer_info": {
                "name": "Saint-Gobain Abrasives",
                "address": "One New Bond Street, Worcester, MA 01615",
                "contact": "800-551-4413",
                "emergency_contact": "800-424-9300"
            },
            "created_by": "Saint-Gobain Abrasives",
            "created_on": "2021-04-09",
            "revision_date": "2021-04-09"
        },
        "toxicological_information": {
            "material_carcinogenic": {
                "status": False,
                "details": "Not classifiable as to carcinogenicity to humans. IARC Monographs. Overall Evaluation of Carcinogenicity: Amorphous Silica, Fused (CAS 60676-86-0) 3 Not classifiable as to carcinogenicity to humans. OSHA Specifically Regulated Substances (29 CFR 1910.1001-1053): Not listed. US. National Toxicology Program (NTP) Report on Carcinogens: Not listed.",
                "source": "MSDS"
            },
            "material_mutagenicity": {
                "status": False,
                "details": "No data available to indicate product or any components present at greater than 0.1% are mutagenic or genotoxic.",
                "source": "MSDS"
            },
            "material_reproductive_toxicity": {
                "status": False,
                "details": "This product is not expected to cause reproductive or developmental effects.",
                "source": "MSDS"
            },
            "material_teratogenicity": {
                "status": False,
                "details": "Based on the available information, Vitrified Bonded Products, typically used as abrasive materials, do not seem to be classified as teratogenic. ",
                "source": "OPENAI"
            },
            "chemical_level_toxicity": [
                {
                    "name": "Amorphous Silica, Fused",
                    "toxicity": {
                        "action": "Oral",
                        "affected": "Rat",
                        "signs_and_symptoms": [],
                        "chemical_carcinogenic": {
                            "status": False,
                            "details": "Not classifiable as to carcinogenicity to humans. IARC Monographs. Overall Evaluation of Carcinogenicity: Amorphous Silica, Fused (CAS 60676-86-0) 3 Not classifiable as to carcinogenicity to humans.",
                            "source": "MSDS"
                        },
                        "chemical_mutagenicity": {
                            "status": False,
                            "details": "No data available to indicate product or any components present at greater than 0.1% are mutagenic or genotoxic.",
                            "source": "MSDS"
                        },
                        "chemical_reproductive_toxicity": {
                            "status": False,
                            "details": "This product is not expected to cause reproductive or developmental effects.",
                            "source": "MSDS"
                        },
                        "chemical_teratogenicity": {
                            "status": False,
                            "details": "Fused amorphous silica, also known as fused quartz, is not classified as a teratogen.",
                            "source": "OPENAI"
                        },
                        "other_info": [
                            "LD50 > 22500 mg/kg"
                        ]
                    },
                    "impacts_on_humans": [
                        "Respiratory tract irritation",
                        "Skin irritation",
                        "Eye irritation",
                        "Prolonged inhalation may be harmful"
                    ]
                },
            ],
            "svhc":
                {
                    "status": False,
                    "details": "",
                    "source": "OPENAI",
                },
            "additional_information": [
                "Prolonged skin contact may cause temporary irritation. Direct contact with eyes may cause temporary irritation."
            ]
        },
        "total_tokens": 6578,
        "total_cost": 0.03863
    }

    # Prompts
    template = """
    Context: You will receive selected chunks from a safety datasheet of a material. Your task is to find the requested information based solely on the provided context. Use the following guidelines:

    1. Information Extraction:
       - For material_info, use only the given context to generate answers.
       - For chemical_level_toxicity, if specific information for that chemical is not available in the document provided, look up information about that chemical and generate an appropriate answer.
       - For fields related to toxicity, if information is not available in the context, answer the query by referring to external knowledge.

    2. Format:
       - Return the answer in JSON format.

    Expected Output:{example}

    Note: Ensure accuracy and conciseness in the extracted information.
    """

    human_query = "context: {docs}, query: {query}"

    order = [
        "document_name",
        "identification",
        "material_composition",
        "toxicological_information",
        "total_tokens",
        "total_cost"
    ]

    # prompts
    identification_prompt = "Return material identification information and last date of revision. Check section 1 and 16."
    chemical_composition_prompt = "Return the chemical composition of the material provided. Check section 3 or 2."
    toxicological_info_prompt = "Return toxicological information. Check section 11. "

    # chunking parameters

    # semantic
    breakpoint_threshold_type = "interquartile"
    breakpoint_threshold_amount = 1.5

    # recursive chunking parameters
    chunk_size = 2000
    chunk_overlap = 600
