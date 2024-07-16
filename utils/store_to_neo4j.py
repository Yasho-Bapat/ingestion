from connectors.neo4j_connector import Neo4jConnector


def store_to_neo4j(data):
    connector = Neo4jConnector()
    session = connector.get_session()

    # Extracting data from the input
    document_name = data.get("document_name")
    identification = data.get("identification")
    toxicological_information = data.get("toxicological_information")

    material_name = identification.get("material_name")
    manufacturer_info = identification.get("manufacturer_info")
    created_by = identification.get("created_by")
    created_on = identification.get("created_on")
    revision_date = identification.get("revision_date")

    # Create Material node
    session.run(
        """
        MERGE (m:Material {name: $material_name})
        SET m.creation_date = $created_on,
            m.rev_date = $revision_date,
            m.doc_name = $document_name
        """,
        material_name=material_name,
        created_on=created_on,
        revision_date=revision_date,
        document_name=document_name
    )

    # Handle manufacturer information
    if manufacturer_info:
        manufacturer_name = manufacturer_info.get("name")
        manufacturer_address = manufacturer_info.get("address")
        manufacturer_contact = manufacturer_info.get("contact")
        manufacturer_emergency_contact = manufacturer_info.get("emergency_contact")

        session.run(
            """
            MERGE (manu:Manufacturer {name: $manufacturer_name})
            SET manu.address = $manufacturer_address,
                manu.contact = $manufacturer_contact,
                manu.emergency_contact = $manufacturer_emergency_contact
            MERGE (m:Material {name: $material_name})
            MERGE (m)-[:MANUFACTURED_BY]->(manu)
            """,
            manufacturer_name=manufacturer_name,
            manufacturer_address=manufacturer_address,
            manufacturer_contact=manufacturer_contact,
            manufacturer_emergency_contact=manufacturer_emergency_contact,
            material_name=material_name
        )

    # Process toxicological information for the material
    if toxicological_information:
        # Carcinogenic Info
        if toxicological_information.get("material_carcinogenic"):
            carcinogenic = toxicological_information.get("material_carcinogenic")
            session.run(
                """
                MERGE (m:Material {name: $material_name})
                MERGE (c:Carcinogen {status: $status, details: $details, source: $source})
                MERGE (m)-[:HAS_CARCINOGEN_INFO]->(c)
                """,
                material_name=material_name,
                status=carcinogenic.get("status"),
                details=carcinogenic.get("details"),
                source=carcinogenic.get("source")
            )

        # Mutagenic Info
        if toxicological_information.get("material_mutagenicity"):
            mutagenic = toxicological_information.get("material_mutagenicity")
            session.run(
                """
                MERGE (m:Material {name: $material_name})
                MERGE (mut:Mutagen {status: $status, details: $details, source: $source})
                MERGE (m)-[:HAS_MUTAGEN_INFO]->(mut)
                """,
                material_name=material_name,
                status=mutagenic.get("status"),
                details=mutagenic.get("details"),
                source=mutagenic.get("source")
            )

        # Reproductive Toxicity Info
        if toxicological_information.get("material_reproductive_toxicity"):
            reproductive_toxicity = toxicological_information.get("material_reproductive_toxicity")
            session.run(
                """
                MERGE (m:Material {name: $material_name})
                MERGE (rep:ReproductiveToxicity {status: $status, details: $details, source: $source})
                MERGE (m)-[:HAS_REPRO_INFO]->(rep)
                """,
                material_name=material_name,
                status=reproductive_toxicity.get("status"),
                details=reproductive_toxicity.get("details"),
                source=reproductive_toxicity.get("source")
            )

        # Teratogenicity Info
        if toxicological_information.get("material_teratogenicity"):
            teratogenicity = toxicological_information.get("material_teratogenicity")
            session.run(
                """
                MERGE (m:Material {name: $material_name})
                MERGE (ter:Teratogen {status: $status, details: $details, source: $source})
                MERGE (m)-[:HAS_TERATOGEN_INFO]->(ter)
                """,
                material_name=material_name,
                status=teratogenicity.get("status"),
                details=teratogenicity.get("details"),
                source=teratogenicity.get("source")
            )

        # Process chemical-level toxicity
        for chemical_info in toxicological_information.get("chemical_level_toxicity", []):
            chemical_name = chemical_info.get("name")
            toxicity = chemical_info.get("toxicity")

            # Create Chemical node
            session.run(
                """
                MERGE (c:Chemical {name: $chemical_name})
                SET c.concentration = $concentration
                """,
                chemical_name=chemical_name,
                concentration=chemical_info.get("concentration")
            )

            # Link Chemical to Material
            session.run(
                """
                MATCH (m:Material {name: $material_name})
                MATCH (c:Chemical {name: $chemical_name})
                MERGE (m)-[:HAS_CHEMICAL]->(c)
                """,
                material_name=material_name,
                chemical_name=chemical_name
            )

            # Carcinogenic Info for Chemical
            if toxicity.get("chemical_carcinogenic"):
                chemical_carcinogenic = toxicity.get("chemical_carcinogenic")
                session.run(
                    """
                    MERGE (c:Chemical {name: $chemical_name})
                    MERGE (cc:Carcinogen {status: $status, details: $details, source: $source})
                    MERGE (c)-[:HAS_CARCINOGEN_INFO]->(cc)
                    """,
                    chemical_name=chemical_name,
                    status=chemical_carcinogenic.get("status"),
                    details=chemical_carcinogenic.get("details"),
                    source=chemical_carcinogenic.get("source")
                )

            # Mutagenic Info for Chemical
            if toxicity.get("chemical_mutagenicity"):
                chemical_mutagenic = toxicity.get("chemical_mutagenicity")
                session.run(
                    """
                    MERGE (c:Chemical {name: $chemical_name})
                    MERGE (cm:Mutagen {status: $status, details: $details, source: $source})
                    MERGE (c)-[:HAS_MUTAGEN_INFO]->(cm)
                    """,
                    chemical_name=chemical_name,
                    status=chemical_mutagenic.get("status"),
                    details=chemical_mutagenic.get("details"),
                    source=chemical_mutagenic.get("source")
                )

            # Reproductive Toxicity Info for Chemical
            if toxicity.get("chemical_reproductive_toxicity"):
                chemical_reproductive_toxicity = toxicity.get("chemical_reproductive_toxicity")
                session.run(
                    """
                    MERGE (c:Chemical {name: $chemical_name})
                    MERGE (cr:ReproductiveToxicity {status: $status, details: $details, source: $source})
                    MERGE (c)-[:HAS_REPRO_INFO]->(cr)
                    """,
                    chemical_name=chemical_name,
                    status=chemical_reproductive_toxicity.get("status"),
                    details=chemical_reproductive_toxicity.get("details"),
                    source=chemical_reproductive_toxicity.get("source")
                )

            # Teratogenicity Info for Chemical
            if toxicity.get("chemical_teratogenic"):
                chemical_teratogenic = toxicity.get("chemical_teratogenic")
                session.run(
                    """
                    MERGE (c:Chemical {name: $chemical_name})
                    MERGE (ct:Teratogen {status: $status, details: $details, source: $source})
                    MERGE (c)-[:HAS_TERATOGEN_INFO]->(ct)
                    """,
                    chemical_name=chemical_name,
                    status=chemical_teratogenic.get("status"),
                    details=chemical_teratogenic.get("details"),
                    source=chemical_teratogenic.get("source")
                )

            # Additional Info for Chemical
            for other_info in toxicity.get("other_info", []):
                session.run(
                    """
                    MATCH (c:Chemical {name: $chemical_name})
                    SET c.additional_info = COALESCE(c.additional_info, []) + $other_info
                    """,
                    chemical_name=chemical_name,
                    other_info=other_info
                )

            # Impacts on Humans for Chemical
            for impact in chemical_info.get("impacts_on_humans", []):
                session.run(
                    """
                    MATCH (c:Chemical {name: $chemical_name})
                    SET c.impacts_on_humans = COALESCE(c.impacts_on_humans, []) + $impact
                    """,
                    chemical_name=chemical_name,
                    impact=impact
                )

        # SVHC Info
        if toxicological_information.get("svhc"):
            svhc = toxicological_information.get("svhc")
            session.run(
                """
                MERGE (m:Material {name: $material_name})
                MERGE (sv:SVHC {status: $status, details: $details, source: $source})
                MERGE (m)-[:HAS_SVHC_INFO]->(sv)
                """,
                material_name=material_name,
                status=svhc.get("status"),
                details=svhc.get("details"),
                source=svhc.get("source")
            )

        # Additional Information
        for additional_info in toxicological_information.get("additional_information", []):
            session.run(
                """
                MATCH (m:Material {name: $material_name})
                SET m.additional_information = COALESCE(m.additional_information, []) + $additional_info
                """,
                material_name=material_name,
                additional_info=additional_info
            )

    # Close the session
    session.close()
