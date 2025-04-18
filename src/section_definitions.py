"""
Section definitions for ProfileDash
Contains descriptions of all profile sections
"""

sections = [
# --- START: Section 1 Definition ---
    {
        "number": 1,
        "title": "Operating Footprint",
        "specs": "Extract data on the total number of employees and their locations, including any available breakdowns (e.g., by region, function). Specify the 'as of' date for employee counts.\n"
                 "Extract data on main operating assets, including their categories (e.g., Manufacturing Plants, Offices, R&D Centers), specific asset names/descriptions, locations (city and country), and ownership status (owned or leased). Specify the 'as of' date for asset information.\n"
                 "Include any relevant quantitative metrics for assets (e.g., production capacity, square footage, book value), clearly specifying units and the 'as of' date.\n"
                 "All extracted data points requiring citation must have a corresponding source reference ID linking to a footnote.\n"
                 "Ensure all footnotes provide precise source details: document name, page number, and specific section/table where the information was found.",
        "schema": {
            "employees": {
                "total": {
                    "value": None, # number
                    "value_source_ref_id": None, # string (e.g., "ref1")
                    "as_of": None, # string (e.g., "December 31, 2023")
                    "as_of_source_ref_id": None # string or same as value_source_ref_id
                },
                "breakdowns": [ # List of employee breakdowns
                    { # Structure definition for ONE item in the list
                        "type": None, # string (e.g., "regional", "functional")
                        "type_source_ref_id": None,
                        "name": None, # string (e.g., "North America", "Manufacturing")
                        "name_source_ref_id": None,
                        "value": None, # number
                        "value_source_ref_id": None,
                        "as_of": None, # string
                        "as_of_source_ref_id": None,
                        "notes": None # Optional string for extra context
                    }
                    # The list can contain zero or more dictionaries matching this structure
                ]
            },
            "assets": {
                "categories": [ # List of asset categories
                    { # Structure definition for ONE item in the list
                        "category_name": None, # string (e.g., "Manufacturing Plants")
                        "category_name_source_ref_id": None,
                        "assets_list": [ # List of specific assets in this category
                            { # Structure definition for ONE asset
                                "asset_name": None, # string (e.g., "Main Production Facility")
                                "asset_name_source_ref_id": None,
                                "location": { # Nested location object
                                    "city": None, # string
                                    "city_source_ref_id": None,
                                    "country": None, # string
                                    "country_source_ref_id": None
                                },
                                "ownership_status": None, # string ("owned" or "leased")
                                "ownership_status_source_ref_id": None,
                                "quantitative_metrics": [ # List of metrics for this asset
                                    { # Structure definition for ONE metric
                                        "metric_name": None, # string (e.g., "Square Footage")
                                        "metric_name_source_ref_id": None,
                                        "value": None, # number or string depending on metric
                                        "value_source_ref_id": None,
                                        "unit": None, # string (e.g., "sq ft", "units/year")
                                        "unit_source_ref_id": None
                                    }
                                    # This list can contain zero or more metric dictionaries
                                ],
                                "as_of": None, # string (date for this asset's info)
                                "as_of_source_ref_id": None,
                                "notes": None # Optional string
                            }
                            # This assets_list can contain zero or more asset dictionaries
                        ]
                    }
                    # This categories list can contain zero or more category dictionaries
                ]
            },
            "footnotes": [ # Top-level list for all footnotes in this section
                { # Structure definition for ONE footnote
                    "id": None, # string (e.g., "ref1")
                    "document": None, # string (e.g., "Annual Report 2023")
                    "page": None, # string or number (e.g., "42", "Appendix A")
                    "section": None # string (e.g., "Company Overview", "Table 5")
                }
                # This list can contain zero or more footnote dictionaries
            ]
        },
        "template": { # Example data aligned with refined schema
            "employees": {
                "total": {
                    "value": 10000,
                    "value_source_ref_id": "ref1",
                    "as_of": "December 31, 2023",
                    "as_of_source_ref_id": "ref1"
                },
                "breakdowns": [
                    {
                        "type": "regional",
                        "type_source_ref_id": "ref1",
                        "name": "North America",
                        "name_source_ref_id": "ref1",
                        "value": 5000,
                        "value_source_ref_id": "ref1",
                        "as_of": "December 31, 2023",
                        "as_of_source_ref_id": "ref1",
                        "notes": "Includes US and Canada operations."
                    },
                     {
                        "type": "functional",
                        "type_source_ref_id": "ref2",
                        "name": "Research & Development",
                        "name_source_ref_id": "ref2",
                        "value": 1200,
                        "value_source_ref_id": "ref2",
                        "as_of": "June 30, 2023",
                        "as_of_source_ref_id": "ref2",
                        "notes": None
                    }
                ]
            },
            "assets": {
                "categories": [
                    {
                        "category_name": "Manufacturing Plants",
                        "category_name_source_ref_id": "ref1",
                        "assets_list": [
                            {
                                "asset_name": "Main Production Facility",
                                "asset_name_source_ref_id": "ref1",
                                "location": {
                                    "city": "Detroit",
                                    "city_source_ref_id": "ref1",
                                    "country": "USA",
                                    "country_source_ref_id": "ref1"
                                },
                                "ownership_status": "owned",
                                "ownership_status_source_ref_id": "ref1",
                                "quantitative_metrics": [
                                    {
                                        "metric_name": "Square Footage",
                                        "metric_name_source_ref_id": "ref1",
                                        "value": 500000,
                                        "value_source_ref_id": "ref1",
                                        "unit": "sq ft",
                                        "unit_source_ref_id": "ref1"
                                    },
                                    {
                                        "metric_name": "Production Capacity",
                                        "metric_name_source_ref_id": "ref1",
                                        "value": 50000,
                                        "value_source_ref_id": "ref1",
                                        "unit": "units/year",
                                        "unit_source_ref_id": "ref1"
                                    }
                                ],
                                "as_of": "December 31, 2023",
                                "as_of_source_ref_id": "ref1",
                                "notes": "Primary facility for product line X."
                            },
                            {
                                "asset_name": "European Assembly Plant",
                                "asset_name_source_ref_id": "ref3",
                                "location": {
                                    "city": "Frankfurt",
                                    "city_source_ref_id": "ref3",
                                    "country": "Germany",
                                    "country_source_ref_id": "ref3"
                                },
                                "ownership_status": "leased",
                                "ownership_status_source_ref_id": "ref3",
                                "quantitative_metrics": [
                                     {
                                        "metric_name": "Lease Expiry",
                                        "metric_name_source_ref_id": "ref3",
                                        "value": "2028-12-31",
                                        "value_source_ref_id": "ref3",
                                        "unit": None,
                                        "unit_source_ref_id": None
                                    }
                                ],
                                "as_of": "December 31, 2023",
                                "as_of_source_ref_id": "ref3",
                                "notes": "Lease includes renewal option."
                            }
                        ]
                    },
                    {
                        "category_name": "R&D Centers",
                        "category_name_source_ref_id": "ref2",
                        "assets_list": [
                             {
                                "asset_name": "Silicon Valley Innovation Hub",
                                "asset_name_source_ref_id": "ref2",
                                "location": {
                                    "city": "Palo Alto",
                                    "city_source_ref_id": "ref2",
                                    "country": "USA",
                                    "country_source_ref_id": "ref2"
                                },
                                "ownership_status": "leased",
                                "ownership_status_source_ref_id": "ref2",
                                "quantitative_metrics": [],
                                "as_of": "June 30, 2023",
                                "as_of_source_ref_id": "ref2",
                                "notes": "Focuses on software development."
                            }
                        ]
                    }
                ]
            },
            "footnotes": [ # Example corresponding footnotes
                {
                    "id": "ref1", 
                    "document": "Annual Report 2023", 
                    "page": "42", 
                    "section": "Operations Overview"
                },
                 {
                    "id": "ref2", 
                    "document": "Investor Presentation Q2 2023", 
                    "page": "15", 
                    "section": "Global Footprint"
                },
                 {
                    "id": "ref3", 
                    "document": "Annual Report 2023", 
                    "page": "F-18", 
                    "section": "Note 7: Leases"
                }
            ]
        }
    },
# --- END: Section 1 Definition ---

# --- START: Section 2 Definition ---
    {
        "number": 2,
        "title": "Products and Services",
        "specs": "Extract a list of key product/service categories and individual products/services within each category.\n"
                 "For each major category and product, extract its value proposition from the customer perspective and any stated competitive advantages (why customers should choose this over competitors).\n"
                 "Capture available performance metrics (e.g., revenue contribution percentage, market share, growth rate) for major categories and products, specifying the 'as of' date or period for each metric.\n"
                 "Extract information on product lifecycle stage (e.g., Growth, Mature, Decline) and market positioning (e.g., Premium, Mid-Market, Low-Cost) if available.\n"
                 "Extract the launch date for key products if mentioned.\n"
                 "All extracted data points requiring citation must have a corresponding source reference ID linking to a footnote.\n"
                 "Ensure all footnotes provide precise source details: document name, page number, and specific section/table.",
        "schema": {
            "product_categories": [ # List of product/service categories
                { # Structure definition for ONE category
                    "name": None, # string (e.g., "Cloud Infrastructure Services")
                    "name_source_ref_id": None,
                    "description": None, # string
                    "description_source_ref_id": None,
                    "value_proposition": None, # string
                    "value_proposition_source_ref_id": None,
                    "competitive_advantage": None, # string
                    "competitive_advantage_source_ref_id": None,
                    "metrics": [ # List of performance metrics for this category
                        { # Structure for ONE metric
                            "name": None, # string (e.g., "Revenue Contribution")
                            "name_source_ref_id": None,
                            "value": None, # number or string
                            "value_source_ref_id": None,
                            "unit": None, # string (e.g., "%", "million USD")
                            "unit_source_ref_id": None,
                            "as_of": None, # string (e.g., "FY 2023", "Q4 2023")
                            "as_of_source_ref_id": None,
                            "notes": None # Optional string
                        }
                    ],
                    "positioning": None, # string (e.g., "Premium", "Mid-Market")
                    "positioning_source_ref_id": None,
                    "lifecycle_stage": None, # string (e.g., "Growth", "Mature")
                    "lifecycle_stage_source_ref_id": None,
                    "products": [ # List of specific products/services within this category
                        { # Structure for ONE product/service
                            "name": None, # string (e.g., "Enterprise Compute Engine")
                            "name_source_ref_id": None,
                            "description": None, # string
                            "description_source_ref_id": None,
                            "value_proposition": None, # string
                            "value_proposition_source_ref_id": None,
                            "competitive_advantage": None, # string
                            "competitive_advantage_source_ref_id": None,
                            "metrics": [ # List of performance metrics for this product
                                { # Structure for ONE metric (same as category metrics)
                                     "name": None, "name_source_ref_id": None,
                                     "value": None, "value_source_ref_id": None,
                                     "unit": None, "unit_source_ref_id": None,
                                     "as_of": None, "as_of_source_ref_id": None,
                                     "notes": None 
                                }
                            ],
                            "positioning": None, # string
                            "positioning_source_ref_id": None,
                            "lifecycle_stage": None, # string
                            "lifecycle_stage_source_ref_id": None,
                            "launch_date": None, # string (e.g., "2017", "Q3 2020")
                            "launch_date_source_ref_id": None,
                            "notes": None # Optional string
                        }
                    ],
                    "notes": None # Optional string for category-level notes
                }
                # This list can contain zero or more category dictionaries
            ],
            "footnotes": [ # Top-level list for all footnotes in this section
                { # Structure definition for ONE footnote
                    "id": None, # string (e.g., "ref1")
                    "document": None, # string (e.g., "Annual Report 2023")
                    "page": None, # string or number
                    "section": None # string 
                }
            ]
        },
        "template": { # Example data aligned with refined schema
            "product_categories": [
                {
                    "name": "Cloud Infrastructure Services",
                    "name_source_ref_id": "ref1",
                    "description": "Enterprise-grade cloud computing infrastructure and related services.",
                    "description_source_ref_id": "ref1",
                    "value_proposition": "Scalable, secure, and cost-effective IT infrastructure without capital expenditure.",
                    "value_proposition_source_ref_id": "ref1",
                    "competitive_advantage": "Industry-leading uptime (stated 99.99%) and integrated security features.",
                    "competitive_advantage_source_ref_id": "ref1",
                    "metrics": [
                        {
                            "name": "Revenue Contribution",
                            "name_source_ref_id": "ref1",
                            "value": 40,
                            "value_source_ref_id": "ref1",
                            "unit": "%",
                            "unit_source_ref_id": "ref1",
                            "as_of": "FY 2023",
                            "as_of_source_ref_id": "ref1",
                            "notes": "Largest contributing category."
                        },
                        {
                            "name": "YoY Growth",
                            "name_source_ref_id": "ref2",
                            "value": 22.5,
                            "value_source_ref_id": "ref2",
                            "unit": "%",
                            "unit_source_ref_id": "ref2",
                            "as_of": "FY 2023",
                            "as_of_source_ref_id": "ref2",
                            "notes": None
                        },
                        {
                            "name": "Market Share",
                            "name_source_ref_id": "ref3",
                            "value": 18,
                            "value_source_ref_id": "ref3",
                            "unit": "%",
                            "unit_source_ref_id": "ref3",
                            "as_of": "Q4 2023",
                            "as_of_source_ref_id": "ref3",
                            "notes": "Based on external market report."
                        }
                    ],
                    "positioning": "Premium",
                    "positioning_source_ref_id": "ref1",
                    "lifecycle_stage": "Growth",
                    "lifecycle_stage_source_ref_id": "ref2",
                    "products": [
                        {
                            "name": "Enterprise Compute Engine",
                            "name_source_ref_id": "ref4",
                            "description": "Virtual machines for large-scale enterprise applications.",
                            "description_source_ref_id": "ref4",
                            "value_proposition": "High-performance computing with automatic scaling and redundancy.",
                            "value_proposition_source_ref_id": "ref4",
                            "competitive_advantage": "Claims 30% better price-performance ratio than leading competitors.",
                            "competitive_advantage_source_ref_id": "ref4",
                            "metrics": [
                                {
                                    "name": "Revenue Contribution (Category)",
                                    "name_source_ref_id": "ref1",
                                    "value": 15, # Example: 15% of category revenue, not total company
                                    "value_source_ref_id": "ref1",
                                    "unit": "%",
                                    "unit_source_ref_id": "ref1",
                                    "as_of": "FY 2023",
                                    "as_of_source_ref_id": "ref1",
                                    "notes": "Assumed as % of category based on context."
                                }
                            ],
                            "positioning": "Premium",
                            "positioning_source_ref_id": "ref4",
                            "lifecycle_stage": "Mature",
                            "lifecycle_stage_source_ref_id": "ref4",
                            "launch_date": "2017",
                            "launch_date_source_ref_id": "ref4",
                            "notes": None
                        }
                    ],
                    "notes": "Strategic focus area for growth."
                }
            ],
            "footnotes": [
                {
                    "id": "ref1",
                    "document": "Annual Report 2023",
                    "page": "15",
                    "section": "Business Segments"
                },
                {
                    "id": "ref2",
                    "document": "Q4 2023 Earnings Call Transcript",
                    "page": "3",
                    "section": "CEO Opening Remarks"
                },
                {
                    "id": "ref3",
                    "document": "Market Analysis Slide Deck",
                    "page": "8",
                    "section": "Competitive Landscape"
                },
                {
                    "id": "ref4",
                    "document": "Product Catalog 2023",
                    "page": "22",
                    "section": "Cloud Solutions"
                }
            ]
        }
    },
# --- END: Section 2 Definition ---

# --- START: Section 3 Definition ---
    {
        "number": 3,
        "title": "Key Customers",
        "specs": "Extract data on customer concentration, including percentages of revenue from the top customer, top 5, and top 10 customers, specifying the 'as of' date or period.\n"
                 "Extract the Company's stated position in the value chain (e.g., OEM, Tier 1, Tier 2 supplier) and any description provided.\n"
                 "Extract a list of the largest customers identified by name.\n"
                 "For each key customer, extract:\n"
                 "  - Relationship details (e.g., duration, start year).\n"
                 "  - Contribution to overall revenue (percentage and/or absolute value), specifying the 'as of' date.\n"
                 "  - Contribution to profit, if available.\n"
                 "  - Customer segmentation details (e.g., industry, geography) if provided.\n"
                 "  - Specific products/services purchased by that customer.\n"
                 "  - Available metrics associated with those products/services for that customer (e.g., revenue, growth, satisfaction scores), including 'as of' dates/periods.\n"
                 "All extracted data points requiring citation must have a corresponding source reference ID linking to a footnote.\n"
                 "Ensure all footnotes provide precise source details: document name, page number, and specific section/table.",
        "schema": {
            "customer_concentration": {
                "top_customer_percentage": {
                    "value": None, # number (%)
                    "value_source_ref_id": None,
                    "as_of": None, # string (e.g., "FY 2023")
                    "as_of_source_ref_id": None
                },
                "top_5_percentage": {
                    "value": None, # number (%)
                    "value_source_ref_id": None,
                    "as_of": None, # string
                    "as_of_source_ref_id": None
                },
                "top_10_percentage": {
                    "value": None, # number (%)
                    "value_source_ref_id": None,
                    "as_of": None, # string
                    "as_of_source_ref_id": None
                },
                "notes": None # Optional string for context on concentration
            },
            "value_chain_position": {
                "position": None, # string (e.g., "Tier 1 Supplier")
                "position_source_ref_id": None,
                "description": None, # string
                "description_source_ref_id": None,
                "notes": None # Optional string
            },
            "customers": [ # List of key customer objects
                { # Structure for ONE key customer
                    "name": None, # string (e.g., "Volkswagen Group")
                    "name_source_ref_id": None,
                    "relationship": {
                        "duration": None, # string (e.g., "15+ years")
                        "duration_source_ref_id": None,
                        "since_year": None, # number or string (e.g., 2008, "approx. 2010")
                        "since_year_source_ref_id": None,
                        "notes": None # Optional string
                    },
                    "revenue_contribution": {
                        "percentage": None, # number (%)
                        "percentage_source_ref_id": None,
                        "value": None, # Optional number (e.g., 250.5)
                        "value_source_ref_id": None,
                        "unit": None, # Optional string (e.g., "million USD")
                        "unit_source_ref_id": None,
                        "as_of": None, # string (e.g., "FY 2023")
                        "as_of_source_ref_id": None
                    },
                    "profit_contribution": { # Optional section if data is available
                        "percentage": None, # number (%)
                        "percentage_source_ref_id": None,
                        "as_of": None, # string
                        "as_of_source_ref_id": None,
                        "notes": None # Optional string
                    },
                    "segmentation": { # Optional section
                        "industry": None, # string (e.g., "Automotive")
                        "industry_source_ref_id": None,
                        "geography": None, # string (e.g., "Europe")
                        "geography_source_ref_id": None
                    },
                    "products_purchased": [ # List of products purchased by this customer
                        { # Structure for ONE product/service
                            "name": None, # string (e.g., "Electronic Control Units")
                            "name_source_ref_id": None,
                            "revenue": { # Optional revenue specific to this product for this customer
                                "value": None, # number
                                "value_source_ref_id": None,
                                "unit": None, # string (e.g., "million USD")
                                "unit_source_ref_id": None,
                                "as_of": None, # string
                                "as_of_source_ref_id": None
                            },
                            "metrics": [ # List of other metrics for this product/customer combo
                                { # Structure for ONE metric
                                    "name": None, # string (e.g., "Year-over-Year Growth")
                                    "name_source_ref_id": None,
                                    "value": None, # number or string
                                    "value_source_ref_id": None,
                                    "unit": None, # string (e.g., "%", "out of 5")
                                    "unit_source_ref_id": None,
                                    "as_of": None, # string
                                    "as_of_source_ref_id": None,
                                    "notes": None
                                }
                            ],
                           "notes": None # Optional string for product-specific notes
                        }
                    ],
                    "notes": None # Optional string for overall customer notes
                }
            ],
            "footnotes": [ # Top-level list for all footnotes in this section
                { # Structure definition for ONE footnote
                    "id": None, # string (e.g., "ref1")
                    "document": None, # string
                    "page": None, # string or number
                    "section": None # string 
                }
            ]
        },
        "template": { # Example data aligned with refined schema
            "customer_concentration": {
                "top_customer_percentage": {
                    "value": 15.3,
                    "value_source_ref_id": "ref1",
                    "as_of": "FY 2023",
                    "as_of_source_ref_id": "ref1"
                },
                "top_5_percentage": {
                    "value": 42.7,
                    "value_source_ref_id": "ref1",
                    "as_of": "FY 2023",
                    "as_of_source_ref_id": "ref1"
                },
                "top_10_percentage": {
                    "value": 68.2,
                    "value_source_ref_id": "ref1",
                    "as_of": "FY 2023",
                    "as_of_source_ref_id": "ref1"
                },
                "notes": "Concentration risk noted in Risk Factors section."
            },
            "value_chain_position": {
                "position": "Tier 1 Supplier",
                "position_source_ref_id": "ref2",
                "description": "Direct supplier to major automotive OEMs, providing integrated systems and modules.",
                "description_source_ref_id": "ref2",
                "notes": None
            },
            "customers": [
                {
                    "name": "Volkswagen Group",
                    "name_source_ref_id": "ref1",
                    "relationship": {
                        "duration": "15+ years",
                        "duration_source_ref_id": "ref3",
                        "since_year": 2008,
                        "since_year_source_ref_id": "ref3",
                        "notes": "Long-standing strategic partner."
                    },
                    "revenue_contribution": {
                        "percentage": 15.3,
                        "percentage_source_ref_id": "ref1",
                        "value": None, # Example: Absolute value not provided in source
                        "value_source_ref_id": None,
                        "unit": None,
                        "unit_source_ref_id": None,
                        "as_of": "FY 2023",
                        "as_of_source_ref_id": "ref1"
                    },
                    "profit_contribution": {
                        "percentage": 18.7, # Example: Profit contribution % might be available
                        "percentage_source_ref_id": "ref1",
                        "as_of": "FY 2023",
                        "as_of_source_ref_id": "ref1",
                        "notes": "Higher than revenue contribution, indicating favorable product mix."
                    },
                    "segmentation": {
                        "industry": "Automotive",
                        "industry_source_ref_id": "ref1",
                        "geography": "Europe",
                        "geography_source_ref_id": "ref1"
                    },
                    "products_purchased": [
                        {
                            "name": "Electronic Control Units",
                            "name_source_ref_id": "ref1",
                            "revenue": {
                                "value": 120.5,
                                "value_source_ref_id": "ref1",
                                "unit": "million USD",
                                "unit_source_ref_id": "ref1",
                                "as_of": "FY 2023",
                                "as_of_source_ref_id": "ref1"
                            },
                            "metrics": [
                                {
                                    "name": "Year-over-Year Growth",
                                    "name_source_ref_id": "ref1",
                                    "value": 5.3,
                                    "value_source_ref_id": "ref1",
                                    "unit": "%",
                                    "unit_source_ref_id": "ref1",
                                    "as_of": "FY 2023",
                                    "as_of_source_ref_id": "ref1",
                                    "notes": None
                                },
                                {
                                    "name": "Customer Satisfaction Score",
                                    "name_source_ref_id": "ref4",
                                    "value": 4.2,
                                    "value_source_ref_id": "ref4",
                                    "unit": "out of 5",
                                    "unit_source_ref_id": "ref4",
                                    "as_of": "FY 2023",
                                    "as_of_source_ref_id": "ref4",
                                    "notes": None
                                }
                            ],
                           "notes": "Core product for this customer."
                        },
                        {
                            "name": "Infotainment Systems", # Another example product
                            "name_source_ref_id": "ref1",
                            "revenue": None, # Assume revenue breakdown not available
                            "metrics": [],
                           "notes": "Newer product line adopted in 2022."
                        }
                    ],
                    "notes": "Largest customer by revenue."
                },
                {
                    "name": "Toyota Motor Corporation",
                    "name_source_ref_id": "ref1",
                    "relationship": {
                        "duration": "10 years",
                        "duration_source_ref_id": "ref3",
                        "since_year": "approx. 2013",
                        "since_year_source_ref_id": "ref3",
                        "notes": None
                    },
                    "revenue_contribution": {
                        "percentage": 12.8,
                        "percentage_source_ref_id": "ref1",
                        "value": None, "value_source_ref_id": None,
                        "unit": None, "unit_source_ref_id": None,
                        "as_of": "FY 2023",
                        "as_of_source_ref_id": "ref1"
                    },
                    "profit_contribution": None, # Example where profit contribution is missing
                    "segmentation": {
                        "industry": "Automotive",
                        "industry_source_ref_id": "ref1",
                        "geography": "Asia-Pacific",
                        "geography_source_ref_id": "ref1"
                    },
                    "products_purchased": [
                        {
                            "name": "Powertrain Components",
                            "name_source_ref_id": "ref1",
                            "revenue": {
                                "value": 95.2,
                                "value_source_ref_id": "ref1",
                                "unit": "million USD",
                                "unit_source_ref_id": "ref1",
                                "as_of": "FY 2023",
                                "as_of_source_ref_id": "ref1"
                            },
                            "metrics": [],
                           "notes": None
                        }
                    ],
                    "notes": "Second largest customer."
                }
            ],
            "footnotes": [
                {
                    "id": "ref1",
                    "document": "Annual Report 2023",
                    "page": "37",
                    "section": "Customer Relationships"
                },
                {
                    "id": "ref2",
                    "document": "Investor Presentation Q4 2023",
                    "page": "15",
                    "section": "Value Chain Position"
                },
                {
                    "id": "ref3",
                    "document": "Annual Report 2023",
                    "page": "38",
                    "section": "Key Account Management"
                },
                {
                    "id": "ref4",
                    "document": "Customer Satisfaction Survey 2023",
                    "page": "5",
                    "section": "OEM Responses"
                }
            ]
        }
    },
# --- END: Section 3 Definition ---

# --- START: Section 4 Definition ---
    {
        "number": 4,
        "title": "Key Suppliers",
        "specs": "Extract data on supplier concentration, including the percentage of total Cost of Goods Sold (COGS) attributed to the largest supplier, top 5, and top 10 suppliers, specifying the 'as of' date or period.\n"
                 "Identify any specific supplier concentration risks mentioned (e.g., single-source dependency, geographic concentration) and any described mitigation efforts.\n"
                 "Extract the Company's stated business model (e.g., B2B, B2C, B2B2C) and any description of its position or margin capture within its value chain, including 'as of' date if applicable.\n"
                 "Extract a list of the largest suppliers identified by name.\n"
                 "For each key supplier, extract:\n"
                 "  - Relationship details (e.g., duration, start year).\n"
                 "  - Contribution to total COGS (percentage and/or absolute value), specifying the 'as of' date.\n"
                 "  - Supplier segmentation details (e.g., industry, geography) if provided.\n"
                 "  - Specific materials or components provided by that supplier.\n"
                 "  - Available cost data or performance metrics associated with those materials/components from that supplier (e.g., defect rate, on-time delivery), including 'as of' dates/periods.\n"
                 "All extracted data points requiring citation must have a corresponding source reference ID linking to a footnote.\n"
                 "Ensure all footnotes provide precise source details: document name, page number, and specific section/table.",
        "schema": {
            "supplier_concentration": {
                "top_supplier_cogs_percentage": { # Renamed for clarity
                    "value": None, # number (%)
                    "value_source_ref_id": None,
                    "as_of": None, # string (e.g., "FY 2023")
                    "as_of_source_ref_id": None
                },
                "top_5_cogs_percentage": { # Renamed for clarity
                    "value": None, # number (%)
                    "value_source_ref_id": None,
                    "as_of": None, # string
                    "as_of_source_ref_id": None
                },
                "top_10_cogs_percentage": { # Renamed for clarity
                    "value": None, # number (%)
                    "value_source_ref_id": None,
                    "as_of": None, # string
                    "as_of_source_ref_id": None
                },
                "concentration_risks": [ # List of identified risks
                    { # Structure for ONE risk
                        "type": None, # string (e.g., "Single-source dependency")
                        "type_source_ref_id": None,
                        "description": None, # string
                        "description_source_ref_id": None,
                        "mitigation_efforts": None, # string
                        "mitigation_efforts_source_ref_id": None,
                        "notes": None # Optional string
                    }
                ],
                "notes": None # Optional string for overall concentration context
            },
            "value_chain_details": { # Renamed for clarity
                "business_model": None, # string (e.g., "B2B", "B2B2C")
                "business_model_source_ref_id": None,
                "position_description": None, # string
                "position_description_source_ref_id": None,
                "margin_capture": { # Optional details on margin capture
                    "description": None, # string (e.g., "Mid-range margin capture")
                    "description_source_ref_id": None,
                    "value": None, # number (e.g., Gross Margin %)
                    "value_source_ref_id": None,
                    "unit": None, # string (e.g., "%")
                    "unit_source_ref_id": None,
                    "as_of": None, # string
                    "as_of_source_ref_id": None
                },
                "notes": None # Optional string
            },
            "suppliers": [ # List of key supplier objects
                { # Structure for ONE key supplier
                    "name": None, # string (e.g., "TSMC")
                    "name_source_ref_id": None,
                    "relationship": { # Optional
                        "duration": None, # string (e.g., "12 years")
                        "duration_source_ref_id": None,
                        "since_year": None, # number or string (e.g., 2011)
                        "since_year_source_ref_id": None,
                        "notes": None # Optional string
                    },
                    "cogs_contribution": {
                        "percentage": None, # number (%)
                        "percentage_source_ref_id": None,
                        "value": None, # Optional number (absolute cost value)
                        "value_source_ref_id": None,
                        "unit": None, # Optional string (e.g., "million USD")
                        "unit_source_ref_id": None,
                        "as_of": None, # string (e.g., "FY 2023")
                        "as_of_source_ref_id": None
                    },
                    "segmentation": { # Optional
                        "industry": None, # string (e.g., "Semiconductor Manufacturing")
                        "industry_source_ref_id": None,
                        "geography": None, # string (e.g., "Taiwan")
                        "geography_source_ref_id": None
                    },
                    "materials_provided": [ # List of materials/components from this supplier
                        { # Structure for ONE material/component
                            "name": None, # string (e.g., "Custom Integrated Circuits")
                            "name_source_ref_id": None,
                            "cost": { # Optional cost specific to this material
                                "value": None, # number
                                "value_source_ref_id": None,
                                "unit": None, # string (e.g., "million USD")
                                "unit_source_ref_id": None,
                                "as_of": None, # string
                                "as_of_source_ref_id": None
                            },
                            "performance_metrics": [ # List of metrics for this material/supplier combo
                                { # Structure for ONE metric
                                    "name": None, # string (e.g., "Defect Rate")
                                    "name_source_ref_id": None,
                                    "value": None, # number or string
                                    "value_source_ref_id": None,
                                    "unit": None, # string (e.g., "%")
                                    "unit_source_ref_id": None,
                                    "as_of": None, # string
                                    "as_of_source_ref_id": None,
                                    "notes": None
                                }
                            ],
                           "notes": None # Optional string for material-specific notes
                        }
                    ],
                    "notes": None # Optional string for overall supplier notes
                }
            ],
            "footnotes": [ # Top-level list for all footnotes in this section
                { # Structure definition for ONE footnote
                    "id": None, # string (e.g., "ref1")
                    "document": None, # string
                    "page": None, # string or number
                    "section": None # string 
                }
            ]
        },
        "template": { # Example data aligned with refined schema
            "supplier_concentration": {
                "top_supplier_cogs_percentage": {
                    "value": 18.2,
                    "value_source_ref_id": "ref1",
                    "as_of": "FY 2023",
                    "as_of_source_ref_id": "ref1"
                },
                "top_5_cogs_percentage": {
                    "value": 45.6,
                    "value_source_ref_id": "ref1",
                    "as_of": "FY 2023",
                    "as_of_source_ref_id": "ref1"
                },
                "top_10_cogs_percentage": {
                    "value": 72.3,
                    "value_source_ref_id": "ref1",
                    "as_of": "FY 2023",
                    "as_of_source_ref_id": "ref1"
                },
                "concentration_risks": [
                    {
                        "type": "Single-source dependency",
                        "type_source_ref_id": "ref2",
                        "description": "Critical semiconductor components sourced exclusively from TSMC.",
                        "description_source_ref_id": "ref2",
                        "mitigation_efforts": "Actively developing secondary supplier relationship with Samsung.",
                        "mitigation_efforts_source_ref_id": "ref2",
                        "notes": "Ongoing qualification process."
                    },
                    {
                        "type": "Geographic concentration",
                        "type_source_ref_id": "ref2",
                        "description": "47% of suppliers located in Asia-Pacific region.",
                        "description_source_ref_id": "ref2",
                        "mitigation_efforts": "Expanding supplier base in Americas and Europe.",
                        "mitigation_efforts_source_ref_id": "ref2",
                        "notes": None
                    }
                ],
                "notes": "Actively monitored by management."
            },
            "value_chain_details": {
                "business_model": "B2B2C",
                "business_model_source_ref_id": "ref3",
                "position_description": "Manufactures components that are integrated into end-user products sold via OEMs.",
                "position_description_source_ref_id": "ref3",
                "margin_capture": {
                    "description": "Mid-range margin capture in the value chain.",
                    "description_source_ref_id": "ref3",
                    "value": 38.5, # Example: Assuming Gross Margin % reflects this
                    "value_source_ref_id": "ref3",
                    "unit": "%",
                    "unit_source_ref_id": "ref3",
                    "as_of": "FY 2023",
                    "as_of_source_ref_id": "ref3"
                },
                "notes": None
            },
            "suppliers": [
                {
                    "name": "TSMC",
                    "name_source_ref_id": "ref1",
                    "relationship": {
                        "duration": "12 years",
                        "duration_source_ref_id": "ref4",
                        "since_year": 2011,
                        "since_year_source_ref_id": "ref4",
                        "notes": "Strategic foundry partner."
                    },
                    "cogs_contribution": {
                        "percentage": 18.2,
                        "percentage_source_ref_id": "ref1",
                        "value": 215.3, # Assume value could be derived or stated elsewhere
                        "value_source_ref_id": "ref1", # Or different ref if calculated
                        "unit": "million USD",
                        "unit_source_ref_id": "ref1",
                        "as_of": "FY 2023",
                        "as_of_source_ref_id": "ref1"
                    },
                    "segmentation": {
                        "industry": "Semiconductor Manufacturing",
                        "industry_source_ref_id": "ref1",
                        "geography": "Taiwan",
                        "geography_source_ref_id": "ref1"
                    },
                    "materials_provided": [
                        {
                            "name": "Custom Integrated Circuits",
                            "name_source_ref_id": "ref1",
                            "cost": None, # COGS contribution at supplier level already captured value
                            "performance_metrics": [
                                {
                                    "name": "Defect Rate",
                                    "name_source_ref_id": "ref5",
                                    "value": 0.05,
                                    "value_source_ref_id": "ref5",
                                    "unit": "%",
                                    "unit_source_ref_id": "ref5",
                                    "as_of": "FY 2023",
                                    "as_of_source_ref_id": "ref5",
                                    "notes": "Exceeds quality targets."
                                },
                                {
                                    "name": "On-Time Delivery",
                                    "name_source_ref_id": "ref5",
                                    "value": 98.7,
                                    "value_source_ref_id": "ref5",
                                    "unit": "%",
                                    "unit_source_ref_id": "ref5",
                                    "as_of": "FY 2023",
                                    "as_of_source_ref_id": "ref5",
                                    "notes": None
                                }
                            ],
                           "notes": "Critical component for premium product lines."
                        }
                    ],
                    "notes": "Largest single supplier."
                },
                {
                    "name": "Foxconn",
                    "name_source_ref_id": "ref1",
                    "relationship": {
                        "duration": "8 years",
                        "duration_source_ref_id": "ref4",
                        "since_year": 2015,
                        "since_year_source_ref_id": "ref4",
                        "notes": None
                    },
                    "cogs_contribution": {
                        "percentage": 12.5,
                        "percentage_source_ref_id": "ref1",
                        "value": 148.2,
                        "value_source_ref_id": "ref1",
                        "unit": "million USD",
                        "unit_source_ref_id": "ref1",
                        "as_of": "FY 2023",
                        "as_of_source_ref_id": "ref1"
                    },
                    "segmentation": {
                        "industry": "Electronics Manufacturing Services",
                        "industry_source_ref_id": "ref1",
                        "geography": "China",
                        "geography_source_ref_id": "ref1"
                    },
                    "materials_provided": [
                        {
                            "name": "PCB Assemblies",
                            "name_source_ref_id": "ref1",
                            "cost": None,
                            "performance_metrics": [],
                           "notes": "Used across multiple product lines."
                        }
                    ],
                    "notes": None
                }
            ],
            "footnotes": [
                {
                    "id": "ref1",
                    "document": "Annual Report 2023",
                    "page": "42",
                    "section": "Supply Chain Overview"
                },
                {
                    "id": "ref2",
                    "document": "Risk Management Assessment 2023",
                    "page": "15",
                    "section": "Supply Chain Risks"
                },
                {
                    "id": "ref3",
                    "document": "Investor Presentation Q4 2023",
                    "page": "18",
                    "section": "Value Chain Analysis"
                },
                {
                    "id": "ref4",
                    "document": "Annual Report 2023",
                    "page": "43",
                    "section": "Strategic Supplier Relationships"
                },
                {
                    "id": "ref5",
                    "document": "Supplier Performance Report 2023",
                    "page": "7",
                    "section": "Top Tier Suppliers"
                }
            ]
        }
    },
# --- END: Section 4 Definition ---

# --- START: Section 5 Definition ---
    {
        "number": 5,
        "title": "Key Competitors",
        "specs": "Extract data for a market overview, including total market size, market growth rate, and the Company's overall market share, specifying the 'as of' date/period for each.\n"
                 "Identify key market segments the Company competes in. For each segment, extract its size, growth rate, the Company's market share within that segment, and competitor market shares/trends if available, specifying the 'as of' date/period.\n"
                 "Extract a list of key competitors identified by name.\n"
                 "For each key competitor, extract:\n"
                 "  - Basic overview details (e.g., headquarters location, public/private status, total revenue), specifying 'as of' date/period.\n"
                 "  - Overall market share and recent trend (e.g., Increasing, Stable, Decreasing).\n"
                 "  - Stated market positioning (e.g., Premium, Mid-Market, Value) and description.\n"
                 "  - Key areas of competition (e.g., specific product categories, services).\n"
                 "  - Geographic areas of strength.\n"
                 "  - Key competitive strengths mentioned.\n"
                 "  - Recent strategic moves (e.g., acquisitions, expansions) and their stated impact.\n"
                 "  - Historical market share data points, if available.\n"
                 "All extracted data points requiring citation must have a corresponding source reference ID linking to a footnote.\n"
                 "Ensure all footnotes provide precise source details: document name, page number, and specific section/table.",
        "schema": {
            "market_overview": {
                "total_market_size": {
                    "value": None, # number
                    "value_source_ref_id": None,
                    "unit": None, # string (e.g., "billion USD")
                    "unit_source_ref_id": None,
                    "as_of": None, # string (e.g., "FY 2023")
                    "as_of_source_ref_id": None
                },
                "market_growth_rate": { # Renamed for clarity
                    "value": None, # number (%)
                    "value_source_ref_id": None,
                    "unit": "%", # Assuming percentage
                    "as_of": None, # string (e.g., "FY 2023 forecast", "2022-2023")
                    "as_of_source_ref_id": None
                },
                "company_market_share": {
                    "value": None, # number (%)
                    "value_source_ref_id": None,
                    "unit": "%",
                    "as_of": None, # string
                    "as_of_source_ref_id": None
                },
                "notes": None # Optional string
            },
            "market_segments": [ # List of key market segments
                { # Structure for ONE segment
                    "name": None, # string (e.g., "Premium Industrial Automation")
                    "name_source_ref_id": None,
                    "size": { # Optional
                        "value": None, "value_source_ref_id": None,
                        "unit": None, "unit_source_ref_id": None,
                        "as_of": None, "as_of_source_ref_id": None
                    },
                    "growth_rate": { # Optional
                        "value": None, "value_source_ref_id": None,
                        "unit": "%", "unit_source_ref_id": None,
                        "as_of": None, "as_of_source_ref_id": None
                    },
                    "company_market_share": { # Optional
                        "value": None, "value_source_ref_id": None,
                        "unit": "%", "unit_source_ref_id": None,
                        "as_of": None, "as_of_source_ref_id": None
                    },
                    "competitor_market_shares": [ # Optional list
                        { # Structure for ONE competitor share in this segment
                            "competitor_name": None, # string
                            "competitor_name_source_ref_id": None,
                            "share_value": None, # number (%)
                            "share_value_source_ref_id": None,
                            "unit": "%", "unit_source_ref_id": None,
                            "as_of": None, "as_of_source_ref_id": None,
                            "trend": None, # Optional string (e.g., "Increasing", "Stable")
                            "trend_source_ref_id": None
                        }
                    ],
                    "notes": None # Optional string
                }
            ],
            "competitors": [ # List of key competitor objects
                { # Structure for ONE competitor
                    "name": None, # string (e.g., "Competitor A")
                    "name_source_ref_id": None,
                    "overview": { # Optional
                        "headquarters": None, # string (e.g., "Munich, Germany")
                        "headquarters_source_ref_id": None,
                        "publicly_traded": None, # boolean or string (e.g., True, "Yes", "Private")
                        "publicly_traded_source_ref_id": None,
                        "revenue": { # Optional revenue
                            "value": None, "value_source_ref_id": None,
                            "unit": None, "unit_source_ref_id": None,
                            "as_of": None, "as_of_source_ref_id": None
                        }
                    },
                    "market_share": { # Optional overall market share
                        "value": None, "value_source_ref_id": None,
                        "unit": "%", "unit_source_ref_id": None,
                        "as_of": None, "as_of_source_ref_id": None,
                        "trend": None, # Optional string
                        "trend_source_ref_id": None
                    },
                    "positioning": { # Optional
                        "segment": None, # string (e.g., "Premium")
                        "segment_source_ref_id": None,
                        "description": None, # string
                        "description_source_ref_id": None
                    },
                    "areas_of_competition": [], # List of strings
                    "areas_of_competition_source_ref_id": None, # Source for the list as a whole
                    "geographic_strength": [], # List of strings (e.g., ["Europe", "North America"])
                    "geographic_strength_source_ref_id": None,
                    "competitive_strengths": [ # List of described strengths
                        {
                            "description": None, # string
                            "description_source_ref_id": None
                        }
                    ],
                    "recent_strategic_moves": [ # List of recent moves
                        {
                            "description": None, # string (e.g., "Acquisition of Smart Robotics Inc.")
                            "description_source_ref_id": None,
                            "details": None, # Optional string for value/date (e.g., "$350M in Q3 2023")
                            "details_source_ref_id": None,
                            "stated_impact": None, # string
                            "stated_impact_source_ref_id": None
                        }
                    ],
                    "historical_market_share": [ # Optional list of historical data points
                         {
                            "period": None, # string (e.g., "2021", "FY2022")
                            "period_source_ref_id": None,
                            "value": None, # number (%)
                            "value_source_ref_id": None,
                            "unit": "%", "unit_source_ref_id": None
                         }
                    ],
                    "notes": None # Optional string for overall competitor notes
                }
            ],
            "footnotes": [ # Top-level list for all footnotes in this section
                { # Structure definition for ONE footnote
                    "id": None, # string (e.g., "ref1")
                    "document": None, # string
                    "page": None, # string or number
                    "section": None # string 
                }
            ]
        },
        "template": { # Example data aligned with refined schema
            "market_overview": {
                "total_market_size": {
                    "value": 85.7,
                    "value_source_ref_id": "ref1",
                    "unit": "billion USD",
                    "unit_source_ref_id": "ref1",
                    "as_of": "FY 2023",
                    "as_of_source_ref_id": "ref1"
                },
                "market_growth_rate": {
                    "value": 4.8,
                    "value_source_ref_id": "ref1",
                    "unit": "%",
                    "unit_source_ref_id": "ref1", # Unit is standard %
                    "as_of": "FY 2023",
                    "as_of_source_ref_id": "ref1"
                },
                "company_market_share": {
                    "value": 15.3,
                    "value_source_ref_id": "ref1",
                    "unit": "%",
                    "unit_source_ref_id": "ref1",
                    "as_of": "FY 2023",
                    "as_of_source_ref_id": "ref1"
                },
                "notes": "Market growth driven by digitalization trends."
            },
            "market_segments": [
                {
                    "name": "Premium Industrial Automation",
                    "name_source_ref_id": "ref1",
                    "size": {
                        "value": 32.4, "value_source_ref_id": "ref1",
                        "unit": "billion USD", "unit_source_ref_id": "ref1",
                        "as_of": "FY 2023", "as_of_source_ref_id": "ref1"
                    },
                    "growth_rate": {
                        "value": 5.7, "value_source_ref_id": "ref1",
                        "unit": "%", "unit_source_ref_id": "ref1",
                        "as_of": "FY 2023", "as_of_source_ref_id": "ref1"
                    },
                    "company_market_share": {
                        "value": 18.9, "value_source_ref_id": "ref1",
                        "unit": "%", "unit_source_ref_id": "ref1",
                        "as_of": "FY 2023", "as_of_source_ref_id": "ref1"
                    },
                    "competitor_market_shares": [
                        {
                            "competitor_name": "Competitor A", "competitor_name_source_ref_id": "ref1",
                            "share_value": 22.5, "share_value_source_ref_id": "ref1",
                            "unit": "%", "unit_source_ref_id": "ref1",
                            "as_of": "FY 2023", "as_of_source_ref_id": "ref1",
                            "trend": "Increasing", "trend_source_ref_id": "ref1"
                        },
                        {
                            "competitor_name": "Competitor B", "competitor_name_source_ref_id": "ref1",
                            "share_value": 14.8, "share_value_source_ref_id": "ref1",
                            "unit": "%", "unit_source_ref_id": "ref1",
                            "as_of": "FY 2023", "as_of_source_ref_id": "ref1",
                            "trend": "Stable", "trend_source_ref_id": "ref1"
                        }
                    ],
                    "notes": "Company's strongest segment."
                },
                {
                    "name": "Mid-Market Process Control",
                    "name_source_ref_id": "ref1",
                    "size": {
                        "value": 28.6, "value_source_ref_id": "ref1",
                        "unit": "billion USD", "unit_source_ref_id": "ref1",
                        "as_of": "FY 2023", "as_of_source_ref_id": "ref1"
                    },
                    "growth_rate": None, # Example: Growth rate not specified for this segment
                    "company_market_share": {
                        "value": 12.7, "value_source_ref_id": "ref1",
                        "unit": "%", "unit_source_ref_id": "ref1",
                        "as_of": "FY 2023", "as_of_source_ref_id": "ref1"
                    },
                    "competitor_market_shares": [], # Example: No competitor data for this segment
                    "notes": "Area targeted for growth."
                }
            ],
            "competitors": [
                {
                    "name": "Competitor A",
                    "name_source_ref_id": "ref2",
                    "overview": {
                        "headquarters": "Munich, Germany", "headquarters_source_ref_id": "ref2",
                        "publicly_traded": True, "publicly_traded_source_ref_id": "ref2",
                        "revenue": {
                            "value": 18.7, "value_source_ref_id": "ref2",
                            "unit": "billion USD", "unit_source_ref_id": "ref2",
                            "as_of": "FY 2023", "as_of_source_ref_id": "ref2"
                        }
                    },
                    "market_share": {
                        "value": 22.5, "value_source_ref_id": "ref2",
                        "unit": "%", "unit_source_ref_id": "ref2",
                        "as_of": "FY 2023", "as_of_source_ref_id": "ref2",
                        "trend": "Increasing", "trend_source_ref_id": "ref2"
                    },
                    "positioning": {
                        "segment": "Premium", "segment_source_ref_id": "ref2",
                        "description": "Focuses on high-end, integrated solutions with premium pricing.", "description_source_ref_id": "ref2"
                    },
                    "areas_of_competition": [
                        "Industrial Automation", "Process Control Systems", "Robotics Integration"
                    ],
                    "areas_of_competition_source_ref_id": "ref2",
                    "geographic_strength": ["Europe", "North America"],
                    "geographic_strength_source_ref_id": "ref2",
                    "competitive_strengths": [
                        { "description": "Market-leading R&D investment (8.7% of revenue).", "description_source_ref_id": "ref2"},
                        { "description": "Strong brand recognition and established service network.", "description_source_ref_id": "ref2"}
                    ],
                    "recent_strategic_moves": [
                        {
                            "description": "Acquisition of Smart Robotics Inc.", "description_source_ref_id": "ref3",
                            "details": "$350M in Q3 2023", "details_source_ref_id": "ref3",
                            "stated_impact": "Strengthened position in robotics integration segment.", "stated_impact_source_ref_id": "ref3"
                        },
                        {
                            "description": "Expansion into Southeast Asian markets.", "description_source_ref_id": "ref3",
                            "details": "New Singapore hub opened Q1 2024", "details_source_ref_id": "ref3",
                            "stated_impact": "Targeting 15% APAC revenue growth by 2025.", "stated_impact_source_ref_id": "ref3"
                        }
                    ],
                    "historical_market_share": [
                         {"period": "2021", "period_source_ref_id": "ref2", "value": 21.2, "value_source_ref_id": "ref2", "unit": "%", "unit_source_ref_id": "ref2"},
                         {"period": "2022", "period_source_ref_id": "ref2", "value": 21.8, "value_source_ref_id": "ref2", "unit": "%", "unit_source_ref_id": "ref2"},
                         {"period": "2023", "period_source_ref_id": "ref2", "value": 22.5, "value_source_ref_id": "ref2", "unit": "%", "unit_source_ref_id": "ref2"}
                    ],
                    "notes": "Primary global competitor."
                },
                { # Example for a competitor with less detail available
                    "name": "Competitor B",
                    "name_source_ref_id": "ref2",
                    "overview": {
                        "headquarters": "Osaka, Japan", "headquarters_source_ref_id": "ref2",
                        "publicly_traded": True, "publicly_traded_source_ref_id": "ref2",
                        "revenue": {
                            "value": 12.3, "value_source_ref_id": "ref2",
                            "unit": "billion USD", "unit_source_ref_id": "ref2",
                            "as_of": "FY 2023", "as_of_source_ref_id": "ref2"
                        }
                    },
                    "market_share": {
                        "value": 14.8, "value_source_ref_id": "ref2",
                        "unit": "%", "unit_source_ref_id": "ref2",
                        "as_of": "FY 2023", "as_of_source_ref_id": "ref2",
                        "trend": "Stable", "trend_source_ref_id": "ref2"
                    },
                    "positioning": {
                        "segment": "Mid-Market", "segment_source_ref_id": "ref2",
                        "description": "Value-oriented solutions with competitive pricing.", "description_source_ref_id": "ref2"
                    },
                    "areas_of_competition": ["Process Control Systems"],
                    "areas_of_competition_source_ref_id": "ref2",
                    "geographic_strength": ["Asia-Pacific"],
                    "geographic_strength_source_ref_id": "ref2",
                    "competitive_strengths": [], # Example: No specific strengths mentioned
                    "recent_strategic_moves": [], # Example: No recent moves mentioned
                    "historical_market_share": [],
                    "notes": "Strong regional competitor in Asia."
                }
            ],
            "footnotes": [
                 {
                    "id": "ref1",
                    "document": "Industry Market Report 2023",
                    "page": "25",
                    "section": "Competitive Landscape"
                },
                {
                    "id": "ref2",
                    "document": "Annual Report 2023",
                    "page": "48",
                    "section": "Competitive Environment"
                },
                {
                    "id": "ref3",
                    "document": "Quarterly Investor Presentation Q4 2023",
                    "page": "12",
                    "section": "Market Developments"
                }
            ]
        }
    },
# --- END: Section 5 Definition ---

# --- START: Section 6 Definition ---
    {
        "number": 6,
        "title": "Operational KPIs",
        "specs": "Extract operational Key Performance Indicators (KPIs) that materially contribute to cash flow generation (focus on operational metrics, not aggregated financials like EBITDA/Net Income which belong in financial sections).\n"
                 "Prioritize metrics related to market share, volumes (production/sales), selling prices/rates, and customer activity (e.g., revenue per customer, user growth).\n"
                 "Include relevant industry-specific operational metrics if available (e.g., capacity utilization, order backlog, on-time delivery, quality metrics).\n"
                 "Provide data for the last 3 years and the most recent year-to-date (YTD) period, where available.\n"
                 "Include any company-provided forecasts or guidance specifically related to these operational KPIs.\n"
                 "Include benchmarks against competitors for specific KPIs, where available.\n"
                 "Extract Management Discussion and Analysis (MDNA) specifically related to these operational KPIs, covering:\n"
                 "  - Key recent performance trends.\n"
                 "  - 2 key achievements.\n"
                 "  - 2 key challenges.\n"
                 "  - 2 areas of potential disconnect between management statements and actual operational KPI performance.\n"
                 "All extracted data points requiring citation must have a corresponding source reference ID linking to a footnote.\n"
                 "Ensure all footnotes provide precise source details: document name, page number, and specific section/table.",
        "schema": {
            "operational_metrics": [ # List of core operational KPIs
                { # Structure for ONE KPI
                    "name": None, # string (e.g., "Market Share")
                    "name_source_ref_id": None,
                    "category": None, # Optional string (e.g., "Market Position", "Operational", "Pricing", "Customer")
                    "category_source_ref_id": None,
                    "description": None, # string (e.g., "Overall market share in primary industry")
                    "description_source_ref_id": None,
                    "data_points": [ # List of historical data points for this KPI
                        {
                            "period": None, # string (e.g., "FY 2021", "Q1 2024")
                            "period_source_ref_id": None,
                            "value": None, # number or string
                            "value_source_ref_id": None,
                            "unit": None, # string (e.g., "%", "million units", "USD")
                            "unit_source_ref_id": None
                            # Optional: "yoy_change": None # number (%) Could be calculated or extracted
                        }
                    ],
                    "guidance": { # Optional guidance for this KPI
                        "period": None, # string (e.g., "FY 2024")
                        "period_source_ref_id": None,
                        "value_range": None, # string (e.g., "16.0-16.5") or number
                        "value_range_source_ref_id": None,
                        "unit": None, # string (e.g., "%")
                        "unit_source_ref_id": None,
                        "notes": None # Optional string
                    },
                    "notes": None # Optional string for overall KPI notes
                }
            ],
            "industry_specific_metrics": [ # Optional list of industry-specific KPIs (same structure as operational_metrics)
                 { # Structure for ONE KPI (same as above)
                    "name": None, "name_source_ref_id": None,
                    "category": None, "category_source_ref_id": None, # Optional category
                    "description": None, "description_source_ref_id": None,
                    "data_points": [
                        {
                            "period": None, "period_source_ref_id": None,
                            "value": None, "value_source_ref_id": None,
                            "unit": None, "unit_source_ref_id": None
                        }
                    ],
                    "guidance": None, # Optional guidance object (same structure as above)
                    "notes": None 
                }
            ],
            "competitor_benchmarks": [ # Optional list of benchmark comparisons
                { # Structure for ONE benchmark metric
                    "metric_name": None, # string (e.g., "Market Share")
                    "metric_name_source_ref_id": None,
                    "period": None, # string (e.g., "FY 2023")
                    "period_source_ref_id": None,
                    "benchmark_data": [
                         { # Data for one company in the benchmark
                              "company_name": None, # string (e.g., "Subject Company", "Competitor A")
                              "company_name_source_ref_id": None, # Maybe same source as metric data
                              "value": None, # number or string
                              "value_source_ref_id": None,
                              "unit": None, # string
                              "unit_source_ref_id": None
                         }
                    ],
                    "notes": None # Optional string for benchmark context
                }
            ],
            "mdna": { # Management Discussion & Analysis specific to Operational KPIs
                "trend_analysis": None, # string summarizing key trends observed in the KPIs
                "trend_analysis_source_ref_id": None,
                "key_achievements": [ # List of 2 achievements
                    {
                        "description": None, # string
                        "description_source_ref_id": None
                    }
                ],
                "key_challenges": [ # List of 2 challenges
                    {
                        "description": None, # string
                        "description_source_ref_id": None
                    }
                ],
                "management_disconnects": [ # List of 2 disconnects
                    {
                        "management_statement": None, # string (quote or summary of statement)
                        "management_statement_source_ref_id": None,
                        "actual_performance": None, # string describing conflicting KPI data
                        "actual_performance_source_ref_id": None,
                        "notes": None # Optional string explaining the disconnect
                    }
                ],
                 "notes": None # Optional overall MDNA notes
            },
            "footnotes": [ # Top-level list for all footnotes in this section
                { # Structure definition for ONE footnote
                    "id": None, # string (e.g., "ref1")
                    "document": None, # string
                    "page": None, # string or number
                    "section": None # string 
                }
            ]
        },
        "template": { # Example data aligned with refined schema
            "operational_metrics": [
                {
                    "name": "Market Share", "name_source_ref_id": "ref1",
                    "category": "Market Position", "category_source_ref_id": "ref1",
                    "description": "Overall market share in primary industry.", "description_source_ref_id": "ref1",
                    "data_points": [
                        {"period": "FY 2021", "period_source_ref_id": "ref1", "value": 14.2, "value_source_ref_id": "ref1", "unit": "%", "unit_source_ref_id": "ref1"},
                        {"period": "FY 2022", "period_source_ref_id": "ref1", "value": 14.8, "value_source_ref_id": "ref1", "unit": "%", "unit_source_ref_id": "ref1"},
                        {"period": "FY 2023", "period_source_ref_id": "ref1", "value": 15.3, "value_source_ref_id": "ref1", "unit": "%", "unit_source_ref_id": "ref1"},
                        {"period": "Q1 2024", "period_source_ref_id": "ref2", "value": 15.7, "value_source_ref_id": "ref2", "unit": "%", "unit_source_ref_id": "ref2"}
                    ],
                    "guidance": {
                        "period": "FY 2024", "period_source_ref_id": "ref3",
                        "value_range": "16.0-16.5", "value_range_source_ref_id": "ref3",
                        "unit": "%", "unit_source_ref_id": "ref3",
                        "notes": "Based on Q1 earnings call update."
                    },
                    "notes": "Consistent upward trend."
                },
                {
                    "name": "Production Volume", "name_source_ref_id": "ref1",
                    "category": "Operational", "category_source_ref_id": "ref1",
                    "description": "Total units produced annually.", "description_source_ref_id": "ref1",
                    "data_points": [
                         {"period": "FY 2021", "period_source_ref_id": "ref1", "value": 2.85, "value_source_ref_id": "ref1", "unit": "million units", "unit_source_ref_id": "ref1"},
                         {"period": "FY 2022", "period_source_ref_id": "ref1", "value": 3.12, "value_source_ref_id": "ref1", "unit": "million units", "unit_source_ref_id": "ref1"},
                         {"period": "FY 2023", "period_source_ref_id": "ref1", "value": 3.45, "value_source_ref_id": "ref1", "unit": "million units", "unit_source_ref_id": "ref1"},
                         {"period": "Q1 2024", "period_source_ref_id": "ref2", "value": 0.88, "value_source_ref_id": "ref2", "unit": "million units", "unit_source_ref_id": "ref2"}
                    ],
                    "guidance": None,
                    "notes": None
                },
                 { # Add more KPIs as found following the structure
                    "name": "Average Selling Price", "name_source_ref_id": "ref1",
                    "category": "Pricing", "category_source_ref_id": "ref1",
                    "description": "Average revenue per unit sold.", "description_source_ref_id": "ref1",
                    "data_points": [
                         {"period": "FY 2021", "period_source_ref_id": "ref1", "value": 1250, "value_source_ref_id": "ref1", "unit": "USD", "unit_source_ref_id": "ref1"},
                         {"period": "FY 2022", "period_source_ref_id": "ref1", "value": 1285, "value_source_ref_id": "ref1", "unit": "USD", "unit_source_ref_id": "ref1"},
                         {"period": "FY 2023", "period_source_ref_id": "ref1", "value": 1325, "value_source_ref_id": "ref1", "unit": "USD", "unit_source_ref_id": "ref1"},
                         {"period": "Q1 2024", "period_source_ref_id": "ref2", "value": 1340, "value_source_ref_id": "ref2", "unit": "USD", "unit_source_ref_id": "ref2"}
                    ],
                    "guidance": None,
                    "notes": "ASP increases lag input cost inflation slightly."
                }
                 # ... potentially more operational_metrics
            ],
            "industry_specific_metrics": [
                {
                    "name": "Manufacturing Capacity Utilization", "name_source_ref_id": "ref1",
                    "category": None, "category_source_ref_id": None,
                    "description": "Percentage of total manufacturing capacity being utilized.", "description_source_ref_id": "ref1",
                    "data_points": [
                         {"period": "FY 2021", "period_source_ref_id": "ref1", "value": 78.3, "value_source_ref_id": "ref1", "unit": "%", "unit_source_ref_id": "ref1"},
                         {"period": "FY 2022", "period_source_ref_id": "ref1", "value": 82.1, "value_source_ref_id": "ref1", "unit": "%", "unit_source_ref_id": "ref1"},
                         {"period": "FY 2023", "period_source_ref_id": "ref1", "value": 85.4, "value_source_ref_id": "ref1", "unit": "%", "unit_source_ref_id": "ref1"},
                         {"period": "Q1 2024", "period_source_ref_id": "ref2", "value": 87.2, "value_source_ref_id": "ref2", "unit": "%", "unit_source_ref_id": "ref2"}
                    ],
                    "guidance": None,
                    "notes": "Approaching optimal levels, indicates potential need for expansion."
                }
                 # ... potentially more industry_specific_metrics
            ],
            "competitor_benchmarks": [
                 {
                    "metric_name": "Market Share", "metric_name_source_ref_id": "ref4",
                    "period": "FY 2023", "period_source_ref_id": "ref4",
                    "benchmark_data": [
                        {"company_name": "Subject Company", "company_name_source_ref_id": "ref4", "value": 15.3, "value_source_ref_id": "ref4", "unit": "%", "unit_source_ref_id": "ref4"},
                        {"company_name": "Competitor A", "company_name_source_ref_id": "ref4", "value": 22.5, "value_source_ref_id": "ref4", "unit": "%", "unit_source_ref_id": "ref4"},
                        {"company_name": "Competitor B", "company_name_source_ref_id": "ref4", "value": 14.8, "value_source_ref_id": "ref4", "unit": "%", "unit_source_ref_id": "ref4"}
                    ],
                    "notes": "Source: Third-party market report."
                }
                # ... potentially more competitor_benchmarks
            ],
            "mdna": {
                "trend_analysis": "Operational performance shows consistent improvement across key metrics during FY2021-FY2023, with continued momentum in Q1 2024. Market share has grown steadily alongside increases in production volume and average selling prices.",
                "trend_analysis_source_ref_id": "ref1", # Assume based on analysis of AR data
                "key_achievements": [
                    {"description": "Achieved 95.8% on-time delivery rate in FY 2023 despite global supply chain disruptions.", "description_source_ref_id": "ref1"},
                    {"description": "Increased average revenue per user by 13% from FY 2021 to FY 2023 through cross-selling.", "description_source_ref_id": "ref1"}
                ],
                "key_challenges": [
                    {"description": "Growing order backlog (+16.8% since FY 2021) indicates potential production capacity constraints.", "description_source_ref_id": "ref2"},
                    {"description": "Average selling price increases lag industry inflation rate (6.0% vs 8.5% over 3 yrs).", "description_source_ref_id": "ref3"} # Example source
                ],
                "management_disconnects": [
                    {
                        "management_statement": "CEO stated in Q4 2023 earnings call: 'Capacity constraints are no longer an issue'.",
                        "management_statement_source_ref_id": "ref5",
                        "actual_performance": "Backlog grew 3.7% in Q1 2024, capacity utilization reached 87.2%.",
                        "actual_performance_source_ref_id": "ref2",
                        "notes": "Data suggests capacity might still be a constraint."
                    },
                     {
                        "management_statement": "Annual report goal: 'maintain pricing parity with Competitor A'.",
                        "management_statement_source_ref_id": "ref1",
                        "actual_performance": "Benchmarking shows ASP 12.8% lower than Competitor A in FY 2023.",
                        "actual_performance_source_ref_id": "ref4",
                        "notes": "Gap widened from 10.5% in FY 2022."
                    }
                ],
                 "notes": None
            },
            "footnotes": [
                {"id": "ref1", "document": "Annual Report 2023", "page": "32", "section": "Operational Performance"},
                {"id": "ref2", "document": "Q1 2024 Quarterly Report", "page": "8", "section": "Key Performance Indicators"},
                {"id": "ref3", "document": "FY 2024 Guidance", "page": "4", "section": "Management Outlook"},
                {"id": "ref4", "document": "Industry Benchmarking Report 2023", "page": "15", "section": "Competitive Metrics"},
                {"id": "ref5", "document": "Q4 2023 Earnings Call Transcript", "page": "7", "section": "CEO Remarks"}
            ]
        }
    },
# --- END: Section 6 Definition ---

# --- START: Section 7 Definition ---
    {
        "number": 7,
        "title": "Summary Financials (Consolidated)",
        "specs": "Extract key consolidated financial metrics: Revenue, EBITDA, EBITDA Margin, Operating Income, Operating Margin, Net Income, Net Margin, Capital Expenditure (Capex), Capex as % of Revenue, and Cash Conversion (e.g., OCF/EBITDA).\n"
                 "Provide data for the last 3 financial years and the 5 most recent quarters, where available.\n"
                 "Include both GAAP and adjusted/non-GAAP measures if provided by the Company, clearly labeling adjusted values and detailing adjustments.\n"
                 "Extract any company-provided financial forecasts or guidance related to these metrics.\n"
                 "Identify and list any material one-time or non-recurring items impacting the reported periods.\n"
                 "Include analysis or commentary on financial performance relative to the industry, if available.\n"
                 "Extract Management Discussion and Analysis (MDNA) specifically related to consolidated financial performance, covering:\n"
                 "  - Key recent financial trends.\n"
                 "  - 2 key financial achievements.\n"
                 "  - 2 key financial challenges.\n"
                 "  - 2 areas of potential disconnect between management statements and actual financial performance.\n"
                 "All extracted data points requiring citation must have a corresponding source reference ID linking to a footnote.\n"
                 "Ensure all footnotes provide precise source details: document name, page number, and specific section/table.",
        "schema": {
            "annual_financials": { # Structure for annual data table
                "columns": [ # Defines the periods/columns
                    {
                        "period": None, # string (e.g., "FY 2021")
                        "period_source_ref_id": None,
                        "end_date": None, # Optional string (e.g., "December 31, 2021")
                        "end_date_source_ref_id": None
                    }
                    # List can contain multiple period dictionaries
                ],
                "metrics": [ # Defines the rows/metrics
                    { # Structure for ONE metric row
                        "name": None, # string (e.g., "Revenue")
                        "name_source_ref_id": None,
                        "description": None, # Optional string
                        "description_source_ref_id": None,
                        "values": [ # List matching the order of columns
                            {
                                "period": None, # string (matching column period)
                                "value": None, # number or string
                                "value_source_ref_id": None,
                                "unit": None, # string (e.g., "million USD")
                                "unit_source_ref_id": None,
                                "yoy_change": None, # Optional number (%)
                                "yoy_change_source_ref_id": None
                            }
                            # List length should match length of 'columns' list
                        ],
                        "adjusted_values": [ # Optional list for adjusted figures
                            {
                                "period": None, # string (matching column period)
                                "value": None, # number or string
                                "value_source_ref_id": None,
                                "unit": None, # string
                                "unit_source_ref_id": None,
                                "adjustment_description": None, # string explaining adjustment
                                "adjustment_description_source_ref_id": None
                            }
                             # List length should match length of 'columns' list where applicable
                        ],
                        "notes": None # Optional string for metric-specific notes
                    }
                    # List can contain multiple metric dictionaries
                ]
            },
            "quarterly_financials": { # Optional structure for quarterly data table (mirrors annual)
                "columns": [ 
                    {
                        "period": None, # string (e.g., "Q1 2023")
                        "period_source_ref_id": None,
                        "end_date": None, # Optional string (e.g., "March 31, 2023")
                        "end_date_source_ref_id": None
                    }
                ],
                "metrics": [ 
                    { # Structure for ONE metric row (same as annual)
                        "name": None, "name_source_ref_id": None,
                        "description": None, "description_source_ref_id": None,
                        "values": [
                            {
                                "period": None, "value": None, "value_source_ref_id": None,
                                "unit": None, "unit_source_ref_id": None,
                                "yoy_change": None, "yoy_change_source_ref_id": None 
                            }
                        ],
                        "adjusted_values": [ # Optional
                             {
                                "period": None, "value": None, "value_source_ref_id": None,
                                "unit": None, "unit_source_ref_id": None,
                                "adjustment_description": None, "adjustment_description_source_ref_id": None
                            }
                        ],
                        "notes": None 
                    }
                ]
            },
            "one_time_items": [ # List of material one-time items
                 { # Structure for ONE item
                     "period": None, # string (e.g., "FY 2021", "Q1 2024")
                     "period_source_ref_id": None,
                     "description": None, # string
                     "description_source_ref_id": None,
                     "impact": { # Optional impact details
                          "value": None, # number (positive or negative)
                          "value_source_ref_id": None,
                          "unit": None, # string (e.g., "million USD")
                          "unit_source_ref_id": None,
                          "affected_metric": None, # string (e.g., "EBITDA", "Net Income")
                          "affected_metric_source_ref_id": None
                     },
                     "notes": None
                 }
            ],
            "guidance_and_forecasts": [ # List of guidance items
                { # Structure for ONE guidance item
                    "metric_name": None, # string (e.g., "Revenue")
                    "metric_name_source_ref_id": None,
                    "period": None, # string (e.g., "FY 2024")
                    "period_source_ref_id": None,
                    "type": None, # string (e.g., "Company Guidance", "Analyst Consensus")
                    "type_source_ref_id": None,
                    "value": { # Could be single value or range
                         "low": None, # Optional number
                         "low_source_ref_id": None,
                         "high": None, # Optional number
                         "high_source_ref_id": None,
                         "point_value": None, # Optional number (if not a range)
                         "point_value_source_ref_id": None,
                         "unit": None, # string (e.g., "million USD", "%")
                         "unit_source_ref_id": None,
                         "yoy_change": { # Optional YoY change implied by guidance
                              "low": None, "low_source_ref_id": None,
                              "high": None, "high_source_ref_id": None,
                              "point_value": None, "point_value_source_ref_id": None,
                              "unit": "%", "unit_source_ref_id": None
                         }
                    },
                    "date_provided": None, # Optional string (e.g., "February 15, 2024")
                    "date_provided_source_ref_id": None,
                    "notes": None
                }
            ],
            "industry_comparison_notes": None, # Optional string for commentary on performance vs industry
            "industry_comparison_notes_source_ref_id": None,
            "mdna": { # MDNA specific to consolidated financials
                "trend_analysis": None, # string
                "trend_analysis_source_ref_id": None,
                "key_achievements": [ # List of 2 achievements
                    { "description": None, "description_source_ref_id": None }
                ],
                "key_challenges": [ # List of 2 challenges
                    { "description": None, "description_source_ref_id": None }
                ],
                "management_disconnects": [ # List of 2 disconnects
                    {
                        "management_statement": None, "management_statement_source_ref_id": None,
                        "actual_performance": None, "actual_performance_source_ref_id": None,
                        "notes": None 
                    }
                ],
                 "notes": None 
            },
            "footnotes": [ # Top-level list for all footnotes in this section
                { # Structure definition for ONE footnote
                    "id": None, "document": None, "page": None, "section": None 
                }
            ]
        },
        "template": { # Example data aligned with refined schema
            "annual_financials": {
                "columns": [
                    {"period": "FY 2021", "period_source_ref_id": "ref1", "end_date": "December 31, 2021", "end_date_source_ref_id": "ref1"},
                    {"period": "FY 2022", "period_source_ref_id": "ref1", "end_date": "December 31, 2022", "end_date_source_ref_id": "ref1"},
                    {"period": "FY 2023", "period_source_ref_id": "ref1", "end_date": "December 31, 2023", "end_date_source_ref_id": "ref1"}
                ],
                "metrics": [
                    { # Revenue Example
                        "name": "Revenue", "name_source_ref_id": "ref1",
                        "description": "Total consolidated revenue", "description_source_ref_id": "ref1",
                        "values": [
                            {"period": "FY 2021", "value": 3562.5, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "yoy_change": None, "yoy_change_source_ref_id": None},
                            {"period": "FY 2022", "value": 4008.7, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "yoy_change": 12.5, "yoy_change_source_ref_id": "ref1"},
                            {"period": "FY 2023", "value": 4572.3, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "yoy_change": 14.1, "yoy_change_source_ref_id": "ref1"}
                        ],
                        "adjusted_values": [], # Example where no adjusted revenue is given
                        "notes": "Growth driven by volume and price increases."
                    },
                    { # EBITDA Example
                        "name": "EBITDA", "name_source_ref_id": "ref1",
                        "description": "Earnings Before Interest, Taxes, Depreciation and Amortization", "description_source_ref_id": "ref1",
                        "values": [
                            {"period": "FY 2021", "value": 748.1, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "yoy_change": None, "yoy_change_source_ref_id": None},
                            {"period": "FY 2022", "value": 865.9, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "yoy_change": 15.7, "yoy_change_source_ref_id": "ref1"},
                            {"period": "FY 2023", "value": 1028.8, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "yoy_change": 18.8, "yoy_change_source_ref_id": "ref1"}
                        ],
                        "adjusted_values": [
                            {"period": "FY 2021", "value": 762.4, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "adjustment_description": "Excludes $14.3M restructuring costs", "adjustment_description_source_ref_id": "ref1"},
                            {"period": "FY 2022", "value": 881.9, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "adjustment_description": "Excludes $16.0M acquisition expenses", "adjustment_description_source_ref_id": "ref1"},
                            {"period": "FY 2023", "value": 1042.5, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "adjustment_description": "Excludes $13.7M legal settlement", "adjustment_description_source_ref_id": "ref1"}
                        ],
                        "notes": None
                    },
                    { # EBITDA Margin Example (Calculated or Stated)
                        "name": "EBITDA Margin", "name_source_ref_id": "ref1", # Source if stated directly
                        "description": "EBITDA as percentage of Revenue", "description_source_ref_id": "ref1",
                        "values": [
                            {"period": "FY 2021", "value": 21.0, "value_source_ref_id": "ref1", "unit": "%", "unit_source_ref_id": "ref1", "yoy_change": None, "yoy_change_source_ref_id": None},
                            {"period": "FY 2022", "value": 21.6, "value_source_ref_id": "ref1", "unit": "%", "unit_source_ref_id": "ref1", "yoy_change": 0.6, "yoy_change_source_ref_id": "ref1"},
                            {"period": "FY 2023", "value": 22.5, "value_source_ref_id": "ref1", "unit": "%", "unit_source_ref_id": "ref1", "yoy_change": 0.9, "yoy_change_source_ref_id": "ref1"}
                        ],
                         "adjusted_values": [], # Could add adjusted margin if relevant
                        "notes": "Margin expansion driven by operating leverage and mix shift."
                    }
                     # ... Add other metrics (OpIncome, NetIncome, Capex, Cash Conversion etc.) following this pattern ...
                ]
            },
            "quarterly_financials": { # Example Quarterly Data
                "columns": [
                    {"period": "Q1 2023", "period_source_ref_id": "ref2", "end_date": "March 31, 2023", "end_date_source_ref_id": "ref2"},
                    {"period": "Q2 2023", "period_source_ref_id": "ref2", "end_date": "June 30, 2023", "end_date_source_ref_id": "ref2"},
                    {"period": "Q3 2023", "period_source_ref_id": "ref2", "end_date": "September 30, 2023", "end_date_source_ref_id": "ref2"},
                    {"period": "Q4 2023", "period_source_ref_id": "ref2", "end_date": "December 31, 2023", "end_date_source_ref_id": "ref2"},
                    {"period": "Q1 2024", "period_source_ref_id": "ref3", "end_date": "March 31, 2024", "end_date_source_ref_id": "ref3"}
                ],
                "metrics": [
                     { # Quarterly Revenue Example
                        "name": "Revenue", "name_source_ref_id": "ref2",
                        "description": "Total consolidated revenue", "description_source_ref_id": "ref2",
                        "values": [
                            {"period": "Q1 2023", "value": 1087.5, "value_source_ref_id": "ref2", "unit": "million USD", "unit_source_ref_id": "ref2", "yoy_change": 13.8, "yoy_change_source_ref_id": "ref2"},
                            {"period": "Q2 2023", "value": 1124.3, "value_source_ref_id": "ref2", "unit": "million USD", "unit_source_ref_id": "ref2", "yoy_change": 14.2, "yoy_change_source_ref_id": "ref2"},
                            {"period": "Q3 2023", "value": 1146.8, "value_source_ref_id": "ref2", "unit": "million USD", "unit_source_ref_id": "ref2", "yoy_change": 14.5, "yoy_change_source_ref_id": "ref2"},
                            {"period": "Q4 2023", "value": 1213.7, "value_source_ref_id": "ref2", "unit": "million USD", "unit_source_ref_id": "ref2", "yoy_change": 13.9, "yoy_change_source_ref_id": "ref2"},
                            {"period": "Q1 2024", "value": 1248.5, "value_source_ref_id": "ref3", "unit": "million USD", "unit_source_ref_id": "ref3", "yoy_change": 14.8, "yoy_change_source_ref_id": "ref3"}
                        ],
                         "adjusted_values": [],
                        "notes": None
                    }
                     # ... Add other quarterly metrics if available ...
                ]
            },
            "one_time_items": [
                {"period": "FY 2021", "period_source_ref_id": "ref1", "description": "Restructuring costs related to European operations consolidation.", "description_source_ref_id": "ref1", "impact": {"value": -14.3, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "affected_metric": "EBITDA", "affected_metric_source_ref_id": "ref1"}, "notes": None},
                {"period": "FY 2023", "period_source_ref_id": "ref1", "description": "Legal settlement with competitor over patent dispute.", "description_source_ref_id": "ref1", "impact": {"value": -13.7, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "affected_metric": "EBITDA", "affected_metric_source_ref_id": "ref1"}, "notes": None}
            ],
            "guidance_and_forecasts": [
                {
                    "metric_name": "Revenue", "metric_name_source_ref_id": "ref4",
                    "period": "FY 2024", "period_source_ref_id": "ref4",
                    "type": "Company Guidance", "type_source_ref_id": "ref4",
                    "value": { 
                         "low": 5050.0, "low_source_ref_id": "ref4", 
                         "high": 5250.0, "high_source_ref_id": "ref4",
                         "point_value": None, "point_value_source_ref_id": None,
                         "unit": "million USD", "unit_source_ref_id": "ref4",
                         "yoy_change": {"low": 10.5, "low_source_ref_id": "ref4", "high": 14.8, "high_source_ref_id": "ref4", "point_value": None, "point_value_source_ref_id": None, "unit": "%", "unit_source_ref_id": "ref4"}
                    },
                    "date_provided": "February 15, 2024", "date_provided_source_ref_id": "ref4",
                    "notes": "Midpoint implies 12.6% YoY growth."
                }
                 # ... Add other guidance items ...
            ],
            "industry_comparison_notes": "Company consistently outperforms industry average revenue growth but lags top peer on EBITDA margin.",
            "industry_comparison_notes_source_ref_id": "ref2", # Example source
            "mdna": {
                "trend_analysis": "Consistent double-digit revenue growth accompanied by steady margin expansion over the past three years, driven by operational leverage and favorable product mix shift.",
                "trend_analysis_source_ref_id": "ref1", # Example: derived from AR MD&A section
                "key_achievements": [
                    {"description": "Achieved record EBITDA of $1,029M in FY 2023, up 18.8% YoY.", "description_source_ref_id": "ref1"},
                    {"description": "Improved cash conversion rate to 87.5% in FY 2023.", "description_source_ref_id": "ref1"}
                ],
                "key_challenges": [
                    {"description": "Slowing Capex growth in FY2023 (+7.9% vs +14.2% prior year) despite strong demand.", "description_source_ref_id": "ref1"},
                    {"description": "Recurring impact of one-time items on reported profitability.", "description_source_ref_id": "ref1"}
                ],
                "management_disconnects": [
                    {
                        "management_statement": "CFO stated goal of '15% revenue growth' for FY2023.", "management_statement_source_ref_id": "ref5",
                        "actual_performance": "Actual FY 2023 revenue growth was 14.1%.", "actual_performance_source_ref_id": "ref1",
                        "notes": "Slight miss versus stated target."
                    },
                    {
                        "management_statement": "Annual report claims 'substantial completion of restructuring initiatives' in FY2023.", "management_statement_source_ref_id": "ref1",
                        "actual_performance": "Q1 2024 report shows $4.2M additional restructuring charges.", "actual_performance_source_ref_id": "ref3",
                        "notes": "Restructuring appears ongoing into FY2024."
                    }
                ],
                 "notes": None
            },
            "footnotes": [
                 {"id": "ref1", "document": "Annual Report 2023", "page": "25-32", "section": "Financial Review"},
                 {"id": "ref2", "document": "FY 2023 Form 10-K", "page": "45-48", "section": "Management's Discussion and Analysis"},
                 {"id": "ref3", "document": "Q1 2024 Quarterly Report", "page": "8-12", "section": "Financial Results"},
                 {"id": "ref4", "document": "FY 2024 Guidance Press Release", "page": "2-3", "section": "Financial Outlook"},
                 {"id": "ref5", "document": "Q3 2023 Earnings Call Transcript", "page": "6", "section": "CFO Remarks"}
            ]
        }
    },
# --- END: Section 7 Definition ---

# --- START: Section 8 Definition ---
    {
        "number": 8,
        "title": "Summary Financials (Segment)",
        "specs": ("Extract a summary of financial performance for each distinct business segment reported by the Company.\n"
                  "Use the Company's exact naming convention for each segment.\n"
                  "For each segment, include all available reported financial metrics (e.g., Revenue, Operating Income, Segment EBITDA, Segment Assets), specifying units.\n"
                  "Provide data for the last 3 financial years and the 5 most recent quarters, where available.\n"
                  "Identify and list separately any material one-time or non-recurring items allocated to specific segments.\n"
                  "Extract Management Discussion and Analysis (MDNA) comments *specifically related to each segment's performance*, covering:\n"
                  "  - Key recent financial trends for the segment.\n"
                  "  - 2 key financial achievements for the segment.\n"
                  "  - 2 key financial challenges for the segment.\n"
                  "  - 2 areas of potential disconnect between management statements and the segment's actual financial performance.\n"
                  "All extracted data points requiring citation must have a corresponding source reference ID linking to a footnote.\n"
                  "Ensure all footnotes provide precise source details: document name, page number, and specific section/table (often found in Segment Information footnote in financials)."),
        "schema": {
            "segments": [ # List of reported segments
                { # Structure for ONE segment
                    "segment_name": None, # string (e.g., "Industrial Automation")
                    "segment_name_source_ref_id": None,
                    "segment_description": None, # Optional string describing the segment's business
                    "segment_description_source_ref_id": None,
                    "annual_financials": { # Structure for annual data (mirrors Section 7 structure)
                        "columns": [ 
                            {
                                "period": None, "period_source_ref_id": None,
                                "end_date": None, "end_date_source_ref_id": None 
                            }
                        ],
                        "metrics": [ 
                            { # Structure for ONE metric row for this segment
                                "name": None, "name_source_ref_id": None, # e.g., "Segment Revenue"
                                "description": None, "description_source_ref_id": None,
                                "values": [ # List matching the order of columns
                                    {
                                        "period": None, "value": None, "value_source_ref_id": None,
                                        "unit": None, "unit_source_ref_id": None,
                                        "yoy_change": None, "yoy_change_source_ref_id": None 
                                    }
                                ],
                                # NOTE: Adjusted values less common at segment level, but could be added if needed
                                "notes": None 
                            }
                            # Include all metrics reported for the segment (Revenue, OpIncome, etc.)
                        ]
                    },
                    "quarterly_financials": { # Optional structure for quarterly data (mirrors annual)
                        "columns": [ 
                            {
                                "period": None, "period_source_ref_id": None,
                                "end_date": None, "end_date_source_ref_id": None 
                            }
                        ],
                        "metrics": [ 
                             { # Structure for ONE metric row for this segment
                                "name": None, "name_source_ref_id": None,
                                "description": None, "description_source_ref_id": None,
                                "values": [
                                    {
                                        "period": None, "value": None, "value_source_ref_id": None,
                                        "unit": None, "unit_source_ref_id": None,
                                        "yoy_change": None, "yoy_change_source_ref_id": None 
                                    }
                                ],
                                "notes": None 
                            }
                        ]
                    },
                    "one_time_items": [ # List of one-time items specific to this segment
                        { # Structure for ONE item (mirrors Section 7 structure)
                            "period": None, "period_source_ref_id": None,
                            "description": None, "description_source_ref_id": None,
                            "impact": { 
                                "value": None, "value_source_ref_id": None,
                                "unit": None, "unit_source_ref_id": None,
                                "affected_metric": None, "affected_metric_source_ref_id": None
                            },
                             "notes": None
                        }
                    ],
                    "mdna": { # MDNA specific to THIS segment
                        "trend_analysis": None, "trend_analysis_source_ref_id": None,
                        "key_achievements": [ {"description": None, "description_source_ref_id": None} ],
                        "key_challenges": [ {"description": None, "description_source_ref_id": None} ],
                        "management_disconnects": [
                            {
                                "management_statement": None, "management_statement_source_ref_id": None,
                                "actual_performance": None, "actual_performance_source_ref_id": None,
                                "notes": None 
                            }
                        ],
                         "notes": None 
                    },
                     "notes": None # Optional overall notes for the segment
                }
                # This list can contain zero or more segment dictionaries
            ],
            "footnotes": [ # Top-level list for all footnotes relevant to segment data
                { # Structure definition for ONE footnote
                    "id": None, "document": None, "page": None, "section": None 
                }
            ]
        },
        "template": { # Example data aligned with refined schema
            "segments": [
                { # Example Segment 1
                    "segment_name": "Industrial Automation",
                    "segment_name_source_ref_id": "ref1",
                    "segment_description": "Provides control systems, robotics, and software for factory automation.",
                    "segment_description_source_ref_id": "ref1",
                    "annual_financials": {
                        "columns": [
                            {"period": "FY 2021", "period_source_ref_id": "ref1", "end_date": "December 31, 2021", "end_date_source_ref_id": "ref1"},
                            {"period": "FY 2022", "period_source_ref_id": "ref1", "end_date": "December 31, 2022", "end_date_source_ref_id": "ref1"},
                            {"period": "FY 2023", "period_source_ref_id": "ref1", "end_date": "December 31, 2023", "end_date_source_ref_id": "ref1"}
                        ],
                        "metrics": [
                            {
                                "name": "Segment Revenue", "name_source_ref_id": "ref1", "description": None, "description_source_ref_id": None,
                                "values": [
                                    {"period": "FY 2021", "value": 2000.0, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "yoy_change": None, "yoy_change_source_ref_id": None},
                                    {"period": "FY 2022", "value": 2200.0, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "yoy_change": 10.0, "yoy_change_source_ref_id": "ref1"},
                                    {"period": "FY 2023", "value": 2500.0, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "yoy_change": 13.6, "yoy_change_source_ref_id": "ref1"}
                                ],
                                "notes": "Driven by new product introductions."
                            },
                            {
                                "name": "Segment Operating Income", "name_source_ref_id": "ref1", "description": None, "description_source_ref_id": None,
                                "values": [
                                    {"period": "FY 2021", "value": 300.0, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "yoy_change": None, "yoy_change_source_ref_id": None},
                                    {"period": "FY 2022", "value": 350.0, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "yoy_change": 16.7, "yoy_change_source_ref_id": "ref1"},
                                    {"period": "FY 2023", "value": 420.0, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "yoy_change": 20.0, "yoy_change_source_ref_id": "ref1"}
                                ],
                                "notes": "Margin expansion due to scale."
                            }
                            # ... Add other reported metrics for this segment
                        ]
                    },
                    "quarterly_financials": { # Example Quarterly data for Segment 1
                         "columns": [
                            {"period": "Q1 2023", "period_source_ref_id": "ref1", "end_date": "March 31, 2023", "end_date_source_ref_id": "ref1"},
                            {"period": "Q2 2023", "period_source_ref_id": "ref1", "end_date": "June 30, 2023", "end_date_source_ref_id": "ref1"},
                            {"period": "Q3 2023", "period_source_ref_id": "ref1", "end_date": "September 30, 2023", "end_date_source_ref_id": "ref1"},
                            {"period": "Q4 2023", "period_source_ref_id": "ref1", "end_date": "December 31, 2023", "end_date_source_ref_id": "ref1"},
                            {"period": "Q1 2024", "period_source_ref_id": "ref2", "end_date": "March 31, 2024", "end_date_source_ref_id": "ref2"}
                        ],
                        "metrics": [
                            {
                                "name": "Segment Revenue", "name_source_ref_id": "ref1", "description": None, "description_source_ref_id": None,
                                "values": [
                                    {"period": "Q1 2023", "value": 600, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "yoy_change": 12, "yoy_change_source_ref_id": "ref1"},
                                    {"period": "Q2 2023", "value": 620, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "yoy_change": 13, "yoy_change_source_ref_id": "ref1"},
                                    {"period": "Q3 2023", "value": 630, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "yoy_change": 14, "yoy_change_source_ref_id": "ref1"},
                                    {"period": "Q4 2023", "value": 650, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "yoy_change": 15, "yoy_change_source_ref_id": "ref1"},
                                    {"period": "Q1 2024", "value": 670, "value_source_ref_id": "ref2", "unit": "million USD", "unit_source_ref_id": "ref2", "yoy_change": 11.7, "yoy_change_source_ref_id": "ref2"}
                                ],
                                "notes": None
                            }
                        ]
                    },
                    "one_time_items": [
                         {"period": "FY 2023", "period_source_ref_id": "ref3", "description": "Restructuring charges related to facility consolidation within segment.", "description_source_ref_id": "ref3", "impact": {"value": -15.0, "value_source_ref_id": "ref3", "unit": "million USD", "unit_source_ref_id": "ref3", "affected_metric": "Segment Operating Income", "affected_metric_source_ref_id": "ref3"}, "notes": None}
                    ],
                    "mdna": {
                        "trend_analysis": "Strong revenue growth driven by new X1000 control system adoption, outpacing market growth.", "trend_analysis_source_ref_id": "ref4",
                        "key_achievements": [
                            {"description": "Achieved record segment operating income in FY2023.", "description_source_ref_id": "ref4"},
                            {"description": "Successfully ramped up production for X1000 series.", "description_source_ref_id": "ref4"}
                        ],
                        "key_challenges": [
                            {"description": "Increased pricing pressure from Asian competitors impacting standard product lines.", "description_source_ref_id": "ref5"},
                            {"description": "Supply chain lead times for specific semiconductor components remain elevated.", "description_source_ref_id": "ref5"}
                        ],
                        "management_disconnects": [
                             {"management_statement": "Management stated supply chain issues were 'fully resolved' in Q4 call.", "management_statement_source_ref_id": "ref5", "actual_performance": "Internal reports show lead times for Component XYZ remain 4 weeks above target.", "actual_performance_source_ref_id": "ref6", "notes": None}
                        ],
                         "notes": None
                    },
                     "notes": "Largest segment by revenue and profit."
                },
                { # Example Segment 2
                    "segment_name": "Process Control Systems",
                    "segment_name_source_ref_id": "ref1",
                    "segment_description": "Provides systems for continuous process industries like chemicals and energy.", "segment_description_source_ref_id": "ref1",
                    "annual_financials": {
                        "columns": [
                            {"period": "FY 2021", "period_source_ref_id": "ref1", "end_date": "December 31, 2021", "end_date_source_ref_id": "ref1"},
                            {"period": "FY 2022", "period_source_ref_id": "ref1", "end_date": "December 31, 2022", "end_date_source_ref_id": "ref1"},
                            {"period": "FY 2023", "period_source_ref_id": "ref1", "end_date": "December 31, 2023", "end_date_source_ref_id": "ref1"}
                        ],
                        "metrics": [
                            {
                                "name": "Segment Revenue", "name_source_ref_id": "ref1", "description": None, "description_source_ref_id": None,
                                "values": [
                                    {"period": "FY 2021", "value": 1500.0, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "yoy_change": None, "yoy_change_source_ref_id": None},
                                    {"period": "FY 2022", "value": 1650.0, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "yoy_change": 10.0, "yoy_change_source_ref_id": "ref1"},
                                    {"period": "FY 2023", "value": 1800.0, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "yoy_change": 9.1, "yoy_change_source_ref_id": "ref1"}
                                ],
                                 "notes": None
                            }
                            # ... Add other metrics like Segment EBITDA if reported ...
                        ]
                    },
                    "quarterly_financials": None, # Example where quarterly segment data isn't provided/required
                    "one_time_items": [],
                    "mdna": {
                         "trend_analysis": "Steady growth slightly below company average, benefiting from energy sector investments.", "trend_analysis_source_ref_id": "ref1",
                         "key_achievements": [{"description": "Secured multi-year contract with major chemical producer.", "description_source_ref_id": "ref1"}],
                         "key_challenges": [{"description": "Longer sales cycles compared to automation segment.", "description_source_ref_id": "ref1"}],
                         "management_disconnects": [],
                         "notes": None
                    },
                    "notes": None
                }
                 # ... Add other segments if reported ...
            ],
            "footnotes": [
                {"id": "ref1", "document": "Annual Report 2023", "page": "F-35", "section": "Note 15: Segment Information"},
                {"id": "ref2", "document": "Q1 2024 Quarterly Report", "page": "18", "section": "Segment Results"},
                {"id": "ref3", "document": "Annual Report 2023", "page": "F-36", "section": "Note 15: Segment Information (One-Time Items)"},
                {"id": "ref4", "document": "Annual Report 2023", "page": "30", "section": "MD&A - Segment Review"},
                {"id": "ref5", "document": "Q4 2023 Earnings Call Transcript", "page": "9", "section": "Segment Performance Discussion"},
                {"id": "ref6", "document": "Internal Performance Review Q1 2024", "page": "5", "section": "Segment KPI Analysis (Hypothetical)"}
            ]
        }
    },
# --- END: Section 8 Definition ---

# --- START: Section 9 Definition ---
    {
        "number": 9,
        "title": "Balance Sheet (Most Recent)",
        "specs": "Extract a summarized balance sheet for the most recent period available.\n"
                 "Present 5-6 key line items on the assets side (e.g., Cash, Receivables, Inventory, PP&E, Intangibles/Goodwill, Other) and 5-6 key line items on the liabilities & equity side (e.g., Short-term Debt, Payables, Other Current Liabilities, Long-term Debt, Other Non-current Liabilities, Total Equity).\n"
                 "For key line items, include value, unit, percentage of total assets (or liabilities & equity), and year-over-year change (%) if available.\n"
                 "Extract key balance sheet metrics: Total Assets, Total Debt, Cash & Equivalents, Net Debt, Net Debt / EBITDA (Leverage Multiple), Interest Coverage Ratio (e.g., EBITDA / Interest Expense), Total Book Equity.\n"
                 "Extract key working capital metrics: Working Capital (Current Assets - Current Liabilities), Current Ratio, Days Sales Outstanding (DSO), Days Inventory Outstanding (DIO), Days Payable Outstanding (DPO), Cash Conversion Cycle (CCC).\n"
                 "Extract details about the debt profile: breakdown by type (e.g., revolving credit, term loan, notes), maturity schedule, and key debt covenants (especially if risk of breach exists).\n"
                 "Identify any significant off-balance sheet items mentioned (e.g., operating leases, purchase commitments, guarantees).\n"
                 "Extract Management Discussion and Analysis (MDNA) specifically identifying the 2-3 areas of balance sheet management the company focuses on or should focus on (e.g., leverage targets, working capital efficiency, liquidity management).\n"
                 "All extracted data points requiring citation must have a corresponding source reference ID linking to a footnote.\n"
                 "Ensure all footnotes provide precise source details: document name, page number, and specific section/table (often Balance Sheet statement and Debt footnote).",
        "schema": {
            "balance_sheet_date": {
                "as_of": None, # string (e.g., "March 31, 2024")
                "as_of_source_ref_id": None
            },
            "assets": [ # List of key asset line items
                { # Structure for ONE asset line
                    "name": None, # string (e.g., "Cash and Cash Equivalents")
                    "name_source_ref_id": None,
                    "value": None, # number
                    "value_source_ref_id": None,
                    "unit": None, # string (e.g., "million USD")
                    "unit_source_ref_id": None,
                    "percentage_of_total_assets": None, # Optional number (%)
                    "percentage_of_total_assets_source_ref_id": None,
                    "yoy_change_percentage": None, # Optional number (%)
                    "yoy_change_percentage_source_ref_id": None,
                    "notes": None # Optional string
                }
            ],
            "liabilities_and_equity": [ # List of key liability & equity line items
                { # Structure for ONE line (same as assets)
                    "name": None, "name_source_ref_id": None, # e.g., "Short-term Debt", "Total Shareholders' Equity"
                    "value": None, "value_source_ref_id": None, # number
                    "unit": None, "unit_source_ref_id": None, # string
                    "percentage_of_total_liabilities_and_equity": None, # Optional number (%)
                    "percentage_of_total_liabilities_and_equity_source_ref_id": None,
                    "yoy_change_percentage": None, # Optional number (%)
                    "yoy_change_percentage_source_ref_id": None,
                    "notes": None # Optional string
                }
            ],
            "key_metrics": [ # List of specific key metrics
                { # Structure for ONE metric
                    "name": None, # string (e.g., "Total Assets", "Net Debt", "Current Ratio", "DSO")
                    "name_source_ref_id": None,
                    "description": None, # Optional string explaining the metric if not standard
                    "description_source_ref_id": None,
                    "value": None, # number or string
                    "value_source_ref_id": None,
                    "unit": None, # string (e.g., "million USD", "x", "days")
                    "unit_source_ref_id": None,
                    "as_of": None, # string (should match balance_sheet_date.as_of)
                    "as_of_source_ref_id": None,
                    "yoy_change": None, # Optional number or string for change value
                    "yoy_change_source_ref_id": None,
                    "yoy_change_unit": None, # Optional string for change unit (e.g., "x", "days", "%")
                    "yoy_change_unit_source_ref_id": None,
                    "notes": None # Optional string
                }
            ],
            "debt_profile": { # Details on debt structure
                "debt_breakdown": [ # List of debt instruments
                    {
                        "type": None, # string (e.g., "Revolving Credit Facility", "Senior Notes due 2028")
                        "type_source_ref_id": None,
                        "amount": None, # number (outstanding amount)
                        "amount_source_ref_id": None,
                        "unit": None, # string (e.g., "million USD")
                        "unit_source_ref_id": None,
                        "percentage_of_total_debt": None, # Optional number (%)
                        "percentage_of_total_debt_source_ref_id": None,
                        "interest_rate": { # Optional interest rate details
                             "description": None, # string (e.g., "SOFR + 1.25%", "Fixed 4.25%")
                             "description_source_ref_id": None,
                             "effective_rate": None, # Optional number (%)
                             "effective_rate_source_ref_id": None
                        },
                        "notes": None
                    }
                ],
                "debt_maturity": [ # List of maturity tranches
                    {
                        "maturity_period": None, # string (e.g., "Within 1 year", "1-2 years", "2028")
                        "maturity_period_source_ref_id": None,
                        "amount": None, # number
                        "amount_source_ref_id": None,
                        "unit": None, # string (e.g., "million USD")
                        "unit_source_ref_id": None,
                        "percentage_of_total_debt": None, # Optional number (%)
                        "percentage_of_total_debt_source_ref_id": None,
                        "notes": None
                    }
                ],
                "covenants": [ # List of key covenants
                    {
                        "name": None, # string (e.g., "Net Debt / EBITDA Ratio")
                        "name_source_ref_id": None,
                        "requirement": None, # string (e.g., "Must not exceed 3.0x")
                        "requirement_source_ref_id": None,
                        "current_value": None, # number or string (e.g., 1.15, "1.15x")
                        "current_value_source_ref_id": None,
                        "compliance_status": None, # string (e.g., "Compliant", "At Risk", "Breached")
                        "compliance_status_source_ref_id": None,
                        "headroom": None, # Optional number or string (e.g., 1.85, "Significant")
                        "headroom_source_ref_id": None,
                        "notes": None # Optional string regarding risk or definition
                    }
                ],
                "notes": None # Optional string for overall debt profile notes
            },
            "off_balance_sheet_items": [ # List of OBS items
                 { # Structure for ONE item
                     "type": None, # string (e.g., "Operating Lease Commitments")
                     "type_source_ref_id": None,
                     "description": None, # string
                     "description_source_ref_id": None,
                     "value": None, # Optional number (e.g., estimated value or commitment amount)
                     "value_source_ref_id": None,
                     "unit": None, # Optional string
                     "unit_source_ref_id": None,
                     "term": None, # Optional string describing duration
                     "term_source_ref_id": None,
                     "notes": None
                 }
            ],
            "mdna": { # MDNA focus on Balance Sheet Management
                "key_balance_sheet_focus_areas": [ # List of 2-3 focus areas
                    {
                        "area": None, # string (e.g., "Working Capital Management")
                        "area_source_ref_id": None, # If explicitly stated as focus
                        "description": None, # string explaining the focus and company's actions/position
                        "description_source_ref_id": None,
                        "supporting_metrics": [ # Optional list of relevant metrics
                            {
                                "name": None, "value": None, "unit": None, "as_of": None, "source_ref_id": None
                            }
                        ],
                        "notes": None
                    }
                ],
                 "notes": None # Optional overall MDNA notes
            },
            "footnotes": [ # Top-level list for all footnotes in this section
                { # Structure definition for ONE footnote
                    "id": None, "document": None, "page": None, "section": None 
                }
            ]
        },
        "template": { # Example data aligned with refined schema
            "balance_sheet_date": {
                "as_of": "March 31, 2024", "as_of_source_ref_id": "ref1"
            },
            "assets": [
                {"name": "Cash and Cash Equivalents", "name_source_ref_id": "ref1", "value": 845.2, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "percentage_of_total_assets": 12.7, "percentage_of_total_assets_source_ref_id": "ref1", "yoy_change_percentage": 8.6, "yoy_change_percentage_source_ref_id": "ref1", "notes": None},
                {"name": "Accounts Receivable, net", "name_source_ref_id": "ref1", "value": 987.3, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "percentage_of_total_assets": 14.9, "percentage_of_total_assets_source_ref_id": "ref1", "yoy_change_percentage": 12.1, "yoy_change_percentage_source_ref_id": "ref1", "notes": "DSO improved."},
                {"name": "Inventories", "name_source_ref_id": "ref1", "value": 752.8, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "percentage_of_total_assets": 11.3, "percentage_of_total_assets_source_ref_id": "ref1", "yoy_change_percentage": 6.8, "yoy_change_percentage_source_ref_id": "ref1", "notes": None},
                {"name": "Property, Plant & Equipment, net", "name_source_ref_id": "ref1", "value": 1875.4, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "percentage_of_total_assets": 28.2, "percentage_of_total_assets_source_ref_id": "ref1", "yoy_change_percentage": 5.7, "yoy_change_percentage_source_ref_id": "ref1", "notes": None},
                {"name": "Intangible Assets and Goodwill", "name_source_ref_id": "ref1", "value": 1945.2, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "percentage_of_total_assets": 29.3, "percentage_of_total_assets_source_ref_id": "ref1", "yoy_change_percentage": 2.1, "yoy_change_percentage_source_ref_id": "ref1", "notes": "Primarily from past acquisitions."},
                {"name": "Other Assets (Current & Non-Current)", "name_source_ref_id": "ref1", "value": 235.6 + 485.7, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "percentage_of_total_assets": 3.5 + 7.3, "percentage_of_total_assets_source_ref_id": "ref1", "yoy_change_percentage": None, "yoy_change_percentage_source_ref_id": None, "notes": "Aggregated other assets."} # Example aggregation
            ],
            "liabilities_and_equity": [
                {"name": "Short-term Debt", "name_source_ref_id": "ref1", "value": 348.5, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "percentage_of_total_liabilities_and_equity": 5.2, "percentage_of_total_liabilities_and_equity_source_ref_id": "ref1", "yoy_change_percentage": 15.3, "yoy_change_percentage_source_ref_id": "ref1", "notes": "Includes current portion of long-term debt."},
                {"name": "Accounts Payable", "name_source_ref_id": "ref1", "value": 542.6, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "percentage_of_total_liabilities_and_equity": 8.2, "percentage_of_total_liabilities_and_equity_source_ref_id": "ref1", "yoy_change_percentage": 7.8, "yoy_change_percentage_source_ref_id": "ref1", "notes": "DPO extended slightly."},
                {"name": "Other Current Liabilities", "name_source_ref_id": "ref1", "value": 387.4, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "percentage_of_total_liabilities_and_equity": 5.8, "percentage_of_total_liabilities_and_equity_source_ref_id": "ref1", "yoy_change_percentage": 6.5, "yoy_change_percentage_source_ref_id": "ref1", "notes": "Includes accrued expenses."},
                {"name": "Long-term Debt", "name_source_ref_id": "ref1", "value": 1745.3, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "percentage_of_total_liabilities_and_equity": 26.3, "percentage_of_total_liabilities_and_equity_source_ref_id": "ref1", "yoy_change_percentage": -3.2, "yoy_change_percentage_source_ref_id": "ref1", "notes": "Net decrease due to repayments."},
                {"name": "Other Non-current Liabilities", "name_source_ref_id": "ref1", "value": 485.7, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "percentage_of_total_liabilities_and_equity": 7.3, "percentage_of_total_liabilities_and_equity_source_ref_id": "ref1", "yoy_change_percentage": 2.5, "yoy_change_percentage_source_ref_id": "ref1", "notes": "Includes deferred taxes and pension liabilities."},
                {"name": "Total Shareholders' Equity", "name_source_ref_id": "ref1", "value": 3132.0, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "percentage_of_total_liabilities_and_equity": 47.2, "percentage_of_total_liabilities_and_equity_source_ref_id": "ref1", "yoy_change_percentage": 9.8, "yoy_change_percentage_source_ref_id": "ref1", "notes": "Increased due to retained earnings."}
            ],
            "key_metrics": [
                {"name": "Total Assets", "name_source_ref_id": "ref1", "description": None, "value": 6641.5, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "as_of": "March 31, 2024", "as_of_source_ref_id": "ref1", "yoy_change": 6.2, "yoy_change_source_ref_id": "ref1", "yoy_change_unit": "%", "yoy_change_unit_source_ref_id": "ref1", "notes": None},
                {"name": "Total Debt", "name_source_ref_id": "ref1", "description": "Short-term Debt + Long-term Debt", "value": 2093.8, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "as_of": "March 31, 2024", "as_of_source_ref_id": "ref1", "yoy_change": -0.6, "yoy_change_source_ref_id": "ref1", "yoy_change_unit": "%", "yoy_change_unit_source_ref_id": "ref1", "notes": "Slight decrease YoY."},
                {"name": "Net Debt", "name_source_ref_id": "ref1", "description": "Total Debt minus Cash and Cash Equivalents", "value": 1248.6, "value_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1", "as_of": "March 31, 2024", "as_of_source_ref_id": "ref1", "yoy_change": -6.9, "yoy_change_source_ref_id": "ref1", "yoy_change_unit": "%", "yoy_change_unit_source_ref_id": "ref1", "notes": None},
                {"name": "Net Debt to EBITDA", "name_source_ref_id": "ref1", "description": "Net Debt divided by LTM EBITDA", "value": 1.15, "value_source_ref_id": "ref1", "unit": "x", "unit_source_ref_id": "ref1", "as_of": "March 31, 2024", "as_of_source_ref_id": "ref1", "yoy_change": -0.25, "yoy_change_source_ref_id": "ref1", "yoy_change_unit": "x", "yoy_change_unit_source_ref_id": "ref1", "notes": "Leverage decreased."},
                {"name": "Cash Conversion Cycle", "name_source_ref_id": "ref1", "description": "DSO + DIO - DPO", "value": 96.3, "value_source_ref_id": "ref1", "unit": "days", "unit_source_ref_id": "ref1", "as_of": "March 31, 2024", "as_of_source_ref_id": "ref1", "yoy_change": -8.5, "yoy_change_source_ref_id": "ref1", "yoy_change_unit": "days", "yoy_change_unit_source_ref_id": "ref1", "notes": "Significant improvement."}
                 # ... Add other key metrics (Interest Coverage, Working Capital, Current Ratio, DSO, DIO, DPO)
            ],
            "debt_profile": {
                "debt_breakdown": [
                    {"type": "Revolving Credit Facility", "type_source_ref_id": "ref2", "amount": 250.0, "amount_source_ref_id": "ref2", "unit": "million USD", "unit_source_ref_id": "ref2", "percentage_of_total_debt": 11.9, "percentage_of_total_debt_source_ref_id": "ref2", "interest_rate": {"description": "SOFR + 1.25%", "description_source_ref_id": "ref2", "effective_rate": 5.85, "effective_rate_source_ref_id": "ref2"}, "notes": "$750M total facility size, undrawn portion $500M."},
                    {"type": "Senior Notes due 2028", "type_source_ref_id": "ref2", "amount": 500.0, "amount_source_ref_id": "ref2", "unit": "million USD", "unit_source_ref_id": "ref2", "percentage_of_total_debt": 23.9, "percentage_of_total_debt_source_ref_id": "ref2", "interest_rate": {"description": "Fixed 4.25%", "description_source_ref_id": "ref2", "effective_rate": 4.25, "effective_rate_source_ref_id": "ref2"}, "notes": None}
                    # ... Add other debt instruments
                ],
                "debt_maturity": [
                    {"maturity_period": "Within 1 year", "maturity_period_source_ref_id": "ref2", "amount": 348.5, "amount_source_ref_id": "ref2", "unit": "million USD", "unit_source_ref_id": "ref2", "percentage_of_total_debt": 16.6, "percentage_of_total_debt_source_ref_id": "ref2", "notes": "Includes current portion of term loan."},
                    {"maturity_period": "1-2 years", "maturity_period_source_ref_id": "ref2", "amount": 325.0, "amount_source_ref_id": "ref2", "unit": "million USD", "unit_source_ref_id": "ref2", "percentage_of_total_debt": 15.5, "percentage_of_total_debt_source_ref_id": "ref2", "notes": None}
                    # ... Add other maturity buckets
                ],
                "covenants": [
                    {"name": "Net Debt / EBITDA Ratio", "name_source_ref_id": "ref2", "requirement": "< 3.0x", "requirement_source_ref_id": "ref2", "current_value": "1.15x", "current_value_source_ref_id": "ref1", "compliance_status": "Compliant", "compliance_status_source_ref_id": "ref2", "headroom": "Significant", "headroom_source_ref_id": "ref2", "notes": None},
                    {"name": "Interest Coverage Ratio", "name_source_ref_id": "ref2", "requirement": "> 4.0x", "requirement_source_ref_id": "ref2", "current_value": "12.8x", "current_value_source_ref_id": "ref1", "compliance_status": "Compliant", "compliance_status_source_ref_id": "ref2", "headroom": "Significant", "headroom_source_ref_id": "ref2", "notes": None}
                ],
                "notes": "Well-structured debt profile with manageable leverage."
            },
            "off_balance_sheet_items": [
                 {"type": "Operating Lease Commitments", "type_source_ref_id": "ref2", "description": "Future minimum lease payments under non-cancelable operating leases, primarily for facilities.", "description_source_ref_id": "ref2", "value": 185.7, "value_source_ref_id": "ref2", "unit": "million USD", "unit_source_ref_id": "ref2", "term": "Various terms through 2032", "term_source_ref_id": "ref2", "notes": None}
                 # ... Add other OBS items like purchase commitments, guarantees
            ],
            "mdna": {
                "key_balance_sheet_focus_areas": [
                    {
                        "area": "Working Capital Management", "area_source_ref_id": "ref3",
                        "description": "Management prioritized improving cash conversion cycle through enhanced credit management and inventory optimization.", "description_source_ref_id": "ref3",
                        "supporting_metrics": [{"name": "Cash Conversion Cycle", "value": 96.3, "unit": "days", "as_of": "Q1 2024", "source_ref_id": "ref1"}],
                        "notes": "Targeting 90 days by year-end 2024."
                    },
                    {
                        "area": "Capital Structure Optimization", "area_source_ref_id": "ref3",
                        "description": "Maintaining conservative leverage (Net Debt/EBITDA 1.15x vs. target 1.5-2.0x) provides significant capacity for strategic M&A.", "description_source_ref_id": "ref3",
                         "supporting_metrics": [{"name": "Net Debt / EBITDA", "value": 1.15, "unit": "x", "as_of": "Q1 2024", "source_ref_id": "ref1"}],
                        "notes": None
                    }
                     # ... Add third focus area if applicable ...
                ],
                 "notes": None
            },
            "footnotes": [
                {"id": "ref1", "document": "Q1 2024 Quarterly Report", "page": "15-18", "section": "Condensed Consolidated Balance Sheets"},
                {"id": "ref2", "document": "Q1 2024 Quarterly Report", "page": "22-25", "section": "Notes - Note 8: Debt and Credit Facilities"},
                {"id": "ref3", "document": "Q1 2024 Earnings Call Transcript", "page": "7-9", "section": "CFO Financial Review"}
            ]
        }
    },
# --- END: Section 9 Definition ---

# --- START: Section 10 Definition ---
    {
        "number": 10,
        "title": "Top 10 Shareholders",
        "specs": "Extract data on the ownership structure, including total outstanding shares and details on different share classes (ticker, voting rights, special rights) if applicable. Specify the 'as of' date for ownership data.\n"
                 "Extract a list of the top 10 shareholders by name, identifying their type (e.g., Family Office, Asset Manager, Insider) and beneficial owner if disclosed.\n"
                 "For each top shareholder, provide the number of shares held, percentage ownership, details on any material changes in ownership over the reporting period (e.g., increase/decrease, amount, period, reason), and board representation (number of seats, names of representatives) if applicable.\n"
                 "Identify and describe any significant shareholder groups (e.g., Founding Families, Management Team, Index Funds), listing members and total group ownership percentage.\n"
                 "Provide details on total insider holdings (executives and directors as a group), listing key individuals if possible.\n"
                 "Extract information on any history of shareholder activism (activist name, campaign period, demands, outcome, current ownership).\n"
                 "Extract details on any known shareholder agreements (parties, type, key provisions, expiration).\n"
                 "All extracted data points requiring citation must have a corresponding source reference ID linking to a footnote.\n"
                 "Ensure all footnotes provide precise source details: document name, page number (or filing date/type like 'Proxy Statement 2024'), and specific section/table.",
        "schema": {
            "ownership_date": {
                "as_of": None, # string (e.g., "March 31, 2024")
                "as_of_source_ref_id": None
            },
            "share_structure": {
                "total_outstanding_shares": {
                    "value": None, # number
                    "value_source_ref_id": None,
                    "unit": None, # string (e.g., "million shares")
                    "unit_source_ref_id": None,
                    "as_of": None, # string (Should match ownership_date.as_of)
                    "as_of_source_ref_id": None
                },
                "share_classes": [ # List of share classes
                    {
                        "class_name": None, # string (e.g., "Common Stock", "Class B")
                        "class_name_source_ref_id": None,
                        "ticker_symbol": None, # Optional string (e.g., "EXMP")
                        "ticker_symbol_source_ref_id": None,
                        "outstanding_shares": None, # Optional number (if different from total)
                        "outstanding_shares_source_ref_id": None,
                        "unit": None, # string (e.g., "million shares")
                        "unit_source_ref_id": None,
                        "voting_rights_per_share": None, # string (e.g., "One vote per share", "10 votes per share")
                        "voting_rights_per_share_source_ref_id": None,
                        "special_rights": None, # Optional string describing dividends, conversion etc.
                        "special_rights_source_ref_id": None,
                        "notes": None
                    }
                ]
            },
            "top_shareholders": [ # List of top shareholder objects (typically up to 10)
                { # Structure for ONE shareholder
                    "rank": None, # number (1, 2, 3...)
                    "name": None, # string (e.g., "Roberts Family Holdings LLC")
                    "name_source_ref_id": None,
                    "type": None, # string (e.g., "Family Investment Vehicle", "Asset Manager", "Individual/Insider")
                    "type_source_ref_id": None,
                    "shares_held": None, # number
                    "shares_held_source_ref_id": None,
                    "unit": "shares", # Assuming unit is shares unless otherwise specified
                    "percentage_ownership": None, # number (%)
                    "percentage_ownership_source_ref_id": None,
                    "beneficial_owner_disclosed": None, # Optional string (e.g., "Thomas J. Roberts (Founder)", "Multiple funds")
                    "beneficial_owner_disclosed_source_ref_id": None,
                    "material_changes": { # Optional object for recent changes
                        "type": None, # string ("Increase" or "Decrease")
                        "type_source_ref_id": None,
                        "amount": None, # number (e.g., 1.2)
                        "amount_source_ref_id": None,
                        "unit": None, # string (e.g., "percentage points", "million shares")
                        "unit_source_ref_id": None,
                        "period": None, # string (e.g., "Last 12 months", "Q1 2024")
                        "period_source_ref_id": None,
                        "description": None, # Optional string explaining reason/context
                        "description_source_ref_id": None
                    },
                    "board_representation": { # Optional object for board seats
                         "seats": None, # number
                         "seats_source_ref_id": None,
                         "total_board_seats": None, # Optional number (for context)
                         "total_board_seats_source_ref_id": None,
                         "representatives": [], # List of strings (names)
                         "representatives_source_ref_id": None
                    },
                    "notes": None # Optional string for shareholder notes
                }
            ],
            "shareholder_groups": [ # Optional list of significant groups
                { # Structure for ONE group
                    "name": None, # string (e.g., "Founding Families")
                    "name_source_ref_id": None,
                    "description": None, # string
                    "description_source_ref_id": None,
                    "members": [], # List of strings (names of shareholders in group)
                    "members_source_ref_id": None,
                    "total_ownership_percentage": None, # number (%)
                    "total_ownership_percentage_source_ref_id": None,
                    "special_rights_or_agreements": None, # Optional string
                    "special_rights_or_agreements_source_ref_id": None,
                    "notes": None
                }
            ],
            "insider_holdings": [ # Optional list for specific insider holdings
                { # Structure for ONE insider
                    "name": None, # string
                    "name_source_ref_id": None,
                    "position": None, # string (e.g., "Chief Executive Officer", "Director")
                    "position_source_ref_id": None,
                    "shares_held": None, # number
                    "shares_held_source_ref_id": None,
                    "unit": "shares",
                    "percentage_ownership": None, # number (%)
                    "percentage_ownership_source_ref_id": None,
                    "notes": None # e.g., "Includes shares held by family trust"
                }
            ],
            "shareholder_activism": [ # Optional list of activism events
                 { # Structure for ONE event
                     "activist_name": None, # string (e.g., "Starboard Value LP")
                     "activist_name_source_ref_id": None,
                     "campaign_period": None, # string (e.g., "Q1 2022 - Q3 2022")
                     "campaign_period_source_ref_id": None,
                     "peak_ownership": None, # Optional number (%)
                     "peak_ownership_source_ref_id": None,
                     "demands": [], # List of strings
                     "demands_source_ref_id": None,
                     "outcome": None, # string describing resolution
                     "outcome_source_ref_id": None,
                     "current_ownership": None, # Optional number (%)
                     "current_ownership_source_ref_id": None,
                     "notes": None
                 }
            ],
            "shareholder_agreements": [ # Optional list of agreements
                 { # Structure for ONE agreement
                     "parties": [], # List of strings (names of parties)
                     "parties_source_ref_id": None,
                     "agreement_type": None, # string (e.g., "Governance Agreement", "Settlement Agreement")
                     "agreement_type_source_ref_id": None,
                     "date_effective": None, # string (e.g., "June 15, 2018")
                     "date_effective_source_ref_id": None,
                     "key_provisions": [], # List of strings describing provisions
                     "key_provisions_source_ref_id": None,
                     "expiration": None, # string (e.g., "None", "Annual Meeting 2024")
                     "expiration_source_ref_id": None,
                     "notes": None
                 }
            ],
            "footnotes": [ # Top-level list for all footnotes in this section
                { # Structure definition for ONE footnote
                    "id": None, "document": None, "page": None, "section": None 
                }
            ]
        },
        "template": { # Example data aligned with refined schema
            "ownership_date": {
                "as_of": "March 31, 2024", "as_of_source_ref_id": "ref1"
            },
            "share_structure": {
                "total_outstanding_shares": {
                    "value": 125.7, "value_source_ref_id": "ref1",
                    "unit": "million shares", "unit_source_ref_id": "ref1",
                    "as_of": "March 31, 2024", "as_of_source_ref_id": "ref1"
                },
                "share_classes": [
                    {
                        "class_name": "Common Stock", "class_name_source_ref_id": "ref1",
                        "ticker_symbol": "EXMP", "ticker_symbol_source_ref_id": "ref1",
                        "outstanding_shares": 125.7, "outstanding_shares_source_ref_id": "ref1",
                        "unit": "million shares", "unit_source_ref_id": "ref1",
                        "voting_rights_per_share": "One vote per share", "voting_rights_per_share_source_ref_id": "ref1",
                        "special_rights": None, "special_rights_source_ref_id": None,
                        "notes": "Only one class of stock outstanding."
                    }
                ]
            },
            "top_shareholders": [
                {
                    "rank": 1,
                    "name": "Roberts Family Holdings LLC", "name_source_ref_id": "ref1",
                    "type": "Family Investment Vehicle", "type_source_ref_id": "ref1",
                    "shares_held": 18850000, "shares_held_source_ref_id": "ref1",
                    "unit": "shares",
                    "percentage_ownership": 15.0, "percentage_ownership_source_ref_id": "ref1",
                    "beneficial_owner_disclosed": "Thomas J. Roberts (Founder)", "beneficial_owner_disclosed_source_ref_id": "ref1",
                    "material_changes": { 
                        "type": "Decrease", "type_source_ref_id": "ref2",
                        "amount": 1.2, "amount_source_ref_id": "ref2",
                        "unit": "percentage points", "unit_source_ref_id": "ref2",
                        "period": "Last 12 months", "period_source_ref_id": "ref2",
                        "description": "Gradual diversification as part of estate planning.", "description_source_ref_id": "ref2"
                    },
                    "board_representation": { 
                         "seats": 2, "seats_source_ref_id": "ref3",
                         "total_board_seats": 11, "total_board_seats_source_ref_id": "ref3",
                         "representatives": ["Thomas J. Roberts (Chairman)", "Sarah Roberts-Chen (Director)"], "representatives_source_ref_id": "ref3"
                    },
                    "notes": "Founder's holding company."
                },
                {
                    "rank": 2,
                    "name": "BlackRock, Inc.", "name_source_ref_id": "ref1",
                    "type": "Asset Manager", "type_source_ref_id": "ref1",
                    "shares_held": 12570000, "shares_held_source_ref_id": "ref1",
                    "unit": "shares",
                    "percentage_ownership": 10.0, "percentage_ownership_source_ref_id": "ref1",
                    "beneficial_owner_disclosed": "Multiple funds managed by BlackRock", "beneficial_owner_disclosed_source_ref_id": "ref1",
                    "material_changes": None, # Example: No material change mentioned
                    "board_representation": None,
                    "notes": "Primarily passive index fund holdings."
                }
                 # ... Add up to 8 more shareholders following the structure ...
            ],
            "shareholder_groups": [
                 {
                    "name": "Founding Families", "name_source_ref_id": "ref3",
                    "description": "Combined holdings of company founders and their families.", "description_source_ref_id": "ref3",
                    "members": ["Roberts Family Holdings LLC (15.0%)", "Chen Family Trust (4.0%)"], "members_source_ref_id": "ref3",
                    "total_ownership_percentage": 19.0, "total_ownership_percentage_source_ref_id": "ref3",
                    "special_rights_or_agreements": "Right to nominate up to 3 board members per Governance Agreement.", "special_rights_or_agreements_source_ref_id": "ref3",
                    "notes": None
                }
                 # ... Add other groups like Management, Index Funds if relevant ...
            ],
            "insider_holdings": [
                 {"name": "James Miller", "name_source_ref_id": "ref4", "position": "Chief Executive Officer", "position_source_ref_id": "ref4", "shares_held": 2510000, "shares_held_source_ref_id": "ref4", "unit": "shares", "percentage_ownership": 2.0, "percentage_ownership_source_ref_id": "ref4", "notes": "Includes direct ownership and family trusts."},
                 {"name": "All Executive Officers and Directors as a group", "name_source_ref_id": "ref4", "position": "Group total", "position_source_ref_id": "ref4", "shares_held": 27650000, "shares_held_source_ref_id": "ref4", "unit": "shares", "percentage_ownership": 22.0, "percentage_ownership_source_ref_id": "ref4", "notes": None}
            ],
            "shareholder_activism": [
                 {
                     "activist_name": "Starboard Value LP", "activist_name_source_ref_id": "ref5",
                     "campaign_period": "Q1 2022 - Q3 2022", "campaign_period_source_ref_id": "ref5",
                     "peak_ownership": 4.2, "peak_ownership_source_ref_id": "ref5",
                     "demands": ["Board refreshment", "Cost-cutting initiatives", "Review of underperforming segments"], "demands_source_ref_id": "ref5",
                     "outcome": "Settlement reached Aug 2022: two new independent directors appointed, strategic review committee formed.", "outcome_source_ref_id": "ref5",
                     "current_ownership": 0.0, "current_ownership_source_ref_id": "ref5", # Assuming they exited
                     "notes": "Exited position in Q1 2023."
                 }
            ],
             "shareholder_agreements": [
                 { 
                     "parties": ["Company", "Roberts Family Holdings LLC", "Chen Family Trust"], "parties_source_ref_id": "ref3",
                     "agreement_type": "Governance Agreement", "agreement_type_source_ref_id": "ref3",
                     "date_effective": "June 15, 2018", "date_effective_source_ref_id": "ref3",
                     "key_provisions": ["Right to nominate up to 3 board members while >15% combined ownership", "Certain major transactions require 2/3 board approval"], "key_provisions_source_ref_id": "ref3",
                     "expiration": "Perpetual unless ownership thresholds unmet", "expiration_source_ref_id": "ref3",
                     "notes": None
                 }
            ],
            "footnotes": [
                {"id": "ref1", "document": "Annual Proxy Statement 2024", "page": "24-28", "section": "Security Ownership"},
                {"id": "ref2", "document": "SEC Form 4 Filings Analysis", "page": "Summary", "section": "Ownership Trend Analysis"},
                {"id": "ref3", "document": "Governance Agreement Summary", "page": "Internal Memo", "section": "Key Terms"},
                {"id": "ref4", "document": "Annual Proxy Statement 2024", "page": "27", "section": "Insider Holdings Table"},
                {"id": "ref5", "document": "Investor Relations Presentation Q1 2024", "page": "32", "section": "Corporate Governance Update"}
            ]
        }
    },
# --- END: Section 10 Definition ---

# --- START: Section 11 Definition ---
    {
        "number": 11,
        "title": "Material Corporate Activity",
        "specs": "Extract a list of material corporate activities undertaken by the Company over the last 3 years. Include strategic reviews, significant financings (debt/equity), capital raises, major investments, acquisitions, and divestitures.\n"
                 "Include details on pending and rumored transactions, as well as completed ones, clearly indicating the status.\n"
                 "Include information on any material transactions that were pursued but failed or were terminated.\n"
                 "Present activities chronologically (most recent first is often preferred).\n"
                 "For each material activity, extract:\n"
                 "  - Date (announcement or completion).\n"
                 "  - Type of activity (e.g., Acquisition, Divestiture, Financing, Strategic Review, Share Repurchase).\n"
                 "  - Target/Asset/Counterparty involved (if applicable).\n"
                 "  - Description of the activity.\n"
                 "  - Transaction value (amount and unit) if disclosed.\n"
                 "  - Key deal structure details (e.g., cash/stock mix, financing source, contingent considerations) if available.\n"
                 "  - Stated strategic rationale (including expected synergies if mentioned).\n"
                 "  - Current status (e.g., Pending, Completed, Terminated, Rumored) and expected closing date if pending.\n"
                 "  - Market reaction (e.g., stock price change on announcement) if mentioned.\n"
                 "  - Post-transaction performance metrics or impact analysis for completed material transactions, if available.\n"
                 "All extracted data points requiring citation must have a corresponding source reference ID linking to a footnote.\n"
                 "Ensure all footnotes provide precise source details: document name, date (for press releases/articles), page number, and specific section/table.",
        "schema": {
            "corporate_activities": [ # List of activities, ideally most recent first
                { # Structure for ONE activity
                    "date": None, # string (e.g., "March 15, 2024", "Q3 2023")
                    "date_source_ref_id": None,
                    "activity_type": None, # string (e.g., "Pending Acquisition", "Divestiture", "Financing")
                    "activity_type_source_ref_id": None,
                    "involved_parties": { # Target, Asset, Counterparty etc.
                         "name": None, # string (e.g., "TechInnovate Solutions, Inc.", "Legacy Components Division")
                         "name_source_ref_id": None,
                         "type": None # Optional string (e.g., "Target Company", "Divested Asset")
                    },
                    "description": None, # string summarizing the activity
                    "description_source_ref_id": None,
                    "transaction_details": { # Optional details on value and structure
                        "value": {
                            "amount": None, # number or string (e.g., 450.0, "Undisclosed")
                            "amount_source_ref_id": None,
                            "unit": None, # string (e.g., "million USD")
                            "unit_source_ref_id": None
                        },
                        "deal_structure": { # Optional sub-object for structure details
                            "cash_component_value": None, "cash_component_value_source_ref_id": None,
                            "cash_component_unit": None, "cash_component_unit_source_ref_id": None,
                            "cash_percentage": None, "cash_percentage_source_ref_id": None, # number (%)
                            "stock_component_value": None, "stock_component_value_source_ref_id": None,
                            "stock_component_unit": None, "stock_component_unit_source_ref_id": None,
                            "stock_percentage": None, "stock_percentage_source_ref_id": None, # number (%)
                            "financing_details": None, # string (e.g., "Funded via cash and new term loan")
                            "financing_details_source_ref_id": None,
                            "contingent_consideration": { # Optional nested object
                                "type": None, # string (e.g., "Earnout")
                                "type_source_ref_id": None,
                                "maximum_value": None, "maximum_value_source_ref_id": None,
                                "unit": None, "unit_source_ref_id": None,
                                "conditions": None, # string
                                "conditions_source_ref_id": None
                            },
                            "notes": None # Optional structure notes
                        }
                    },
                    "strategic_rationale": { # Optional rationale details
                        "description": None, # string
                        "description_source_ref_id": None,
                        "expected_synergies": { # Optional nested object for synergies
                             "cost_synergies_value": None, "cost_synergies_value_source_ref_id": None,
                             "cost_synergies_unit": None, "cost_synergies_unit_source_ref_id": None, # e.g., "million USD annually"
                             "cost_synergies_timeline": None, "cost_synergies_timeline_source_ref_id": None, # e.g., "Within 24 months"
                             "revenue_synergies_value": None, "revenue_synergies_value_source_ref_id": None,
                             "revenue_synergies_unit": None, "revenue_synergies_unit_source_ref_id": None,
                             "revenue_synergies_timeline": None, "revenue_synergies_timeline_source_ref_id": None
                        },
                        "divested_financial_profile": { # Optional for divestitures
                             "annual_revenue": None, "annual_revenue_source_ref_id": None,
                             "revenue_unit": None, "revenue_unit_source_ref_id": None,
                             "ebitda_margin": None, "ebitda_margin_source_ref_id": None,
                             "margin_unit": "%",
                             "period": None, "period_source_ref_id": None # e.g., "FY 2022"
                        },
                        "notes": None
                    },
                    "status": { # Optional status details
                        "current_status": None, # string (e.g., "Pending regulatory approval", "Completed", "Terminated")
                        "current_status_source_ref_id": None,
                        "expected_closing_date": None, # string (e.g., "Q3 2024")
                        "expected_closing_date_source_ref_id": None,
                        "termination_reason": None, # Optional string for terminated deals
                        "termination_reason_source_ref_id": None
                    },
                    "market_reaction": { # Optional market reaction details
                         "stock_price_change": None, # number (%)
                         "stock_price_change_source_ref_id": None,
                         "period": None, # string (e.g., "Day of announcement")
                         "period_source_ref_id": None,
                         "notes": None
                    },
                     "post_transaction_impact": { # Optional impact details for completed deals
                         "use_of_proceeds": None, # string (e.g., "Debt reduction, share repurchase")
                         "use_of_proceeds_source_ref_id": None,
                         "financial_impact_description": None, # string (e.g., margin improvement)
                         "financial_impact_description_source_ref_id": None,
                         "financial_impact_value": None, # number
                         "financial_impact_value_source_ref_id": None,
                         "financial_impact_unit": None, # string (e.g., "percentage points increase")
                         "financial_impact_unit_source_ref_id": None,
                         "integration_status": None, # string for acquisitions
                         "integration_status_source_ref_id": None,
                         "notes": None
                    },
                    "notes": None # Optional overall notes for the activity
                }
            ],
            "footnotes": [ # Top-level list for all footnotes in this section
                { # Structure definition for ONE footnote
                    "id": None, "document": None, "page": None, "section": None, "date": None # Added optional date for PRs/Articles
                }
            ]
        },
        "template": { # Example data aligned with refined schema
            "corporate_activities": [
                { # Example: Pending Acquisition
                    "date": "March 15, 2024", "date_source_ref_id": "ref1",
                    "activity_type": "Pending Acquisition", "activity_type_source_ref_id": "ref1",
                    "involved_parties": {"name": "TechInnovate Solutions, Inc.", "name_source_ref_id": "ref1", "type": "Target Company"},
                    "description": "Announced agreement to acquire TechInnovate Solutions, a provider of advanced industrial IoT solutions.", "description_source_ref_id": "ref1",
                    "transaction_details": {
                        "value": {"amount": 450.0, "amount_source_ref_id": "ref1", "unit": "million USD", "unit_source_ref_id": "ref1"},
                        "deal_structure": {
                            "cash_component_value": 325.0, "cash_component_value_source_ref_id": "ref1", "cash_component_unit": "million USD", "cash_component_unit_source_ref_id": "ref1", "cash_percentage": 72.2, "cash_percentage_source_ref_id": "ref1",
                            "stock_component_value": 125.0, "stock_component_value_source_ref_id": "ref1", "stock_component_unit": "million USD", "stock_component_unit_source_ref_id": "ref1", "stock_percentage": 27.8, "stock_percentage_source_ref_id": "ref1",
                            "financing_details": "Funded through existing cash reserves and a new $200M term loan facility.", "financing_details_source_ref_id": "ref1",
                            "contingent_consideration": None, "notes": None
                        }
                    },
                    "strategic_rationale": {
                        "description": "Expands industrial automation offerings with complementary IoT capabilities, expected to accelerate digital transformation initiatives.", "description_source_ref_id": "ref1",
                        "expected_synergies": {
                             "cost_synergies_value": 35.0, "cost_synergies_value_source_ref_id": "ref1", "cost_synergies_unit": "million USD annually", "cost_synergies_unit_source_ref_id": "ref1", "cost_synergies_timeline": "Within 24 months of closing", "cost_synergies_timeline_source_ref_id": "ref1",
                             "revenue_synergies_value": 65.0, "revenue_synergies_value_source_ref_id": "ref1", "revenue_synergies_unit": "million USD annually", "revenue_synergies_unit_source_ref_id": "ref1", "revenue_synergies_timeline": "By year 3 post-closing", "revenue_synergies_timeline_source_ref_id": "ref1"
                        },
                        "divested_financial_profile": None, "notes": None
                    },
                    "status": { "current_status": "Pending regulatory approval", "current_status_source_ref_id": "ref1", "expected_closing_date": "Q3 2024", "expected_closing_date_source_ref_id": "ref1", "termination_reason": None },
                    "market_reaction": { "stock_price_change": 3.5, "stock_price_change_source_ref_id": "ref2", "period": "Day of announcement", "period_source_ref_id": "ref2", "notes": None },
                    "post_transaction_impact": None,
                    "notes": "Expected to be accretive to EPS in year 2."
                },
                 { # Example: Completed Divestiture
                    "date": "October 12, 2023", "date_source_ref_id": "ref3",
                    "activity_type": "Divestiture", "activity_type_source_ref_id": "ref3",
                    "involved_parties": {"name": "Legacy Components Division", "name_source_ref_id": "ref3", "type": "Divested Asset"},
                    "description": "Completed sale of non-core Legacy Components Division to Industrial Partners Group.", "description_source_ref_id": "ref3",
                    "transaction_details": {
                        "value": {"amount": 185.0, "amount_source_ref_id": "ref3", "unit": "million USD", "unit_source_ref_id": "ref3"},
                        "deal_structure": {
                            "cash_component_value": 185.0, "cash_component_value_source_ref_id": "ref3", "cash_component_unit": "million USD", "cash_component_unit_source_ref_id": "ref3", "cash_percentage": 100.0, "cash_percentage_source_ref_id": "ref3",
                            "stock_component_value": None, "stock_percentage": None, "financing_details": None,
                            "contingent_consideration": {
                                "type": "Earnout", "type_source_ref_id": "ref3",
                                "maximum_value": 25.0, "maximum_value_source_ref_id": "ref3", "unit": "million USD", "unit_source_ref_id": "ref3",
                                "conditions": "Based on division achieving EBITDA targets through 2025", "conditions_source_ref_id": "ref3"
                            },
                            "notes": None
                        }
                    },
                    "strategic_rationale": {
                        "description": "Divested non-core business with declining margins to focus resources on higher-growth automation segments.", "description_source_ref_id": "ref3",
                        "expected_synergies": None,
                        "divested_financial_profile": { 
                             "annual_revenue": 120.0, "annual_revenue_source_ref_id": "ref3", "revenue_unit": "million USD", "revenue_unit_source_ref_id": "ref3",
                             "ebitda_margin": 12.5, "ebitda_margin_source_ref_id": "ref3", "margin_unit": "%", "period": "FY 2022", "period_source_ref_id": "ref3"
                        },
                        "notes": None
                    },
                    "status": { "current_status": "Completed", "current_status_source_ref_id": "ref3", "expected_closing_date": None, "termination_reason": None },
                    "market_reaction": None,
                     "post_transaction_impact": {
                         "use_of_proceeds": "Debt reduction ($100M) and share repurchase program ($85M).", "use_of_proceeds_source_ref_id": "ref4",
                         "financial_impact_description": "Consolidated EBITDA margin improvement.", "financial_impact_description_source_ref_id": "ref4",
                         "financial_impact_value": 0.8, "financial_impact_value_source_ref_id": "ref4",
                         "financial_impact_unit": "percentage points", "financial_impact_unit_source_ref_id": "ref4",
                         "integration_status": None, "notes": None
                    },
                    "notes": None
                }
                 # ... Add other activities like financing, share repurchase, terminated deals etc. ...
            ],
            "footnotes": [
                 {"id": "ref1", "document": "TechInnovate Acquisition Press Release", "page": "1-3", "section": "Transaction Details", "date": "March 15, 2024"},
                 {"id": "ref2", "document": "Bloomberg Financial Data", "page": None, "section": "Stock Price Movement", "date": "March 15, 2024"},
                 {"id": "ref3", "document": "Legacy Components Divestiture Press Release", "page": "1-2", "section": "Transaction Overview", "date": "October 12, 2023"},
                 {"id": "ref4", "document": "Q4 2023 Earnings Call Transcript", "page": "6", "section": "CFO Financial Review", "date": "February 8, 2024"}
                 # ... Add other footnotes ...
            ]
        }
    },
# --- END: Section 11 Definition ---

# --- START: Section 12 Definition ---
    {
        "number": 12,
        "title": "Key Decision Makers",
        "specs": "Extract details on the Company's leadership structure (e.g., separate/combined Chair/CEO, Lead Independent Director). Specify the 'as of' date for the information.\n"
                 "Provide an overview of the Board of Directors composition (total members, number independent, average tenure).\n"
                 "Extract a list of senior executives (typically C-suite and key operational leaders).\n"
                 "For each executive, extract:\n"
                 "  - Name, position/title, appointment date, age.\n"
                 "  - Educational background (degree, institution, year).\n"
                 "  - Relevant prior experience (company, position, period).\n"
                 "  - Detailed compensation structure for the most recent reported year (base salary, bonus target/actual, long-term incentives with breakdown - e.g., PSUs, RSUs, options with vesting/exercise details), and total compensation.\n"
                 "  - Stock ownership details (shares owned, % outstanding, ownership requirement status).\n"
                 "  - Key direct reports, if available.\n"
                 "Extract a list of Board of Directors members.\n"
                 "For each board member, extract:\n"
                 "  - Name, position on board (e.g., Chairman, Lead Independent Director, Director), independence status (boolean or string), appointment date.\n"
                 "  - Age, primary current role/affiliation outside the Company (if applicable).\n"
                 "  - Relevant prior experience or background summary.\n"
                 "  - Committee memberships (listing committees and role - e.g., Chair, Member, Financial Expert).\n"
                 "  - Key skills or expertise contributed to the board.\n"
                 "  - Any disclosed relationships between board members or executives.\n"
                 "  - Board meeting attendance record (% for latest year).\n"
                 "  - Director compensation details for the most recent reported year (e.g., cash retainer, committee fees, equity grants).\n"
                 "  - Stock ownership details.\n"
                 "Extract details on Board Committees (name, members with roles, key responsibilities).\n"
                 "Identify any recent material leadership changes (departures, appointments) and their stated impact.\n"
                 "Describe the decision-making structure or key authorities delegated to management vs. board, if outlined.\n"
                 "All extracted data points requiring citation must have a corresponding source reference ID linking to a footnote.\n"
                 "Ensure all footnotes provide precise source details: document name (e.g., Proxy Statement, Annual Report), date/year, page number, and specific section/table.",
        "schema": {
            "leadership_overview": {
                "as_of_date": None, # string (e.g., "March 31, 2024")
                "as_of_date_source_ref_id": None,
                "board_composition": {
                    "total_members": None, # number
                    "total_members_source_ref_id": None,
                    "independent_members_count": None, # number
                    "independent_members_count_source_ref_id": None,
                    "average_tenure": None, # number (years)
                    "average_tenure_source_ref_id": None,
                    "unit": "years", # Assuming unit is years
                    "notes": None # Optional string (e.g., gender diversity stats if available)
                },
                "leadership_structure_description": None, # string (e.g., "Separate Chairman and CEO roles with independent Lead Director")
                "leadership_structure_description_source_ref_id": None
            },
            "executives": [ # List of key executive objects
                { # Structure for ONE executive
                    "name": None, "name_source_ref_id": None,
                    "position": None, "position_source_ref_id": None, # string (e.g., "Chief Executive Officer")
                    "appointed_date": None, "appointed_date_source_ref_id": None, # string (e.g., "March 2018")
                    "age": None, "age_source_ref_id": None, # Optional number
                    "education": [ # List of education details
                        {"degree": None, "institution": None, "year": None, "source_ref_id": None}
                    ],
                    "prior_experience": [ # List of prior roles
                        {"company": None, "position": None, "period": None, "source_ref_id": None}
                    ],
                    "compensation": { # Compensation details for a specific year
                        "year": None, # string (e.g., "FY 2023")
                        "year_source_ref_id": None,
                        "base_salary": {"value": None, "unit": "USD", "source_ref_id": None},
                        "annual_bonus": { # Optional bonus details
                             "target_percentage": None, "target_percentage_source_ref_id": None, # % of base
                             "actual_value": None, "actual_value_source_ref_id": None, # number (USD)
                             "percentage_of_target_achieved": None, "percentage_of_target_achieved_source_ref_id": None # Optional number (%)
                        },
                        "long_term_incentives": { # Optional LTI details
                            "total_grant_value": None, "total_grant_value_source_ref_id": None, # number (USD)
                            "breakdown": [ # List of LTI components
                                {
                                    "type": None, # string (e.g., "Performance Stock Units", "Restricted Stock Units", "Stock Options")
                                    "type_source_ref_id": None,
                                    "grant_date_value": None, # number (USD)
                                    "grant_date_value_source_ref_id": None,
                                    "vesting_details": None, # string describing vesting
                                    "vesting_details_source_ref_id": None,
                                    # Optional fields specific to options:
                                    "shares_granted": None, "shares_granted_source_ref_id": None,
                                    "exercise_price": None, "exercise_price_source_ref_id": None,
                                    "exercise_price_unit": "USD",
                                    "expiration": None, "expiration_source_ref_id": None # e.g., "10 years from grant"
                                }
                            ]
                        },
                        "other_compensation": {"value": None, "unit": "USD", "description": None, "source_ref_id": None}, # Optional for perks etc.
                        "total_compensation": {"value": None, "unit": "USD", "source_ref_id": None}
                    },
                    "stock_ownership": { # Optional ownership details
                        "as_of_date": None, "as_of_date_source_ref_id": None,
                        "shares_owned": None, "shares_owned_source_ref_id": None, # number
                        "percentage_of_outstanding": None, "percentage_of_outstanding_source_ref_id": None, # number (%)
                        "ownership_requirement": { # Optional guideline info
                            "multiple_of_salary": None, # number (e.g., 6)
                            "multiple_of_salary_source_ref_id": None,
                            "status": None, # string (e.g., "Exceeded", "Met", "Below Target")
                            "status_source_ref_id": None
                        },
                         "notes": None # Optional string (e.g., includes family trusts)
                    },
                    "direct_reports": [], # Optional list of strings (titles or names)
                    "direct_reports_source_ref_id": None,
                    "notes": None # Optional overall executive notes
                }
            ],
            "board_members": [ # List of board member objects
                { # Structure for ONE board member
                    "name": None, "name_source_ref_id": None,
                    "position": None, "position_source_ref_id": None, # e.g., "Chairman", "Director"
                    "independent_status": None, # boolean or string (e.g., True, "Independent", "Non-Independent")
                    "independent_status_source_ref_id": None,
                    "appointed_date": None, "appointed_date_source_ref_id": None, # string
                    "appointed_lead_director_date": None, "appointed_lead_director_date_source_ref_id": None, # Optional string
                    "appointed_chair_date": None, "appointed_chair_date_source_ref_id": None, # Optional string
                    "age": None, "age_source_ref_id": None, # Optional number
                    "primary_affiliation": { # Optional info on current role elsewhere
                        "company": None, "company_source_ref_id": None,
                        "position": None, "position_source_ref_id": None,
                        "since": None, "since_source_ref_id": None
                    },
                    "background_summary": None, "background_summary_source_ref_id": None, # string
                    "committee_memberships": [ # List of committee roles
                         {
                             "committee_name": None, # string (e.g., "Audit Committee")
                             "role": None, # string (e.g., "Chair", "Member", "Financial Expert")
                             "source_ref_id": None
                         }
                    ],
                    "skills_expertise": [], # Optional list of strings
                    "skills_expertise_source_ref_id": None,
                    "relationships": [], # Optional list of strings describing relationships
                    "relationships_source_ref_id": None,
                    "meetings_attended_percentage": None, # Optional number (%)
                    "meetings_attended_percentage_source_ref_id": None,
                    "meetings_attended_year": None, # Optional string (e.g., "FY 2023")
                    "meetings_attended_year_source_ref_id": None,
                    "compensation": { # Optional compensation details for the director
                        "year": None, "year_source_ref_id": None,
                        "cash_retainer": {"value": None, "unit": "USD", "source_ref_id": None},
                        "committee_fees": {"value": None, "unit": "USD", "description": None, "source_ref_id": None}, # Aggregate or list
                        "lead_director_fee": {"value": None, "unit": "USD", "source_ref_id": None}, # Optional
                        "chair_fee": {"value": None, "unit": "USD", "source_ref_id": None}, # Optional
                        "equity_grants": { # Optional equity info
                            "grant_date_value": None, "grant_date_value_source_ref_id": None,
                            "form": None, # string (e.g., "Restricted Stock Units")
                            "form_source_ref_id": None,
                            "vesting": None, # string
                            "vesting_source_ref_id": None
                         },
                        "total_compensation": {"value": None, "unit": "USD", "source_ref_id": None}
                    },
                     "stock_ownership": { # Optional ownership details (simpler than exec usually)
                        "as_of_date": None, "as_of_date_source_ref_id": None,
                        "shares_owned": None, "shares_owned_source_ref_id": None, # number
                        "notes": None 
                    },
                    "notes": None # Optional overall board member notes
                }
            ],
            "committees": [ # Optional list detailing committees
                 { # Structure for ONE committee
                     "name": None, # string (e.g., "Audit Committee")
                     "name_source_ref_id": None,
                     "members": [ # List of members and roles
                          {
                              "name": None, # string
                              "role": None, # string (e.g., "Chair", "Member")
                              "financial_expert": None, # Optional boolean
                              "source_ref_id": None
                          }
                     ],
                     "key_responsibilities": [], # List of strings
                     "key_responsibilities_source_ref_id": None,
                     "meetings_per_year": None, # Optional number or string
                     "meetings_per_year_source_ref_id": None,
                     "notes": None
                 }
            ],
            "recent_leadership_changes": [ # Optional list of changes
                 { # Structure for ONE change
                     "date": None, "date_source_ref_id": None,
                     "change_type": None, # string (e.g., "Appointment", "Departure", "Retirement")
                     "change_type_source_ref_id": None,
                     "person": {
                          "name": None, "name_source_ref_id": None,
                          "position": None, "position_source_ref_id": None # Position appointed to or departed from
                     },
                     "details": None, # string describing the change (e.g., replacing whom, reason)
                     "details_source_ref_id": None,
                     "stated_impact": None, # Optional string
                     "stated_impact_source_ref_id": None,
                     "notes": None
                 }
            ],
            "decision_making_structure": { # Optional section
                "description": None, # string summarizing structure
                "description_source_ref_id": None,
                "key_authorities": [ # List describing who approves what
                     {
                         "body": None, # string (e.g., "Board of Directors", "CEO")
                         "authority_areas": [], # List of strings
                         "source_ref_id": None
                     }
                ],
                 "notes": None
            },
            "footnotes": [ # Top-level list for all footnotes in this section
                { # Structure definition for ONE footnote
                    "id": None, "document": None, "page": None, "section": None, "date": None # Optional date
                }
            ]
        },
        "template": { # Example data aligned with refined schema
             "leadership_overview": {
                "as_of_date": "March 31, 2024", "as_of_date_source_ref_id": "ref1",
                "board_composition": {
                    "total_members": 11, "total_members_source_ref_id": "ref1",
                    "independent_members_count": 8, "independent_members_count_source_ref_id": "ref1",
                    "average_tenure": 6.3, "average_tenure_source_ref_id": "ref1",
                    "unit": "years", "notes": "36% gender/ethnic diversity."
                },
                "leadership_structure_description": "Separate Chairman (Founder) and CEO roles. Lead Independent Director appointed 2019.", "leadership_structure_description_source_ref_id": "ref1"
            },
            "executives": [
                 { # Example CEO
                    "name": "James W. Miller", "name_source_ref_id": "ref2",
                    "position": "Chief Executive Officer", "position_source_ref_id": "ref2",
                    "appointed_date": "March 2018", "appointed_date_source_ref_id": "ref2",
                    "age": 56, "age_source_ref_id": "ref2",
                    "education": [
                        {"degree": "MBA", "institution": "Harvard Business School", "year": 1996, "source_ref_id": "ref2"},
                        {"degree": "BS, Mechanical Engineering", "institution": "MIT", "year": 1990, "source_ref_id": "ref2"}
                    ],
                    "prior_experience": [
                        {"company": "Industrial Systems Inc.", "position": "COO", "period": "2014-2018", "source_ref_id": "ref2"},
                        {"company": "General Electric", "position": "Various leadership roles", "period": "1996-2010", "source_ref_id": "ref2"}
                    ],
                    "compensation": { 
                        "year": "FY 2023", "year_source_ref_id": "ref2",
                        "base_salary": {"value": 1250000, "unit": "USD", "source_ref_id": "ref2"},
                        "annual_bonus": { 
                             "target_percentage": 150, "target_percentage_source_ref_id": "ref2",
                             "actual_value": 1968750, "actual_value_source_ref_id": "ref2", 
                             "percentage_of_target_achieved": 105, "percentage_of_target_achieved_source_ref_id": "ref2"
                        },
                        "long_term_incentives": { 
                            "total_grant_value": 6500000, "total_grant_value_source_ref_id": "ref2",
                            "breakdown": [
                                {"type": "Performance Stock Units", "type_source_ref_id": "ref2", "grant_date_value": 3900000, "grant_date_value_source_ref_id": "ref2", "vesting_details": "3-year performance period (Rel. TSR & ROIC)", "vesting_details_source_ref_id": "ref2"},
                                {"type": "Restricted Stock Units", "type_source_ref_id": "ref2", "grant_date_value": 1300000, "grant_date_value_source_ref_id": "ref2", "vesting_details": "3-year ratable vesting", "vesting_details_source_ref_id": "ref2"},
                                {"type": "Stock Options", "type_source_ref_id": "ref2", "grant_date_value": 1300000, "grant_date_value_source_ref_id": "ref2", "vesting_details": "3-year ratable vesting", "vesting_details_source_ref_id": "ref2", "shares_granted": 92857, "shares_granted_source_ref_id": "ref2", "exercise_price": 56.00, "exercise_price_source_ref_id": "ref2", "expiration": "10 years from grant", "expiration_source_ref_id": "ref2"}
                            ]
                        },
                        "other_compensation": None,
                        "total_compensation": {"value": 9718750, "unit": "USD", "source_ref_id": "ref2"}
                    },
                    "stock_ownership": { 
                        "as_of_date": "December 31, 2023", "as_of_date_source_ref_id": "ref2",
                        "shares_owned": 2510000, "shares_owned_source_ref_id": "ref2",
                        "percentage_of_outstanding": 2.0, "percentage_of_outstanding_source_ref_id": "ref2",
                        "ownership_requirement": { "multiple_of_salary": 6, "multiple_of_salary_source_ref_id": "ref2", "status": "Exceeded", "status_source_ref_id": "ref2"},
                         "notes": "Includes shares held directly and in family trusts."
                    },
                    "direct_reports": ["CFO", "COO", "CTO", "EVP HR", "General Counsel"], "direct_reports_source_ref_id": "ref1", # Example source
                    "notes": None
                }
                 # ... Add other executives ...
            ],
            "board_members": [
                 { # Example Chairman
                    "name": "Thomas J. Roberts", "name_source_ref_id": "ref1",
                    "position": "Chairman of the Board", "position_source_ref_id": "ref1",
                    "independent_status": False, "independent_status_source_ref_id": "ref1",
                    "appointed_date": "1985", "appointed_date_source_ref_id": "ref1",
                    "appointed_chair_date": "2005", "appointed_chair_date_source_ref_id": "ref1",
                    "age": 72, "age_source_ref_id": "ref1",
                    "primary_affiliation": None, # Example: Primarily involved with the company
                    "background_summary": "Founder of the Company; previously CEO until 2018.", "background_summary_source_ref_id": "ref1",
                    "committee_memberships": [
                        {"committee_name": "Executive Committee", "role": "Chair", "source_ref_id": "ref1"}
                    ],
                    "skills_expertise": ["Industry Knowledge", "Strategy", "Leadership"], "skills_expertise_source_ref_id": "ref1",
                    "relationships": [{"description": "Father of Sarah Roberts-Chen (Director)", "source_ref_id": "ref1"}],
                    "meetings_attended_percentage": 100, "meetings_attended_percentage_source_ref_id": "ref1",
                    "meetings_attended_year": "FY 2023", "meetings_attended_year_source_ref_id": "ref1",
                    "compensation": { 
                        "year": "FY 2023", "year_source_ref_id": "ref2",
                        "cash_retainer": {"value": 150000, "unit": "USD", "source_ref_id": "ref2"},
                        "equity_grants": {"grant_date_value": 275000, "grant_date_value_source_ref_id": "ref2", "form": "RSUs", "form_source_ref_id": "ref2", "vesting": "1-year cliff", "vesting_source_ref_id": "ref2"},
                        "total_compensation": {"value": 425000, "unit": "USD", "source_ref_id": "ref2"}
                    },
                     "stock_ownership": { "as_of_date": "Dec 31, 2023", "as_of_date_source_ref_id": "ref2", "shares_owned": 18850000, "shares_owned_source_ref_id": "ref2", "notes": "Held via Roberts Family Holdings LLC"},
                    "notes": "Significant influence due to founder status and large shareholding."
                },
                 { # Example Lead Independent Director
                    "name": "Dr. Elena M. Rodriguez", "name_source_ref_id": "ref1",
                    "position": "Lead Independent Director", "position_source_ref_id": "ref1",
                    "independent_status": True, "independent_status_source_ref_id": "ref1",
                    "appointed_date": "2015", "appointed_date_source_ref_id": "ref1",
                    "appointed_lead_director_date": "2019", "appointed_lead_director_date_source_ref_id": "ref1",
                    "age": 62, "age_source_ref_id": "ref1",
                    "primary_affiliation": {"company": "TechSolutions, Inc.", "position": "CEO", "since": 2017, "source_ref_id": "ref1"},
                    "background_summary": "Former CTO at TechSolutions and EVP at Innovex Systems. Holds PhD in Electrical Engineering.", "background_summary_source_ref_id": "ref1",
                    "committee_memberships": [
                        {"committee_name": "Nominating & Governance", "role": "Chair", "source_ref_id": "ref1"},
                        {"committee_name": "Compensation Committee", "role": "Member", "source_ref_id": "ref1"}
                    ],
                    "skills_expertise": ["Technology Strategy", "Executive Leadership", "Risk Management"], "skills_expertise_source_ref_id": "ref1",
                    "relationships": [], "relationships_source_ref_id": None,
                    "meetings_attended_percentage": 100, "meetings_attended_percentage_source_ref_id": "ref1",
                    "meetings_attended_year": "FY 2023", "meetings_attended_year_source_ref_id": "ref1",
                    "compensation": { 
                        "year": "FY 2023", "year_source_ref_id": "ref2",
                        "cash_retainer": {"value": 120000, "unit": "USD", "source_ref_id": "ref2"},
                         "committee_fees": {"value": 20000, "unit": "USD", "description": "Chair fee", "source_ref_id": "ref2"}, 
                         "lead_director_fee": {"value": 30000, "unit": "USD", "source_ref_id": "ref2"},
                        "equity_grants": {"grant_date_value": 225000, "grant_date_value_source_ref_id": "ref2", "form": "RSUs", "form_source_ref_id": "ref2", "vesting": "1-year cliff", "vesting_source_ref_id": "ref2"},
                        "total_compensation": {"value": 395000, "unit": "USD", "source_ref_id": "ref2"}
                    },
                     "stock_ownership": {"as_of_date": "Dec 31, 2023", "as_of_date_source_ref_id": "ref2", "shares_owned": 45000, "shares_owned_source_ref_id": "ref2", "notes": None},
                    "notes": None
                }
                # ... Add other board members ...
            ],
             "committees": [
                 { 
                     "name": "Audit Committee", "name_source_ref_id": "ref1",
                     "members": [
                          {"name": "Richard Taylor", "role": "Chair", "financial_expert": True, "source_ref_id": "ref1"},
                          {"name": "Katherine Wong", "role": "Member", "financial_expert": True, "source_ref_id": "ref1"},
                          {"name": "Dr. David Johnson", "role": "Member", "financial_expert": False, "source_ref_id": "ref1"}
                     ],
                     "key_responsibilities": ["Oversight of financial reporting", "Oversight of independent auditors", "Internal audit function", "Risk management policies"], "key_responsibilities_source_ref_id": "ref1",
                     "meetings_per_year": 6, "meetings_per_year_source_ref_id": "ref1",
                     "notes": "All members are independent."
                 }
                  # ... Add other committees ...
            ],
            "recent_leadership_changes": [
                 { 
                     "date": "January 15, 2024", "date_source_ref_id": "ref3",
                     "change_type": "Appointment", "change_type_source_ref_id": "ref3",
                     "person": {"name": "Lisa Chen", "name_source_ref_id": "ref3", "position": "Chief Technology Officer", "position_source_ref_id": "ref3"},
                     "details": "Replaced Robert Thompson (retired). Previously SVP, Advanced Technology.", "details_source_ref_id": "ref3",
                     "stated_impact": "Signals increased focus on IoT and AI technologies.", "stated_impact_source_ref_id": "ref3",
                     "notes": None
                 }
                  # ... Add other changes ...
            ],
            "decision_making_structure": {
                "description": "Traditional corporate hierarchy led by CEO, with major strategic decisions requiring Board approval. Executive Committee oversees operational execution.", "description_source_ref_id": "ref6",
                "key_authorities": [ 
                     {"body": "Board of Directors", "authority_areas": ["Major M&A (>$50M)", "Annual Budgets", "Exec Appointments/Comp"], "source_ref_id": "ref6"},
                     {"body": "CEO", "authority_areas": ["Day-to-day operations", "Capex up to $10M", "Hiring below EVP"], "source_ref_id": "ref6"}
                ],
                 "notes": None
            },
            "footnotes": [
                {"id": "ref1", "document": "Annual Proxy Statement 2024", "page": "12-15", "section": "Corporate Governance"},
                {"id": "ref2", "document": "Annual Proxy Statement 2024", "page": "35-52", "section": "Executive and Director Compensation"},
                {"id": "ref3", "document": "Press Release: CTO Appointment", "page": "1-2", "section": "Full Announcement", "date": "Jan 15, 2024"},
                {"id": "ref4", "document": "Annual Proxy Statement 2024", "page": "27", "section": "Insider Holdings Table"}, # Assuming insider group total is here
                {"id": "ref5", "document": "Annual Proxy Statement 2024", "page": "45", "section": "Compensation Discussion & Analysis"}, # Example source for survey
                {"id": "ref6", "document": "Corporate Governance Guidelines", "page": "8-12", "section": "Decision Authority Matrix", "date": "Mar 2023"}
            ]
        }
    },
# --- END: Section 12 Definition ---

# --- START: Section 13 Definition ---
    {
        "number": 13,
        "title": "Strategic Objectives",
        "specs": "Extract details on the historical evolution of the Company's strategy, if described.\n"
                 "Identify and extract the 3 most important strategic objectives the Company is currently pursuing (forward-looking goals).\n"
                 "For each objective, extract:\n"
                 "  - Its title or clear description.\n"
                 "  - The stated timeframe or target horizon.\n"
                 "  - Key metrics or KPIs used to measure progress towards the objective, including current values and targets where available.\n"
                 "  - Any commentary provided on the competitive context for the objective.\n"
                 "Identify and extract the 3 most important strategies the Company is using *to achieve these objectives*, focusing on how existing assets or capabilities are leveraged.\n"
                 "For each strategy, extract:\n"
                 "  - Its title or clear description.\n"
                 "  - Which strategic objective(s) it supports.\n"
                 "  - The existing assets or capabilities being leveraged.\n"
                 "  - Details on resource allocation (e.g., investment amounts, team focus) if provided.\n"
                 "  - Any metrics tracking the implementation progress of the strategy itself.\n"
                 "Maintain a clear distinction between objectives (future goals) and strategies (current actions/leverage).\n"
                 "All extracted data points requiring citation must have a corresponding source reference ID linking to a footnote.\n"
                 "Ensure all footnotes provide precise source details: document name, date, page number, and specific section/table.",
        "schema": {
            "strategic_evolution": { # Optional section on historical shifts
                "description": None, # string summarizing evolution
                "description_source_ref_id": None,
                "historical_shifts": [ # List of past strategic periods/focuses
                    {
                        "period": None, # string (e.g., "2016-2019")
                        "period_source_ref_id": None,
                        "primary_focus": None, # string
                        "primary_focus_source_ref_id": None,
                        "key_initiatives": [], # List of strings
                        "key_initiatives_source_ref_id": None
                    }
                ],
                "notes": None
            },
            "strategic_objectives": [ # List of key objectives (aim for top 3)
                { # Structure for ONE objective
                    "priority": None, # Optional number (1, 2, 3) if ranked
                    "objective_title": None, # string
                    "objective_title_source_ref_id": None,
                    "description": None, # string explaining the goal
                    "description_source_ref_id": None,
                    "timeframe": { # Optional timeframe details
                        "start_year": None, # number or string
                        "start_year_source_ref_id": None,
                        "target_year": None, # number or string (e.g., 2025)
                        "target_year_source_ref_id": None,
                        "horizon_description": None, # Optional string (e.g., "Next 3 years")
                        "horizon_description_source_ref_id": None
                    },
                    "progress_metrics": [ # List of KPIs measuring progress
                        { # Structure for ONE metric
                            "name": None, # string (e.g., "Recurring Revenue Percentage")
                            "name_source_ref_id": None,
                            "current_status": { # Optional current value
                                "value": None, "value_source_ref_id": None,
                                "unit": None, "unit_source_ref_id": None,
                                "as_of": None, "as_of_source_ref_id": None
                            },
                            "target": { # Optional target value
                                "value": None, "value_source_ref_id": None, # Can be range string e.g. "40-45"
                                "unit": None, "unit_source_ref_id": None,
                                "by_year_or_period": None, "by_year_or_period_source_ref_id": None
                            },
                             "historical_tracking": [ # Optional list showing past progress
                                 {"period": None, "value": None, "unit": None, "source_ref_id": None}
                             ],
                             "notes": None
                        }
                    ],
                    "competitive_context": { # Optional context
                         "description": None, # string comparing to competitors or market
                         "description_source_ref_id": None,
                         "benchmarks": [ # Optional list of specific benchmark data
                              {
                                   "item_name": None, # e.g., "Industry Average", "Competitor A"
                                   "value": None,
                                   "unit": None,
                                   "source_ref_id": None
                              }
                         ]
                    },
                    "supporting_strategies": [ # List of strategy titles linked to this objective
                        # Populated based on the strategies defined below
                    ],
                    "notes": None # Optional overall objective notes
                }
            ],
            "key_strategies": [ # List of key strategies (aim for top 3)
                { # Structure for ONE strategy
                     "strategy_title": None, # string
                     "strategy_title_source_ref_id": None,
                     "description": None, # string explaining the strategy
                     "description_source_ref_id": None,
                     "linked_objectives": [], # List of objective titles this strategy supports
                     "capabilities_leveraged": [ # List of existing assets/capabilities used
                          {
                               "capability": None, # string (e.g., "Large installed base", "Global service network")
                               "capability_source_ref_id": None
                          }
                     ],
                     "resource_allocation": { # Optional resource details
                          "investment_description": None, # string (e.g., "Sales team expansion", "R&D funding")
                          "investment_description_source_ref_id": None,
                          "value": None, # number
                          "value_source_ref_id": None,
                          "unit": None, # string (e.g., "million USD annually")
                          "unit_source_ref_id": None,
                          "timeframe": None, # Optional string
                          "timeframe_source_ref_id": None,
                          "notes": None
                     },
                     "implementation_progress": { # Optional progress tracking
                           "metric_name": None, # string (e.g., "Subscription Conversion Rate")
                           "metric_name_source_ref_id": None,
                           "current_value": None, "current_value_source_ref_id": None,
                           "unit": None, "unit_source_ref_id": None,
                           "target_value": None, "target_value_source_ref_id": None,
                           "as_of": None, "as_of_source_ref_id": None,
                           "notes": None
                     },
                     "notes": None # Optional overall strategy notes
                }
            ],
            "footnotes": [ # Top-level list for all footnotes in this section
                { # Structure definition for ONE footnote
                    "id": None, "document": None, "page": None, "section": None, "date": None 
                }
            ]
        },
        "template": { # Example data aligned with refined schema
            "strategic_evolution": {
                "description": "Company strategy shifted from hardware focus (pre-2019) towards integrated solutions and recurring revenue (2022-Present).", "description_source_ref_id": "ref1",
                "historical_shifts": [
                    {"period": "2019-2021", "period_source_ref_id": "ref1", "primary_focus": "Digital transformation initiation", "primary_focus_source_ref_id": "ref1", "key_initiatives": ["IoT capability development", "Cloud platform build-out"], "key_initiatives_source_ref_id": "ref1"}
                ],
                "notes": "Evolution driven by market trends and competitive pressures."
            },
            "strategic_objectives": [
                { 
                    "priority": 1,
                    "objective_title": "Increase recurring revenue share", "objective_title_source_ref_id": "ref2",
                    "description": "Transition from primarily hardware sales to subscription/service models to reach 40% recurring revenue.", "description_source_ref_id": "ref2",
                    "timeframe": {"start_year": 2022, "start_year_source_ref_id": "ref2", "target_year": 2025, "target_year_source_ref_id": "ref2"},
                    "progress_metrics": [
                        {
                            "name": "Recurring Revenue % of Total", "name_source_ref_id": "ref2",
                            "current_status": {"value": 28, "unit": "%", "as_of": "Q1 2024", "source_ref_id": "ref3"},
                            "target": {"value": 40, "unit": "%", "by_year_or_period": 2025, "source_ref_id": "ref2"},
                            "historical_tracking": [ {"period": "FY2022", "value": 22, "unit": "%", "source_ref_id": "ref4"}, {"period": "FY2023", "value": 26, "unit": "%", "source_ref_id": "ref4"} ],
                            "notes": "Slight deceleration in Q1 2024."
                        },
                        {
                            "name": "Annual Recurring Revenue (ARR)", "name_source_ref_id": "ref2",
                            "current_status": {"value": 1280, "unit": "million USD", "as_of": "Q1 2024", "source_ref_id": "ref3"},
                            "target": {"value": 2000, "unit": "million USD", "by_year_or_period": 2025, "source_ref_id": "ref2"},
                            "historical_tracking": [],
                            "notes": None
                        }
                    ],
                    "competitive_context": {
                         "description": "Target aligns with top-tier competitors like Competitor A (currently at 35%). Industry average is ~22%.", "description_source_ref_id": "ref5",
                         "benchmarks": [ {"item_name": "Competitor A RR%", "value": 35, "unit": "%", "source_ref_id": "ref5"} ]
                    },
                    "supporting_strategies": ["Leverage existing customer base for subscription conversions", "Enhance software platform with industry-specific solutions"], # Titles from strategies below
                    "notes": "Highest priority objective per investor day."
                },
                 { 
                    "priority": 2,
                    "objective_title": "Expand Asia-Pacific Market Share", "objective_title_source_ref_id": "ref2",
                    "description": "Grow market share in high-growth APAC region from 18% to 25%.", "description_source_ref_id": "ref2",
                    "timeframe": {"target_year": 2026, "target_year_source_ref_id": "ref2"},
                    "progress_metrics": [
                         {
                            "name": "APAC Market Share", "name_source_ref_id": "ref3",
                            "current_status": {"value": 18, "unit": "%", "as_of": "Q1 2024", "source_ref_id": "ref3"},
                            "target": {"value": 25, "unit": "%", "by_year_or_period": 2026, "source_ref_id": "ref2"},
                            "historical_tracking": [{"period": "FY2022", "value": 16.5, "unit":"%", "source_ref_id": "ref4"}],
                            "notes": None
                         }
                    ],
                     "competitive_context": {"description": "APAC market growing at 12.5% annually. Regional competitors have strong local presence.", "description_source_ref_id": "ref5"},
                    "supporting_strategies": ["Leverage Singapore manufacturing hub for localized production", "Strengthen strategic partnerships with local system integrators"],
                    "notes": None
                }
                 # ... Add objective 3 ...
            ],
            "key_strategies": [
                 { # Example strategy 1
                     "strategy_title": "Leverage existing customer base for subscription conversions", "strategy_title_source_ref_id": "ref2",
                     "description": "Utilize large installed hardware base to cross-sell connected services and software subscriptions.", "description_source_ref_id": "ref2",
                     "linked_objectives": ["Increase recurring revenue share"],
                     "capabilities_leveraged": [
                          {"capability": "Installed base > 120k units", "capability_source_ref_id": "ref6"},
                          {"capability": "Global service network (1500+ technicians)", "capability_source_ref_id": "ref6"}
                     ],
                     "resource_allocation": { 
                          "investment_description": "Dedicated solutions sales team expansion & software dev.", "investment_description_source_ref_id": "ref6",
                          "value": 60, "value_source_ref_id": "ref6", "unit": "million USD annually", "unit_source_ref_id": "ref6",
                          "notes": "$25M Sales, $35M R&D"
                     },
                     "implementation_progress": { 
                           "metric_name": "Subscription Conversion Rate (Eligible Base)", "metric_name_source_ref_id": "ref3",
                           "current_value": 18, "current_value_source_ref_id": "ref3", "unit": "%", "unit_source_ref_id": "ref3",
                           "target_value": 30, "target_value_source_ref_id": "ref2", "as_of": "Q1 2024", "as_of_source_ref_id": "ref3",
                           "notes": None
                     },
                     "notes": None
                 },
                 { # Example strategy 2
                     "strategy_title": "Enhance software platform with industry-specific solutions", "strategy_title_source_ref_id": "ref2",
                     "description": "Develop vertical software modules addressing unique customer challenges.", "description_source_ref_id": "ref2",
                     "linked_objectives": ["Increase recurring revenue share"],
                     "capabilities_leveraged": [
                          {"capability": "Deep industry expertise (35+ years)", "capability_source_ref_id": "ref6"},
                          {"capability": "Domain-specific software engineers (300+)", "capability_source_ref_id": "ref6"}
                     ],
                     "resource_allocation": {
                         "investment_description": "Vertical solution R&D teams & targeted acquisitions", "investment_description_source_ref_id": "ref6",
                         "value": 45, "value_source_ref_id": "ref6", "unit": "million USD R&D annually + $200M M&A budget", "unit_source_ref_id": "ref6",
                         "timeframe": "2022-2025 (M&A)", "timeframe_source_ref_id": "ref6",
                         "notes": None
                     },
                      "implementation_progress": {
                           "metric_name": "Vertical Solutions Launched", "metric_name_source_ref_id": "ref3",
                           "current_value": 7, "current_value_source_ref_id": "ref3", "unit": "modules", "unit_source_ref_id": "ref3",
                           "target_value": 12, "target_value_source_ref_id": "ref2", "as_of": "Q1 2024", "as_of_source_ref_id": "ref3",
                            "notes": None
                      },
                     "notes": None
                 }
                  # ... Add strategy 3 ...
            ],
            "footnotes": [
                 {"id": "ref1", "document": "Strategic Review Presentation", "page": "5-8", "section": "Strategic Evolution", "date": "Nov 10, 2022"},
                 {"id": "ref2", "document": "Three-Year Strategic Plan", "page": "12-28", "section": "Strategic Priorities", "date": "Nov 10, 2022"},
                 {"id": "ref3", "document": "Q1 2024 Quarterly Report", "page": "8-15", "section": "Strategic Initiatives Progress", "date": "Apr 25, 2024"},
                 {"id": "ref4", "document": "Annual Report 2023", "page": "24-32", "section": "Strategy Implementation", "date": "Feb 15, 2024"},
                 {"id": "ref5", "document": "Industry Market Analysis Report", "page": "45-52", "section": "Competitive Landscape", "date": "Jan 2024"},
                 {"id": "ref6", "document": "Capital Allocation & Investment Plan", "page": "18-24", "section": "Strategic Initiative Funding", "date": "Dec 12, 2023"}
            ]
        }
    },
# --- END: Section 13 Definition ---

# --- START: Section 14 Definition ---
    {
        "number": 14,
        "title": "Strategic Constraints",
        "specs": "Extract an overview description of the main strategic constraints facing the Company.\n"
                 "Identify and extract details on the 3 most important constraints that significantly hinder the Company's ability to achieve its strategic objectives (defined in Section 13).\n"
                 "For each constraint, extract:\n"
                 "  - Its name/title and category (e.g., Human Capital, Operations, Technology, Market, Regulatory).\n"
                 "  - A clear description of the constraint and its root causes.\n"
                 "  - Which specific strategic objective(s) it primarily affects and a description of that impact.\n"
                 "  - Quantitative data demonstrating the impact of the constraint (e.g., talent gap numbers, capacity shortfalls, delayed timelines, estimated financial impact), specifying 'as of' dates.\n"
                 "  - Information on the historical evolution of the constraint, if available.\n"
                 "  - Competitive benchmarking data showing how the Company fares relative to competitors facing similar constraints.\n"
                 "  - Details on current and planned mitigation efforts undertaken by the Company, including an assessment of their likely effectiveness.\n"
                 "Identify and describe any significant emerging constraints that may become material in the near future (next 1-2 years), including potential impact and early indicators.\n"
                 "All extracted data points requiring citation must have a corresponding source reference ID linking to a footnote.\n"
                 "Ensure all footnotes provide precise source details: document name, date, page number, and specific section/table (often Risk Factors, MD&A).",
        "schema": {
            "constraints_overview": { # Optional overview
                "description": None, # string summarizing key constraints
                "description_source_ref_id": None
            },
            "primary_constraints": [ # List of top 3 constraints
                { # Structure for ONE primary constraint
                    "priority": None, # Optional number (1, 2, 3)
                    "name": None, # string (e.g., "Technical Talent Acquisition and Retention")
                    "name_source_ref_id": None,
                    "category": None, # string (e.g., "Human Capital", "Operations", "Technology")
                    "category_source_ref_id": None,
                    "description": None, # string explaining the constraint
                    "description_source_ref_id": None,
                    "root_causes": [ # Optional list of root causes
                        {
                             "cause": None, # string
                             "explanation": None, # string
                             "source_ref_id": None
                        }
                    ],
                    "affected_objectives": [ # List of objectives impacted
                        {
                            "objective_title": None, # string (matching title from Section 13)
                            "impact_description": None, # string explaining how it's impacted
                            "source_ref_id": None
                        }
                    ],
                    "quantified_impact": { # Optional quantified impact details
                        "metrics": [ # List of metrics demonstrating impact
                            {
                                 "metric_name": None, # string (e.g., "Talent Gap", "Lead Time Impact")
                                 "value": None, # number or string
                                 "unit": None, # string (e.g., "engineers", "%", "weeks")
                                 "comparison_point": None, # Optional string (e.g., "vs Target", "vs Competitor Avg")
                                 "as_of": None, # string
                                 "source_ref_id": None
                            }
                        ],
                        "financial_impact_estimate": { # Optional estimated financial cost
                            "description": None, # string (e.g., "Estimated annual lost revenue opportunity")
                            "low_value": None, # number
                            "high_value": None, # number
                            "unit": None, # string (e.g., "million USD annually")
                            "as_of": None, # string
                            "source_ref_id": None
                        },
                         "notes": None
                    },
                    "historical_evolution": { # Optional historical context
                        "description": None, # string
                        "description_source_ref_id": None,
                        "trend_metrics": [ # Optional list showing trend over time
                            {
                                "name": None, # string (e.g., "Avg Time to Fill Technical Positions")
                                "values": [ {"period": None, "value": None, "unit": None, "source_ref_id": None} ]
                            }
                        ]
                    },
                    "competitive_comparison": { # Optional benchmarking
                        "description": None, # string summarizing comparison
                        "description_source_ref_id": None,
                         "benchmarks": [ # List of benchmark data points
                             {
                                 "competitor_name": None, # string
                                 "metric_name": None, # string
                                 "company_value": None,
                                 "competitor_value": None,
                                 "unit": None,
                                 "notes": None, # e.g., Explaining competitor advantage/disadvantage
                                 "source_ref_id": None
                             }
                         ]
                    },
                    "mitigation_efforts": { # Company's response
                        "current_initiatives": [ # List of ongoing actions
                            {
                                "name": None, # string (e.g., "Enhanced Compensation Package")
                                "description": None, # string
                                "implementation_date": None, # string
                                "status_or_impact": None, # string describing progress/effect
                                "source_ref_id": None
                            }
                        ],
                        "planned_initiatives": [ # List of future actions
                             {
                                "name": None, # string
                                "description": None, # string
                                "timeline": None, # string
                                "expected_impact": None, # string
                                "budget_allocation": None, # Optional string or object
                                "source_ref_id": None
                            }
                        ],
                        "overall_effectiveness_assessment": None, # string evaluating mitigation success
                        "overall_effectiveness_assessment_source_ref_id": None
                    },
                    "notes": None # Optional overall constraint notes
                }
            ],
            "emerging_constraints": [ # Optional list of potential future constraints
                { # Structure for ONE emerging constraint
                    "name": None, "name_source_ref_id": None,
                    "description": None, "description_source_ref_id": None,
                    "potential_impact": {
                         "affected_objectives": [], # List of strings (objective titles)
                         "business_implications": None, # string
                         "earliest_impact_estimate": None, # string (e.g., "2025-2026")
                         "source_ref_id": None
                    },
                    "early_indicators": {
                        "description": None, # string describing early signs
                        "metrics": [], # Optional list of metrics
                        "source_ref_id": None
                    },
                     "monitoring_approach": { # Optional
                          "description": None, # string
                          "source_ref_id": None
                     },
                     "preliminary_mitigation_planning": { # Optional
                          "description": None, # string
                          "source_ref_id": None
                     },
                    "notes": None
                }
            ],
            "footnotes": [ # Top-level list for all footnotes in this section
                { # Structure definition for ONE footnote
                    "id": None, "document": None, "page": None, "section": None, "date": None 
                }
            ]
        },
        "template": { # Example data aligned with refined schema
            "constraints_overview": {
                "description": "The Company faces several strategic constraints potentially limiting achievement of objectives, primarily related to talent acquisition, regional manufacturing capacity, and legacy system integration.", "description_source_ref_id": "ref1"
            },
            "primary_constraints": [
                { # Example Constraint 1: Talent
                    "priority": 1,
                    "name": "Technical Talent Acquisition and Retention", "name_source_ref_id": "ref1",
                    "category": "Human Capital", "category_source_ref_id": "ref1",
                    "description": "Severe shortage of qualified software/AI engineers impedes digital transformation and recurring revenue goals.", "description_source_ref_id": "ref1",
                    "root_causes": [
                        {"cause": "Late strategic pivot to software", "explanation": "Significant investment began 2018, lagging key competitors.", "source_ref_id": "ref2"},
                        {"cause": "Competition for Talent", "explanation": "Intense global competition for software/AI expertise.", "source_ref_id": "ref2"}
                    ],
                    "affected_objectives": [
                        {"objective_title": "Increase recurring revenue share", "impact_description": "Software development velocity limited, delaying new service launches.", "source_ref_id": "ref2"}
                    ],
                    "quantified_impact": {
                        "metrics": [
                            {"metric_name": "Talent Gap (Software Engineers)", "value": 200, "unit": "engineers (40% shortfall)", "comparison_point": "vs Target Headcount 500", "as_of": "Q1 2024", "source_ref_id": "ref3"},
                            {"metric_name": "Product Dev Cycle Time (Connected Products)", "value": 18, "unit": "months", "comparison_point": "vs Competitor Avg 12 months", "as_of": "Q1 2024", "source_ref_id": "ref3"}
                        ],
                        "financial_impact_estimate": {"description": "Estimated delay in recurring revenue growth", "low_value": 60, "high_value": 85, "unit": "million USD annually", "as_of": "FY2023 Estimate", "source_ref_id": "ref2"},
                        "notes": None
                    },
                    "historical_evolution": {
                        "description": "Constraint intensified significantly over past 24 months.", "description_source_ref_id": "ref4",
                        "trend_metrics": [
                             {"name": "Avg Time to Fill Technical Positions", "values": [ {"period": "2022", "value": 95, "unit": "days", "source_ref_id": "ref4"}, {"period": "2023", "value": 110, "unit": "days", "source_ref_id": "ref4"}]},
                             {"name": "Technical Talent Attrition Rate", "values": [ {"period": "2022", "value": 18, "unit": "%", "source_ref_id": "ref4"}, {"period": "2023", "value": 16, "unit": "%", "source_ref_id": "ref4"}]}
                        ]
                    },
                    "competitive_comparison": {
                         "description": "Company vacancy rate (18%) higher than industry (15%) and leader Competitor A (12%).", "description_source_ref_id": "ref5",
                         "benchmarks": [{"competitor_name": "Competitor A", "metric_name": "Vacancy Rate", "company_value": 18, "competitor_value": 12, "unit": "%", "notes": "Competitor A benefits from early university partnerships.", "source_ref_id": "ref5"}]
                    },
                    "mitigation_efforts": {
                        "current_initiatives": [
                            {"name": "Enhanced Comp Package", "description": "+15-20% salary bands, equity awards.", "implementation_date": "Jan 2023", "status_or_impact": "Attrition reduced slightly (18%->16%).", "source_ref_id": "ref6"},
                            {"name": "Global Talent Hubs", "description": "New centers in Bangalore/Warsaw.", "implementation_date": "2023-2024", "status_or_impact": "45 hires in Bangalore, Warsaw opening Q2 2024.", "source_ref_id": "ref6"}
                        ],
                        "planned_initiatives": [
                             {"name": "Acqui-hiring Strategy", "description": "Acquire 2-3 small software firms for talent.", "timeline": "2024-2025", "expected_impact": "+75-100 engineers", "budget_allocation": "$100M allocated", "source_ref_id": "ref6"}
                        ],
                        "overall_effectiveness_assessment": "Mitigation narrowing but not closing gap; constraint likely remains through 2025.", "overall_effectiveness_assessment_source_ref_id": "ref6"
                    },
                    "notes": None
                },
                { # Example Constraint 2: Capacity
                    "priority": 2,
                    "name": "Manufacturing Capacity Limitations in Asia-Pacific", "name_source_ref_id": "ref1",
                    "category": "Operations", "category_source_ref_id": "ref1",
                    "description": "Insufficient local capacity limits ability to meet regional demand and market share targets.", "description_source_ref_id": "ref1",
                    "root_causes": [{"cause": "Historical focus on Western markets", "explanation": "Limited early investment in Asia.", "source_ref_id": "ref7"}],
                    "affected_objectives": [ {"objective_title": "Expand Asia-Pacific Market Share", "impact_description": "Extended lead times and higher logistics costs reduce competitiveness.", "source_ref_id": "ref2"} ],
                    "quantified_impact": {
                        "metrics": [{"metric_name": "Capacity Gap", "value": 7000, "unit": "units annually", "comparison_point": "vs Projected Demand", "as_of": "Q1 2024", "source_ref_id": "ref7"}],
                        "financial_impact_estimate": {"description": "Estimated annual lost revenue opportunity", "low_value": 180, "high_value": None, "unit": "million USD", "as_of": "FY 2023", "source_ref_id": "ref2"},
                        "notes": None
                    },
                    "historical_evolution": None,
                    "competitive_comparison": {
                         "description": "Competitor X has 7 regional facilities vs. Company's 1 (+ expansion).", "description_source_ref_id": "ref5",
                         "benchmarks": [{"competitor_name": "Regional Competitor X", "metric_name": "Local Production %", "company_value": 35, "competitor_value": 85, "unit": "%", "source_ref_id": "ref7"}] # Example metric
                    },
                    "mitigation_efforts": {
                        "current_initiatives": [
                             {"name": "Singapore Facility Expansion", "description": "150k sq ft expansion.", "implementation_date": "2023-2025", "status_or_impact": "45% complete (Q1 2024), expected +65% capacity.", "source_ref_id": "ref7"}
                        ],
                        "planned_initiatives": [
                             {"name": "Contract Manufacturing Network", "description": "Partnerships in Vietnam/Malaysia.", "timeline": "H2 2024 Start", "expected_impact": "+5000 units/year capacity.", "budget_allocation": None, "source_ref_id": "ref7"}
                        ],
                        "overall_effectiveness_assessment": "Will largely address constraint by late 2025, but short-term impact remains.", "overall_effectiveness_assessment_source_ref_id": "ref7"
                    },
                    "notes": None
                }
                # ... Add constraint 3 ...
            ],
             "emerging_constraints": [
                 {
                    "name": "Increasing Regulatory Complexity (Energy/Cyber)", "name_source_ref_id": "ref9",
                    "description": "Diverging global regulations increase compliance costs and time-to-market.", "description_source_ref_id": "ref9",
                    "potential_impact": {
                         "affected_objectives": ["Achieve industry leadership in sustainable manufacturing solutions", "Increase recurring revenue share"],
                         "business_implications": "Requires market-specific variations, higher R&D allocation to compliance.", "earliest_impact_estimate": "2025-2026", "source_ref_id": "ref9"
                    },
                    "early_indicators": {"description": "EU Cyber Resilience Act (2024-25), China Environmental Standards (2025).", "metrics": [], "source_ref_id": "ref9"},
                    "monitoring_approach": {"description": "Cross-functional regulatory monitoring team established.", "source_ref_id": "ref9"},
                    "preliminary_mitigation_planning": {"description": "Modular product architecture development underway.", "source_ref_id": "ref9"},
                    "notes": None
                 }
                  # ... Add other emerging constraints ...
            ],
            "footnotes": [
                {"id": "ref1", "document": "Risk Management Assessment", "page": "12-18", "section": "Strategic Constraint Analysis", "date": "Feb 2024"},
                {"id": "ref2", "document": "Three-Year Strategic Plan", "page": "30-32", "section": "Implementation Challenges", "date": "Nov 10, 2022"},
                {"id": "ref3", "document": "Q1 2024 Quarterly Report", "page": "15-16", "section": "Operational Challenges", "date": "Apr 25, 2024"},
                {"id": "ref4", "document": "HR Talent Assessment", "page": "8-12", "section": "Technical Talent Gap Analysis", "date": "Jan 2024"},
                {"id": "ref5", "document": "Industry Competitive Analysis", "page": "22-28", "section": "Comparative Operational Capabilities", "date": "Mar 2024"},
                {"id": "ref6", "document": "Talent Strategy Presentation", "page": "5-14", "section": "Technical Talent Initiatives", "date": "Mar 15, 2024"},
                {"id": "ref7", "document": "APAC Mfg Capacity Analysis", "page": "3-8", "section": "Capacity Gap Assessment", "date": "Feb 5, 2024"},
                #{"id": "ref8", ... } # (Example only, need real refs for other data points if used)
                {"id": "ref9", "document": "Emerging Risk Assessment", "page": "10-18", "section": "Potential Future Constraints", "date": "Jan 15, 2024"}
            ]
        }
    },
# --- END: Section 14 Definition ---

# --- START: Section 15 Definition ---
    {
        "number": 15,
        "title": "Strengths",
        "specs": "Extract an overview description summarizing the Company's core competitive strengths.\n"
                 "Identify and extract details on the 3 most relevant strengths that currently enable the Company to compete effectively. Focus on existing strengths, not future plans.\n"
                 "Prioritize strengths based on their impact on the Company's ability to compete and generate economic value.\n"
                 "For each strength, extract:\n"
                 "  - Its name/title and category (e.g., Technology/IP, Operations, Customer Relationships, Brand, Expertise).\n"
                 "  - A clear description of the strength.\n"
                 "  - Details on how the strength was developed (e.g., R&D investment, acquisitions, long-term focus, key hires), including timelines or investment values if available.\n"
                 "  - Quantitative data and metrics that substantiate the strength and its magnitude (e.g., patent counts, performance metrics vs competitors, cost advantages, market share in segments where strength applies).\n"
                 "  - Competitive benchmarking data comparing the strength to key competitors or industry averages.\n"
                 "  - A description of the specific competitive advantage(s) derived from this strength and how they translate to business performance (e.g., pricing power, higher win rates, customer loyalty, lower costs).\n"
                 "  - Examples of how the Company is currently leveraging this strength in its operations or strategy.\n"
                 "Identify and briefly describe any significant emerging strengths if they are close to becoming competitively relevant.\n"
                 "Ensure the analysis focuses on the Company's strengths relative to competitors, not just positive market trends.\n"
                 "All extracted data points requiring citation must have a corresponding source reference ID linking to a footnote.\n"
                 "Ensure all footnotes provide precise source details: document name, date, page number, and specific section/table.",
        "schema": {
            "strengths_overview": { # Optional overview
                "description": None, # string summarizing core strengths
                "description_source_ref_id": None
            },
            "primary_strengths": [ # List of top 3 strengths
                { # Structure for ONE primary strength
                    "priority": None, # Optional number (1, 2, 3)
                    "name": None, # string (e.g., "Proprietary Energy Optimization Technology")
                    "name_source_ref_id": None,
                    "category": None, # string (e.g., "Technology/Intellectual Property", "Operations")
                    "category_source_ref_id": None,
                    "description": None, # string explaining the strength
                    "description_source_ref_id": None,
                    "development_history": { # Optional details on how it was built
                        "summary": None, # Optional string summary
                        "summary_source_ref_id": None,
                        "timeline": { # Optional timeline object
                            "inception_year": None, "inception_year_source_ref_id": None,
                            "key_milestone_year": None, "key_milestone_year_source_ref_id": None,
                            "milestone_description": None, "milestone_description_source_ref_id": None,
                            "current_state": None, "current_state_source_ref_id": None
                        },
                        "investment": { # Optional investment object
                            "value": None, "value_source_ref_id": None,
                            "unit": None, "unit_source_ref_id": None,
                            "period": None, "period_source_ref_id": None
                        },
                        "key_events": [ # Optional list of key development events
                             {"year": None, "event_description": None, "source_ref_id": None}
                        ],
                        "notes": None
                    },
                    "quantification_and_evidence": { # Data substantiating the strength
                        "key_metrics": [ # List of metrics
                             {
                                 "metric_name": None, # string (e.g., "Patent Portfolio Size", "Avg Customer Energy Cost Reduction")
                                 "value": None, # number or string
                                 "unit": None, # string
                                 "comparison_point": None, # Optional string (e.g., "vs Competitor A", "vs Industry Avg")
                                 "comparison_value": None, # Optional number/string
                                 "advantage_description": None, # Optional string quantifying advantage (e.g., "4.2 ppts better")
                                 "as_of": None, # string
                                 "source_ref_id": None
                             }
                        ],
                        "third_party_validation": { # Optional validation
                             "source_name": None, # string (e.g., "Industry Efficiency Institute")
                             "ranking_or_finding": None, # string
                             "date_or_period": None, # string
                             "source_ref_id": None
                        },
                        "notes": None
                    },
                    "competitive_advantage_analysis": { # Explaining the impact
                        "summary": None, # Optional string summarizing the advantage
                        "summary_source_ref_id": None,
                        "advantages_list": [ # List of specific advantages
                            {
                                "advantage": None, # string (e.g., "Superior cost reduction creates compelling ROI")
                                "impact": None, # string quantifying business impact (e.g., "18% higher win rate...")
                                "source_ref_id": None
                            }
                        ],
                        "relevant_customer_segments": [ # Optional segments where advantage is key
                             {
                                 "segment_name": None, # string
                                 "advantage_manifestation": None, # string describing impact in segment
                                 "supporting_metric": None, # Optional string (e.g., "Market Share: 42%")
                                 "source_ref_id": None
                             }
                        ],
                        "notes": None
                    },
                    "current_leverage": { # How the company uses the strength now
                         "summary": None, # Optional summary string
                         "summary_source_ref_id": None,
                         "specific_applications": [ # List of applications
                              {
                                   "application_name": None, # string (e.g., "Premium tier products", "Consulting Services")
                                   "revenue_contribution": { # Optional financial link
                                        "value": None, "unit": None, "as_of": None, "source_ref_id": None
                                   },
                                   "growth_rate": { # Optional growth link
                                        "value": None, "unit": "%", "period": None, "source_ref_id": None
                                   },
                                   "notes": None
                              }
                         ],
                         "strategic_importance": None, # string linking strength to strategic objectives
                         "strategic_importance_source_ref_id": None,
                         "notes": None
                    },
                    "notes": None # Optional overall strength notes
                }
            ],
            "emerging_strengths": [ # Optional list of developing strengths
                { # Structure for ONE emerging strength
                    "name": None, "name_source_ref_id": None,
                    "category": None, "category_source_ref_id": None,
                    "description": None, "description_source_ref_id": None,
                    "development_stage": {
                        "description": None, # e.g., "Late-stage development", "Pilot phase"
                        "expected_commercial_launch": None, # string
                        "source_ref_id": None
                    },
                    "potential_impact": {
                         "description": None, # string describing potential advantage
                         "earliest_material_impact": None, # string (e.g., "2025")
                         "source_ref_id": None
                    },
                    "notes": None
                }
            ],
            "footnotes": [ # Top-level list for all footnotes in this section
                { # Structure definition for ONE footnote
                    "id": None, "document": None, "page": None, "section": None, "date": None 
                }
            ]
        },
        "template": { # Example data aligned with refined schema
            "strengths_overview": {
                "description": "The Company possesses distinctive strengths in proprietary energy optimization technology, global manufacturing scale allowing regional customization, and deep expertise in integrating modern systems with legacy infrastructure.", "description_source_ref_id": "ref1"
            },
            "primary_strengths": [
                { # Example Strength 1: Technology
                    "priority": 1,
                    "name": "Proprietary Energy Optimization Technology", "name_source_ref_id": "ref1",
                    "category": "Technology/Intellectual Property", "category_source_ref_id": "ref1",
                    "description": "Portfolio of 28 patented algorithms/designs delivering superior energy efficiency (15-20% > competitors).", "description_source_ref_id": "ref2",
                    "development_history": {
                        "summary": "Developed over ~10 years with significant R&D investment and targeted acquisition.", "summary_source_ref_id": "ref2",
                        "timeline": {"inception_year": 2014, "key_milestone_year": 2017, "milestone_description": "ML algorithm breakthrough", "current_state": "4th gen platform", "source_ref_id": "ref2"},
                        "investment": {"value": 215, "unit": "million USD", "period": "2014-2023", "source_ref_id": "ref2"},
                        "key_events": [ {"year": 2016, "event_description": "Acquired EnergyTech Inc. ($45M)", "source_ref_id": "ref2"} ],
                        "notes": None
                    },
                    "quantification_and_evidence": {
                        "key_metrics": [
                             {"metric_name": "Avg Customer Energy Cost Reduction", "value": 18.5, "unit": "%", "comparison_point": "vs Industry Avg", "comparison_value": "12.3%", "advantage_description": "6.2 ppts better", "as_of": "Q1 2024", "source_ref_id": "ref3"},
                             {"metric_name": "Customer ROI Timeline", "value": 14.7, "unit": "months", "comparison_point": "vs Industry Avg", "comparison_value": "22.5 months", "advantage_description": "7.8 months faster", "as_of": "Q1 2024", "source_ref_id": "ref3"}
                        ],
                        "third_party_validation": {"source_name": "Industrial Efficiency Institute", "ranking_or_finding": "Highest rated energy mgmt solution (2023)", "date_or_period": "2023", "source_ref_id": "ref4"},
                        "notes": None
                    },
                    "competitive_advantage_analysis": {
                        "summary": "Technology provides compelling ROI, barriers to entry, and ecosystem advantage.", "summary_source_ref_id": "ref5",
                        "advantages_list": [
                            {"advantage": "Superior ROI drives higher win rates.", "impact": "18% higher win rate when efficiency is key factor.", "source_ref_id": "ref5"},
                            {"advantage": "IP creates barrier to replication.", "impact": "8 ppt gross margin premium on these solutions.", "source_ref_id": "ref5"}
                        ],
                        "relevant_customer_segments": [{"segment_name": "Automotive Manufacturing", "advantage_manifestation": "22% energy reduction vs. 15% avg.", "supporting_metric": "Market Share: 42%", "source_ref_id": "ref5"}],
                        "notes": None
                    },
                    "current_leverage": {
                         "summary": "Leveraged in premium products and consulting services.", "summary_source_ref_id": "ref6",
                         "specific_applications": [
                              {"application_name": "Premium Tier Automation Products", "revenue_contribution": {"value": 485, "unit": "million USD", "as_of": "FY 2023", "source_ref_id": "ref6"}, "growth_rate": {"value": 22.5, "unit": "%", "period": "FY23 YoY", "source_ref_id": "ref6"}, "notes": None},
                              {"application_name": "Energy Management Consulting", "revenue_contribution": {"value": 95, "unit": "million USD", "as_of": "FY 2023", "source_ref_id": "ref6"}, "growth_rate": {"value": 32.8, "unit": "%", "period": "FY23 YoY", "source_ref_id": "ref6"}, "notes": None}
                         ],
                         "strategic_importance": "Core enabler for Sustainable Manufacturing leadership objective.", "strategic_importance_source_ref_id": "ref1",
                         "notes": None
                    },
                    "notes": None
                },
                 { # Example Strength 2: Operations
                    "priority": 2,
                    "name": "Global Manufacturing Scale with Regional Customization", "name_source_ref_id": "ref1",
                    "category": "Operations", "category_source_ref_id": "ref1",
                    "description": "Network of 8 facilities across 3 continents with flexible production systems enabling scale economies and local adaptation.", "description_source_ref_id": "ref7",
                    "development_history": None, # Example where development history isn't detailed
                    "quantification_and_evidence": {
                         "key_metrics": [
                              {"metric_name": "Mfg Cost Advantage", "value": 12.5, "unit": "% lower", "comparison_point": "vs Regional Avg", "as_of": "FY 2023", "source_ref_id": "ref7"},
                              {"metric_name": "On-Time Delivery Rate", "value": 95.8, "unit": "%", "comparison_point": "vs Industry Avg", "comparison_value": "87.5%", "advantage_description": "8.3 ppts better", "as_of": "Q1 2024", "source_ref_id": "ref7"}
                         ],
                         "third_party_validation": None, "notes": None
                    },
                    "competitive_advantage_analysis": {
                        "summary": "Enables cost leadership and superior customer responsiveness.", "summary_source_ref_id": "ref5",
                        "advantages_list": [
                            {"advantage": "Scale enables 12.5% cost advantage.", "impact": "Supports 3-5 ppt price premium with comparable margins.", "source_ref_id": "ref5"},
                            {"advantage": "Regional production reduces lead times.", "impact": "4.3 week avg delivery advantage vs centralized competitors.", "source_ref_id": "ref5"}
                        ],
                         "relevant_customer_segments": [], "notes": None
                    },
                     "current_leverage": {
                         "summary": "Supports regional product variants and rapid response offerings.", "summary_source_ref_id": "ref6",
                         "specific_applications": [{"application_name": "Regional Product Variants", "revenue_contribution": {"value": 22, "unit": "% of total", "as_of": "FY 2023", "source_ref_id": "ref6"}, "notes": "112 variants offered."}],
                         "strategic_importance": "Key enabler for APAC growth objective.", "strategic_importance_source_ref_id": "ref1",
                         "notes": None
                    },
                    "notes": None
                 }
                 # ... Add Strength 3 ...
            ],
            "emerging_strengths": [
                 { 
                    "name": "AI-Enhanced Predictive Maintenance Capabilities", "name_source_ref_id": "ref9",
                    "category": "Technology", "category_source_ref_id": "ref9",
                    "description": "Developing ML for predictive maintenance, initial deployments show 35% greater accuracy.", "description_source_ref_id": "ref9",
                    "development_stage": {"description": "Late-stage development, 28 customer pilots.", "expected_commercial_launch": "Q3 2024", "source_ref_id": "ref9"},
                    "potential_impact": {"description": "Potential differentiator for recurring revenue service contracts.", "earliest_material_impact": "2025", "source_ref_id": "ref9"},
                    "notes": None
                 }
            ],
            "footnotes": [
                 {"id": "ref1", "document": "Competitive Positioning Assessment", "page": "8-15", "section": "Core Strengths", "date": "Mar 2024"},
                 {"id": "ref2", "document": "Technology Portfolio Review", "page": "12-18", "section": "Energy Optimization", "date": "Feb 2024"},
                 {"id": "ref3", "document": "Product Performance Metrics", "page": "5-9", "section": "Energy Management", "date": "Q1 2024"},
                 {"id": "ref4", "document": "Industry Competitive Analysis", "page": "22-28", "section": "Comparative Capabilities", "date": "Mar 2024"},
                 {"id": "ref5", "document": "Win/Loss Analysis Report", "page": "10-18", "section": "Advantage Factors", "date": "Q4 2023"},
                 {"id": "ref6", "document": "Annual Report 2023", "page": "35-42", "section": "Segment Analysis", "date": "Feb 15, 2024"},
                 {"id": "ref7", "document": "Mfg Capabilities Review", "page": "4-15", "section": "Global Footprint", "date": "Jan 2024"},
                 # {"id": "ref8", ...} # Example ref for integration strength if added
                 {"id": "ref9", "document": "Emerging Capabilities Report", "page": "8-12", "section": "AI/Predictive", "date": "Mar 2024"}
            ]
        }
    },
# --- END: Section 15 Definition ---

# --- START: Section 16 Definition ---
    {
        "number": 16,
        "title": "Weaknesses",
        "specs": "Extract an overview description summarizing the Company's main competitive weaknesses or internal limitations.\n"
                 "Identify and extract details on the 3 most relevant weaknesses that currently prevent the Company from serving customers effectively or competing successfully against key competitors.\n"
                 "Prioritize weaknesses based on their material impact on the Company's competitive standing and financial performance.\n"
                 "For each weakness, extract:\n"
                 "  - Its name/title and category (e.g., Capabilities/Resources, Operations, Go-to-Market, Technology).\n"
                 "  - A clear description of the weakness and its underlying root causes, including how it developed if relevant.\n"
                 "  - Quantitative data demonstrating the negative impact of the weakness (e.g., capability gaps vs competitors, higher costs, lower market share in affected segments, slower timelines), specifying 'as of' dates.\n"
                 "  - Competitive benchmarking data comparing the Company's performance in the area of weakness to key competitors or industry averages.\n"
                 "  - A description of the specific competitive disadvantage(s) resulting from this weakness and how they manifest (e.g., lower win rates in specific scenarios, inability to compete in certain segments, margin pressure).\n"
                 "  - Details on current mitigation efforts undertaken by the Company and an assessment of their effectiveness to date.\n"
                 "Identify and briefly describe any significant emerging weaknesses if they pose a potential near-term threat.\n"
                 "Ensure the analysis focuses on company-specific weaknesses relative to competitors, not just general market threats.\n"
                 "All extracted data points requiring citation must have a corresponding source reference ID linking to a footnote.\n"
                 "Ensure all footnotes provide precise source details: document name, date, page number, and specific section/table.",
        "schema": {
            "weaknesses_overview": { # Optional overview
                "description": None, # string summarizing key weaknesses
                "description_source_ref_id": None
            },
            "primary_weaknesses": [ # List of top 3 weaknesses
                { # Structure for ONE primary weakness
                    "priority": None, # Optional number (1, 2, 3)
                    "name": None, # string (e.g., "Limited Software Development Capacity")
                    "name_source_ref_id": None,
                    "category": None, # string (e.g., "Capabilities/Resources", "Operations")
                    "category_source_ref_id": None,
                    "description": None, # string explaining the weakness
                    "description_source_ref_id": None,
                    "development_and_root_causes": { # Optional details on origin/causes
                        "summary": None, # Optional string summary
                        "summary_source_ref_id": None,
                        "root_causes_list": [ # List of root causes
                            {
                                "cause": None, # string
                                "explanation": None, # string
                                "source_ref_id": None
                            }
                        ],
                         "timeline_notes": None, # Optional string on historical development
                         "timeline_notes_source_ref_id": None
                    },
                    "quantification_and_evidence": { # Data substantiating the weakness
                        "key_metrics": [ # List of metrics demonstrating the weakness/gap
                             {
                                 "metric_name": None, # string (e.g., "Talent Gap", "Time-to-Market Lag")
                                 "company_performance": None, # number or string
                                 "unit": None, # string
                                 "benchmark_point": None, # Optional string (e.g., "vs Target", "vs Competitor Avg")
                                 "benchmark_value": None, # Optional number/string
                                 "performance_gap": None, # Optional string quantifying the gap (e.g., "40% shortfall", "50% slower")
                                 "as_of": None, # string
                                 "source_ref_id": None
                             }
                        ],
                         "financial_impact_estimate": { # Optional estimated financial cost/loss
                            "description": None, # string (e.g., "Estimated annual revenue opportunity lost")
                            "low_value": None, "high_value": None, "unit": None, 
                            "as_of": None, "source_ref_id": None
                        },
                         "notes": None
                    },
                    "competitive_disadvantage_analysis": { # Explaining the impact vs competitors
                        "summary": None, # Optional string summarizing the disadvantage
                        "summary_source_ref_id": None,
                        "disadvantages_list": [ # List of specific disadvantages
                            {
                                "disadvantage": None, # string (e.g., "Extended time-to-market for digital features")
                                "impact": None, # string quantifying business impact (e.g., "42% of competitive losses cite timing...")
                                "source_ref_id": None
                            }
                        ],
                        "affected_customer_segments": [ # Optional segments where disadvantage is key
                             {
                                 "segment_name": None, # string
                                 "disadvantage_manifestation": None, # string describing impact in segment
                                 "supporting_metric": None, # Optional string (e.g., "Market Share: 12% vs 15% overall")
                                 "source_ref_id": None
                             }
                        ],
                        "notes": None
                    },
                    "mitigation_efforts": { # Company's response (if any described)
                        "summary": None, # Optional summary string
                        "summary_source_ref_id": None,
                        "current_initiatives": [ # List of ongoing actions
                            {
                                "name": None, # string (e.g., "Global Development Center Expansion")
                                "description": None, # string
                                "implementation_status": None, # string describing progress/effect
                                "effectiveness_assessment": None, # Optional string evaluating success
                                "source_ref_id": None
                            }
                        ],
                         "planned_initiatives": [], # Optional list of future actions (same structure as current)
                        "overall_effectiveness_assessment": None, # string evaluating mitigation success overall
                        "overall_effectiveness_assessment_source_ref_id": None,
                        "notes": None
                    },
                    "notes": None # Optional overall weakness notes
                }
            ],
            "emerging_weaknesses": [ # Optional list of developing weaknesses
                { # Structure for ONE emerging weakness
                    "name": None, "name_source_ref_id": None,
                    "category": None, "category_source_ref_id": None,
                    "description": None, "description_source_ref_id": None,
                    "development_stage": {
                        "description": None, # e.g., "Early manifestation", "Gap widening"
                        "competitive_position_indicator": None, # string comparing to competitors
                        "source_ref_id": None
                    },
                    "potential_impact": {
                         "description": None, # string describing potential disadvantage
                         "earliest_material_impact": None, # string (e.g., "2025")
                         "source_ref_id": None
                    },
                    "early_indicators": { # Optional
                        "description": None, "metrics": [], "source_ref_id": None
                    },
                    "notes": None
                }
            ],
            "footnotes": [ # Top-level list for all footnotes in this section
                { # Structure definition for ONE footnote
                    "id": None, "document": None, "page": None, "section": None, "date": None 
                }
            ]
        },
        "template": { # Example data aligned with refined schema
            "weaknesses_overview": {
                "description": "Key competitive weaknesses include limited software development capacity compared to digital leaders, insufficient manufacturing scale in high-growth APAC markets, and service network density gaps in emerging regions.", "description_source_ref_id": "ref1"
            },
            "primary_weaknesses": [
                { # Example Weakness 1: Capabilities
                    "priority": 1,
                    "name": "Limited Software Development Capacity", "name_source_ref_id": "ref1",
                    "category": "Capabilities/Resources", "category_source_ref_id": "ref1",
                    "description": "Insufficient software engineering talent and infrastructure hinders ability to meet market demand for connected products and services.", "description_source_ref_id": "ref2",
                    "development_and_root_causes": {
                        "summary": "Late strategic pivot to software (started 2018) and legacy hardware-focused talent strategy created current gap.", "summary_source_ref_id": "ref2",
                        "root_causes_list": [ {"cause": "Late strategy shift", "explanation": "Began significant software investment 3-4 years after leaders.", "source_ref_id": "ref2"} ],
                        "timeline_notes": "Centralized software org established 2022.", "timeline_notes_source_ref_id": "ref2"
                    },
                    "quantification_and_evidence": {
                        "key_metrics": [
                             {"metric_name": "Talent Gap (Software Engineers)", "company_performance": 300, "unit": "engineers", "benchmark_point": "vs Target", "benchmark_value": "500", "performance_gap": "40% shortfall", "as_of": "Q1 2024", "source_ref_id": "ref3"},
                             {"metric_name": "Time-to-Market (Connected Products)", "company_performance": 18, "unit": "months", "benchmark_point": "vs Competitor Avg", "benchmark_value": "12 months", "performance_gap": "50% slower", "as_of": "FY 2023", "source_ref_id": "ref3"}
                        ],
                         "financial_impact_estimate": {"description": "Est. lost annual revenue opportunity (delayed digital offerings)", "low_value": 120, "high_value": 150, "unit": "million USD", "as_of": "FY 2023", "source_ref_id": "ref3"},
                         "notes": None
                    },
                    "competitive_disadvantage_analysis": {
                        "summary": "Results in slower feature rollout and lower win rates in digital RFPs.", "summary_source_ref_id": "ref5",
                        "disadvantages_list": [
                            {"disadvantage": "Slower time-to-market for new digital features.", "impact": "Cited as loss reason in 42% of digital RFP defeats.", "source_ref_id": "ref5"},
                            {"disadvantage": "Limited ability to support customer customizations.", "impact": "35% win rate vs 65% competitor avg when customization is key.", "source_ref_id": "ref5"}
                        ],
                        "affected_customer_segments": [{"segment_name": "Large Enterprise (Digital Focus)", "disadvantage_manifestation": "Win rate declining (52% Q1 2024 vs 58% FY 2023)", "supporting_metric": "Market Share: 12%", "source_ref_id": "ref5"}],
                        "notes": None
                    },
                    "mitigation_efforts": {
                        "summary": "Efforts underway but insufficient to close gap near-term.", "summary_source_ref_id": "ref6",
                        "current_initiatives": [
                            {"name": "Global Dev Centers (Bangalore/Warsaw)", "description": "Access new talent pools.", "implementation_status": "45 hires vs 120 target (behind schedule).", "effectiveness_assessment": "Partial", "source_ref_id": "ref6"},
                            {"name": "Technology Partnerships", "description": "Leverage cloud provider platforms.", "implementation_status": "2 partnerships active.", "effectiveness_assessment": "Promising but early.", "source_ref_id": "ref6"}
                        ],
                        "planned_initiatives": [{"name": "Acqui-hiring", "description": "Target 2-3 small software firms.", "timeline": "2024-2025", "expected_impact": "+75-100 engineers", "budget_allocation": "$100M", "source_ref_id": "ref6"}],
                        "overall_effectiveness_assessment": "Weakness likely remains significant competitive disadvantage through 2025.", "overall_effectiveness_assessment_source_ref_id": "ref6",
                        "notes": None
                    },
                    "notes": "Primary constraint on achieving 40% recurring revenue target."
                }
                # ... Add Weakness 2 (e.g., APAC Capacity) and Weakness 3 (e.g., Service Network) following structure ...
            ],
            "emerging_weaknesses": [
                 {
                    "name": "Competitive Gap in Applied AI Capabilities", "name_source_ref_id": "ref11",
                    "category": "Technology Positioning", "category_source_ref_id": "ref11",
                    "description": "Company lagging leaders in commercializing AI for predictive maintenance and autonomous optimization.", "description_source_ref_id": "ref11",
                    "development_stage": {"description": "Company has pilot projects; 3-5 competitors have commercial AI features.", "competitive_position_indicator": "Filed 14 AI patents vs leader's 38 in 2023.", "source_ref_id": "ref11"},
                    "potential_impact": {"description": "Risk of losing premium segment share as AI becomes expected feature.", "earliest_material_impact": "H2 2025", "source_ref_id": "ref11"},
                    "early_indicators": {"description": "AI capabilities cited in 22% of RFPs (Q1 2024) vs 8% (Q1 2023).", "source_ref_id": "ref11"},
                    "notes": "Requires focused R&D or acquisition."
                 }
                 # ... Add other emerging weaknesses ...
            ],
            "footnotes": [
                {"id": "ref1", "document": "Strategic SWOT Analysis", "page": "15-22", "section": "Internal Weaknesses", "date": "Mar 2024"},
                {"id": "ref2", "document": "Digital Transformation Review", "page": "8-12", "section": "Software Dev Challenges", "date": "Feb 2024"},
                {"id": "ref3", "document": "Technical Resource Plan", "page": "15-20", "section": "Gap Analysis", "date": "Jan 2024"},
                # {"id": "ref4", ...} # References for competitive comparison
                {"id": "ref5", "document": "Win/Loss Analysis Report", "page": "22-30", "section": "Disadvantage Factors", "date": "Q4 2023"},
                {"id": "ref6", "document": "Software Talent Strategy Update", "page": "3-10", "section": "Progress vs Targets", "date": "Mar 15, 2024"},
                # {"id": "ref7", ...} # References for APAC capacity example if included
                # {"id": "ref8", ...} # References for Service network example if included
                {"id": "ref11", "document": "Emerging Competitive Risks", "page": "5-12", "section": "Developing Disadvantages", "date": "Apr 2024"}
                # ... Add all other necessary footnotes
            ]
        }
    },
# --- END: Section 16 Definition ---

# --- START: Section 17 Definition ---
    {
        "number": 17,
        "title": "Opportunities",
        "specs": "Extract an overview description summarizing the most promising near-term opportunities available to the Company.\n"
                 "Identify and extract details on 3 specific, actionable opportunities achievable within the next 12-24 months that could materially impact performance.\n"
                 "Focus only on opportunities where the Company has existing capabilities or strengths that can be readily leveraged for capturing value.\n"
                 "For each key opportunity, extract:\n"
                 "  - Its name/title and a clear description.\n"
                 "  - The specific Company strength(s) or capability(ies) that enable this opportunity.\n"
                 "  - An estimate of the market potential or addressable size for the opportunity, if available.\n"
                 "  - A high-level implementation plan summary, including expected timeframe and required investment (if stated).\n"
                 "  - Quantified potential financial impact (e.g., incremental revenue, profit, ROI) with timelines, where possible.\n"
                 "  - A brief assessment of the key risks associated with pursuing the opportunity.\n"
                 "Prioritize opportunities based on potential financial impact and feasibility within the 12-24 month timeframe.\n"
                 "Avoid speculative opportunities requiring significant new capability development not already underway.\n"
                 "All extracted data points requiring citation must have a corresponding source reference ID linking to a footnote.\n"
                 "Ensure all footnotes provide precise source details: document name, date, page number, and specific section/table.",
        "schema": {
            "opportunities_overview": { # Optional overview
                "description": None, # string summarizing key opportunities
                "description_source_ref_id": None
            },
            "key_opportunities": [ # List of top 3 opportunities
                { # Structure for ONE key opportunity
                    "priority": None, # Optional number (1, 2, 3)
                    "name": None, # string (e.g., "Expansion of Energy Optimization Services")
                    "name_source_ref_id": None,
                    "description": None, # string explaining the opportunity
                    "description_source_ref_id": None,
                    "link_to_strengths": { # How existing strengths enable this
                        "summary": None, # Optional string summary
                        "summary_source_ref_id": None,
                        "strengths_leveraged": [ # List of relevant strengths
                            {
                                "strength_name": None, # string (Ideally matching a name from Section 15)
                                "application_detail": None, # string explaining how it applies here
                                "source_ref_id": None
                            }
                        ]
                    },
                    "market_potential": { # Optional market sizing
                        "addressable_base_description": None, # string (e.g., "Existing customers not using solution X")
                        "addressable_base_description_source_ref_id": None,
                        "size_value": None, # number or string
                        "size_value_source_ref_id": None,
                        "size_unit": None, # string (e.g., "customers", "million USD TAM")
                        "size_unit_source_ref_id": None,
                        "as_of": None, # string
                        "as_of_source_ref_id": None,
                        "conversion_target_description": None, # Optional string (e.g., "Target 35% penetration")
                        "conversion_target_description_source_ref_id": None,
                        "notes": None
                    },
                    "implementation_summary": { # Optional summary of plan/timeline/investment
                        "description": None, # string summarizing plan
                        "description_source_ref_id": None,
                        "timeframe": None, # string (e.g., "12-18 months", "Launch Q3 2024")
                        "timeframe_source_ref_id": None,
                        "required_investment": { # Optional investment details
                            "value": None, "unit": None, "source_ref_id": None
                        },
                        "notes": None
                    },
                    "financial_impact": { # Optional quantified potential impact
                        "incremental_revenue_potential": { # e.g., Over 1-2 years
                            "low_value": None, "high_value": None, "point_value": None,
                            "unit": None, "timeframe": None, "source_ref_id": None
                        },
                        "incremental_profit_potential": { # e.g., Over 1-2 years
                            "low_value": None, "high_value": None, "point_value": None,
                            "unit": None, "margin_percentage": None, "timeframe": None, "source_ref_id": None
                        },
                        "roi_metrics": { # Optional ROI estimates
                             "payback_period": {"value": None, "unit": "months", "source_ref_id": None},
                             "irr_estimate": {"value": None, "unit": "%", "timeframe": None, "source_ref_id": None}
                        },
                        "notes": None
                    },
                    "risk_assessment": { # Optional brief risk summary
                         "summary": None, # string
                         "summary_source_ref_id": None,
                         "key_risks": [], # List of strings
                         "key_risks_source_ref_id": None,
                         "overall_risk_level": None, # Optional string (e.g., "Low", "Medium")
                         "overall_risk_level_source_ref_id": None
                    },
                    "notes": None # Optional overall opportunity notes
                }
            ],
            "footnotes": [ # Top-level list for all footnotes in this section
                { # Structure definition for ONE footnote
                    "id": None, "document": None, "page": None, "section": None, "date": None 
                }
            ]
        },
        "template": { # Example data aligned with refined schema
            "opportunities_overview": {
                "description": "Several near-term opportunities leverage existing strengths, primarily focusing on cross-selling advanced services to the installed base and expanding service coverage in growing markets.", "description_source_ref_id": "ref1"
            },
            "key_opportunities": [
                { # Example Opportunity 1
                    "priority": 1,
                    "name": "Expansion of Energy Optimization Services to Existing Customer Base", "name_source_ref_id": "ref1",
                    "description": "Deploy proven energy optimization technology to the 68% of existing customers currently not using these solutions.", "description_source_ref_id": "ref1",
                    "link_to_strengths": {
                        "summary": "Leverages proprietary tech and strong customer relationships.", "summary_source_ref_id": "ref2",
                        "strengths_leveraged": [
                            {"strength_name": "Proprietary Energy Optimization Technology", "application_detail": "Direct application of existing, patented technology.", "source_ref_id": "ref2"},
                            {"strength_name": "Strong Customer Relationships", "application_detail": "Lower acquisition cost via installed base (92% retention).", "source_ref_id": "ref2"}
                        ]
                    },
                    "market_potential": {
                        "addressable_base_description": "815 existing customers (1250 locations) without energy optimization solution.", "addressable_base_description_source_ref_id": "ref3",
                        "size_value": None, "size_unit": None, "as_of": "Q1 2024", "as_of_source_ref_id": "ref3",
                        "conversion_target_description": "Targeting 35% penetration within 18 months.", "conversion_target_description_source_ref_id": "ref3",
                        "notes": "Based on historical cross-sell conversion rates."
                    },
                    "implementation_summary": {
                        "description": "Phased rollout involving sales training, targeted outreach, and deployment.", "description_source_ref_id": "ref4",
                        "timeframe": "18 months (starting Q3 2024)", "timeframe_source_ref_id": "ref4",
                        "required_investment": {"value": 12.5, "unit": "million USD", "source_ref_id": "ref4"},
                        "notes": "Primarily SG&A and deployment resources."
                    },
                    "financial_impact": {
                        "incremental_revenue_potential": {"point_value": 80.7, "unit": "million USD", "timeframe": "Cumulative over 2 years", "source_ref_id": "ref5"},
                        "incremental_profit_potential": {"point_value": 23.8, "unit": "million USD", "margin_percentage": 29.5, "timeframe": "Cumulative over 2 years", "source_ref_id": "ref5"},
                        "roi_metrics": {"payback_period": {"value": 14, "unit": "months", "source_ref_id": "ref5"}, "irr_estimate": {"value": 85, "unit": "%", "timeframe": "3-year", "source_ref_id": "ref5"}},
                        "notes": "Assumes average contract value of $160k."
                    },
                    "risk_assessment": {
                         "summary": "Low risk given existing tech and customer base.", "summary_source_ref_id": "ref6",
                         "key_risks": ["Lower than expected conversion rate", "Implementation resource constraints"], "key_risks_source_ref_id": "ref6",
                         "overall_risk_level": "Low", "overall_risk_level_source_ref_id": "ref6"
                    },
                    "notes": "High priority initiative for FY2024-2025."
                },
                 { # Example Opportunity 2
                    "priority": 2,
                    "name": "Asia-Pacific Service Network Expansion", "name_source_ref_id": "ref1",
                    "description": "Accelerate service network build-out in APAC to improve response times and enable premium service contracts.", "description_source_ref_id": "ref1",
                    "link_to_strengths": {
                        "summary": "Leverages Singapore hub and integration expertise.", "summary_source_ref_id": "ref2",
                        "strengths_leveraged": [
                             {"strength_name": "Global Manufacturing Scale", "application_detail": "Utilize Singapore facility as regional service HQ.", "source_ref_id": "ref2"}
                        ]
                    },
                    "market_potential": {
                        "addressable_base_description": "385 APAC customer sites without premium service.", "addressable_base_description_source_ref_id": "ref3",
                        "conversion_target_description": "Target 45% service attach rate (from 28% currently).", "conversion_target_description_source_ref_id": "ref3",
                        "notes": "Mature markets achieve 65% attach rate."
                    },
                    "implementation_summary": {
                         "description": "Hire 80 technicians, establish 4 parts depots.", "description_source_ref_id": "ref4",
                         "timeframe": "24 months", "timeframe_source_ref_id": "ref4",
                         "required_investment": {"value": 18.5, "unit": "million USD", "source_ref_id": "ref4"},
                         "notes": None
                    },
                    "financial_impact": {
                         "incremental_revenue_potential": {"point_value": 55.3, "unit": "million USD", "timeframe": "Cumulative over 2 years", "source_ref_id": "ref5"},
                         "incremental_profit_potential": {"point_value": 14.3, "unit": "million USD", "margin_percentage": 25.8, "timeframe": "Cumulative over 2 years", "source_ref_id": "ref5"},
                         "roi_metrics": {"payback_period": {"value": 22, "unit": "months", "source_ref_id": "ref5"}, "irr_estimate": {"value": 58, "unit": "%", "timeframe": "3-year", "source_ref_id": "ref5"}},
                         "notes": "Margin lower initially due to ramp-up."
                    },
                     "risk_assessment": {
                         "summary": "Medium risk due to execution challenges in diverse markets.", "summary_source_ref_id": "ref6",
                         "key_risks": ["Technician retention", "Local competition"], "key_risks_source_ref_id": "ref6",
                         "overall_risk_level": "Medium", "overall_risk_level_source_ref_id": "ref6"
                     },
                    "notes": None
                 }
                 # ... Add Opportunity 3 ...
            ],
            "footnotes": [
                {"id": "ref1", "document": "Strategic Opportunities Assessment", "page": "5-12", "section": "Near-Term Opportunity Analysis", "date": "Mar 2024"},
                {"id": "ref2", "document": "Competitive Positioning Assessment", "page": "8-15", "section": "Core Strengths", "date": "Mar 2024"},
                {"id": "ref3", "document": "Market Analysis Report", "page": "18-25", "section": "Addressable Market Analysis", "date": "Q1 2024"},
                {"id": "ref4", "document": "Strategic Initiative Planning", "page": "10-22", "section": "Implementation Roadmaps", "date": "Feb 2024"},
                {"id": "ref5", "document": "Financial Projections", "page": "15-28", "section": "Growth Initiative ROI Analysis", "date": "Mar 2024"},
                {"id": "ref6", "document": "Risk Assessment Report", "page": "8-14", "section": "Growth Initiative Risk Analysis", "date": "Q1 2024"}
            ]
        }
    },
# --- END: Section 17 Definition ---

# --- START: Section 18 Definition ---
    {
        "number": 18,
        "title": "Threats",
        "specs": "Extract an overview description summarizing the most significant external threats facing the Company.\n"
                 "Identify and extract details on the 3 most significant threats to the Company's performance or competitive position within the next 12-24 months.\n"
                 "Prioritize threats based on potential financial impact and likelihood of occurrence.\n"
                 "Include competitive threats (specific actions by competitors), potential technological disruptions, adverse regulatory changes, supply chain risks, or other relevant external factors.\n"
                 "For each key threat, extract:\n"
                 "  - Its name/title and category (e.g., Competitive, Market, Technological, Regulatory, Supply Chain).\n"
                 "  - A clear description of the threat and its root causes or drivers.\n"
                 "  - Quantitative analysis of the potential negative impact on the Company (e.g., potential revenue loss, margin compression, market share erosion, increased costs), specifying timeframes.\n"
                 "  - An assessment of the threat's likelihood, timeframe for impact, and velocity (is it static, accelerating?). Include early warning indicators if identified.\n"
                 "  - Details on the Company's current mitigation efforts (if any are described) and an assessment of their potential effectiveness.\n"
                 "  - Relevant context on key competitors' strategies or positioning related to this threat.\n"
                 "Ensure the analysis focuses on external threats or competitive actions, distinct from the Company's internal weaknesses (covered in Section 16).\n"
                 "All extracted data points requiring citation must have a corresponding source reference ID linking to a footnote.\n"
                 "Ensure all footnotes provide precise source details: document name, date, page number, and specific section/table (often Risk Factors, MD&A, Competitive Landscape).",
        "schema": {
            "threats_overview": { # Optional overview
                "description": None, # string summarizing key threats
                "description_source_ref_id": None
            },
            "key_threats": [ # List of top 3 threats
                { # Structure for ONE key threat
                    "priority": None, # Optional number (1, 2, 3)
                    "name": None, # string (e.g., "Accelerating Price Erosion in Core Hardware")
                    "name_source_ref_id": None,
                    "category": None, # string (e.g., "Competitive/Market", "Technological", "Regulatory")
                    "category_source_ref_id": None,
                    "description": None, # string explaining the threat
                    "description_source_ref_id": None,
                    "root_causes_or_drivers": [ # Optional list of contributing factors
                        {
                             "cause": None, # string
                             "explanation": None, # string
                             "source_ref_id": None
                        }
                    ],
                    "potential_impact_analysis": { # Quantifying the negative impact
                        "summary": None, # Optional string summarizing impact
                        "summary_source_ref_id": None,
                        "impact_metrics": [ # List of specific potential impacts
                            {
                                 "metric_name": None, # string (e.g., "Revenue Impact", "Margin Impact", "Market Share Loss")
                                 "potential_impact_value": None, # number or string (can be range)
                                 "unit": None, # string (e.g., "million USD annually", "% points", "% share")
                                 "timeframe": None, # string (e.g., "Next 12-18 months")
                                 "notes": None, # Optional context
                                 "source_ref_id": None
                             }
                        ],
                        "notes": None
                    },
                    "threat_assessment": { # Likelihood, timing, velocity
                        "likelihood": None, # string (e.g., "High", "Medium", "Low")
                        "likelihood_source_ref_id": None,
                        "timeframe": None, # string (e.g., "Ongoing", "Next 12-24 months")
                        "timeframe_source_ref_id": None,
                        "velocity": None, # string (e.g., "Accelerating", "Stable", "Decelerating")
                        "velocity_source_ref_id": None,
                        "early_warning_indicators": [ # Optional list of indicators
                             {
                                  "indicator": None, # string (e.g., "Competitor pricing announcements")
                                  "current_reading": None, # string describing current state
                                  "threshold": None, # Optional string describing trigger level
                                  "source_ref_id": None
                             }
                        ],
                        "notes": None
                    },
                    "company_mitigation_efforts": { # Company's response (if described)
                        "summary": None, # Optional string summarizing efforts
                        "summary_source_ref_id": None,
                        "initiatives": [ # List of mitigation actions
                            {
                                "initiative_name": None, # string (e.g., "Value-based pricing strategy")
                                "description": None, # string
                                "implementation_status": None, # string describing progress/effect
                                "effectiveness_assessment": None, # string evaluating likely success
                                "source_ref_id": None
                            }
                        ],
                        "overall_effectiveness_assessment": None, # string evaluating mitigation success overall
                        "overall_effectiveness_assessment_source_ref_id": None,
                        "notes": None
                    },
                    "related_competitor_context": { # Optional context on competitors related to this threat
                        "description": None, # string
                        "description_source_ref_id": None,
                        "competitor_actions": [ # List of competitor actions
                             {
                                 "competitor_name": None, # string
                                 "action": None, # string
                                 "impact_on_threat": None, # string
                                 "source_ref_id": None
                             }
                        ],
                        "notes": None
                    },
                    "notes": None # Optional overall threat notes
                }
            ],
            "footnotes": [ # Top-level list for all footnotes in this section
                { # Structure definition for ONE footnote
                    "id": None, "document": None, "page": None, "section": None, "date": None 
                }
            ]
        },
        "template": { # Example data aligned with refined schema
            "threats_overview": {
                "description": "Key near-term threats include intensifying price erosion in core hardware, a widening digital capabilities gap versus software-native competitors, and potential service erosion in emerging markets.", "description_source_ref_id": "ref1"
            },
            "key_threats": [
                { # Example Threat 1: Price Erosion
                    "priority": 1,
                    "name": "Accelerating Price Erosion in Core Hardware Products", "name_source_ref_id": "ref1",
                    "category": "Competitive/Market", "category_source_ref_id": "ref1",
                    "description": "Intensifying price competition from lower-cost Asian manufacturers is compressing margins in standard hardware lines (PLCs, HMIs, Drives).", "description_source_ref_id": "ref2",
                    "root_causes_or_drivers": [
                        {"cause": "Manufacturing cost disadvantage", "explanation": "Company's APAC capacity limits lead to 12.5% higher unit costs vs regional players.", "source_ref_id": "ref2"},
                        {"cause": "Commoditization", "explanation": "Expired patents on core components enable feature parity from competitors.", "source_ref_id": "ref2"}
                    ],
                    "potential_impact_analysis": {
                        "summary": "Potential for significant revenue and margin impact if trends continue.", "summary_source_ref_id": "ref3",
                        "impact_metrics": [
                            {"metric_name": "Gross Margin Compression (Hardware)", "potential_impact_value": "2.5-4.0", "unit": "% points", "timeframe": "Next 12-18 months", "notes": "Based on current competitive pricing actions.", "source_ref_id": "ref3"},
                            {"metric_name": "Revenue Impact (Hardware)", "potential_impact_value": "75-120", "unit": "million USD annually", "timeframe": "By FY 2025", "notes": "Due to price concessions and potential share loss.", "source_ref_id": "ref3"}
                        ],
                        "notes": "Impact concentrated in standard product lines (~42% of revenue)."
                    },
                    "threat_assessment": {
                        "likelihood": "High", "likelihood_source_ref_id": "ref3",
                        "timeframe": "Ongoing, accelerating", "timeframe_source_ref_id": "ref3",
                        "velocity": "Accelerating", "velocity_source_ref_id": "ref3", # Price erosion worsened from Q4'23 to Q1'24
                        "early_warning_indicators": [
                             {"indicator": "Hardware Price Realization Rate", "current_reading": "Declined 1.0 ppt sequentially in Q1 2024", "threshold": "Sequential decline > 1.5 ppt", "source_ref_id": "ref3"},
                             {"indicator": "Competitor Capacity Announcements (Asia)", "current_reading": "+35% announced by 3 players", "threshold": None, "source_ref_id": "ref2"}
                        ],
                        "notes": None
                    },
                    "company_mitigation_efforts": {
                        "summary": "Mitigation partially effective but unlikely to fully offset pressure.", "summary_source_ref_id": "ref4",
                        "initiatives": [
                            {"initiative_name": "Value-based pricing/bundling", "description": "Shift focus from hardware price to solution value.", "implementation_status": "Rolled out Q1 2024", "effectiveness_assessment": "Limited success so far (15% bundle adoption).", "source_ref_id": "ref4"},
                            {"initiative_name": "Accelerated APAC Mfg Expansion", "description": "Increase local production to reduce cost.", "implementation_status": "45% complete, completion Q3 2025", "effectiveness_assessment": "Will help but cost gap remains vs lowest cost players.", "source_ref_id": "ref4"}
                        ],
                        "overall_effectiveness_assessment": "Projected to mitigate $10-15M of EBITDA impact, leaving $25-35M exposure.", "overall_effectiveness_assessment_source_ref_id": "ref4",
                        "notes": None
                    },
                    "related_competitor_context": {
                        "description": "Regional Competitor X aggressively expanding capacity and using low price strategy.", "description_source_ref_id": "ref5",
                        "competitor_actions": [{"competitor_name": "Regional Competitor X", "action": "+40% capacity expansion", "impact_on_threat": "Increases pricing pressure", "source_ref_id": "ref5"}],
                        "notes": None
                    },
                    "notes": None
                },
                 { # Example Threat 2: Digital Gap
                    "priority": 2,
                    "name": "Digital Capabilities Gap vs. Software-Native Competitors", "name_source_ref_id": "ref1",
                    "category": "Technological/Competitive", "category_source_ref_id": "ref1",
                    "description": "Widening gap in software/AI capabilities vs new entrants and transforming traditional competitors risks loss of high-growth digital deals.", "description_source_ref_id": "ref2",
                     "root_causes_or_drivers": [
                        {"cause": "Talent Shortfall", "explanation": "40% gap vs required software engineers.", "source_ref_id": "ref2"},
                        {"cause": "Legacy Tech Stack", "explanation": "Core platform limits development velocity.", "source_ref_id": "ref2"}
                    ],
                    "potential_impact_analysis": {
                         "summary": "Threatens recurring revenue targets and potentially valuation.", "summary_source_ref_id": "ref3",
                        "impact_metrics": [
                             {"metric_name": "Recurring Revenue Target Attainment", "potential_impact_value": "Reach 32% vs 40% target", "unit": "% of Revenue", "timeframe": "by 2025", "source_ref_id": "ref3"},
                             {"metric_name": "Valuation Multiple Compression", "potential_impact_value": "0.5-1.2", "unit": "turns EV/EBITDA", "timeframe": "Potential", "notes": "If transition lags peers significantly.", "source_ref_id": "ref3"}
                        ],
                         "notes": None
                    },
                    "threat_assessment": {
                        "likelihood": "High", "likelihood_source_ref_id": "ref3",
                        "timeframe": "Ongoing", "timeframe_source_ref_id": "ref3",
                        "velocity": "Increasing", "velocity_source_ref_id": "ref3", # Based on competitor moves
                        "early_warning_indicators": [ {"indicator": "Win Rate in Digital RFPs", "current_reading": "Declined from 45% to 38% vs software natives YoY", "threshold": "<35%", "source_ref_id": "ref4"} ],
                        "notes": None
                    },
                    "company_mitigation_efforts": {
                         "summary": "Efforts underway but significantly lagging competitor investments.", "summary_source_ref_id": "ref4",
                         "initiatives": [
                             {"initiative_name": "Global Dev Centers", "description": "Expand talent pools.", "implementation_status": "Behind hiring schedule.", "effectiveness_assessment": "Insufficient scale.", "source_ref_id": "ref4"},
                             {"initiative_name": "Technology Partnerships", "description": "Leverage cloud platforms.", "implementation_status": "Active", "effectiveness_assessment": "Positive but limited scope.", "source_ref_id": "ref4"}
                         ],
                         "overall_effectiveness_assessment": "Unlikely to close gap vs leaders in 12-24 months.", "overall_effectiveness_assessment_source_ref_id": "ref4",
                         "notes": None
                    },
                    "related_competitor_context": {
                        "description": "Competitor A investing $350M/yr in digital, SoftwareAutomation Inc growing 85% YoY.", "description_source_ref_id": "ref5",
                        "competitor_actions": [],
                        "notes": None
                    },
                    "notes": None
                 }
                 # ... Add Threat 3 ...
            ],
            "footnotes": [
                {"id": "ref1", "document": "Strategic Risk Assessment", "page": "8-15", "section": "Material Threats Analysis", "date": "Mar 2024"},
                {"id": "ref2", "document": "Competitive Landscape Analysis", "page": "15-25", "section": "Key Competitor Actions", "date": "Feb 2024"},
                {"id": "ref3", "document": "Financial Impact Analysis - Threats", "page": "5-12", "section": "Threat Scenario Modeling", "date": "Feb 2024"},
                {"id": "ref4", "document": "Mitigation Plan Review", "page": "10-18", "section": "Effectiveness Assessment", "date": "Mar 2024"},
                {"id": "ref5", "document": "Competitive Intelligence Report", "page": "8-20", "section": "Competitor Strategy Update", "date": "Q1 2024"}
            ]
        }
    },
# --- END: Section 18 Definition ---

# --- START: Section 19 Definition ---
    {
        "number": 19,
        "title": "Sellside Positioning - Macro",
        "specs": "Extract an overview description summarizing the key positive macroeconomic trends supporting the Company's performance and investment thesis.\n"
                 "Identify and extract details on the 3 most important positive macroeconomic trends (economic indicators, broad market forces) that benefit the Company.\n"
                 "Focus only on positive macro trends; do not include industry-specific trends (covered later) or company-specific factors.\n"
                 "For each macro trend, extract:\n"
                 "  - Its name/title and category (e.g., Investment Trends, Labor Market, Trade Patterns, Energy Markets, Regulatory Environment).\n"
                 "  - A clear description of the trend.\n"
                 "  - Quantitative data demonstrating the trend, covering recent history (e.g., last 24 months) and future outlook/forecasts (e.g., next 12-24 months) where available. Include relevant indicators (e.g., GDP growth, capex growth, interest rate trends, labor costs, supply chain indices, regulatory spending).\n"
                 "  - Regional or sector breakdowns if relevant and available.\n"
                 "  - A clear explanation of how this specific macro trend directly benefits the Company, ideally supported by quantitative links (e.g., correlation between trend and company performance, size of exposure to benefiting sector).\n"
                 "All extracted data points requiring citation must have a corresponding source reference ID linking to a footnote.\n"
                 "Ensure all footnotes provide precise source details: document name (e.g., Economic Report, Forecast Publication), date, page number, and specific section/table.",
        "schema": {
            "overview": { # Optional overview
                "description": None, # string summarizing positive macro tailwinds
                "description_source_ref_id": None
            },
            "macro_trends": [ # List of top 3 positive trends
                { # Structure for ONE macro trend
                    "priority": None, # Optional number (1, 2, 3)
                    "name": None, # string (e.g., "Manufacturing Capital Expenditure Growth")
                    "name_source_ref_id": None,
                    "category": None, # string (e.g., "Investment Trends", "Labor Market Trends")
                    "category_source_ref_id": None,
                    "description": None, # string explaining the trend
                    "description_source_ref_id": None,
                    "supporting_data": { # Quantitative data for the trend
                         "historical_data": [ # List of historical data points/metrics
                              {
                                   "metric_name": None, # string (e.g., "Global Mfg Capex Growth")
                                   "values": [ # List of values over time
                                        {"period": None, "value": None, "unit": None, "source_ref_id": None}
                                   ],
                                   "notes": None
                              }
                         ],
                         "forecast_data": [ # List of forecast data points/metrics
                              {
                                   "metric_name": None, # string
                                   "values": [ # List of values over time
                                        {"period": None, "value": None, "unit": None, "source_ref_id": None}
                                   ],
                                   "notes": None
                              }
                         ],
                         "regional_or_sector_breakdown": [ # Optional list of breakdowns
                              {
                                   "area_name": None, # string (e.g., "North America", "Automation-Specific")
                                   "value": None,
                                   "unit": None,
                                   "period": None, # e.g., "2025 Forecast"
                                   "source_ref_id": None
                              }
                         ],
                         "notes": None # Optional notes on the data
                    },
                    "impact_on_company": { # Explanation of the positive link to the company
                        "description": None, # string explaining the benefit
                        "description_source_ref_id": None,
                        "quantification": None, # Optional string quantifying the link (e.g., "Each 1% capex growth correlates to 0.85% revenue growth")
                        "quantification_source_ref_id": None,
                        "relevant_company_metric": { # Optional link to specific company performance
                             "metric_name": None, # e.g., "Industrial Automation Segment Growth"
                             "value": None,
                             "unit": None,
                             "period": None,
                             "source_ref_id": None
                        },
                        "notes": None
                    },
                    "notes": None # Optional overall trend notes
                }
            ],
            "footnotes": [ # Top-level list for all footnotes in this section
                { # Structure definition for ONE footnote
                    "id": None, "document": None, "page": None, "section": None, "date": None 
                }
            ]
        },
        "template": { # Example data aligned with refined schema
            "overview": {
                "description": "The Company benefits from several positive macroeconomic tailwinds, including strong manufacturing capital expenditure focused on automation, inflationary labor pressures driving productivity investments, and supportive trends in supply chain regionalization.", "description_source_ref_id": "ref1"
            },
            "macro_trends": [
                { # Example Trend 1: Capex
                    "priority": 1,
                    "name": "Robust Manufacturing Capital Expenditure Growth (Automation Focus)", "name_source_ref_id": "ref2",
                    "category": "Investment Trends", "category_source_ref_id": "ref2",
                    "description": "Global manufacturers continue to increase capital spending, with a particular focus on automation technologies to enhance productivity and address labor challenges.", "description_source_ref_id": "ref2",
                    "supporting_data": {
                         "historical_data": [
                              {"metric_name": "Global Mfg Capex Growth", "values": [ {"period": "2023", "value": 5.3, "unit": "%", "source_ref_id": "ref2"}, {"period": "2024", "value": 6.2, "unit": "%", "source_ref_id": "ref2"} ], "notes": None},
                              {"metric_name": "Automation-Specific Capex Growth", "values": [ {"period": "2023", "value": 8.4, "unit": "%", "source_ref_id": "ref2"}, {"period": "2024", "value": 12.5, "unit": "%", "source_ref_id": "ref2"} ], "notes": None}
                         ],
                         "forecast_data": [
                              {"metric_name": "Global Mfg Capex Growth", "values": [ {"period": "2025F", "value": 6.8, "unit": "%", "source_ref_id": "ref2"} ], "notes": None},
                              {"metric_name": "Automation-Specific Capex Growth", "values": [ {"period": "2025F", "value": 14.8, "unit": "%", "source_ref_id": "ref2"} ], "notes": None}
                         ],
                         "regional_or_sector_breakdown": [
                              {"area_name": "Asia-Pacific Capex Growth", "value": 8.2, "unit": "%", "period": "2025F", "source_ref_id": "ref2"}
                         ],
                         "notes": "Automation spending growing significantly faster than overall capex."
                    },
                    "impact_on_company": {
                        "description": "Directly supports revenue growth as the Company's core products are key components of automation capex.", "description_source_ref_id": "ref2",
                        "quantification": "Each 1% increase in global automation capex historically correlates to ~0.85% Company revenue growth (2-qtr lag).", "quantification_source_ref_id": "ref3", # Example internal analysis source
                        "relevant_company_metric": {"metric_name": "Company Revenue Growth", "value": 14.8, "unit": "%", "period": "Q1 2024 YoY", "source_ref_id": "ref3"},
                        "notes": "Company exposed to ~83% of revenue in benefiting segments."
                    },
                    "notes": None
                },
                { # Example Trend 2: Labor Costs
                    "priority": 2,
                    "name": "Rising Manufacturing Labor Costs & Shortages", "name_source_ref_id": "ref3",
                    "category": "Labor Market Trends", "category_source_ref_id": "ref3",
                    "description": "Sustained increases in manufacturing wages globally, coupled with persistent skilled labor shortages, incentivize investment in automation for productivity and cost control.", "description_source_ref_id": "ref3",
                     "supporting_data": {
                         "historical_data": [
                              {"metric_name": "Global Mfg Labor Cost Growth", "values": [ {"period": "2023", "value": 4.2, "unit": "%", "source_ref_id": "ref3"}, {"period": "2024", "value": 5.5, "unit": "%", "source_ref_id": "ref3"} ], "notes": None}
                         ],
                         "forecast_data": [
                              {"metric_name": "Global Mfg Labor Cost Growth", "values": [ {"period": "2025F", "value": 6.2, "unit": "%", "source_ref_id": "ref3"} ], "notes": None}
                         ],
                         "regional_or_sector_breakdown": [
                              {"area_name": "North America Labor Cost Growth", "value": 7.5, "unit": "%", "period": "2025F", "source_ref_id": "ref3"}
                         ],
                         "notes": "Skilled labor shortages also cited as major driver."
                    },
                     "impact_on_company": {
                        "description": "Increases the ROI and urgency for customers to adopt the Company's automation solutions.", "description_source_ref_id": "ref3",
                        "quantification": "Automation project payback periods shortened by ~35% in 2024 vs 2022 due to higher labor cost avoidance.", "quantification_source_ref_id": "ref3",
                        "relevant_company_metric": {"metric_name": "Industrial Automation Segment Growth", "value": 14.8, "unit": "%", "period": "Q1 2024 YoY", "source_ref_id": "ref3"},
                        "notes": "Labor cost savings is #1 driver cited by 78% of new customers (2024)."
                    },
                    "notes": None
                },
                 { # Example Trend 3: Reshoring
                    "priority": 3,
                    "name": "Reshoring and Supply Chain Regionalization Initiatives", "name_source_ref_id": "ref4",
                    "category": "Trade/Investment Patterns", "category_source_ref_id": "ref4",
                    "description": "Ongoing trend of companies moving manufacturing back to or closer to home markets (North America, Europe) drives investment in new, highly automated facilities.", "description_source_ref_id": "ref4",
                    "supporting_data": {
                         "historical_data": [
                              {"metric_name": "N. American Reshoring Projects Announced", "values": [ {"period": "2023", "value": 1250, "unit": "projects", "source_ref_id": "ref4"}, {"period": "2024", "value": 1580, "unit": "projects", "source_ref_id": "ref4"} ], "notes": None},
                              {"metric_name": "Capital Investment in Reshoring (N.Am)", "values": [ {"period": "2023", "value": 185, "unit": "billion USD", "source_ref_id": "ref4"}, {"period": "2024", "value": 225, "unit": "billion USD", "source_ref_id": "ref4"} ], "notes": None}
                         ],
                         "forecast_data": [], # Example: No specific forecast cited
                         "regional_or_sector_breakdown": [
                              {"area_name": "Automotive Sector", "value": 28.5, "unit": "% of reshoring projects", "period": "2024", "source_ref_id": "ref4"},
                              {"area_name": "Electronics Sector", "value": 22.3, "unit": "% of reshoring projects", "period": "2024", "source_ref_id": "ref4"}
                         ],
                         "notes": None
                    },
                     "impact_on_company": {
                        "description": "Company is geographically well-positioned (80% revenue N.Am/Europe) to benefit from investments in new, highly automated facilities driven by reshoring.", "description_source_ref_id": "ref4",
                        "quantification": "New reshored facilities have ~35% higher automation content; Company captures ~22% share of automation spend in these projects.", "quantification_source_ref_id": "ref4",
                        "relevant_company_metric": {"metric_name": "North America Revenue Growth", "value": 15.2, "unit": "%", "period": "Q1 2024 YoY", "source_ref_id": "ref3"}, # Example metric link
                        "notes": None
                    },
                    "notes": None
                 }
                 # ... Potentially add other positive trends like Energy Efficiency Focus or specific Regulatory Tailwinds if relevant ...
            ],
            "footnotes": [
                {"id": "ref1", "document": "Macroeconomic Impact Analysis", "page": "3-4", "section": "Executive Summary", "date": "Mar 2025"},
                {"id": "ref2", "document": "Global Manufacturing Investment Outlook", "page": "12-18", "section": "Capex Trends", "date": "Feb 2025"},
                {"id": "ref3", "document": "Manufacturing Labor Market Report", "page": "22-28", "section": "Wage Inflation", "date": "Jan 2025"},
                {"id": "ref4", "document": "Supply Chain Restructuring Analysis", "page": "15-24", "section": "Reshoring Trends", "date": "Mar 2025"}
                # {"id": "ref5", ...} # Add other footnotes as needed
            ]
        }
    },
# --- END: Section 19 Definition ---

# --- START: Section 20 Definition ---
    {
        "number": 20,
        "title": "Sellside Positioning - Industry",
        "specs": "Extract an overview description summarizing the key positive industry dynamics and trends benefiting the Company's relevant sectors (e.g., Industrial Automation, Process Control).\n"
                 "Identify and extract details on the 3 most important positive industry trends.\n"
                 "Focus only on industry-specific trends (e.g., technology adoption within the industry, segment growth drivers, favorable competitive dynamics, beneficial regulatory shifts within the industry); do not repeat broad macro trends from Section 19.\n"
                 "For each industry trend, extract:\n"
                 "  - Its name/title and category (e.g., Technology Adoption, Business Model Evolution, Segment Growth, Competitive Landscape Shift).\n"
                 "  - A clear description of the industry trend.\n"
                 "  - Quantitative data demonstrating the trend, covering recent history (e.g., last 24 months) and future outlook/forecasts (e.g., next 12-24 months) where available. Include relevant indicators (e.g., industry segment size/growth rates, technology penetration rates, pricing trends within the industry, competitor consolidation/exits).\n"
                 "  - Specific segment or product breakdowns if relevant and available.\n"
                 "  - A clear explanation of how this specific industry trend directly benefits the Company, ideally supported by quantitative links demonstrating the Company's alignment or outperformance relative to the trend (e.g., Company growth in benefiting segment vs. industry, market share in growing niche).\n"
                 "All extracted data points requiring citation must have a corresponding source reference ID linking to a footnote.\n"
                 "Ensure all footnotes provide precise source details: document name (e.g., Industry Report, Analyst Research), date, page number, and specific section/table.",
        "schema": {
            "overview": { # Optional overview
                "description": None, # string summarizing positive industry tailwinds
                "description_source_ref_id": None
            },
            "industry_trends": [ # List of top 3 positive trends
                { # Structure for ONE industry trend
                    "priority": None, # Optional number (1, 2, 3)
                    "name": None, # string (e.g., "Accelerating Industrial Digitalization")
                    "name_source_ref_id": None,
                    "category": None, # string (e.g., "Technology Adoption", "Business Model Evolution")
                    "category_source_ref_id": None,
                    "description": None, # string explaining the trend within the industry
                    "description_source_ref_id": None,
                    "supporting_data": { # Quantitative data for the trend
                         "historical_data": [ # List of historical data points/metrics
                              {
                                   "metric_name": None, # string (e.g., "Industrial IoT Device Installations")
                                   "values": [ # List of values over time
                                        {"period": None, "value": None, "unit": None, "growth_rate": None, "growth_unit": "%", "source_ref_id": None}
                                   ],
                                   "notes": None
                              }
                         ],
                         "forecast_data": [ # List of forecast data points/metrics
                              {
                                   "metric_name": None, # string
                                   "values": [ # List of values over time
                                        {"period": None, "value": None, "unit": None, "growth_rate": None, "growth_unit": "%", "source_ref_id": None}
                                   ],
                                   "notes": None
                              }
                         ],
                         "segment_or_product_breakdown": [ # Optional list of breakdowns within the industry
                              {
                                   "area_name": None, # string (e.g., "Smart Manufacturing Platforms")
                                   "value": None, # e.g., market size or growth rate
                                   "unit": None, # e.g., "billion USD", "% CAGR"
                                   "period": None, # e.g., "2023-2026F"
                                   "source_ref_id": None
                              }
                         ],
                         "notes": None # Optional notes on the data
                    },
                    "company_alignment_and_benefit": { # Explanation of the positive link to the company
                        "description": None, # string explaining how the company benefits specifically
                        "description_source_ref_id": None,
                        "company_performance_in_trend": { # Optional link to specific company performance data showing alignment/outperformance
                             "metric_name": None, # e.g., "Company Digital Offerings Growth Rate"
                             "value": None,
                             "unit": None,
                             "period": None,
                             "comparison_to_industry": None, # Optional string (e.g., "Outpacing industry growth of X%")
                             "source_ref_id": None
                        },
                        "notes": None
                    },
                    "notes": None # Optional overall trend notes
                }
            ],
            "footnotes": [ # Top-level list for all footnotes in this section
                { # Structure definition for ONE footnote
                    "id": None, "document": None, "page": None, "section": None, "date": None 
                }
            ]
        },
        "template": { # Example data aligned with refined schema
            "overview": {
                "description": "The Company operates within favorable industry dynamics, including accelerating digitalization, a shift towards integrated solutions driving higher margins, and strong demand for energy optimization technologies.", "description_source_ref_id": "ref1"
            },
            "industry_trends": [
                { # Example Trend 1: Digitalization
                    "priority": 1,
                    "name": "Accelerating Industrial Digitalization & IIoT Adoption", "name_source_ref_id": "ref2",
                    "category": "Technology Adoption", "category_source_ref_id": "ref2",
                    "description": "Rapid adoption of connected devices, software platforms, and data analytics within manufacturing and process industries creates significant demand for advanced automation solutions.", "description_source_ref_id": "ref2",
                    "supporting_data": {
                         "historical_data": [
                              {"metric_name": "Industrial Automation Software Market Size", "values": [ {"period": "2023", "value": 28.5, "unit": "billion USD", "growth_rate": 18.2, "growth_unit": "%", "source_ref_id": "ref2"}, {"period": "2024", "value": 34.2, "unit": "billion USD", "growth_rate": 20.0, "growth_unit": "%", "source_ref_id": "ref2"} ], "notes": None}
                         ],
                         "forecast_data": [
                               {"metric_name": "Industrial Automation Software Market Size", "values": [ {"period": "2025F", "value": 41.5, "unit": "billion USD", "growth_rate": 21.3, "growth_unit": "%", "source_ref_id": "ref2"} ], "notes": None}
                         ],
                         "segment_or_product_breakdown": [
                              {"area_name": "Smart Manufacturing Platforms", "value": 28.5, "unit": "% CAGR", "period": "2023-2026F", "source_ref_id": "ref2"},
                              {"area_name": "Industrial Data Analytics", "value": 32.4, "unit": "% CAGR", "period": "2023-2026F", "source_ref_id": "ref2"}
                         ],
                         "notes": "IIoT device installations forecast to grow >20% annually."
                    },
                    "company_alignment_and_benefit": {
                        "description": "The Company is well-positioned with its expanding portfolio of connected products and software, directly capturing this high-growth trend.", "description_source_ref_id": "ref2",
                        "company_performance_in_trend": { 
                             "metric_name": "Company Connected Product Revenue Growth", 
                             "value": 32.8, "unit": "%", "period": "FY23 YoY", 
                             "comparison_to_industry": "Significantly outpacing overall hardware market growth.", 
                             "source_ref_id": "ref3" # Assuming company report links this
                        },
                        "notes": "Supports strategic goal of increasing recurring revenue."
                    },
                    "notes": None
                },
                { # Example Trend 2: Solution Shift
                    "priority": 2,
                    "name": "Industry Shift from Hardware to Integrated Solutions", "name_source_ref_id": "ref3",
                    "category": "Business Model Evolution", "category_source_ref_id": "ref3",
                    "description": "Customers increasingly prefer integrated hardware/software/service solutions over standalone hardware, favoring vendors who offer higher-value, outcome-oriented packages.", "description_source_ref_id": "ref3",
                     "supporting_data": {
                         "historical_data": [
                              {"metric_name": "Solution Package Adoption Rate", "values": [ {"period": "2023", "value": 38.5, "unit": "% of new installs", "source_ref_id": "ref3"}, {"period": "2024", "value": 45.2, "unit": "% of new installs", "source_ref_id": "ref3"} ], "notes": "Accelerating trend."},
                              {"metric_name": "Industry Revenue Mix (Software/Services)", "values": [ {"period": "2023", "value": 37.5, "unit": "%", "source_ref_id": "ref3"}, {"period": "2024", "value": 41.8, "unit": "%", "source_ref_id": "ref3"} ], "notes": None}
                         ],
                         "forecast_data": [
                               {"metric_name": "Solution Package Adoption Rate", "values": [ {"period": "2025F", "value": 52.5, "unit": "% of new installs", "source_ref_id": "ref3"} ], "notes": None},
                               {"metric_name": "Industry Revenue Mix (Software/Services)", "values": [ {"period": "2025F", "value": 45.0, "unit": "%", "source_ref_id": "ref3"} ], "notes": None}
                         ],
                         "segment_or_product_breakdown": [],
                         "notes": "Shift driven by desire for single vendor accountability and faster ROI."
                    },
                     "company_alignment_and_benefit": {
                        "description": "Company's strategy aligns with this trend, shifting its own mix towards higher-margin software/services faster than the industry average.", "description_source_ref_id": "ref3",
                        "company_performance_in_trend": {
                            "metric_name": "Company Software/Service Revenue Mix", 
                            "value": 41.8, # Company's own mix % (Hypothetical matching industry for simplicity, likely different)
                            "unit": "%", 
                            "period": "FY24 YTD", 
                            "comparison_to_industry": "Shift rate outpacing industry average.", 
                            "source_ref_id": "ref3" 
                        },
                        "notes": "Supports margin expansion goals."
                    },
                    "notes": None
                },
                 { # Example Trend 3: Energy Focus
                    "priority": 3,
                    "name": "Prioritization of Energy Optimization Technologies", "name_source_ref_id": "ref4",
                    "category": "Industry Solution Focus", "category_source_ref_id": "ref4",
                    "description": "Energy efficiency and management have become critical purchasing criteria in industrial automation due to cost pressures and sustainability mandates.", "description_source_ref_id": "ref4",
                    "supporting_data": {
                         "historical_data": [
                              {"metric_name": "Industrial Energy Management Market Size", "values": [ {"period": "2023", "value": 35.8, "unit": "billion USD", "growth_rate": 18.5, "growth_unit": "%", "source_ref_id": "ref4"} ], "notes": None}
                         ],
                         "forecast_data": [
                              {"metric_name": "Industrial Energy Management Market Size", "values": [ {"period": "2025F", "value": 51.2, "unit": "billion USD", "growth_rate": 20.5, "growth_unit": "%", "source_ref_id": "ref4"} ], "notes": None}
                         ],
                         "segment_or_product_breakdown": [
                              {"area_name": "Energy Optimization Software", "value": 25.0, "unit": "% CAGR", "period": "2023-2026F", "source_ref_id": "ref4"}
                         ],
                         "notes": "Sustainability regulations amplify this trend."
                    },
                     "company_alignment_and_benefit": {
                        "description": "Company's leading Energy Optimization Technology directly addresses this key industry demand driver, providing a strong competitive advantage.", "description_source_ref_id": "ref5",
                        "company_performance_in_trend": {
                             "metric_name": "Company Energy Solution Revenue Growth", 
                             "value": 22.5, "unit": "%", "period": "FY23 YoY", 
                             "comparison_to_industry": "Exceeds overall market segment growth of 18.5%", 
                             "source_ref_id": "ref5"
                        },
                        "notes": "Supports premium pricing and market share gains in relevant applications."
                    },
                    "notes": None
                 }
            ],
            "footnotes": [
                 {"id": "ref1", "document": "Industry Analysis Report", "page": "3-5", "section": "Executive Summary", "date": "Mar 2025"},
                 {"id": "ref2", "document": "Industrial Digitalization Trends", "page": "12-18", "section": "IoT & Software", "date": "Feb 2025"},
                 {"id": "ref3", "document": "Automation Business Models Analysis", "page": "8-15", "section": "Solution Shift", "date": "Jan 2025"},
                 {"id": "ref4", "document": "Industrial Energy Management Report", "page": "22-30", "section": "Market Sizing", "date": "Mar 2025"},
                 {"id": "ref5", "document": "Company Performance Metrics Q1 2024", "page": "Internal", "section": "Segment Review", "date": "Apr 2024"}
            ]
        }
    },
# --- END: Section 20 Definition ---

# --- START: Section 21 Definition ---
    {
        "number": 21,
        "title": "Sellside Positioning - Competitive Positioning",
        "specs": "Extract an overview description summarizing the Company's key competitive advantages and overall market standing.\n"
                 "Identify and extract details on the 3 most important specific competitive advantages that positively impact the Company's economic performance, focusing on the next 12 months.\n"
                 "For each advantage, extract:\n"
                 "  - Its name/title and category (e.g., Technological Differentiation, Operational Excellence, Customer Loyalty, Brand Strength).\n"
                 "  - A clear description of the advantage.\n"
                 "  - Specific, quantitative evidence substantiating the advantage (e.g., performance metrics vs competitors, market share in niche, cost advantage data, pricing premium achieved, patent portfolio strength).\n"
                 "  - Data showing how this advantage translates directly into superior financial performance or market outcomes relative to specific competitors or industry benchmarks (e.g., higher margins, faster growth in relevant segment, higher win rates, better retention).\n"
                 "  - Customer validation points if available (e.g., retention rates, satisfaction scores, testimonials directly linked to the advantage).\n"
                 "Focus on measurable, defensible advantages, supported by data.\n"
                 "All extracted data points requiring citation must have a corresponding source reference ID linking to a footnote.\n"
                 "Ensure all footnotes provide precise source details: document name, date, page number, and specific section/table (often Competitive Analysis, MD&A, Investor Presentations).",
        "schema": {
            "overview": { # Optional overview
                "description": None, # string summarizing key competitive advantages
                "description_source_ref_id": None
            },
            "competitive_advantages": [ # List of top 3 advantages
                { # Structure for ONE key advantage
                    "priority": None, # Optional number (1, 2, 3)
                    "name": None, # string (e.g., "Proprietary Energy Optimization Technology")
                    "name_source_ref_id": None,
                    "category": None, # string (e.g., "Technological Differentiation", "Operational Excellence")
                    "category_source_ref_id": None,
                    "description": None, # string explaining the advantage
                    "description_source_ref_id": None,
                    "quantitative_evidence": [ # List of data points proving the advantage
                        {
                            "metric_name": None, # string (e.g., "Energy Efficiency Performance")
                            "company_value": None, # number or string
                            "unit": None, # string
                            "comparison_point": None, # string (e.g., "vs Competitor A", "vs Industry Avg")
                            "comparison_value": None, # number or string
                            "advantage_quantification": None, # string quantifying difference (e.g., "4.2 ppts better", "3.8 months faster")
                            "as_of": None, # string
                            "source_ref_id": None
                        }
                        # Include multiple metrics as needed
                    ],
                    "financial_impact_link": { # How it drives financial performance
                        "summary": None, # Optional string summary
                        "summary_source_ref_id": None,
                        "impacts": [ # List of financial impacts
                            {
                                "impact_area": None, # string (e.g., "Revenue Growth", "Margin Premium", "Win Rate")
                                "quantification": None, # string describing the financial benefit (e.g., "Contributes ~0.8 ppts to EBITDA margin", "Supports 5% price premium")
                                "supporting_metric_value": None, # Optional number/string (e.g., value of margin premium)
                                "supporting_metric_unit": None, # Optional string
                                "source_ref_id": None
                            }
                        ],
                        "notes": None
                    },
                    "customer_validation": { # Optional evidence from customers
                        "summary": None, # Optional string summary
                        "summary_source_ref_id": None,
                        "validation_points": [ # List of validation points
                             {
                                 "metric_name": None, # string (e.g., "Client Retention Rate (for this product)")
                                 "value": None, # number or string
                                 "unit": None, # string
                                 "comparison_point": None, # Optional string
                                 "comparison_value": None, # Optional number/string
                                 "source_ref_id": None
                             }
                        ],
                        "notes": None
                    },
                    "notes": None # Optional overall advantage notes
                }
            ],
            "footnotes": [ # Top-level list for all footnotes in this section
                { # Structure definition for ONE footnote
                    "id": None, "document": None, "page": None, "section": None, "date": None 
                }
            ]
        },
        "template": { # Example data aligned with refined schema
            "overview": {
                "description": "The Company maintains significant competitive advantages through its differentiated technology in energy optimization, superior operational scale and efficiency, and specialized system integration expertise, translating to demonstrable financial outperformance.", "description_source_ref_id": "ref1"
            },
            "competitive_advantages": [
                { # Example Advantage 1: Technology
                    "priority": 1,
                    "name": "Proprietary Energy Optimization Technology", "name_source_ref_id": "ref1",
                    "category": "Technological Differentiation", "category_source_ref_id": "ref1",
                    "description": "Patented algorithms (28 patents) deliver measurably superior energy efficiency vs competitors.", "description_source_ref_id": "ref2",
                    "quantitative_evidence": [
                        {"metric_name": "Energy Efficiency Performance", "company_value": 18.5, "unit": "% reduction", "comparison_point": "vs Competitor A", "comparison_value": "14.3%", "advantage_quantification": "4.2 ppts better", "as_of": "Q1 2024", "source_ref_id": "ref2"},
                        {"metric_name": "Customer ROI Timeline", "company_value": 14.7, "unit": "months", "comparison_point": "vs Industry Avg", "comparison_value": "22.5 months", "advantage_quantification": "7.8 months faster", "as_of": "Q1 2024", "source_ref_id": "ref2"},
                        {"metric_name": "Market Share (Energy Mgmt Segment)", "company_value": 18.9, "unit": "%", "comparison_point": None, "comparison_value": None, "advantage_quantification": "+2.5 ppts gain in 12 months", "as_of": "FY 2023", "source_ref_id": "ref2"}
                    ],
                    "financial_impact_link": {
                        "summary": "Drives premium pricing, higher win rates, and significant revenue.", "summary_source_ref_id": "ref3",
                        "impacts": [
                            {"impact_area": "Margin Premium", "quantification": "Supports ~8 ppt gross margin premium vs standard hardware.", "supporting_metric_value": None, "supporting_metric_unit": None, "source_ref_id": "ref3"},
                            {"impact_area": "Win Rate", "quantification": "Win rate 18 ppts higher (65% vs 47%) when efficiency is key.", "supporting_metric_value": None, "supporting_metric_unit": None, "source_ref_id": "ref3"},
                            {"impact_area": "Revenue Contribution", "quantification": "$485M revenue in FY23, growing 22.5% YoY.", "supporting_metric_value": 485, "supporting_metric_unit": "M USD", "source_ref_id": "ref3"}
                        ],
                        "notes": None
                    },
                    "customer_validation": {
                         "summary": "High retention and satisfaction scores validate value proposition.", "summary_source_ref_id": "ref3",
                         "validation_points": [
                              {"metric_name": "Client Retention Rate (Energy)", "value": 95.8, "unit": "%", "comparison_point": "vs Industry Avg", "comparison_value": "82.5%", "source_ref_id": "ref3"},
                              {"metric_name": "Cross-Sell Rate", "value": 65, "unit": "% of energy customers buy other products", "comparison_point": "vs Industry Avg", "comparison_value": "42%", "source_ref_id": "ref3"}
                         ],
                         "notes": None
                    },
                    "notes": "Technology protected by strong IP portfolio."
                },
                { # Example Advantage 2: Operations
                    "priority": 2,
                    "name": "Global Manufacturing Scale & Flexibility", "name_source_ref_id": "ref1",
                    "category": "Operational Excellence", "category_source_ref_id": "ref1",
                    "description": "Network of 8 global facilities enables scale economies (cost advantage) and regional customization.", "description_source_ref_id": "ref4",
                    "quantitative_evidence": [
                        {"metric_name": "Manufacturing Cost Advantage", "company_value": 12.5, "unit": "% lower", "comparison_point": "vs Regional Avg", "comparison_value": None, "advantage_quantification": None, "as_of": "FY 2023", "source_ref_id": "ref4"},
                        {"metric_name": "On-Time Delivery Rate", "company_value": 95.8, "unit": "%", "comparison_point": "vs Industry Avg", "comparison_value": "87.5%", "advantage_quantification": "8.3 ppts better", "as_of": "Q1 2024", "source_ref_id": "ref4"},
                        {"metric_name": "Avg Product Changeover Time", "company_value": 3.2, "unit": "hours", "comparison_point": "vs Industry Benchmark", "comparison_value": "8.5 hours", "advantage_quantification": "62% faster", "as_of": "FY 2023", "source_ref_id": "ref4"}
                    ],
                     "financial_impact_link": {
                        "summary": "Translates to higher gross margins and pricing flexibility.", "summary_source_ref_id": "ref5",
                        "impacts": [
                             {"impact_area": "Gross Margin", "quantification": "Company Gross Margin 3.5 ppts above industry avg.", "supporting_metric_value": 42.5, "supporting_metric_unit": "% (Company GM)", "source_ref_id": "ref5"},
                             {"impact_area": "Pricing Power", "quantification": "Maintains 3-5% price premium despite cost advantage.", "supporting_metric_value": None, "supporting_metric_unit": None, "source_ref_id": "ref5"}
                        ],
                        "notes": None
                    },
                     "customer_validation": {
                        "summary": "Customers value faster delivery and customization options.", "summary_source_ref_id": "ref5",
                        "validation_points": [
                            {"metric_name": "Delivery Time Advantage", "value": "Avg 4.3 weeks faster", "unit": "weeks", "comparison_point": "vs centralized competitors", "source_ref_id": "ref5"},
                             {"metric_name": "Customization Fulfillment Rate", "value": 72, "unit": "% fulfilled w/o ECO", "comparison_point": "vs Industry Avg", "comparison_value": "35%", "source_ref_id": "ref5"}
                        ],
                        "notes": None
                     },
                    "notes": None
                },
                 { # Example Advantage 3: Integration Expertise
                    "priority": 3,
                    "name": "Legacy & Modern System Integration Expertise", "name_source_ref_id": "ref1",
                    "category": "Technical Capability", "category_source_ref_id": "ref1",
                    "description": "Specialized engineering team (160 certified) skilled at integrating new tech with diverse older systems, enabling incremental customer modernization.", "description_source_ref_id": "ref6",
                     "quantitative_evidence": [
                        {"metric_name": "Supported Legacy Protocols", "company_value": 45, "unit": "protocols", "comparison_point": "vs Competitor A", "comparison_value": "32", "advantage_quantification": "40% more", "as_of": "Q1 2024", "source_ref_id": "ref6"},
                        {"metric_name": "Integration Success Rate", "company_value": 94.5, "unit": "%", "comparison_point": "vs Industry Avg", "comparison_value": "72%", "advantage_quantification": "22.5 ppts higher", "as_of": "FY 2023", "source_ref_id": "ref6"},
                        {"metric_name": "Avg Integration Timeline", "company_value": 4.2, "unit": "months", "comparison_point": "vs Industry Avg", "comparison_value": "7.5 months", "advantage_quantification": "44% faster", "as_of": "FY 2023", "source_ref_id": "ref6"}
                     ],
                     "financial_impact_link": {
                        "summary": "Drives high-margin service revenue and customer stickiness.", "summary_source_ref_id": "ref7",
                        "impacts": [
                            {"impact_area": "Integration Services Revenue", "quantification": "$215M revenue in FY23, growing 18.5% YoY.", "supporting_metric_value": 215, "supporting_metric_unit": "M USD", "source_ref_id": "ref7"},
                            {"impact_area": "Customer Retention", "quantification": "Supports 92% service contract renewal rate vs 78% industry avg.", "supporting_metric_value": 92, "supporting_metric_unit": "%", "source_ref_id": "ref7"}
                        ],
                         "notes": None
                    },
                    "customer_validation": {
                        "summary": "Reduces customer implementation costs significantly.", "summary_source_ref_id": "ref6",
                        "validation_points": [{"metric_name": "Implementation Cost Saving", "value": "50-65%", "unit": "% lower", "comparison_point": "vs Full System Replacement", "source_ref_id": "ref6"}],
                         "notes": None
                    },
                    "notes": None
                }
            ],
            "footnotes": [
                {"id": "ref1", "document": "Competitive Positioning Assessment", "page": "8-15", "section": "Core Strengths", "date": "Mar 2025"},
                {"id": "ref2", "document": "Energy Management Solutions Performance", "page": "12-18", "section": "Benchmarking", "date": "Feb 2025"},
                {"id": "ref3", "document": "Financial Performance Review FY2023", "page": "Internal", "section": "Segment Profitability", "date": "Jan 2025"},
                {"id": "ref4", "document": "Manufacturing Capabilities Report", "page": "5-15", "section": "Benchmarking", "date": "Dec 2024"},
                {"id": "ref5", "document": "Operational Excellence Analysis", "page": "18-25", "section": "Delivery & Cost", "date": "Mar 2025"},
                {"id": "ref6", "document": "Integration Capabilities Assessment", "page": "22-30", "section": "Performance Metrics", "date": "Dec 2023"},
                {"id": "ref7", "document": "Service Segment Performance Report", "page": "10-18", "section": "Integration Business", "date": "Jan 2025"}
            ]
        }
    },
# --- END: Section 21 Definition ---

# --- START: Section 22 Definition ---
    {
        "number": 22,
        "title": "Sellside Positioning - Operating Performance",
        "specs": "Extract an overview description highlighting the Company's exceptional operating performance and execution capabilities over the last 24 months.\n"
                 "Identify and extract details on the 3 most important operating performance metrics or achievements demonstrating this strength.\n"
                 "Focus on measurable, company-specific KPIs beyond standard financials (e.g., market share gains in key segments, strong volume growth, improving pricing realization, customer value expansion like ARPU growth, efficiency gains like utilization or OTD rates).\n"
                 "For each key metric/achievement, extract:\n"
                 "  - Its name/title and category (e.g., Market Position, Customer Value, Operational Excellence).\n"
                 "  - A clear description of the performance or achievement.\n"
                 "  - Quantitative data demonstrating the performance trend over the last 24 months (preferably quarterly if available), including growth rates or improvement percentages.\n"
                 "  - Comparison to relevant benchmarks (e.g., prior periods, internal targets, industry growth rates) to emphasize outperformance.\n"
                 "  - Analysis of the key drivers behind this strong operating performance (e.g., specific initiatives, product success, team execution).\n"
                 "  - The direct link or contribution of this operating performance to positive financial outcomes (e.g., revenue growth acceleration, margin support, cash flow improvement).\n"
                 "  - Commentary on the sustainability or future trajectory of this performance, if available.\n"
                 "All extracted data points requiring citation must have a corresponding source reference ID linking to a footnote.\n"
                 "Ensure all footnotes provide precise source details: document name, date, page number, and specific section/table (often MD&A, Earnings Calls, Investor Presentations).",
        "schema": {
            "overview": { # Optional overview
                "description": None, # string summarizing strong operating performance
                "description_source_ref_id": None
            },
            "key_operating_highlights": [ # List of top 3 performance highlights
                { # Structure for ONE highlight
                    "priority": None, # Optional number (1, 2, 3)
                    "name": None, # string (e.g., "Premium Segment Market Share Expansion")
                    "name_source_ref_id": None,
                    "category": None, # string (e.g., "Market Position", "Customer Value", "Operational Excellence")
                    "category_source_ref_id": None,
                    "description": None, # string describing the achievement/performance
                    "description_source_ref_id": None,
                    "performance_data": [ # List of metrics quantifying the performance
                        {
                            "metric_name": None, # string (e.g., "Premium Ind. Automation Market Share")
                            "trend_data": [ # List of values over time
                                {"period": None, "value": None, "unit": None, "source_ref_id": None}
                            ],
                            "growth_or_improvement": None, # Optional string quantifying change (e.g., "+3.1 ppts over 24 months")
                            "growth_or_improvement_source_ref_id": None,
                            "comparison_to_benchmark": { # Optional comparison
                                 "benchmark_name": None, # string (e.g., "Industry Growth Rate", "Competitor A Share Change")
                                 "benchmark_value": None,
                                 "unit": None,
                                 "outperformance_description": None, # string (e.g., "Outperformed industry by 8.8 ppts")
                                 "source_ref_id": None
                            },
                            "notes": None
                        }
                        # Include multiple relevant metrics
                    ],
                    "performance_drivers": [ # List of key reasons for success
                        {
                            "driver": None, # string (e.g., "New Product Introduction (X1000 series)")
                            "explanation": None, # Optional string with more detail
                            "source_ref_id": None
                        }
                    ],
                    "financial_impact_link": { # How it contributes to financials
                        "description": None, # string explaining link (e.g., "Drives high-margin revenue growth")
                        "quantification": None, # Optional string (e.g., "Contributed ~65% of total revenue growth in FY23")
                        "quantification_source_ref_id": None,
                        "notes": None
                    },
                     "future_trajectory_commentary": { # Optional outlook based on this performance
                          "description": None, # string
                          "description_source_ref_id": None
                     },
                    "notes": None # Optional overall highlight notes
                }
            ],
            "footnotes": [ # Top-level list for all footnotes in this section
                { # Structure definition for ONE footnote
                    "id": None, "document": None, "page": None, "section": None, "date": None 
                }
            ]
        },
        "template": { # Example data aligned with refined schema
            "overview": {
                "description": "The Company demonstrates exceptional operating execution, highlighted by significant market share gains in premium segments, strong growth in revenue per customer, and notable manufacturing efficiency improvements over the past 24 months.", "description_source_ref_id": "ref1"
            },
            "key_operating_highlights": [
                { # Example Highlight 1: Market Share
                    "priority": 1,
                    "name": "Premium Segment Market Share Expansion", "name_source_ref_id": "ref1",
                    "category": "Market Position", "category_source_ref_id": "ref1",
                    "description": "Substantial share gains achieved in high-margin premium Industrial Automation and Energy Management segments, outpacing competitors.", "description_source_ref_id": "ref2",
                    "performance_data": [
                        {
                            "metric_name": "Premium Ind. Automation Mkt Share", "metric_name_source_ref_id": "ref2",
                            "trend_data": [ 
                                {"period": "Q1 2022", "value": 15.8, "unit": "%", "source_ref_id": "ref2"}, # Example baseline
                                {"period": "Q1 2024", "value": 18.9, "unit": "%", "source_ref_id": "ref2"}
                            ],
                            "growth_or_improvement": "+3.1 ppts over 24 months", "growth_or_improvement_source_ref_id": "ref2",
                            "comparison_to_benchmark": {"benchmark_name": "Total Addressable Market Growth", "benchmark_value": 5.3, "unit": "% (FY23)", "outperformance_description": "Company segment growth significantly higher", "source_ref_id": "ref2"},
                            "notes": None
                        },
                        { # Add another metric for this highlight
                            "metric_name": "Energy Mgmt Solutions Mkt Share", "metric_name_source_ref_id": "ref2",
                            "trend_data": [ 
                                {"period": "FY 2022", "value": 16.4, "unit": "%", "source_ref_id": "ref2"}, 
                                {"period": "FY 2023", "value": 18.9, "unit": "%", "source_ref_id": "ref2"}
                            ],
                            "growth_or_improvement": "+2.5 ppts YoY", "growth_or_improvement_source_ref_id": "ref2",
                             "comparison_to_benchmark": None, # Example no direct comparison cited
                            "notes": "Driven by proprietary technology advantage."
                        }
                    ],
                    "performance_drivers": [
                        {"driver": "New Product Introduction Success", "explanation": "X1000 series and 4th gen energy platform gained rapid adoption.", "source_ref_id": "ref2"},
                        {"driver": "Targeted Sales Initiatives", "explanation": "Specialized sales teams focused on premium segments.", "source_ref_id": "ref3"}
                    ],
                    "financial_impact_link": {
                        "description": "Market share gains disproportionately contribute to revenue growth and margin expansion due to higher segment profitability.", "description_source_ref_id": "ref3",
                        "quantification": "~65% of overall revenue growth (FY23) attributed to share gains; premium segments carry 8-12 ppt higher gross margin.", "quantification_source_ref_id": "ref3"},
                    "future_trajectory_commentary": {
                         "description": "Projected continued share gains of 1.5-2.0 ppts over next 12 months.", "description_source_ref_id": "ref3"
                     },
                    "notes": None
                },
                { # Example Highlight 2: Customer Value
                    "priority": 2,
                    "name": "Significant Revenue Per Customer Expansion", "name_source_ref_id": "ref1",
                    "category": "Customer Value", "category_source_ref_id": "ref1",
                    "description": "Successfully increased average revenue per customer through cross-selling, upselling (solutions), and service attachment.", "description_source_ref_id": "ref4",
                    "performance_data": [
                         {
                            "metric_name": "Avg Annual Revenue Per Customer", "metric_name_source_ref_id": "ref4",
                            "trend_data": [ 
                                {"period": "FY 2022", "value": 52300, "unit": "USD", "source_ref_id": "ref4"}, 
                                {"period": "FY 2023", "value": 54800, "unit": "USD", "source_ref_id": "ref4"}
                            ],
                            "growth_or_improvement": "+4.8% YoY (FY23)", "growth_or_improvement_source_ref_id": "ref4",
                             "comparison_to_benchmark": {"benchmark_name": "Peer Average ARPU Growth", "benchmark_value": 2.5, "unit": "%", "outperformance_description": "Nearly 2x peer average growth", "source_ref_id": "ref4"},
                            "notes": "Continued growth to $56.8k annualized in Q1 2024."
                         },
                         {
                            "metric_name": "Avg Products Per Customer", "metric_name_source_ref_id": "ref4",
                            "trend_data": [ 
                                {"period": "FY 2022", "value": 1.8, "unit": "categories", "source_ref_id": "ref4"}, 
                                {"period": "FY 2023", "value": 2.3, "unit": "categories", "source_ref_id": "ref4"}
                            ],
                            "growth_or_improvement": "+27.8% YoY (FY23)", "growth_or_improvement_source_ref_id": "ref4",
                             "comparison_to_benchmark": {"benchmark_name": "Industry Average", "benchmark_value": 1.7, "unit": "categories", "outperformance_description": "Significantly higher cross-sell penetration", "source_ref_id": "ref4"},
                            "notes": None
                         }
                    ],
                     "performance_drivers": [
                         {"driver": "Solution Selling Approach", "explanation": "Bundling hardware, software, services increases initial deal value.", "source_ref_id": "ref4"},
                         {"driver": "Customer Success Program", "explanation": "Proactive engagement identifies upsell opportunities.", "source_ref_id": "ref4"}
                     ],
                    "financial_impact_link": {
                        "description": "Expanding value from existing customer base improves sales efficiency and profitability.", "description_source_ref_id": "ref5",
                        "quantification": "Growth from existing customers offers ~85% higher ROI vs new customer acquisition.", "quantification_source_ref_id": "ref5"
                    },
                    "future_trajectory_commentary": {"description": "Targeting continued 6-8% annual ARPU growth.", "description_source_ref_id": "ref5"},
                    "notes": None
                },
                 { # Example Highlight 3: Efficiency
                    "priority": 3,
                    "name": "Manufacturing Efficiency and Output Gains", "name_source_ref_id": "ref1",
                    "category": "Operational Excellence", "category_source_ref_id": "ref1",
                    "description": "Significant improvements in manufacturing productivity, cost per unit, and capacity utilization while maintaining high quality.", "description_source_ref_id": "ref6",
                     "performance_data": [
                         {
                            "metric_name": "Manufacturing Capacity Utilization", "metric_name_source_ref_id": "ref6",
                            "trend_data": [ {"period": "FY 2022", "value": 82.1, "unit": "%", "source_ref_id": "ref6"}, {"period": "Q1 2024", "value": 87.2, "unit": "%", "source_ref_id": "ref6"} ],
                            "growth_or_improvement": "+5.1 ppts over 9 quarters", "growth_or_improvement_source_ref_id": "ref6",
                             "comparison_to_benchmark": {"benchmark_name": "Industry Average", "benchmark_value": 75.5, "unit": "%", "outperformance_description": "11.7 ppts above average", "source_ref_id": "ref6"},
                             "notes": None
                         },
                         {
                            "metric_name": "Manufacturing Cost Per Unit Index", "metric_name_source_ref_id": "ref6",
                            "trend_data": [ {"period": "FY 2022", "value": 100, "unit": "index", "source_ref_id": "ref6"}, {"period": "Q1 2024", "value": 94.5, "unit": "index", "source_ref_id": "ref6"} ],
                            "growth_or_improvement": "-5.5% reduction over 9 quarters", "growth_or_improvement_source_ref_id": "ref6",
                             "comparison_to_benchmark": {"benchmark_name": "Industry Average Cost Trend", "benchmark_value": "+2.5", "unit": "% increase over same period", "outperformance_description": "Significant relative cost improvement", "source_ref_id": "ref6"},
                             "notes": None
                         }
                     ],
                     "performance_drivers": [
                         {"driver": "Lean Manufacturing Initiatives", "explanation": "Reduced waste and improved workflows.", "source_ref_id": "ref7"},
                         {"driver": "Targeted Automation Investments", "explanation": "Upgraded key production lines.", "source_ref_id": "ref7"}
                     ],
                    "financial_impact_link": {
                        "description": "Directly contributes to gross margin improvement and fixed cost leverage.", "description_source_ref_id": "ref7",
                        "quantification": "Contributed ~0.7 ppts to Gross Margin improvement in FY23.", "quantification_source_ref_id": "ref7"},
                    "future_trajectory_commentary": {"description": "Further 2.0-2.5% cost reduction targeted over next 12 months.", "description_source_ref_id": "ref7"},
                    "notes": None
                 }
            ],
            "footnotes": [
                 {"id": "ref1", "document": "Operational Performance Assessment", "page": "3-6", "section": "Executive Summary", "date": "Mar 2025"},
                 {"id": "ref2", "document": "Market Share Analysis Report", "page": "10-15", "section": "Segment Share Trends", "date": "Feb 2025"},
                 {"id": "ref3", "document": "Strategic Growth Analysis", "page": "22-28", "section": "Market Share Impact", "date": "Jan 2025"},
                 {"id": "ref4", "document": "Customer Metrics Analysis", "page": "8-16", "section": "Customer Value Growth", "date": "Mar 2025"},
                 {"id": "ref5", "document": "Revenue Growth Drivers Report", "page": "15-22", "section": "Cross-Selling Impact", "date": "Feb 2025"},
                 {"id": "ref6", "document": "Manufacturing Performance Report", "page": "5-18", "section": "Production Metrics", "date": "Jan 2025"},
                 {"id": "ref7", "document": "Operational Efficiency Analysis", "page": "12-20", "section": "Cost Improvement Initiatives", "date": "Mar 2025"}
            ]
        }
    },
# --- END: Section 22 Definition ---

# --- START: Section 23 Definition ---
    {
        "number": 23,
        "title": "Sellside Positioning - Financial Performance",
        "specs": "Extract an overview description highlighting the Company's exceptional financial performance and achievements over the last 24 months.\n"
                 "Identify and extract details on the 3 most important financial achievements or metrics demonstrating this superior performance.\n"
                 "Focus on key metrics demonstrating growth, profitability, and particularly strong cash flow generation (e.g., Revenue Growth + Margin Expansion, Superior Cash Conversion, Industry-Leading ROIC).\n"
                 "For each key achievement/metric, extract:\n"
                 "  - Its name/title and category (e.g., Growth & Profitability, Cash Generation, Capital Efficiency).\n"
                 "  - A clear description of the achievement.\n"
                 "  - Quantitative data demonstrating the performance over the last 24 months (preferably quarterly if available), including growth rates or levels achieved.\n"
                 "  - Explicit comparisons to relevant industry benchmarks and specific key competitors, quantifying the Company's outperformance.\n"
                 "  - Analysis of the key drivers enabling this financial achievement (linking back to operational performance or strategic execution where possible).\n"
                 "  - Discussion of how this financial strength translates to shareholder value or strategic flexibility (e.g., funding growth, debt paydown, shareholder returns).\n"
                 "Present the information in a compelling 'sellside' manner, emphasizing strengths and outperformance, but always backed by verifiable data.\n"
                 "All extracted data points requiring citation must have a corresponding source reference ID linking to a footnote.\n"
                 "Ensure all footnotes provide precise source details: document name (e.g., Earnings Release, Annual Report, Investor Presentation), date, page number, and specific section/table.",
        "schema": {
            "overview": { # Optional overview
                "description": None, # string summarizing exceptional financial performance
                "description_source_ref_id": None
            },
            "financial_highlights": [ # List of top 3 financial achievements
                { # Structure for ONE highlight
                    "priority": None, # Optional number (1, 2, 3)
                    "name": None, # string (e.g., "Accelerating Revenue Growth with Margin Expansion")
                    "name_source_ref_id": None,
                    "category": None, # string (e.g., "Growth & Profitability", "Cash Generation")
                    "category_source_ref_id": None,
                    "description": None, # string describing the achievement
                    "description_source_ref_id": None,
                    "performance_data": [ # List of metrics quantifying the achievement
                        {
                            "metric_name": None, # string (e.g., "Quarterly Revenue Growth (YoY)")
                            "trend_data": [ # List of values over time
                                {"period": None, "value": None, "unit": None, "source_ref_id": None}
                            ],
                            "key_period_highlight": None, # Optional string highlighting peak/recent (e.g., "14.8% in Q1 2024")
                            "key_period_highlight_source_ref_id": None,
                            "notes": None
                        }
                        # Include multiple relevant metrics (e.g., Revenue Growth, EBITDA Margin Trend)
                    ],
                    "peer_comparison": { # Quantitative comparison to peers/industry
                        "summary": None, # Optional summary string
                        "summary_source_ref_id": None,
                        "comparisons": [ # List of specific comparisons
                            {
                                 "metric_name": None, # string (e.g., "Revenue Growth (FY 2023)")
                                 "company_value": None,
                                 "unit": "%",
                                 "peer_average_value": None,
                                 "outperformance_value": None, # number (e.g., 5.8)
                                 "outperformance_unit": "percentage points",
                                 "peer_ranking": None, # Optional string (e.g., "1st out of 5")
                                 "source_ref_id": None
                            }
                            # Include comparisons for key metrics (Rev Growth, Margin, EBITDA Growth etc.)
                        ],
                        "notes": None
                    },
                    "achievement_drivers": [ # List of key reasons for this financial success
                        {
                            "driver": None, # string (e.g., "Mix Shift to Higher-Margin Products")
                            "explanation": None, # Optional string quantifying contribution
                            "source_ref_id": None
                        }
                    ],
                    "implications_for_value": { # Link to shareholder value / flexibility
                         "description": None, # string
                         "description_source_ref_id": None,
                         "examples": [], # Optional list of strings (e.g., "Supports dividend growth", "Enables strategic M&A")
                         "examples_source_ref_id": None
                    },
                    "notes": None # Optional overall highlight notes
                }
            ],
            "footnotes": [ # Top-level list for all footnotes in this section
                { # Structure definition for ONE footnote
                    "id": None, "document": None, "page": None, "section": None, "date": None 
                }
            ]
        },
        "template": { # Example data aligned with refined schema
            "overview": {
                "description": "The Company exhibits exceptional financial strength, characterized by accelerating top-line growth coupled with margin expansion, superior cash flow conversion significantly exceeding peers, and industry-leading returns on invested capital, demonstrating effective execution and capital discipline.", "description_source_ref_id": "ref1"
            },
            "financial_highlights": [
                { # Example Highlight 1: Growth & Profitability
                    "priority": 1,
                    "name": "Accelerating Revenue Growth with Margin Expansion", "name_source_ref_id": "ref1",
                    "category": "Growth & Profitability", "category_source_ref_id": "ref1",
                    "description": "Demonstrated ability to consistently accelerate revenue growth while simultaneously expanding EBITDA margins, showcasing strong market demand and operational leverage.", "description_source_ref_id": "ref2",
                    "performance_data": [
                        {
                            "metric_name": "Quarterly Revenue Growth (YoY)", "metric_name_source_ref_id": "ref2",
                            "trend_data": [ {"period": "Q1 2023", "value": 13.8, "unit": "%", "source_ref_id": "ref2"}, {"period": "Q4 2023", "value": 13.9, "unit": "%", "source_ref_id": "ref2"}, {"period": "Q1 2024", "value": 14.8, "unit": "%", "source_ref_id": "ref2"} ],
                            "key_period_highlight": "Accelerated to 14.8% in Q1 2024", "key_period_highlight_source_ref_id": "ref2",
                            "notes": None
                        },
                         {
                            "metric_name": "Quarterly EBITDA Margin", "metric_name_source_ref_id": "ref2",
                            "trend_data": [ {"period": "Q1 2023", "value": 22.0, "unit": "%", "source_ref_id": "ref2"}, {"period": "Q4 2023", "value": 23.0, "unit": "%", "source_ref_id": "ref2"}, {"period": "Q1 2024", "value": 23.0, "unit": "%", "source_ref_id": "ref2"} ],
                            "key_period_highlight": "+1.0 ppt expansion over last 4 quarters reported", "key_period_highlight_source_ref_id": "ref2",
                            "notes": None
                        }
                    ],
                    "peer_comparison": {
                        "summary": "Company significantly outperforms peers on both growth and profitability expansion.", "summary_source_ref_id": "ref3",
                        "comparisons": [
                            {"metric_name": "Revenue Growth (FY 2023)", "company_value": 14.1, "unit": "%", "peer_average_value": 8.3, "outperformance_value": 5.8, "outperformance_unit": "ppts", "peer_ranking": "1st of 5", "source_ref_id": "ref3"},
                            {"metric_name": "EBITDA Growth (FY 2023)", "company_value": 18.8, "unit": "%", "peer_average_value": 11.5, "outperformance_value": 7.3, "outperformance_unit": "ppts", "peer_ranking": "1st of 5", "source_ref_id": "ref3"},
                            {"metric_name": "EBITDA Margin Expansion (FY22-FY23)", "company_value": 0.9, "unit": "ppts", "peer_average_value": -0.3, "outperformance_value": 1.2, "outperformance_unit": "ppts", "peer_ranking": "1st of 5", "source_ref_id": "ref3"}
                        ],
                        "notes": None
                    },
                    "achievement_drivers": [
                        {"driver": "Mix Shift to Software/Services", "explanation": "Contributed ~35% of margin expansion", "source_ref_id": "ref3"},
                        {"driver": "Premium Segment Share Gains", "explanation": "Higher margin sales grew faster than overall average", "source_ref_id": "ref3"}
                    ],
                    "implications_for_value": {"description": "Demonstrates strong competitive positioning and operational leverage, supporting premium valuation.", "description_source_ref_id": "ref1", "examples": [], "examples_source_ref_id": None},
                    "notes": None
                },
                { # Example Highlight 2: Cash Flow
                    "priority": 2,
                    "name": "Superior Cash Flow Generation and Conversion", "name_source_ref_id": "ref1",
                    "category": "Cash Generation", "category_source_ref_id": "ref1",
                    "description": "Consistently converts a high percentage of earnings into free cash flow, significantly exceeding peer averages and providing substantial financial flexibility.", "description_source_ref_id": "ref4",
                     "performance_data": [
                         {
                            "metric_name": "Cash Conversion Ratio (OCF/EBITDA)", "metric_name_source_ref_id": "ref4",
                            "trend_data": [ {"period": "FY 2022", "value": 85.8, "unit": "%", "source_ref_id": "ref4"}, {"period": "FY 2023", "value": 87.5, "unit": "%", "source_ref_id": "ref4"} ],
                            "key_period_highlight": "Improved 1.7 ppts YoY in FY23", "key_period_highlight_source_ref_id": "ref4",
                            "notes": "Driven by working capital improvements."
                        },
                          {
                            "metric_name": "Free Cash Flow (FCF) Margin", "metric_name_source_ref_id": "ref4",
                            "trend_data": [ {"period": "FY 2022", "value": 11.5, "unit": "%", "source_ref_id": "ref4"}, {"period": "FY 2023", "value": 13.1, "unit": "%", "source_ref_id": "ref4"} ],
                            "key_period_highlight": "Improved 1.6 ppts YoY in FY23", "key_period_highlight_source_ref_id": "ref4",
                            "notes": None
                        }
                     ],
                    "peer_comparison": {
                         "summary": "Company leads peers significantly in cash conversion and FCF generation.", "summary_source_ref_id": "ref5",
                         "comparisons": [
                            {"metric_name": "Cash Conversion (FY 2023)", "company_value": 87.5, "unit": "%", "peer_average_value": 78.2, "outperformance_value": 9.3, "outperformance_unit": "ppts", "peer_ranking": "1st of 5", "source_ref_id": "ref5"},
                            {"metric_name": "FCF Margin (FY 2023)", "company_value": 13.1, "unit": "%", "peer_average_value": 9.5, "outperformance_value": 3.6, "outperformance_unit": "ppts", "peer_ranking": "1st of 5", "source_ref_id": "ref5"}
                         ],
                         "notes": None
                    },
                     "achievement_drivers": [
                        {"driver": "Working Capital Optimization", "explanation": "Cash Conversion Cycle reduced by 8.5 days YoY", "source_ref_id": "ref5"},
                        {"driver": "Capital Expenditure Efficiency", "explanation": "Capex/Revenue ratio decreased while growing output", "source_ref_id": "ref5"}
                    ],
                     "implications_for_value": {
                         "description": "Strong FCF enables balanced capital allocation: funding growth, debt reduction ($85M in FY23), and shareholder returns ($290M in FY23).", "description_source_ref_id": "ref5",
                         "examples": ["Supports consistent dividend increases", "Provides capacity for strategic M&A"], "examples_source_ref_id": None
                     },
                    "notes": None
                },
                 { # Example Highlight 3: ROIC
                    "priority": 3,
                    "name": "Industry-Leading Return on Invested Capital (ROIC)", "name_source_ref_id": "ref1",
                    "category": "Capital Efficiency", "category_source_ref_id": "ref1",
                    "description": "Consistently generates returns significantly above cost of capital and peer averages, indicating efficient capital deployment and strong competitive moat.", "description_source_ref_id": "ref6",
                    "performance_data": [
                         {
                            "metric_name": "ROIC", "metric_name_source_ref_id": "ref6",
                            "trend_data": [ {"period": "FY 2022", "value": 17.8, "unit": "%", "source_ref_id": "ref6"}, {"period": "FY 2023", "value": 19.8, "unit": "%", "source_ref_id": "ref6"}, {"period": "Q1 2024 Ann.", "value": 22.3, "unit": "%", "source_ref_id": "ref6"} ],
                            "key_period_highlight": "Reached record 22.3% (annualized) in Q1 2024", "key_period_highlight_source_ref_id": "ref6",
                            "notes": "Consistent improvement trend."
                        },
                         {
                            "metric_name": "ROIC vs WACC Spread", "metric_name_source_ref_id": "ref6",
                            "trend_data": [ {"period": "FY 2022", "value": 9.3, "unit": "ppts", "source_ref_id": "ref6"}, {"period": "FY 2023", "value": 10.5, "unit": "ppts", "source_ref_id": "ref6"} ],
                            "key_period_highlight": "Spread widened by 1.2 ppts in FY23", "key_period_highlight_source_ref_id": "ref6",
                            "notes": "Demonstrates significant economic value creation."
                        }
                    ],
                    "peer_comparison": {
                         "summary": "Company ROIC substantially outperforms peer group.", "summary_source_ref_id": "ref7",
                        "comparisons": [
                            {"metric_name": "ROIC (FY 2023)", "company_value": 19.8, "unit": "%", "peer_average_value": 13.5, "outperformance_value": 6.3, "outperformance_unit": "ppts", "peer_ranking": "1st of 5", "source_ref_id": "ref7"}
                        ],
                         "notes": None
                    },
                     "achievement_drivers": [
                        {"driver": "Focus on High-Return Segments", "explanation": "Shift towards software/services with higher ROIC.", "source_ref_id": "ref7"},
                        {"driver": "Asset Turnover Improvement", "explanation": "Capital Turnover increased from 1.42x to 1.48x (FY22-FY23).", "source_ref_id": "ref7"}
                     ],
                    "implications_for_value": {
                        "description": "Superior ROIC justifies premium valuation multiples and indicates sustainable competitive advantages.", "description_source_ref_id": "ref7",
                        "examples": [], "examples_source_ref_id": None
                    },
                    "notes": None
                 }
            ],
            "footnotes": [
                 {"id": "ref1", "document": "Financial Performance Summary", "page": "3-5", "section": "Executive Overview", "date": "Mar 2025"},
                 {"id": "ref2", "document": "Q1 2024 Earnings Release", "page": "5-8", "section": "Financial Highlights", "date": "Apr 25, 2024"},
                 {"id": "ref3", "document": "Growth Analysis Report", "page": "10-15", "section": "Peer Comparison", "date": "Feb 2024"},
                 {"id": "ref4", "document": "Cash Flow Performance Analysis", "page": "8-12", "section": "Cash Flow Metrics", "date": "Mar 2024"},
                 {"id": "ref5", "document": "Working Capital Mgmt Report", "page": "15-22", "section": "Peer Benchmarking", "date": "Jan 2024"},
                 {"id": "ref6", "document": "Capital Efficiency Analysis", "page": "5-12", "section": "ROIC Performance", "date": "Feb 2024"},
                 {"id": "ref7", "document": "Competitive Financial Benchmarking", "page": "18-25", "section": "Return Metrics Comparison", "date": "Mar 2024"}
            ]
        }
    },
# --- END: Section 23 Definition ---

# --- START: Section 24 Definition ---
    {
        "number": 24,
        "title": "Sellside Positioning - Management",
        "specs": "Extract an overview description positioning the Company's management team and Board of Directors as experienced, capable, and aligned with shareholder interests.\n"
                 "Identify and extract details on the 3 most important facts or achievements related to management/board strength over the last 24 months.\n"
                 "Focus on quantifiable achievements demonstrating successful leadership (e.g., delivering superior shareholder returns, successful execution of strategic initiatives with measurable results, positive financial improvements under their tenure).\n"
                 "For key individuals (CEO, CFO, potentially Chairman or key operational leader), highlight relevant background and experience that directly supports their ability to lead the Company effectively in its current strategic direction.\n"
                 "Emphasize successful execution of specific strategic initiatives, supported by concrete data points demonstrating progress or completion.\n"
                 "Include positive aspects of corporate governance or board structure where available (e.g., independence, relevant expertise, effective oversight).\n"
                 "Present the information persuasively, always underpinning positive assertions with specific facts, numbers, and source references.\n"
                 "All extracted data points requiring citation must have a corresponding source reference ID linking to a footnote.\n"
                 "Ensure all footnotes provide precise source details: document name (e.g., Proxy Statement, Annual Report, Press Release), date, page number, and specific section/table.",
        "schema": {
            "overview": { # Optional overview
                "description": None, # string summarizing management strength and alignment
                "description_source_ref_id": None
            },
            "key_management_strengths_achievements": [ # List of top 3 strengths/achievements
                { # Structure for ONE strength/achievement
                    "priority": None, # Optional number (1, 2, 3)
                    "title": None, # string (e.g., "CEO's Successful Digital Transformation Leadership")
                    "title_source_ref_id": None,
                    "focus_area": None, # string (e.g., "Executive Leadership", "Strategic Execution", "Financial Management", "Governance")
                    "focus_area_source_ref_id": None,
                    "description": None, # string detailing the strength/achievement
                    "description_source_ref_id": None,
                    "supporting_evidence": [ # List of quantitative data points/examples
                        {
                             "evidence_type": None, # string (e.g., "Metric", "Initiative Outcome", "Background Detail", "Governance Fact")
                             "description": None, # string describing the specific data point
                             "quantification": None, # Optional string/number quantifying the point (e.g., "125% TSR", "Recurring revenue +6 ppts")
                             "unit": None, # Optional string (e.g., "%", "ppts")
                             "period": None, # Optional string (e.g., "CEO Tenure", "FY23")
                             "comparison": None, # Optional string comparing to benchmark (e.g., "vs Industry +47 ppts")
                             "source_ref_id": None
                        }
                    ],
                    "link_to_value_creation": { # Optional link to outcomes
                         "description": None, # string explaining how this benefits company/shareholders
                         "source_ref_id": None
                    },
                    "notes": None # Optional notes
                }
            ],
            "footnotes": [ # Top-level list for all footnotes in this section
                { # Structure definition for ONE footnote
                    "id": None, "document": None, "page": None, "section": None, "date": None 
                }
            ]
        },
        "template": { # Example data aligned with refined schema
            "overview": {
                "description": "Led by an experienced CEO with a proven track record in digital transformation, supported by a financially disciplined CFO and an expert Board, the management team has demonstrated strong execution capabilities, delivering superior shareholder returns and effectively navigating strategic shifts.", "description_source_ref_id": "ref1"
            },
            "key_management_strengths_achievements": [
                { # Example 1: CEO Performance
                    "priority": 1,
                    "title": "CEO James Miller: Proven Digital Transformation Leader Delivering Shareholder Value", "title_source_ref_id": "ref1",
                    "focus_area": "Executive Leadership & Strategy Execution", "focus_area_source_ref_id": "ref1",
                    "description": "CEO Miller has successfully steered the Company through a critical strategic pivot towards higher-margin digital and service offerings, leveraging prior experience to drive significant recurring revenue growth and portfolio optimization.", "description_source_ref_id": "ref2",
                    "supporting_evidence": [
                        {"evidence_type": "Metric", "description": "Total Shareholder Return during CEO tenure", "quantification": "125", "unit": "%", "period": "Mar 2018 - Mar 2024", "comparison": "vs Industry +78%", "source_ref_id": "ref4"},
                        {"evidence_type": "Metric", "description": "Recurring Revenue Growth", "quantification": "+6 ppts", "unit": "increase (% of total)", "period": "Q1 2022 - Q1 2024", "comparison": None, "source_ref_id": "ref3"},
                        {"evidence_type": "Initiative Outcome", "description": "Successful Divestiture of Legacy Components", "quantification": "$185M proceeds", "unit": None, "period": "Oct 2023", "comparison": "+0.8 ppts EBITDA margin impact", "source_ref_id": "ref5"},
                        {"evidence_type": "Background Detail", "description": "Prior COO role involved similar successful digital shift (10% -> 28% recurring revenue)", "quantification": None, "unit": None, "period": "2014-2018", "comparison": None, "source_ref_id": "ref2"}
                    ],
                    "link_to_value_creation": {"description": "Leadership directly correlates to significant outperformance versus peers and strategic repositioning towards higher-value business models.", "source_ref_id": "ref4"},
                    "notes": None
                },
                { # Example 2: CFO Performance
                    "priority": 2,
                    "title": "CFO Sarah Wilson: Driving Financial Discipline and Superior Cash Generation", "title_source_ref_id": "ref1",
                    "focus_area": "Financial Management & Capital Allocation", "focus_area_source_ref_id": "ref1",
                    "description": "CFO Wilson has implemented rigorous financial controls and capital allocation discipline, resulting in industry-leading cash conversion, ROIC improvement, and a strengthened balance sheet.", "description_source_ref_id": "ref6",
                    "supporting_evidence": [
                        {"evidence_type": "Metric", "description": "Free Cash Flow Conversion (FCF/EBITDA)", "quantification": 87.5, "unit": "%", "period": "FY 2023", "comparison": "vs Peer Avg 78.2%", "source_ref_id": "ref10"}, # Assuming ref10 covers FCF conversion
                        {"evidence_type": "Metric", "description": "Return on Invested Capital (ROIC)", "quantification": 19.8, "unit": "%", "period": "FY 2023", "comparison": "+2.0 ppts YoY, vs Peer Avg 13.5%", "source_ref_id": "ref10"},
                        {"evidence_type": "Metric", "description": "Cash Conversion Cycle Reduction", "quantification": "-8.5 days", "unit": None, "period": "YoY Q1 2024", "comparison": None, "source_ref_id": "ref10"},
                        {"evidence_type": "Initiative Outcome", "description": "Balanced Capital Allocation", "quantification": "$290M shareholder returns + $85M net debt reduction", "unit": None, "period": "FY 2023", "comparison": None, "source_ref_id": "ref10"}
                    ],
                    "link_to_value_creation": {"description": "Strong financial stewardship enhances strategic flexibility for growth and M&A while directly contributing to shareholder returns.", "source_ref_id": "ref6"},
                    "notes": "Background includes prior successful balance sheet optimization."
                },
                 { # Example 3: Board Oversight / Governance
                    "priority": 3,
                    "title": "Experienced Board with Strong Independent Oversight", "title_source_ref_id": "ref1",
                    "focus_area": "Governance & Strategic Oversight", "focus_area_source_ref_id": "ref1",
                    "description": "The Board, led by experienced Founder Chairman Roberts and Lead Independent Director Dr. Rodriguez, provides robust strategic oversight and governance, evidenced by high independence levels and successful navigation of strategic reviews.", "description_source_ref_id": "ref11",
                    "supporting_evidence": [
                        {"evidence_type": "Governance Fact", "description": "Board Independence", "quantification": "8 of 11 (73%) directors are independent", "unit": None, "period": "Proxy 2024", "comparison": "Exceeds typical index requirements", "source_ref_id": "ref11"},
                        {"evidence_type": "Governance Fact", "description": "Lead Independent Director Role Established", "quantification": None, "unit": None, "period": "Since 2019", "comparison": None, "source_ref_id": "ref11"},
                        {"evidence_type": "Initiative Outcome", "description": "Successful 2022 Strategic Review", "quantification": "Led to divestiture, restructuring, new 3-year plan", "unit": None, "period": "Completed Nov 2022", "comparison": "Addressed prior activist concerns", "source_ref_id": "ref10"}, # Re-use footnote if applicable
                        {"evidence_type": "Background Detail", "description": "Chairman Roberts' 40+ years industry experience", "quantification": None, "unit": None, "period": None, "comparison": None, "source_ref_id": "ref2"},
                        {"evidence_type": "Background Detail", "description": "Lead Director Rodriguez's tech CEO background", "quantification": None, "unit": None, "period": None, "comparison": None, "source_ref_id": "ref11"}
                    ],
                    "link_to_value_creation": {"description": "Strong governance structure and experienced oversight enhance long-term strategic decision-making and risk management.", "source_ref_id": "ref11"},
                    "notes": None
                 }
            ],
            "footnotes": [
                 {"id": "ref1", "document": "Management Assessment Report", "page": "3-5", "section": "Executive Summary", "date": "Mar 2024"},
                 {"id": "ref2", "document": "Annual Proxy Statement 2024", "page": "12-18", "section": "Director and Exec Officer Info", "date": "Feb 2024"},
                 {"id": "ref3", "document": "CEO Performance Review", "page": "5-10", "section": "Strategic Initiative Implementation", "date": "Jan 2024"},
                 {"id": "ref4", "document": "CEO Performance Metrics", "page": "8-12", "section": "Long-term Value Creation", "date": "Feb 2024"},
                 {"id": "ref5", "document": "Legacy Components Divestiture Press Release", "page": "1-2", "section": "Transaction Overview", "date": "Oct 12, 2023"},
                 {"id": "ref6", "document": "CFO Performance Assessment", "page": "3-8", "section": "Financial Excellence Metrics", "date": "Jan 2024"},
                 {"id": "ref7", "document": "Investor Relations Effectiveness Survey", "page": "10-12", "section": "Financial Communication Rating", "date": "Dec 2023"},
                 # {"id": "ref8", ... } # Assuming CTO example added if needed
                 # {"id": "ref9", ... } # Assuming CTO example added if needed
                 {"id": "ref10", "document": "Board Effectiveness Review", "page": "8-15", "section": "Chairman Leadership & Strategic Review", "date": "Jan 2024"},
                 {"id": "ref11", "document": "Corporate Governance Assessment", "page": "12-18", "section": "Governance Ratings & Structure", "date": "Dec 2023"}
            ]
        }
    },
# --- END: Section 24 Definition ---

# --- START: Section 25 Definition ---
    {
        "number": 25,
        "title": "Sellside Positioning - Potential Investor Concerns and Mitigants",
        "specs": "Identify and extract details on the 5 most important potential concerns an investor might have when considering the Company.\n"
                 "Focus on fundamental business concerns (e.g., competitive threats, capability gaps, market risks, margin pressures) and potential valuation issues.\n"
                 "For each potential concern, extract:\n"
                 "  - The name/title of the concern and its category (e.g., Operational Capability, Competitive Landscape, Margin Sustainability, Valuation).\n"
                 "  - A clear description of the potential concern.\n"
                 "  - 2-3 specific data points or observations that might support this concern from an investor's perspective.\n"
                 "For each concern, immediately follow with 1-2 compelling mitigants or counterarguments, focusing on existing strengths, actions already taken, or structural advantages (not just future plans).\n"
                 "For each mitigant, extract:\n"
                 "  - A clear description of the mitigant.\n"
                 "  - Specific quantitative data points or evidence supporting the mitigant and demonstrating how it addresses or reduces the concern.\n"
                 "Ensure all concerns and mitigants are presented objectively but framed constructively from a 'sellside' perspective, acknowledging the concern while emphasizing the strength of the mitigant.\n"
                 "All extracted data points requiring citation must have a corresponding source reference ID linking to a footnote.\n"
                 "Ensure all footnotes provide precise source details: document name, date, page number, and specific section/table.",
        "schema": {
            "overview": { # Optional overview
                "description": None, # string acknowledging potential concerns but positioning them as manageable
                "description_source_ref_id": None
            },
            "investor_concerns": [ # List of top 5 concerns & mitigants
                { # Structure for ONE concern/mitigant pair
                    "concern": { # Details of the potential concern
                        "name": None, # string (e.g., "Software Development Capability Gap")
                        "name_source_ref_id": None,
                        "category": None, # string (e.g., "Operational Capability", "Valuation")
                        "category_source_ref_id": None,
                        "description": None, # string explaining the investor concern
                        "description_source_ref_id": None,
                        "supporting_points": [ # 2-3 data points backing the concern
                            {
                                 "point": None, # string describing the data point
                                 "quantification": None, # Optional string/number
                                 "unit": None, # Optional string
                                 "period": None, # Optional string
                                 "source_ref_id": None
                            }
                        ],
                        "notes": None # Optional internal notes on the concern
                    },
                    "mitigants": [ # List of 1-2 mitigants addressing THIS concern
                        { # Structure for ONE mitigant
                             "name": None, # string summarizing the mitigant (e.g., "Strategic Technology Partnerships Established")
                             "name_source_ref_id": None,
                             "description": None, # string explaining how it mitigates the concern
                             "description_source_ref_id": None,
                             "supporting_data": [ # Specific data points proving the mitigant
                                 {
                                      "data_point": None, # string describing the evidence
                                      "quantification": None, # Optional string/number
                                      "unit": None, # Optional string
                                      "period": None, # Optional string
                                      "source_ref_id": None
                                 }
                             ],
                             "notes": None # Optional notes on the mitigant
                        }
                    ]
                }
            ],
            "footnotes": [ # Top-level list for all footnotes in this section
                { # Structure definition for ONE footnote
                    "id": None, "document": None, "page": None, "section": None, "date": None 
                }
            ]
        },
        "template": { # Example data aligned with refined schema
            "overview": {
                "description": "While acknowledging areas for continued focus, potential investor concerns regarding capability gaps, competitive pressures, and valuation are effectively mitigated by the Company's strategic actions, existing technological advantages, superior financial performance, and demonstrated execution capabilities.", "description_source_ref_id": "ref1" # Example overall positioning source
            },
            "investor_concerns": [
                { # Example Concern 1: Software Gap
                    "concern": {
                        "name": "Software Development Capability Gap vs Peers", "name_source_ref_id": "ref1",
                        "category": "Operational Capability", "category_source_ref_id": "ref1",
                        "description": "Concern that limited internal software engineering scale could impede digital transformation and recurring revenue growth targets compared to more software-focused competitors.", "description_source_ref_id": "ref2",
                        "supporting_points": [
                            {"point": "Current software engineer headcount gap", "quantification": "40% shortfall (300 vs 500 target)", "unit": None, "period": "Q1 2024", "source_ref_id": "ref2"},
                            {"point": "Slower time-to-market for connected products", "quantification": "18 months vs 12 months competitor avg", "unit": None, "period": "FY 2023", "source_ref_id": "ref2"},
                            {"point": "Lagging digital feature ratings vs peers", "quantification": "Score 6.2/10 vs industry 7.5/10", "unit": None, "period": "Q1 2024", "source_ref_id": "ref4"} # Example different source
                        ],
                        "notes": None
                    },
                    "mitigants": [
                        {
                             "name": "Strategic Technology Partnerships Amplify Capacity", "name_source_ref_id": "ref3",
                             "description": "Partnerships with major cloud providers effectively extend development capabilities (~15% capacity boost) by leveraging pre-built services, reducing need for custom coding.", "description_source_ref_id": "ref3",
                             "supporting_data": [
                                 {"data_point": "Utilize 85+ pre-built cloud services", "quantification": "Reduces custom dev by ~35%", "unit": None, "period": "Ongoing", "source_ref_id": "ref3"},
                                 {"data_point": "Dedicated partner dev resources equivalent to ~45 FTEs included", "quantification": None, "unit": None, "period": None, "source_ref_id": "ref3"}
                             ],
                             "notes": None
                        },
                         {
                             "name": "Existing Proprietary Tech Drives High-Value Recurring Revenue", "name_source_ref_id": "ref3",
                             "description": "Core high-margin recurring revenue growth is driven by existing, patented energy optimization tech requiring less incremental software development than building entirely new platforms.", "description_source_ref_id": "ref3",
                             "supporting_data": [
                                 {"data_point": "Energy Optimization Revenue Growth", "quantification": 22.5, "unit": "% YoY", "period": "FY 2023", "source_ref_id": "ref3"},
                                 {"data_point": "Energy Optimization Gross Margin Premium", "quantification": "+8 ppts", "unit": None, "period": "FY 2023", "source_ref_id": "ref3"}
                             ],
                             "notes": "Focus on monetizing existing IP."
                        }
                    ]
                },
                { # Example Concern 2: APAC Capacity
                    "concern": {
                        "name": "Asia-Pacific Manufacturing Capacity Constraints", "name_source_ref_id": "ref1",
                        "category": "Geographic Expansion Risk", "category_source_ref_id": "ref1",
                        "description": "Concern that limited local manufacturing footprint in high-growth APAC markets hinders competitiveness (lead times, cost) and ability to reach market share goals.", "description_source_ref_id": "ref4",
                        "supporting_points": [
                            {"point": "Significant capacity misalignment", "quantification": "APAC is 18% of revenue but only 7.5% of mfg capacity", "unit": None, "period": "Q1 2024", "source_ref_id": "ref4"},
                            {"point": "Longer regional lead times", "quantification": "8.2 weeks vs 3.5 weeks for local peers", "unit": None, "period": "Q1 2024", "source_ref_id": "ref4"}
                        ],
                        "notes": None
                    },
                    "mitigants": [
                        {
                             "name": "Capacity Expansion Underway & On Track", "name_source_ref_id": "ref5",
                             "description": "Singapore facility expansion (targeting +65% regional capacity) is 45% complete and on schedule for Q3 2025 completion, already improving lead times.", "description_source_ref_id": "ref5",
                             "supporting_data": [
                                 {"data_point": "Lead time improvement", "quantification": "Reduced from 8.2 to 7.5 weeks", "unit": None, "period": "Q4'23 vs Q1'24", "source_ref_id": "ref5"}
                             ],
                             "notes": None
                        },
                         {
                             "name": "Contract Manufacturing Secured", "name_source_ref_id": "ref5",
                             "description": "Agreements signed (Q1 2024) with 3 regional contract manufacturers, adding flexible capacity (+5k units/yr) starting H2 2024.", "description_source_ref_id": "ref5",
                             "supporting_data": [
                                  {"data_point": "Combined capacity increase (Expansion + CM)", "quantification": "Sufficient to meet projected demand for 25% market share target", "unit": None, "period": "by 2026", "source_ref_id": "ref5"}
                             ],
                             "notes": "Mitigates reliance on single facility expansion."
                        }
                    ]
                },
                { # Example Concern 3: Valuation
                    "concern": {
                        "name": "Premium Valuation Relative to Peers", "name_source_ref_id": "ref1",
                        "category": "Valuation", "category_source_ref_id": "ref1",
                        "description": "Concern that the Company's current valuation multiples (e.g., EV/EBITDA) trade at a significant premium to traditional industrial peers, implying potential downside risk.", "description_source_ref_id": "ref14",
                        "supporting_points": [
                            {"point": "EV/EBITDA Multiple Premium", "quantification": "14.5x vs Peer Avg 11.9x", "unit": None, "period": "Current", "source_ref_id": "ref14"},
                            {"point": "Forward P/E Premium", "quantification": "22.8x vs Index Avg 19.5x", "unit": None, "period": "Current", "source_ref_id": "ref14"}
                        ],
                        "notes": None
                    },
                    "mitigants": [
                         {
                             "name": "Superior Financial Performance Justifies Premium", "name_source_ref_id": "ref15",
                             "description": "Premium valuation is supported by demonstrably superior growth, profitability, cash generation, and returns compared to the peer group.", "description_source_ref_id": "ref15",
                             "supporting_data": [
                                  {"data_point": "Revenue Growth Outperformance (FY23)", "quantification": "+5.8 ppts vs peer avg", "unit": None, "period": None, "source_ref_id": "ref15"},
                                  {"data_point": "EBITDA Margin Outperformance (FY23)", "quantification": "+3.3 ppts vs peer avg", "unit": None, "period": None, "source_ref_id": "ref15"},
                                  {"data_point": "ROIC Outperformance (FY23)", "quantification": "+6.3 ppts vs peer avg", "unit": None, "period": None, "source_ref_id": "ref15"},
                                  {"data_point": "FCF Margin Outperformance (FY23)", "quantification": "+3.6 ppts vs peer avg", "unit": None, "period": None, "source_ref_id": "ref15"}
                             ],
                             "notes": "Ranked #1 or #2 vs peers across key metrics."
                        },
                        {
                             "name": "Business Mix Transition Supports Re-Rating", "name_source_ref_id": "ref15",
                             "description": "Ongoing shift towards higher-quality, higher-margin software & services revenue (currently 30%, tracking towards 40%) justifies valuation closer to industrial software peers than traditional hardware companies.", "description_source_ref_id": "ref15",
                             "supporting_data": [
                                 {"data_point": "Recurring Revenue %", "quantification": "28% vs peer avg ~15%", "unit": None, "period": "Q1 2024", "source_ref_id": "ref15"},
                                 {"data_point": "Software/Service Gross Margin", "quantification": "~68% vs hardware ~40%", "unit": None, "period": "FY 2023", "source_ref_id": "ref15"}
                             ],
                             "notes": "Market values recurring revenue models more highly."
                        }
                    ]
                }
                # ... Add Concerns 4 and 5 ...
            ],
            "footnotes": [
                {"id": "ref1", "document": "Investor Concerns Analysis", "page": "3-4", "section": "Executive Summary", "date": "Mar 2024"},
                {"id": "ref2", "document": "Technical Resource Gap Assessment", "page": "8-12", "section": "Software Dev Capacity", "date": "Feb 2024"},
                {"id": "ref3", "document": "Strategic Technology Partnership Report", "page": "5-10", "section": "Capacity Enhancement", "date": "Jan 2024"},
                # {"id": "ref4", ...} # Add other necessary footnotes
            ]
        }
    },
# --- END: Section 25 Definition ---

# --- START: Section 26 Definition ---
    {
        "number": 26,
        "title": "Buyside Due Diligence - Macro",
        "specs": "From a potential buyer's perspective, analyze the 3 most important macroeconomic trends that could pose a material risk to the Company's economic performance over the next 12-24 months.\n"
                 "Focus primarily on downside risks and potential negative impacts related to economic indicators (e.g., slowing growth, interest rates, inflation, labor costs, supply chain disruptions, FX volatility, geopolitical issues).\n"
                 "For each key macro risk trend, extract:\n"
                 "  - Its name/title and category (e.g., Monetary Policy Impact, Cost Structure Impact, Geopolitical Risk).\n"
                 "  - A clear description of the potential risk trend.\n"
                 "  - Quantitative analysis of the Company's sensitivity to this factor, demonstrating potential negative impacts on revenue, margins, cash flow, or valuation under adverse scenarios.\n"
                 "  - Benchmarking against competitors' sensitivity or historical performance during similar macro events, highlighting areas where the Company might be relatively more vulnerable.\n"
                 "  - An assessment of the Company's existing mitigation strategies related to this risk and their perceived limitations or effectiveness from a buyer's viewpoint.\n"
                 "  - Formulate 2-3 detailed, data-driven due diligence questions a potential buyer should ask management to thoroughly investigate the Company's exposure and preparedness for this specific macro risk.\n"
                 "All analysis should be supported by specific data points, quantitative examples, and source references.\n"
                 "All extracted data points requiring citation must have a corresponding source reference ID linking to a footnote.\n"
                 "Ensure all footnotes provide precise source details: document name, date, page number, and specific section/table.",
        "schema": {
            "overview": { # Optional overview
                "description": None, # string summarizing key macro risks from buyside perspective
                "description_source_ref_id": None
            },
            "key_macro_risks": [ # List of top 3 macro risks
                { # Structure for ONE key macro risk
                    "priority": None, # Optional number (1, 2, 3)
                    "name": None, # string (e.g., "Interest Rate Sensitivity / Capex Cycle Downturn")
                    "name_source_ref_id": None,
                    "category": None, # string (e.g., "Monetary Policy Impact", "Cost Structure Impact")
                    "category_source_ref_id": None,
                    "risk_description": None, # string explaining the risk trend
                    "risk_description_source_ref_id": None,
                    "company_sensitivity_analysis": { # Quantitative analysis of company exposure/impact
                        "summary": None, # Optional string summarizing sensitivity
                        "summary_source_ref_id": None,
                        "sensitivity_metrics": [ # List of metrics/scenarios
                            {
                                 "metric_name": None, # string (e.g., "Revenue Beta to Industrial Capex")
                                 "value": None, # number or string
                                 "unit": None, # string
                                 "period_or_scenario": None, # string (e.g., "Historical", "Downside Scenario: Capex Growth 2%")
                                 "financial_impact_quantification": None, # string describing impact (e.g., "-2.6 ppts Revenue Growth")
                                 "source_ref_id": None
                            }
                        ],
                        "notes": None
                    },
                    "competitive_benchmarking": { # How company compares to peers on this risk
                        "summary": None, # Optional string summarizing relative vulnerability
                        "summary_source_ref_id": None,
                         "benchmarks": [ # List of benchmark data points
                             {
                                 "competitor_name": None, # string
                                 "metric_name": None, # string (e.g., "Revenue Beta", "Margin Impact during Downturn")
                                 "company_value": None,
                                 "competitor_value": None,
                                 "unit": None,
                                 "relative_vulnerability": None, # string (e.g., "Company more sensitive due to X")
                                 "source_ref_id": None
                             }
                         ],
                         "notes": None
                    },
                    "mitigation_assessment": { # Buyside view on company's mitigations
                        "summary": None, # string evaluating effectiveness/limitations
                        "summary_source_ref_id": None,
                        "specific_mitigations_analyzed": [ # List of mitigations and buyside comments
                            {
                                 "mitigation_name": None, # string (e.g., "Recurring Revenue Growth")
                                 "effectiveness_commentary": None, # string (e.g., "Partially effective but mix still lags Leader A")
                                 "limitations": None, # Optional string
                                 "source_ref_id": None
                            }
                        ],
                        "notes": None
                    },
                    "due_diligence_questions": [ # List of 2-3 questions for buyer
                         {
                              "question": None, # string - the specific question to ask
                              "rationale": None, # string explaining why it's important
                              "data_requested": None, # Optional string describing needed data
                              "source_ref_id": None # Optional reference if question derived from specific doc point
                         }
                    ],
                    "notes": None # Optional overall risk notes
                }
            ],
            "footnotes": [ # Top-level list for all footnotes in this section
                { # Structure definition for ONE footnote
                    "id": None, "document": None, "page": None, "section": None, "date": None 
                }
            ]
        },
        "template": { # Example data aligned with refined schema
            "overview": {
                "description": "Buyside diligence should focus on quantifying the Company's sensitivity to a potential industrial capex slowdown driven by higher interest rates, persistent input cost inflation impacting margins, and significant foreign exchange exposure given its global footprint.", "description_source_ref_id": "ref1"
            },
            "key_macro_risks": [
                { # Example Risk 1: Capex Cycle
                    "priority": 1,
                    "name": "Interest Rate Sensitivity / Capex Cycle Downturn Risk", "name_source_ref_id": "ref1",
                    "category": "Monetary Policy Impact", "category_source_ref_id": "ref1",
                    "risk_description": "Sustained higher interest rates globally may dampen industrial capex, slowing demand for the Company's core automation products, particularly impacting revenue growth and potentially pricing power.", "risk_description_source_ref_id": "ref2",
                    "company_sensitivity_analysis": {
                        "summary": "Company revenue growth shows high correlation (0.85x beta, R^2=0.72) to industrial capex with a 2-qtr lag. Downside scenarios indicate material impact.", "summary_source_ref_id": "ref3",
                        "sensitivity_metrics": [
                            {"metric_name": "Revenue Growth Sensitivity", "value": "0.85", "unit": "x Beta to Global Ind. Capex", "period_or_scenario": "Historical Analysis", "financial_impact_quantification": None, "source_ref_id": "ref3"},
                            {"metric_name": "EBITDA Margin Sensitivity", "value": "-0.7 ppts", "unit": None, "period_or_scenario": "Scenario: Ind. Capex Growth slows 3ppts", "financial_impact_quantification": "Margin contracts to 22.5%", "source_ref_id": "ref3"},
                            {"metric_name": "Cash Flow Sensitivity", "value": "-45M USD", "unit": None, "period_or_scenario": "Scenario: Ind. Capex Growth slows 3ppts", "financial_impact_quantification": None, "source_ref_id": "ref3"}
                        ],
                        "notes": "Industrial Automation segment (55% revenue) has highest sensitivity (1.2x Beta)."
                    },
                    "competitive_benchmarking": {
                        "summary": "Company appears slightly more sensitive than Competitor A (higher service mix) but less sensitive than Competitor B and Regional Competitor X.", "summary_source_ref_id": "ref4",
                         "benchmarks": [
                             {"competitor_name": "Competitor A", "metric_name": "Revenue Beta", "company_value": 1.10, "competitor_value": 1.05, "unit": "x", "relative_vulnerability": "Company slightly higher", "source_ref_id": "ref4"},
                             {"competitor_name": "Competitor B", "metric_name": "Margin Impact (2018-19 Slowdown)", "company_value": -1.2, "competitor_value": -1.5, "unit": "ppts", "relative_vulnerability": "Company slightly more resilient", "source_ref_id": "ref4"}
                         ],
                         "notes": None
                    },
                    "mitigation_assessment": {
                        "summary": "Strategies like recurring revenue shift help but Company remains significantly exposed due to high hardware mix.", "summary_source_ref_id": "ref5",
                        "specific_mitigations_analyzed": [
                             {"mitigation_name": "Recurring Revenue Growth", "effectiveness_commentary": "Partially effective (28% mix) but still lags Leader A (35%).", "limitations": "Transition pace dependent on software capabilities.", "source_ref_id": "ref5"}
                        ],
                        "notes": "Limited operational cost flexibility."
                    },
                    "due_diligence_questions": [
                         {"question": "Provide detailed backlog data (aging, book-to-bill by segment, cancellation rates) for the past 8 quarters to assess forward visibility under potential slowdown.", "rationale": "Leading indicator of demand impact.", "data_requested": "Quarterly backlog details & history.", "source_ref_id": "ref6"},
                         {"question": "Quantify fixed vs. variable costs by segment and detail specific cost reduction levers available, including timelines and savings potential, under a 5% revenue decline scenario.", "rationale": "Assess margin resilience and cost flexibility.", "data_requested": "Cost structure breakdown & contingency plans.", "source_ref_id": "ref6"},
                         {"question": "What is the sensitivity of the Company's financial covenants (specifically leverage and interest coverage) to potential EBITDA declines outlined in the capex slowdown scenarios?", "rationale": "Assess potential financial distress risk.", "data_requested": "Covenant sensitivity analysis.", "source_ref_id": "ref6"}
                    ],
                    "notes": None
                },
                 { # Example Risk 2: Inflation
                    "priority": 2,
                    "name": "Input Cost Inflation & Margin Pressure", "name_source_ref_id": "ref1",
                    "category": "Cost Structure Impact", "category_source_ref_id": "ref1",
                    "risk_description": "Persistent inflation in key inputs (electronics, metals, labor) coupled with potentially weakening pricing power in core hardware markets threatens gross and EBITDA margins.", "risk_description_source_ref_id": "ref7",
                     "company_sensitivity_analysis": {
                        "summary": "Company has demonstrated partial ability to pass through costs, but a significant negative price/cost gap emerged in Q1 2024 (-2.2 ppts). High exposure to electronic component inflation.", "summary_source_ref_id": "ref8",
                        "sensitivity_metrics": [
                            {"metric_name": "Price/Cost Gap (Avg TTM)", "value": "-1.5 ppts", "unit": None, "period_or_scenario": "Q2'23-Q1'24", "financial_impact_quantification": None, "source_ref_id": "ref8"},
                            {"metric_name": "EBITDA Margin Sensitivity", "value": "-0.8 ppts", "unit": None, "period_or_scenario": "Scenario: Input costs +2ppts above forecast", "financial_impact_quantification": "Approx $42M EBITDA impact", "source_ref_id": "ref8"}
                         ],
                         "notes": "Electronics are 38% of direct material costs."
                    },
                    "competitive_benchmarking": {
                        "summary": "Company's ability to pass through costs appears mid-pack; better than B/X but lagging A.", "summary_source_ref_id": "ref9",
                        "benchmarks": [{"competitor_name": "Competitor A", "metric_name": "Price/Cost Gap (TTM)", "company_value": -1.5, "competitor_value": -0.8, "unit": "ppts", "relative_vulnerability": "Company more exposed", "source_ref_id": "ref9"}]
                    },
                     "mitigation_assessment": {
                         "summary": "Hedging provides short-term buffer; value pricing helps but limited to certain lines; cost reduction efforts partially offsetting.", "summary_source_ref_id": "ref10",
                         "specific_mitigations_analyzed": [{"mitigation_name": "Procurement Contracts", "effectiveness_commentary": "60% coverage, avg 6-month duration - limited long-term protection.", "limitations": None, "source_ref_id": "ref10"}],
                         "notes": None
                    },
                     "due_diligence_questions": [
                        {"question": "Provide detailed breakdown of input cost inflation by major category (electronics, metals, labor, logistics) and the effectiveness of specific pass-through mechanisms (price increases, surcharges, contract clauses) over the past 8 quarters.", "rationale": "Need granular view of inflation sources and pricing power.", "data_requested": "Cost category inflation vs price realization data.", "source_ref_id": "ref11"},
                        {"question": "What percentage of COGS is covered by long-term supplier agreements (>12 months) with fixed pricing or defined escalators? Detail key supplier relationships and negotiation leverage.", "rationale": "Assess structural cost protection.", "data_requested": "Supplier contract coverage details.", "source_ref_id": "ref11"}
                     ],
                    "notes": None
                 }
                # ... Add Risk 3 (e.g., FX Exposure) ...
            ],
            "footnotes": [
                 {"id": "ref1", "document": "Macroeconomic Risk Assessment", "page": "3-5", "section": "Executive Summary", "date": "Mar 2024"},
                 {"id": "ref2", "document": "Central Bank Policy Analysis", "page": "8-15", "section": "Interest Rate Projections", "date": "Mar 2024"},
                 {"id": "ref3", "document": "Industrial Capex Sensitivity Analysis", "page": "10-18", "section": "Company Impact Assessment", "date": "Feb 2024"},
                 {"id": "ref4", "document": "Competitive Benchmarking: Capex Cycle Impact", "page": "15-22", "section": "Relative Performance Analysis", "date": "Jan 2024"},
                 {"id": "ref5", "document": "Capex Cycle Mitigation Strategies", "page": "5-12", "section": "Strategy Assessment", "date": "Mar 2024"},
                 {"id": "ref6", "document": "Due Diligence Framework: Capex Cycle Risk", "page": "3-8", "section": "Key Investigation Areas", "date": "Mar 2024"},
                 {"id": "ref7", "document": "Inflation Outlook Report", "page": "5-12", "section": "Industrial Input Costs", "date": "Feb 2024"},
                 {"id": "ref8", "document": "Cost Structure and Inflation Impact Analysis", "page": "8-15", "section": "Margin Sensitivity", "date": "Jan 2024"},
                 {"id": "ref9", "document": "Competitive Benchmarking: Inflation Response", "page": "10-18", "section": "Margin Protection Capabilities", "date": "Feb 2024"},
                 {"id": "ref10", "document": "Inflation Mitigation Strategies", "page": "5-12", "section": "Effectiveness Assessment", "date": "Mar 2024"},
                 {"id": "ref11", "document": "Due Diligence Framework: Inflation Risk", "page": "8-15", "section": "Key Investigation Areas", "date": "Mar 2024"}
                 # {"id": "ref12", ... } # Footnotes for FX example if added
            ]
        }
    },
# --- END: Section 26 Definition ---

# --- START: Section 27 Definition ---
    {
        "number": 27,
        "title": "Buyside Due Diligence - Industry",
        "specs": "From a potential buyer's perspective, analyze the 3 most important industry trends or competitive dynamics that could pose a material risk to the Company's economic performance over the next 12-24 months.\n"
                 "Focus primarily on downside risks (e.g., disruptive technologies, intensifying competition, changing customer preferences, unfavorable regulatory shifts within the industry, business model obsolescence).\n"
                 "For each key industry risk trend, extract:\n"
                 "  - Its name/title and category (e.g., Competitive Dynamics, Technology Disruption, Regulatory Change).\n"
                 "  - A clear description of the industry trend and why it poses a risk to the Company.\n"
                 "  - Quantitative analysis of the Company's vulnerability to this trend (e.g., exposure of revenue/margins, gap vs competitors on key capabilities, customer segment risk), including adverse scenarios.\n"
                 "  - Benchmarking against key competitors' positioning, strategies, and vulnerabilities related to this trend.\n"
                 "  - An assessment of the Company's strategic response and mitigation efforts, evaluating their adequacy and potential limitations from a buyer's viewpoint.\n"
                 "  - Formulate 2-3 detailed, data-driven due diligence questions a potential buyer should ask management to probe the Company's exposure and strategic response to this specific industry risk.\n"
                 "All analysis should be supported by specific data points, quantitative examples, and source references.\n"
                 "All extracted data points requiring citation must have a corresponding source reference ID linking to a footnote.\n"
                 "Ensure all footnotes provide precise source details: document name, date, page number, and specific section/table.",
        "schema": {
            "overview": { # Optional overview
                "description": None, # string summarizing key industry risks/challenges from buyside perspective
                "description_source_ref_id": None
            },
            "key_industry_risks": [ # List of top 3 industry risks
                { # Structure for ONE key industry risk
                    "priority": None, # Optional number (1, 2, 3)
                    "name": None, # string (e.g., "Software-Centric Disruption by New Entrants")
                    "name_source_ref_id": None,
                    "category": None, # string (e.g., "Competitive Dynamics", "Technology Disruption")
                    "category_source_ref_id": None,
                    "risk_description": None, # string explaining the industry trend and its risk to the company
                    "risk_description_source_ref_id": None,
                    "company_vulnerability_analysis": { # Quantitative analysis of company exposure/impact
                        "summary": None, # Optional string summarizing vulnerability
                        "summary_source_ref_id": None,
                        "vulnerability_metrics": [ # List of metrics/scenarios showing vulnerability
                            {
                                 "metric_name": None, # string (e.g., "Win Rate vs Software Natives", "Revenue Exposure in Vulnerable Segment")
                                 "value": None, # number or string
                                 "unit": None, # string
                                 "trend": None, # Optional string describing trend (e.g., "Declining")
                                 "period_or_scenario": None, # string (e.g., "TTM", "Severe Disruption Scenario")
                                 "financial_impact_quantification": None, # string describing potential impact (e.g., "-3.5 ppts Revenue Growth")
                                 "source_ref_id": None
                            }
                        ],
                        "notes": None
                    },
                    "competitive_benchmarking": { # How company compares to peers regarding this industry risk
                        "summary": None, # Optional string summarizing relative positioning/response
                        "summary_source_ref_id": None,
                         "benchmarks": [ # List of benchmark data points
                             {
                                 "competitor_name": None, # string
                                 "metric_name": None, # string (e.g., "Software Revenue %", "Cloud Platform Maturity")
                                 "company_value": None,
                                 "competitor_value": None,
                                 "unit": None,
                                 "relative_position": None, # string (e.g., "Company lagging due to X")
                                 "source_ref_id": None
                             }
                         ],
                         "notes": None
                    },
                    "company_response_assessment": { # Buyside view on company's strategic response
                        "summary": None, # string evaluating effectiveness/limitations of response
                        "summary_source_ref_id": None,
                        "specific_responses_analyzed": [ # List of responses and buyside comments
                            {
                                 "response_name": None, # string (e.g., "Digital Transformation Investment")
                                 "status_or_progress": None, # string (e.g., "$150M/yr vs $350M/yr for Leader A")
                                 "effectiveness_commentary": None, # string (e.g., "Insufficient scale to close gap quickly.")
                                 "limitations": None, # Optional string
                                 "source_ref_id": None
                            }
                        ],
                        "notes": None
                    },
                    "due_diligence_questions": [ # List of 2-3 questions for buyer
                         {
                              "question": None, "rationale": None, "data_requested": None, "source_ref_id": None
                         }
                    ],
                    "notes": None # Optional overall risk notes
                }
            ],
            "footnotes": [ # Top-level list for all footnotes in this section
                { # Structure definition for ONE footnote
                    "id": None, "document": None, "page": None, "section": None, "date": None 
                }
            ]
        },
        "template": { # Example data aligned with refined schema
            "overview": {
                "description": "Key industry risks requiring buyside diligence include accelerating disruption from software-native competitors challenging the Company's core model, increasing commoditization and price pressure in standard hardware segments, and evolving regulatory hurdles particularly around cybersecurity and energy efficiency.", "description_source_ref_id": "ref1"
            },
            "key_industry_risks": [
                { # Example Risk 1: Software Disruption
                    "priority": 1,
                    "name": "Software-Centric Disruption by New Entrants", "name_source_ref_id": "ref1",
                    "category": "Competitive Dynamics / Technology Disruption", "category_source_ref_id": "ref1",
                    "risk_description": "Well-funded software-native players (e.g., SoftwareAutomation Inc.) entering market with cloud-based, AI-driven platforms threaten to displace traditional hardware-centric models, especially in high-value digital transformation projects.", "risk_description_source_ref_id": "ref2",
                    "company_vulnerability_analysis": {
                        "summary": "Company vulnerable due to lagging software capabilities, lower recurring revenue mix, and declining win rates against software natives in key segments.", "summary_source_ref_id": "ref3",
                        "vulnerability_metrics": [
                            {"metric_name": "Win Rate vs Software Natives (Digital RFPs)", "value": "42%", "unit": None, "trend": "Declined from 52% (2022)", "period_or_scenario": "Q1 2024", "financial_impact_quantification": "Est. $85-140M revenue risk by 2025", "source_ref_id": "ref3"},
                            {"metric_name": "Software/Service Revenue Mix", "value": "30%", "unit": None, "trend": "Growing but lags leaders", "period_or_scenario": "Q1 2024", "financial_impact_quantification": "Limits valuation multiple vs SaaS peers", "source_ref_id": "ref3"},
                            {"metric_name": "Cloud Platform Maturity Score", "value": "6.2/10", "unit": None, "trend": None, "period_or_scenario": "Q1 2024", "financial_impact_quantification": "Hinders feature velocity and integration", "source_ref_id": "ref4"}
                        ],
                        "notes": "Enterprise segment most vulnerable (win rate dropped to 52% from 65%)."
                    },
                    "competitive_benchmarking": {
                        "summary": "Competitor A investing heavily ($350M/yr) and transforming faster (45% SW/Service mix). SoftwareAutomation sets high bar with cloud-native AI.", "summary_source_ref_id": "ref4",
                         "benchmarks": [
                             {"competitor_name": "Competitor A", "metric_name": "SW/Service Revenue %", "company_value": 30, "competitor_value": 45, "unit": "%", "relative_position": "Company lagging significantly", "source_ref_id": "ref4"},
                             {"competitor_name": "SoftwareAutomation", "metric_name": "Feature Release Cycle", "company_value": "Quarterly", "competitor_value": "Monthly", "unit": None, "relative_position": "Company significantly slower", "source_ref_id": "ref4"}
                         ],
                         "notes": "Competitor B also lagging but less direct threat in digital."
                    },
                    "company_response_assessment": {
                         "summary": "Response (talent hubs, partnerships) directionally correct but lacks scale/speed vs threat.", "summary_source_ref_id": "ref5",
                         "specific_responses_analyzed": [
                             {"response_name": "Digital Transformation Investment", "status_or_progress": "$150M/yr (3.3% rev)", "effectiveness_commentary": "Insufficient vs Competitor A ($350M/yr, 4.8% rev).", "limitations": "Talent gap remains.", "source_ref_id": "ref5"},
                             {"response_name": "Cloud Platform Development", "status_or_progress": "2nd Gen platform", "effectiveness_commentary": "Lacks open APIs and advanced AI of leading platforms.", "limitations": "Legacy architecture challenges.", "source_ref_id": "ref5"}
                         ],
                         "notes": "Risk of falling further behind without more aggressive action/M&A."
                    },
                    "due_diligence_questions": [
                         {"question": "Provide the detailed cloud platform roadmap, including specific plans and timelines for achieving feature parity with Competitor A and key software natives, along with required resources and technical risks.", "rationale": "Assess feasibility and competitiveness of platform strategy.", "data_requested": "Technical roadmap, resource plan, gap analysis.", "source_ref_id": "ref6"},
                         {"question": "What is the customer churn rate specifically for customers who evaluated but did not select the Company's digital/subscription offerings in the past 12 months?", "rationale": "Quantify customer loss directly due to digital capability gap.", "data_requested": "Churn analysis for lost digital deals.", "source_ref_id": "ref6"},
                         {"question": "Detail the M&A pipeline and strategy focused on acquiring software/AI capabilities needed to close the competitive gap. What targets are being evaluated?", "rationale": "Assess inorganic options to accelerate digital transformation.", "data_requested": "M&A pipeline, target criteria, valuation approach.", "source_ref_id": "ref6"}
                    ],
                    "notes": None
                },
                { # Example Risk 2: Hardware Commoditization
                    "priority": 2,
                    "name": "Hardware Commoditization & Price Pressure", "name_source_ref_id": "ref1",
                    "category": "Market Dynamics", "category_source_ref_id": "ref1",
                    "risk_description": "Standard hardware components (PLCs, HMIs, Drives) facing accelerating price erosion due to commoditization and aggressive pricing from Asian competitors.", "risk_description_source_ref_id": "ref7",
                     "company_vulnerability_analysis": {
                         "summary": "Significant revenue (~42%) exposed to standard hardware lines where margins are compressing (-1.3 ppts YoY in Q1 2024).", "summary_source_ref_id": "ref8",
                         "vulnerability_metrics": [
                             {"metric_name": "Standard Hardware Price Erosion", "value": "-3.2%", "unit": None, "trend": "Accelerating (vs -2.5% in FY23)", "period_or_scenario": "Q1 2024", "financial_impact_quantification": "Potential -1.5 ppts EBITDA margin impact if trend hits -6%", "source_ref_id": "ref8"},
                             {"metric_name": "Asia-Pacific Hardware Margin", "value": "32.5%", "unit": None, "trend": None, "period_or_scenario": "Q1 2024", "financial_impact_quantification": "vs 38.5% in N.Am/Europe due to price pressure", "source_ref_id": "ref8"}
                         ],
                         "notes": "Small business segment highly price sensitive."
                    },
                     "competitive_benchmarking": {
                         "summary": "Competitor A better insulated via software mix; Regional Competitor X exacerbates pressure with lower cost base.", "summary_source_ref_id": "ref9",
                         "benchmarks": [
                             {"competitor_name": "Competitor A", "metric_name": "Standard Hardware Exposure", "company_value": 42, "competitor_value": 35, "unit": "% of revenue", "relative_position": "Company more exposed", "source_ref_id": "ref9"},
                             {"competitor_name": "Regional Competitor X", "metric_name": "Pricing vs Company", "company_value": None, "competitor_value": "-15 to -20%", "unit": None, "relative_position": "Significant price undercutting", "source_ref_id": "ref9"}
                         ],
                         "notes": None
                     },
                     "company_response_assessment": {
                         "summary": "Shift to solutions and value pricing helps but doesn't fully negate hardware margin pressure.", "summary_source_ref_id": "ref10",
                          "specific_responses_analyzed": [
                              {"response_name": "Solution Bundling", "status_or_progress": "45% adoption rate", "effectiveness_commentary": "Helps differentiate but underlying hardware price still visible.", "limitations": "Customer resistance to bundles in some segments.", "source_ref_id": "ref10"},
                               {"response_name": "Manufacturing Cost Reduction", "status_or_progress": "Cost/unit down 3.8% FY23", "effectiveness_commentary": "Positive but lags price erosion rate.", "limitations": "Fixed cost structure limits flexibility.", "source_ref_id": "ref10"}
                          ],
                         "notes": None
                     },
                    "due_diligence_questions": [
                         {"question": "Provide gross margin analysis by product SKU for standard hardware lines over 8 quarters, isolating price, volume, mix, and cost impacts.", "rationale": "Understand precise drivers of margin compression.", "data_requested": "SKU-level margin bridge analysis.", "source_ref_id": "ref11"},
                         {"question": "What is the competitive pricing intelligence process, and how does the Company plan to respond to further potential price cuts of 10-15% from Asian competitors?", "rationale": "Assess strategic response to aggressive competition.", "data_requested": "Pricing strategy docs, competitive response plans.", "source_ref_id": "ref11"}
                    ],
                    "notes": None
                 }
                  # ... Add Risk 3 (e.g., Regulatory Hurdles) ...
            ],
            "footnotes": [
                {"id": "ref1", "document": "Industry Risk Assessment", "page": "3-5", "section": "Executive Summary", "date": "Mar 2024"},
                {"id": "ref2", "document": "Competitive Landscape Analysis", "page": "8-15", "section": "New Entrant Overview", "date": "Feb 2024"},
                {"id": "ref3", "document": "Software Disruption Impact Analysis", "page": "10-18", "section": "Company Vulnerability", "date": "Jan 2024"},
                {"id": "ref4", "document": "Competitive Benchmarking: Digital Capabilities", "page": "12-22", "section": "Relative Positioning", "date": "Mar 2024"},
                {"id": "ref5", "document": "Digital Transformation Strategy Assessment", "page": "5-15", "section": "Implementation Progress", "date": "Feb 2024"},
                {"id": "ref6", "document": "Due Diligence Framework: Digital Disruption", "page": "8-12", "section": "Key Questions", "date": "Mar 2024"},
                {"id": "ref7", "document": "Industry Pricing Trends Analysis", "page": "5-15", "section": "Hardware Pricing", "date": "Jan 2024"},
                {"id": "ref8", "document": "Price Erosion Impact Assessment", "page": "10-20", "section": "Company Vulnerability", "date": "Feb 2024"},
                {"id": "ref9", "document": "Competitive Benchmarking: Pricing Power", "page": "15-25", "section": "Relative Positioning", "date": "Mar 2024"},
                {"id": "ref10", "document": "Pricing Strategy Effectiveness Review", "page": "8-15", "section": "Initiative Assessment", "date": "Jan 2024"},
                {"id": "ref11", "document": "Due Diligence Framework: Pricing Pressure", "page": "5-10", "section": "Key Questions", "date": "Mar 2024"}
                 # {"id": "ref12", ...} # Footnotes for Regulatory example if added
            ]
        }
    },
# --- END: Section 27 Definition ---

    # --- START: Section 28 Definition ---
    {
        "number": 28,
        "title": "Buyside Due Diligence - Competitive Positioning",
        "specs": ("From a potential buyer's perspective, critically evaluate the Company's competitive positioning and claimed advantages.\n"
                  "Analyze market share trends (overall, segment, geography) over the past 24-36 months. Identify whether share is being gained, lost, or maintained against specific key competitors. Quantify the rate of change.\n"
                  "Assess the true defensibility and sustainability of claimed product/service differentiation. Use objective metrics (e.g., performance benchmarks vs competitors, feature parity analysis, third-party reviews) to validate claims. Identify areas where differentiation may be eroding.\n"
                  "Evaluate the Company's actual pricing power. Analyze price realization rates, discounting levels (vs list price), and price premiums/discounts relative to key competitors across major product lines and customer segments. Assess ability to pass through cost inflation.\n"
                  "Analyze the Company's relative cost position. Benchmark key cost metrics (e.g., COGS as % of revenue, SG&A as % of revenue, manufacturing cost per unit, R&D efficiency) against peers. Identify sources of cost advantage or disadvantage.\n"
                  "Critically assess claimed competitive advantages (from Section 21). For each key claimed advantage, formulate specific diligence questions aimed at validating its magnitude, sustainability, and true contribution to economic performance.\n"
                  "Identify key competitive disadvantages or vulnerabilities (potentially referencing Section 16) that require further investigation.\n"
                  "All analysis must be supported by specific, quantifiable data points and trends, citing sources.\n"
                  "Formulate 2-3 detailed, data-driven due diligence questions for each major topic area (Market Position, Differentiation, Pricing Power, Cost Position, Advantages/Disadvantages).\n"
                  "All extracted data points requiring citation must have a corresponding source reference ID linking to a footnote.\n"
                  "Ensure all footnotes provide precise source details: document name, date, page number, and specific section/table."),
        "schema": {
            "overview": { # Optional overview
                "description": None, # string summarizing buyside view on competitive position (strengths & concerns)
                "description_source_ref_id": None
            },
            "market_position_assessment": { # Renamed from template for clarity
                "summary": None, # string summarizing share trends and position
                "summary_source_ref_id": None,
                "market_share_analysis": [ # List analyzing share trends vs competitors
                    {
                        "segment_or_area": None, # string (e.g., "Overall", "Premium Automation Segment", "APAC Region")
                        "current_share": None, # number (%)
                        "share_trend_24m": None, # number (ppt change) or string ("Stable")
                        "vs_competitor_trend": None, # string comparing vs key peers (e.g., "Gaining vs B, Losing vs A")
                        "sustainability_comment": None, # Optional string on sustainability of share/trend
                        "source_ref_id": None
                    }
                ],
                "win_loss_analysis_summary": { # Optional summary of win/loss data
                     "overall_win_rate": None, # number (%)
                     "win_rate_trend_24m": None, # number (ppt change)
                     "key_loss_reasons": [], # List of strings
                     "source_ref_id": None
                },
                "due_diligence_questions": [ # List of question objects
                    {"question": None, "rationale": None, "data_requested": None, "source_ref_id": None}
                ],
                "notes": None
            },
            "product_differentiation_assessment": { # Renamed from template
                "summary": None, # string summarizing strength/weakness of differentiation
                "summary_source_ref_id": None,
                "key_product_line_assessments": [ # Assessment by product line/area
                     {
                          "product_area": None, # string (e.g., "Energy Optimization Tech", "Standard PLCs")
                          "differentiation_claim": None, # string (Company's claimed advantage)
                          "validation_metrics": [ # List of metrics validating/challenging the claim
                               {
                                    "metric_name": None, # e.g., "Performance vs Competitor A"
                                    "value": None, # e.g., "+4.2 ppts efficiency"
                                    "source_ref_id": None
                               }
                          ],
                          "sustainability_assessment": None, # string on how defensible it is
                          "source_ref_id": None # Source for overall assessment of this area
                     }
                ],
                "customer_perception_summary": { # Optional summary of customer views
                      "nps_score": None, "unit": "NPS", "trend_24m": None, "vs_peer_avg": None, "source_ref_id": None
                },
                "due_diligence_questions": [
                    {"question": None, "rationale": None, "data_requested": None, "source_ref_id": None}
                ],
                "notes": None
            },
            "pricing_power_assessment": { # Renamed from template
                "summary": None, # string summarizing true pricing power
                "summary_source_ref_id": None,
                "key_pricing_metrics": [ # List of metrics
                    {
                        "metric_name": None, # e.g., "Price Realization Rate", "Premium vs Competitor A", "Cost Pass-Through Rate"
                        "current_value": None,
                        "unit": None,
                        "trend_24m": None, # e.g., "Declined 1.7 ppts"
                        "comparison": None, # e.g., "vs Industry Avg +5.4 ppts"
                        "implication": None, # Optional string explaining what metric shows
                        "source_ref_id": None
                    }
                ],
                "due_diligence_questions": [
                     {"question": None, "rationale": None, "data_requested": None, "source_ref_id": None}
                ],
                "notes": None
            },
            "cost_position_assessment": { # Renamed from template
                "summary": None, # string summarizing relative cost position
                "summary_source_ref_id": None,
                "key_cost_metrics": [ # List of metrics
                    {
                         "metric_name": None, # e.g., "Gross Margin vs Peers", "Mfg Cost/Unit Index vs Peers", "SG&A % Revenue vs Peers"
                         "company_value": None,
                         "unit": None,
                         "comparison_value": None, # Peer average or specific competitor
                         "comparison_point": None, # Name of peer/benchmark
                         "relative_position": None, # string (e.g., "+1.2 ppts advantage", "-5 index points disadvantage")
                         "trend_24m": None, # Optional string/number
                         "source_ref_id": None
                    }
                ],
                 "key_cost_drivers": [], # Optional list of strings identifying main cost drivers/issues
                 "key_cost_drivers_source_ref_id": None,
                "due_diligence_questions": [
                    {"question": None, "rationale": None, "data_requested": None, "source_ref_id": None}
                ],
                "notes": None
            },
            "advantages_disadvantages_validation": { # Renamed from template
                "summary": None, # Overall summary of validated strengths and key risks
                "summary_source_ref_id": None,
                "validated_advantages": [ # List confirming key strengths from Section 21
                    {
                        "advantage_name": None, # Match name from Section 21
                        "validation_summary": None, # string confirming evidence
                        "sustainability_comment": None, # string on outlook
                        "source_ref_id": None
                    }
                ],
                "key_risks_and_vulnerabilities": [ # Highlighting key disadvantages/risks
                     {
                         "vulnerability_name": None, # e.g., "Digital Capability Gap"
                         "risk_summary": None, # string explaining risk from buyside view
                         "quantification": None, # Optional string quantifying risk
                         "source_ref_id": None
                     }
                ],
                "due_diligence_questions": [ # Specific questions on advantages/disadvantages
                    {"question": None, "rationale": None, "data_requested": None, "source_ref_id": None}
                ],
                 "notes": None
            },
            "footnotes": [ # Top-level list for all footnotes in this section
                { # Structure definition for ONE footnote
                    "id": None, "document": None, "page": None, "section": None, "date": None 
                }
            ]
        },
        "template": { # Example data aligned with refined schema
            "overview": {
                "description": "While the Company holds defensible advantages in energy optimization and operational efficiency, buyside diligence should focus on the sustainability of market share trends against increasingly digital competitors, true pricing power in core hardware segments, and the execution risk associated with closing the software capability gap.", "description_source_ref_id": "ref1"
            },
            "market_position_assessment": {
                "summary": "Overall market share stable but slight recent decline; gaining share in premium automation but losing ground vs specific digital competitors. Win rates declining slightly overall.", "summary_source_ref_id": "ref2",
                "market_share_analysis": [
                    {"segment_or_area": "Overall", "current_share": 15.8, "share_trend_24m": "+0.7 ppts", "vs_competitor_trend": "Stable vs A/B, losing slightly to C/Software natives", "sustainability_comment": "Overall share stable, but underlying shifts require scrutiny.", "source_ref_id": "ref2"},
                    {"segment_or_area": "Premium Automation", "current_share": 18.9, "share_trend_24m": "+3.1 ppts", "vs_competitor_trend": "Gaining vs B, stable vs A", "sustainability_comment": "Strong but Competitor A investing heavily.", "source_ref_id": "ref2"}
                ],
                "win_loss_analysis_summary": { "overall_win_rate": 45.2, "win_rate_trend_24m": -2.5, "key_loss_reasons": ["Price (Standard Hardware)", "Missing Digital Features", "Competitor Relationship"], "source_ref_id": "ref2"},
                "due_diligence_questions": [
                     {"question": "Provide cohort analysis of market share showing gains/losses by customer acquisition year and segment.", "rationale": "Understand if share gains are from new wins or legacy base.", "data_requested": "Market share cohort data.", "source_ref_id": "ref4"},
                     {"question": "Detail win rates specifically against software-native competitors over the past 8 quarters.", "rationale": "Quantify the impact of digital disruption.", "data_requested": "Win/loss data vs. specific disruptors.", "source_ref_id": "ref4"}
                ],
                "notes": None
            },
            "product_differentiation_assessment": {
                 "summary": "Strong differentiation in energy efficiency (validated) and reliability. Service metrics strong. However, digital feature set lags key competitors.", "summary_source_ref_id": "ref5",
                 "key_product_line_assessments": [
                      {"product_area": "Energy Optimization Tech", "differentiation_claim": "Superior efficiency", "validation_metrics": [{"metric_name": "Efficiency vs Industry Avg", "value": "+6.2 ppts better", "source_ref_id": "ref5"}], "sustainability_assessment": "Sustainable near-term due to patents, but requires ongoing R&D.", "source_ref_id": "ref5"},
                      {"product_area": "Digital Platform Features", "differentiation_claim": "Comprehensive connected solution", "validation_metrics": [{"metric_name": "Feature Score vs Competitor A", "value": "72 vs 82.5", "source_ref_id": "ref5"}], "sustainability_assessment": "Gap likely to widen without accelerated development.", "source_ref_id": "ref5"}
                 ],
                 "customer_perception_summary": {"nps_score": 42, "unit": "NPS", "trend_24m": "+5 pts", "vs_peer_avg": "+7 pts", "source_ref_id": "ref6"},
                 "due_diligence_questions": [
                     {"question": "What is the detailed technical roadmap and investment plan ($ and FTEs) for the digital platform to achieve feature parity with Competitor A and key software natives?", "rationale": "Assess commitment and feasibility of closing the digital gap.", "data_requested": "Detailed roadmap, resource plan.", "source_ref_id": "ref7"},
                     {"question": "Provide third-party validation or head-to-head testing results for product reliability (MTBF) against Competitors A and B.", "rationale": "Verify claims of superior reliability.", "data_requested": "Independent test reports.", "source_ref_id": "ref7"}
                 ],
                 "notes": None
            },
             "pricing_power_assessment": {
                 "summary": "Demonstrated ability to pass through costs better than industry average in 2023, but realization rates softening and price premium vs leader narrowing. Significant pressure in standard hardware.", "summary_source_ref_id": "ref8",
                 "key_pricing_metrics": [
                      {"metric_name": "Price Realization Rate (FY23)", "current_value": 82.7, "unit": "%", "trend_24m": "Down from 84.4% (FY22)", "comparison": "Still above industry avg 78.5%", "implication": "Some softening of pricing power.", "source_ref_id": "ref8"},
                      {"metric_name": "Price Premium vs Competitor A", "current_value": 3.2, "unit": "%", "trend_24m": "Down from 3.7%", "comparison": None, "implication": "Leader A closing gap slightly.", "source_ref_id": "ref8"},
                      {"metric_name": "Cost Pass-Through Rate (FY23)", "current_value": 102.4, "unit": "%", "trend_24m": "Up significantly from 65.5% (FY22)", "comparison": "Well above industry avg 85.5%", "implication": "Successfully passed on costs in FY23.", "source_ref_id": "ref8"}
                 ],
                "due_diligence_questions": [
                     {"question": "Provide detailed pricing analysis by SKU/product line showing list price changes, average selling price (ASP) trends, and discount levels for the past 8 quarters.", "rationale": "Uncover true net pricing trends masked by averages.", "data_requested": "SKU-level ASP and discount data.", "source_ref_id": "ref9"},
                     {"question": "What specific mechanisms are used for cost pass-through, and what percentage of contracts allow for direct material or labor cost adjustments?", "rationale": "Assess structural ability to manage future inflation.", "data_requested": "Contract analysis, pricing policy details.", "source_ref_id": "ref9"}
                ],
                "notes": None
            },
            "cost_position_assessment": {
                 "summary": "Overall cost position appears favorable vs industry average (Gross Margin, SG&A % Rev), but manufacturing cost per unit potentially lags key competitors like A and C.", "summary_source_ref_id": "ref10",
                 "key_cost_metrics": [
                      {"metric_name": "Gross Margin", "company_value": 42.5, "unit": "%", "comparison_value": 41.3, "comparison_point": "Industry Avg", "relative_position": "+1.2 ppts advantage", "trend_24m": "-0.8 ppts", "source_ref_id": "ref10"},
                      {"metric_name": "SG&A % Revenue", "company_value": 22.8, "unit": "%", "comparison_value": 23.5, "comparison_point": "Industry Avg", "relative_position": "-0.7 ppts advantage (better)", "trend_24m": "-0.5 ppts", "source_ref_id": "ref10"},
                      {"metric_name": "Mfg Cost/Unit Index", "company_value": 100, "unit": "Index", "comparison_value": 95, "comparison_point": "Competitor A", "relative_position": "-5 points disadvantage", "trend_24m": "-3.0%", "source_ref_id": "ref10"}
                 ],
                 "key_cost_drivers": ["Higher labor costs in Western facilities", "Component sourcing costs"], "key_cost_drivers_source_ref_id": "ref10",
                 "due_diligence_questions": [
                      {"question": "Provide a detailed manufacturing cost benchmark study comparing Company's cost per unit against Competitors A, B, and C by major product line and geography.", "rationale": "Validate relative manufacturing cost position.", "data_requested": "Detailed cost benchmarking data.", "source_ref_id": "ref11"},
                      {"question": "What is the roadmap for further manufacturing cost reduction, including specific automation investments, supply chain optimization efforts, and expected savings?", "rationale": "Assess potential for future cost improvements.", "data_requested": "Cost reduction plan and targets.", "source_ref_id": "ref11"}
                 ],
                 "notes": "Efficiency gains partially offset hardware margin pressure."
            },
             "advantages_disadvantages_validation": {
                 "summary": "Energy optimization tech and integration expertise appear to be validated advantages. Key risks center on digital capability gap and hardware commoditization.", "summary_source_ref_id": "ref12",
                 "validated_advantages": [
                     {"advantage_name": "Energy Optimization Technology", "validation_summary": "Supported by superior performance metrics, customer ROI data, and market share gains.", "sustainability_comment": "Sustainable near-term (IP), requires ongoing R&D.", "source_ref_id": "ref12"},
                     {"advantage_name": "Integration Expertise", "validation_summary": "Validated by high success rates, faster timelines vs peers, and strong service revenue.", "sustainability_comment": "Depends on retaining specialized talent.", "source_ref_id": "ref12"}
                 ],
                 "key_risks_and_vulnerabilities": [
                     {"vulnerability_name": "Digital Capability Gap", "risk_summary": "Lags key competitors, impacting win rates and recurring revenue transition.", "quantification": "40% engineer gap, feature score 6.2/10", "source_ref_id": "ref12"},
                     {"vulnerability_name": "Hardware Commoditization", "risk_summary": "Significant revenue (~42%) exposed to accelerating price erosion.", "quantification": "Margins compressed 1.3 ppts in FY23", "source_ref_id": "ref12"}
                 ],
                 "due_diligence_questions": [
                     {"question": "What is the multi-year plan and budget to sustain the competitive advantage in energy optimization technology, including R&D roadmap and patent strategy?", "rationale": "Validate defensibility of key strength.", "data_requested": "Energy tech roadmap & budget.", "source_ref_id": "ref13"},
                     {"question": "Provide a detailed customer cohort analysis showing adoption rates, revenue per customer, and retention for customers primarily utilizing standard hardware vs. those adopting integrated solutions/services.", "rationale": "Quantify the financial benefit and risk associated with the business model transition.", "data_requested": "Customer cohort financial analysis.", "source_ref_id": "ref13"}
                 ],
                 "notes": None
            },
            "footnotes": [
                {"id": "ref1", "document": "Competitive Position Assessment", "page": "3-5", "section": "Executive Summary", "date": "Mar 2024"},
                {"id": "ref2", "document": "Market Share Analysis", "page": "8-12", "section": "Trends & Win Rates", "date": "Feb 2024"},
                {"id": "ref3", "document": "Competitive Landscape Overview", "page": "10-15", "section": "Peer Analysis", "date": "Jan 2024"},
                {"id": "ref4", "document": "Due Diligence Framework: Market Position", "page": "5-8", "section": "Key Questions", "date": "Mar 2024"},
                {"id": "ref5", "document": "Product Benchmarking Study", "page": "12-18", "section": "Differentiation Metrics", "date": "Dec 2023"},
                {"id": "ref6", "document": "Customer Satisfaction Survey Results", "page": "8-15", "section": "Loyalty Metrics", "date": "Feb 2024"},
                {"id": "ref7", "document": "Due Diligence Framework: Product", "page": "6-9", "section": "Key Questions", "date": "Mar 2024"},
                {"id": "ref8", "document": "Pricing Power Analysis", "page": "5-10", "section": "Key Metrics", "date": "Jan 2024"},
                {"id": "ref9", "document": "Due Diligence Framework: Pricing", "page": "4-7", "section": "Key Questions", "date": "Mar 2024"},
                {"id": "ref10", "document": "Cost Structure Benchmarking", "page": "8-14", "section": "Relative Efficiency", "date": "Feb 2024"},
                {"id": "ref11", "document": "Due Diligence Framework: Cost Position", "page": "6-8", "section": "Key Questions", "date": "Mar 2024"},
                {"id": "ref12", "document": "Competitive Advantage Assessment", "page": "5-12", "section": "Validation & Risks", "date": "Mar 2024"},
                {"id": "ref13", "document": "Due Diligence Framework: Comp. Strategy", "page": "7-10", "section": "Key Questions", "date": "Mar 2024"},
                 {"id": "ref14", "document": "Valuation Analysis Report", "page": "5-10", "section": "Relative Valuation Metrics", "date": "Mar 2024"}, # Ref from Sec 25 template
                 {"id": "ref15", "document": "Financial Performance Benchmarking", "page": "12-18", "section": "Peer Comparison", "date": "Mar 2024"} # Ref from Sec 25 template
            ]
        }
    },
# --- END: Section 28 Definition ---

# --- START: Section 29 Definition ---
    {
        "number": 29,
        "title": "Buyside Due Diligence - Operating Performance",
        "specs": ("From a potential buyer's perspective, critically analyze the 3 most important operating metrics that materially impact the Company's economic performance and valuation, focusing on risks and sustainability over the last 24 months.\n"
                  "Go beyond standard financial statement items. Prioritize metrics like market share trends in key segments (risk of loss?), volume vs price drivers of growth, unit economics/margins, customer acquisition cost (CAC) trends, customer lifetime value (CLTV) vs CAC, customer churn/retention rates (especially by cohort or segment), and asset utilization trends (potential inefficiencies?).\n"
                  "For each key operating metric analyzed:\n"
                  "  - Provide a clear definition and explain its relevance from a buyside diligence perspective (what risk/opportunity does it highlight?).\n"
                  "  - Present historical data (last 24 months, quarterly if possible), clearly showing trends and volatility.\n"
                  "  - Benchmark against key competitors and/or industry averages, focusing on areas where the Company underperforms or where positive trends might be unsustainable.\n"
                  "  - Analyze the underlying *drivers* of the metric's performance, questioning the sustainability or quality of those drivers.\n"
                  "  - Assess the *sustainability* of the current performance trend, explicitly identifying potential risks or headwinds that could cause deterioration.\n"
                  "  - Quantify the *potential financial impact* of any identified risks related to this metric (e.g., impact of rising churn on future revenue, impact of falling utilization on margins).\n"
                  "  - Formulate 2-3 specific, data-driven due diligence questions a potential buyer must ask to validate the metric, understand its drivers, and assess associated risks.\n"
                  "All data points must reference the specific point in time or time period they relate to.\n"
                  "All analysis should be supported by specific data points, quantitative examples, and source references.\n"
                  "Ensure all footnotes provide precise source details: document name, date, page number, and specific section/table."),
        "schema": {
            "overview": { # Optional overview
                "description": None, # string summarizing key operating performance risks/areas for diligence
                "description_source_ref_id": None
            },
            "key_operating_metrics_analysis": [ # List of 3 key metrics analyzed for risk/sustainability
                { # Structure for ONE metric analysis
                    "priority": None, # Optional number (1, 2, 3)
                    "metric_name": None, # string (e.g., "Customer Churn Rate", "Premium Segment Market Share Trend")
                    "metric_name_source_ref_id": None,
                    "definition_and_relevance": None, # string explaining metric and why it's key for DD
                    "definition_and_relevance_source_ref_id": None,
                    "historical_trend_analysis": {
                        "summary": None, # string describing the observed trend
                        "summary_source_ref_id": None,
                        "data_points": [ # List of quarterly/annual data
                            {"period": None, "value": None, "unit": None, "source_ref_id": None}
                        ],
                         "notes": None # Optional notes on trend calculation/volatility
                    },
                    "benchmark_analysis": { # Comparison focusing on relative weakness or risk
                        "summary": None, # string summarizing comparison outcome
                        "summary_source_ref_id": None,
                        "benchmarks": [ # List of comparisons
                            {
                                "comparison_point": None, # string (e.g., "Competitor A", "Industry Average")
                                "company_value": None,
                                "benchmark_value": None,
                                "unit": None,
                                "relative_performance_comment": None, # string highlighting gap or risk
                                "source_ref_id": None
                            }
                        ],
                        "notes": None
                    },
                    "driver_analysis": { # Analysis of what's driving the metric
                        "summary": None, # string summarizing key drivers
                        "summary_source_ref_id": None,
                        "key_drivers": [ # List of drivers
                            {
                                "driver": None, # string
                                "impact": None, # string (e.g., "Positive but potentially temporary", "Negative due to...")
                                "sustainability_concern": None, # Optional string raising question about driver persistence
                                "source_ref_id": None
                            }
                        ],
                         "notes": None
                    },
                    "sustainability_assessment": { # Assessment of trend persistence & risks
                        "assessment": None, # string (e.g., "Trend appears sustainable", "Significant risk of deterioration due to X")
                        "assessment_source_ref_id": None,
                        "key_risks": [], # List of strings describing risks to the metric
                        "key_risks_source_ref_id": None
                    },
                    "potential_financial_impact": { # Quantified risk impact
                        "description": None, # string explaining potential financial consequence
                        "description_source_ref_id": None,
                        "quantification_scenario": { # Example scenario
                            "scenario_name": None, # e.g., "Scenario: Churn increases 2 ppts"
                            "impact_metric": None, # e.g., "Annual Recurring Revenue Loss"
                            "value": None,
                            "unit": None,
                            "period": None,
                            "source_ref_id": None
                        },
                        "notes": None
                    },
                    "due_diligence_questions": [ # List of 2-3 DD questions for this metric
                         {
                              "question": None, "rationale": None, "data_requested": None, "source_ref_id": None
                         }
                    ],
                    "notes": None # Optional overall metric notes
                }
            ],
            "footnotes": [ # Top-level list for all footnotes in this section
                { # Structure definition for ONE footnote
                    "id": None, "document": None, "page": None, "section": None, "date": None 
                }
            ]
        },
        "template": { # Example data aligned with refined schema
            "overview": {
                "description": "Buyside diligence on operating performance should focus on the sustainability of recent market share gains in premium segments given competitive responses, the underlying drivers and cohort behavior of customer churn improvements, and potential risks to manufacturing utilization from slowing demand or supply issues.", "description_source_ref_id": "ref1"
            },
            "key_operating_metrics_analysis": [
                { # Example Analysis 1: Market Share Sustainability
                    "priority": 1,
                    "metric_name": "Premium Segment Market Share Trend", "metric_name_source_ref_id": "ref2",
                    "definition_and_relevance": "Company's share in high-margin Premium Industrial Automation segment. Key to validating growth story and margin assumptions; gains need to be sustainable against competition.", "definition_and_relevance_source_ref_id": "ref2",
                    "historical_trend_analysis": {
                        "summary": "Strong gains over past 24m, increasing from 15.8% to 18.9%.", "summary_source_ref_id": "ref2",
                        "data_points": [ {"period": "Q1 2022", "value": 15.8, "unit": "%", "source_ref_id": "ref2"}, {"period": "Q1 2024", "value": 18.9, "unit": "%", "source_ref_id": "ref2"} ],
                        "notes": "Growth driven primarily in FY23."
                    },
                    "benchmark_analysis": {
                        "summary": "Gains outpaced key competitors A (+0.8ppts) and B (-0.5ppts) over same period.", "summary_source_ref_id": "ref3",
                        "benchmarks": [{"comparison_point": "Competitor A Share Change", "company_value": "+3.1 ppts", "benchmark_value": "+0.8 ppts", "unit": None, "relative_performance_comment": "Company gained share significantly faster.", "source_ref_id": "ref3"}],
                        "notes": None
                    },
                    "driver_analysis": {
                        "summary": "Driven by successful new product launch (X1000) and competitor B's product cycle issues.", "summary_source_ref_id": "ref2",
                        "key_drivers": [
                            {"driver": "X1000 Product Launch", "impact": "Positive", "sustainability_concern": "Initial launch boost may fade.", "source_ref_id": "ref2"},
                            {"driver": "Competitor B Product Delays", "impact": "Positive", "sustainability_concern": "Competitor B expected to launch new competing product H2 2024.", "source_ref_id": "ref3"}
                        ],
                        "notes": None
                    },
                    "sustainability_assessment": {
                        "assessment": "Risk that recent strong gains may not be sustainable as competitors respond and initial launch impact diminishes.", "assessment_source_ref_id": "ref1",
                        "key_risks": ["Increased competition from Competitor A/B new launches", "Cannibalization of older products"], "key_risks_source_ref_id": "ref1"
                    },
                    "potential_financial_impact": {
                        "description": "Slowing share gains could impact revenue growth targets and potentially margins if price competition increases.", "description_source_ref_id": "ref1",
                        "quantification_scenario": {"scenario_name": "Scenario: Share gain rate halves", "impact_metric": "FY25 Revenue Growth", "value": "-1.5 ppts", "unit": None, "period": "FY2025", "source_ref_id": "ref1"}
                    },
                    "due_diligence_questions": [
                         {"question": "Provide market share data broken down by product generation (e.g., X1000 vs older models) and customer cohort (new vs existing) for the premium automation segment.", "rationale": "Understand the source and stickiness of share gains.", "data_requested": "Detailed cohort share analysis.", "source_ref_id": "ref1"},
                         {"question": "What is management's competitive response plan to Competitor A's increased investment and Competitor B's anticipated new product launch in the premium segment?", "rationale": "Assess proactive strategy vs reactive.", "data_requested": "Competitive response plan, R&D pipeline.", "source_ref_id": "ref1"}
                    ],
                    "notes": None
                },
                 { # Example Analysis 2: Churn
                    "priority": 2,
                    "metric_name": "Customer Churn Rate (Annualized)", "metric_name_source_ref_id": "ref5",
                    "definition_and_relevance": "Percentage of customers lost annually. High churn indicates dissatisfaction or competitive vulnerability, impacting LTV and recurring revenue stability.", "definition_and_relevance_source_ref_id": "ref5",
                    "historical_trend_analysis": {
                        "summary": "Overall churn improved significantly from 8.2% (Q1 2022) to 6.0% (Q1 2024).", "summary_source_ref_id": "ref5",
                        "data_points": [ {"period": "Q1 2022", "value": 8.2, "unit": "%", "source_ref_id": "ref5"}, {"period": "Q1 2023", "value": 7.0, "unit": "%", "source_ref_id": "ref5"}, {"period": "Q1 2024", "value": 6.0, "unit": "%", "source_ref_id": "ref5"} ],
                        "notes": "Improvement consistent over period."
                    },
                    "benchmark_analysis": {
                         "summary": "Current churn significantly better than industry average (9.0%) and key competitors A (7.5%) and B (8.2%).", "summary_source_ref_id": "ref6",
                         "benchmarks": [{"comparison_point": "Industry Average", "company_value": 6.0, "benchmark_value": 9.0, "unit": "%", "relative_performance_comment": "Company 3 ppts better.", "source_ref_id": "ref6"}],
                         "notes": None
                    },
                    "driver_analysis": {
                        "summary": "Driven by improved product reliability, proactive customer success initiatives, and increased adoption of stickier subscription services.", "summary_source_ref_id": "ref5",
                        "key_drivers": [
                             {"driver": "Customer Success Program", "impact": "Positive", "sustainability_concern": "Scalability as customer base grows?", "source_ref_id": "ref5"},
                             {"driver": "Subscription Model Adoption", "impact": "Positive (lower churn for subscribers)", "sustainability_concern": "Pace of adoption slowing?", "source_ref_id": "ref5"}
                        ],
                        "notes": None
                    },
                     "sustainability_assessment": {
                         "assessment": "Improvement trend likely sustainable but further significant reduction below 6% may be difficult. Risk if key drivers falter.", "assessment_source_ref_id": "ref1",
                         "key_risks": ["Competition targeting installed base", "Failure to scale customer success team"], "key_risks_source_ref_id": "ref1"
                     },
                    "potential_financial_impact": {
                        "description": "If churn reverts towards industry average, it would negatively impact recurring revenue growth and customer lifetime value.", "description_source_ref_id": "ref1",
                        "quantification_scenario": {"scenario_name": "Scenario: Churn increases to 8%", "impact_metric": "Annual Recurring Revenue", "value": "-$35M", "unit": "USD", "period": "Annual impact", "source_ref_id": "ref1"}
                    },
                     "due_diligence_questions": [
                        {"question": "Provide customer churn data segmented by customer size, geography, product line, and acquisition cohort for the past 36 months.", "rationale": "Identify specific segments driving churn improvement or posing risk.", "data_requested": "Detailed segmented churn analysis.", "source_ref_id": "ref1"},
                        {"question": "What is the quantitative impact of the Customer Success program on churn reduction and upsell rates? Provide supporting data and cost analysis for the program.", "rationale": "Validate effectiveness and ROI of key retention driver.", "data_requested": "Customer Success program metrics and financials.", "source_ref_id": "ref1"}
                    ],
                    "notes": None
                 }
                 # ... Add Metric Analysis 3 (e.g., Capacity Utilization Risks) ...
            ],
            "footnotes": [
                {"id": "ref1", "document": "Buyside Ops DD Memo (Internal)", "page": "5", "section": "Key Risk Areas", "date": "Apr 2024"},
                {"id": "ref2", "document": "Market Share Analysis Report", "page": "10-15", "section": "Premium Segment", "date": "Feb 2025"},
                # {"id": "ref3", ...} # Add footnotes for competitor share data if different
                {"id": "ref4", "document": "Competitive Benchmarking: Digital", "page": "12-22", "section": "Relative Positioning", "date": "Mar 2024"}, # Example reuse
                {"id": "ref5", "document": "Customer Retention Analysis", "page": "Internal", "section": "Churn Trends", "date": "Q1 2024"},
                {"id": "ref6", "document": "Industry Customer Loyalty Study", "page": "45", "section": "Churn Benchmarks", "date": "Feb 2024"}
                # ... Add all other necessary footnotes
            ]
        }
    },
# --- END: Section 29 Definition ---

# --- START: Section 30 Definition ---
    {
        "number": 30,
        "title": "Buyside Due Diligence - Financial Performance",
        "specs": ("From a potential buyer's perspective, critically analyze 5-7 key financial metrics to identify potential risks, quality concerns, and areas requiring deeper investigation.\n"
                  "Focus on the quality and sustainability of reported earnings, margins, cash flows, and returns. Go beyond headline numbers.\n"
                  "For each key financial metric analyzed:\n"
                  "  - Provide a clear definition and explain its relevance for assessing financial health and risk from a buyside perspective.\n"
                  "  - Present historical data (last 24 months, quarterly if possible), showing trends, volatility, and comparisons to relevant benchmarks (peers, industry, internal budgets/forecasts).\n"
                  "  - Perform a 'Quality Assessment': Analyze accounting policies, identify one-time items, non-recurring revenues/costs, unusual adjustments, or potential earnings management indicators that might distort the underlying performance.\n"
                  "  - Assess 'Sustainability': Evaluate whether the current level or trend of the metric is sustainable given underlying drivers, potential headwinds (macro/industry/competitive), and company-specific factors. Identify key risks to future performance.\n"
                  "  - Quantify the 'Potential Financial Impact' of identified quality concerns or sustainability risks (e.g., impact of normalizing margins, impact of non-recurring items ending, sensitivity to driver changes).\n"
                  "  - Formulate 2-3 specific, data-driven due diligence questions a potential buyer must ask to probe the quality, sustainability, and risks associated with the metric.\n"
                  "Include forensic accounting review points if apparent from the documents (e.g., unusual changes in accounting estimates, large unexplained accruals, revenue recognition timing issues).\n"
                  "All analysis must be supported by specific data points, quantitative examples, and source references.\n"
                  "Ensure all footnotes provide precise source details: document name, date, page number, and specific section/table (Financial Statements, Notes, MD&A)."),
        "schema": {
            "overview": { # Optional overview
                "description": None, # string summarizing key financial diligence areas and potential risks
                "description_source_ref_id": None
            },
            "key_financial_metrics_analysis": [ # List of 5-7 key metrics analyzed
                { # Structure for ONE metric analysis
                    "priority": None, # Optional number
                    "metric_name": None, # string (e.g., "Recurring Revenue Quality", "Gross Margin Sustainability")
                    "metric_name_source_ref_id": None,
                    "definition_and_relevance": None, # string explaining metric and buyside importance
                    "definition_and_relevance_source_ref_id": None,
                    "historical_trend_and_benchmark": { # Combined trend and comparison data
                        "summary": None, # string describing trend relative to benchmarks
                        "summary_source_ref_id": None,
                        "trend_data": [ # List of quarterly/annual data
                            {"period": None, "value": None, "unit": None, "source_ref_id": None}
                        ],
                        "benchmark_comparison": [ # List of comparisons
                            {
                                "comparison_point": None, # string (e.g., "Peer Average", "Budget")
                                "company_value": None,
                                "benchmark_value": None,
                                "unit": None,
                                "variance_comment": None, # string explaining gap/performance vs benchmark
                                "source_ref_id": None
                            }
                        ],
                        "notes": None # Optional notes on data
                    },
                    "quality_assessment": { # Assessing accounting, adjustments, one-timers
                        "assessment_summary": None, # string summarizing quality concerns or lack thereof
                        "assessment_summary_source_ref_id": None,
                        "supporting_points": [ # List of observations
                            {
                                 "point_type": None, # string (e.g., "Accounting Policy", "One-Time Item", "Adjustment Analysis")
                                 "description": None, # string detailing the observation
                                 "potential_impact": None, # Optional string on how it might distort results
                                 "source_ref_id": None
                            }
                        ],
                        "forensic_review_flags": [], # Optional list of strings noting potential red flags
                        "forensic_review_flags_source_ref_id": None,
                        "notes": None
                    },
                    "sustainability_assessment": { # Assessing if trend/level can continue
                        "assessment_summary": None, # string (e.g., "High risk of margin compression", "Growth appears sustainable if X holds")
                        "assessment_summary_source_ref_id": None,
                        "key_drivers_and_risks": [ # List analyzing drivers and associated risks
                            {
                                "driver_or_risk": None, # string
                                "impact": None, # string (e.g., "Positive driver but dependent on...", "Negative risk due to...")
                                "mitigation_assessment": None, # Optional string on company's mitigation (if any)
                                "source_ref_id": None
                            }
                        ],
                        "notes": None
                    },
                    "potential_financial_impact_quantification": { # Quantified risk impact
                        "summary": None, # string summarizing potential downside/normalization impact
                        "summary_source_ref_id": None,
                        "quantification_scenarios": [ # List of scenarios
                            { 
                                "scenario_name": None, # e.g., "Scenario: Normalize One-Time Items", "Scenario: Margin reverts to peer avg"
                                "impact_metric": None, # e.g., "Adjusted EBITDA", "Implied Valuation Change"
                                "value_impact": None, # number or string
                                "unit": None,
                                "period": None,
                                "assumptions": None, # Optional string of assumptions
                                "source_ref_id": None
                            }
                        ],
                        "notes": None
                    },
                    "due_diligence_questions": [ # List of 2-3 DD questions for this metric
                         {
                              "question": None, "rationale": None, "data_requested": None, "source_ref_id": None
                         }
                    ],
                    "notes": None # Optional overall metric notes
                }
            ],
            "footnotes": [ # Top-level list for all footnotes in this section
                { # Structure definition for ONE footnote
                    "id": None, "document": None, "page": None, "section": None, "date": None 
                }
            ]
        },
        "template": { # Example data aligned with refined schema
            "overview": {
                "description": "While reported financials show strong headline growth and profitability, buyside diligence should focus on the quality and sustainability of recurring revenue, potential gross margin pressure from hardware commoditization, working capital normalization risks, and the impact of capitalized software development costs.", "description_source_ref_id": "ref1"
            },
            "key_financial_metrics_analysis": [
                { # Example Analysis 1: Recurring Revenue Quality
                    "priority": 1,
                    "metric_name": "Recurring Revenue Quality & Sustainability", "metric_name_source_ref_id": "ref2",
                    "definition_and_relevance": "Assesses the predictability and quality of the growing recurring revenue stream, critical for supporting higher valuation multiples.", "definition_and_relevance_source_ref_id": "ref2",
                    "historical_trend_and_benchmark": {
                        "summary": "Recurring revenue grew from 22% to 28.5% of total over 9 quarters, outpacing industry but slightly slower than top competitor A.", "summary_source_ref_id": "ref2",
                        "trend_data": [ {"period": "Q1 2022", "value": 22.0, "unit": "%", "source_ref_id": "ref2"}, {"period": "Q1 2024", "value": 28.5, "unit": "%", "source_ref_id": "ref2"} ],
                        "benchmark_comparison": [{"comparison_point": "Competitor A Recur%", "company_value": 28.5, "benchmark_value": 35.2, "unit": "%", "variance_comment": "Company lags leader A but ahead of avg (25.5%)", "source_ref_id": "ref3"}],
                        "notes": None
                    },
                    "quality_assessment": {
                        "assessment_summary": "Revenue recognition appears appropriate (ASC 606). Mix includes high-quality subscription (~60% of recurring) and standard maintenance (~40%). No major one-timers identified.", "assessment_summary_source_ref_id": "ref4",
                        "supporting_points": [ {"point_type": "Rev Rec Policy", "description": "Standard subscription/service recognition.", "potential_impact": None, "source_ref_id": "ref4"} ],
                        "forensic_review_flags": [], "notes": None
                    },
                    "sustainability_assessment": {
                        "assessment_summary": "Growth sustainability concern due to software capability gap and potential churn increase if product lags.", "assessment_summary_source_ref_id": "ref5",
                        "key_drivers_and_risks": [ {"driver_or_risk": "Driver: Cross-selling to installed base", "impact": "Positive but conversion rate plateauing?", "mitigation_assessment": None, "source_ref_id": "ref5"}, {"driver_or_risk": "Risk: Competition from SaaS natives", "impact": "Could increase churn/slow new adoption", "mitigation_assessment": "Company response lagging", "source_ref_id": "ref5"} ],
                        "notes": None
                    },
                    "potential_financial_impact_quantification": {
                         "summary": "Failure to reach 40% target could impact valuation.", "summary_source_ref_id": "ref5",
                         "quantification_scenarios": [{"scenario_name": "Scenario: Recurring Rev plateaus at 32%", "impact_metric": "EV/EBITDA Multiple", "value_impact": "-0.5x to -1.0x", "unit": None, "period": "Target Valuation", "assumptions": "Market continues to reward recurring revenue", "source_ref_id": "ref5"}]
                    },
                    "due_diligence_questions": [
                        {"question": "Provide a detailed cohort analysis of recurring revenue customers showing retention rates, expansion revenue (upsell/cross-sell), and average revenue per user (ARPU) trends by cohort.", "rationale": "Assess true stickiness and growth potential within recurring base.", "data_requested": "Recurring revenue cohort data.", "source_ref_id": "ref1"},
                        {"question": "What percentage of recurring revenue is tied to multi-year contracts versus month-to-month or annual renewals? Provide breakdown by contract length.", "rationale": "Understand predictability and lock-in of recurring stream.", "data_requested": "Contract length distribution for recurring revenue.", "source_ref_id": "ref1"}
                    ],
                    "notes": None
                },
                 { # Example Analysis 2: Gross Margin
                    "priority": 2,
                    "metric_name": "Gross Margin Sustainability", "metric_name_source_ref_id": "ref31", # Using refs from Section 7 template
                    "definition_and_relevance": "Measures profitability after direct costs; sustainability crucial for earnings quality and cash flow.", "definition_and_relevance_source_ref_id": "ref31",
                    "historical_trend_and_benchmark": {
                        "summary": "Gross margin declined consistently from 43.8% (Q1'22) to 41.3% (Q1'24), slightly underperforming industry average (43.1%) recently despite previous outperformance.", "summary_source_ref_id": "ref31",
                        "trend_data": [ {"period": "Q1 2022", "value": 43.8, "unit": "%", "source_ref_id": "ref31"}, {"period": "Q1 2024", "value": 41.3, "unit": "%", "source_ref_id": "ref31"} ],
                        "benchmark_comparison": [{"comparison_point": "Industry Average (Q1'24)", "company_value": 41.3, "benchmark_value": 43.1, "unit": "%", "variance_comment": "Company now 1.8 ppts below average", "source_ref_id": "ref32"}],
                        "notes": "Declining trend is a key concern."
                    },
                     "quality_assessment": {
                         "assessment_summary": "COGS accounting appears standard. Main quality issue is understanding mix impact vs pure price/cost pressure.", "assessment_summary_source_ref_id": "ref33",
                         "supporting_points": [{"point_type": "Cost Allocation", "description": "Standard inventory accounting (FIFO).", "potential_impact": None, "source_ref_id": "ref33"}],
                         "forensic_review_flags": [], "notes": None
                     },
                    "sustainability_assessment": {
                        "assessment_summary": "High risk of further compression due to hardware price pressure and rising input costs, only partially offset by mix shift.", "assessment_summary_source_ref_id": "ref34",
                        "key_drivers_and_risks": [ {"driver_or_risk": "Risk: Hardware Price Erosion", "impact": "Accelerating (-3.2% Q1'24) in largest segment.", "mitigation_assessment": "Bundling/value-pricing partially effective.", "source_ref_id": "ref34"}, {"driver_or_risk": "Risk: Input Cost Inflation", "impact": "Negative price/cost gap widened in Q1'24.", "mitigation_assessment": "Hedging provides limited protection.", "source_ref_id": "ref34"} ],
                        "notes": None
                    },
                    "potential_financial_impact_quantification": {
                        "summary": "Potential for significant EBITDA impact if margins continue to decline.", "summary_source_ref_id": "ref34",
                        "quantification_scenarios": [{"scenario_name": "Scenario: Gross Margin drops another 1 ppt", "impact_metric": "Annual EBITDA", "value_impact": "~$45M reduction", "unit": None, "period": "Next 12M", "assumptions": "Constant revenue", "source_ref_id": "ref34"}]
                    },
                     "due_diligence_questions": [
                         {"question": "Provide a detailed gross margin bridge analysis for the past 8 quarters, quantifying the impact of volume, price, mix, input costs, manufacturing efficiencies, and FX.", "rationale": "Isolate true drivers of margin change.", "data_requested": "Quarterly margin bridge.", "source_ref_id": "ref1"},
                         {"question": "What are the specific contractual protections or pass-through mechanisms for key input cost categories (electronics, metals)? Quantify historical effectiveness.", "rationale": "Assess ability to mitigate future inflation.", "data_requested": "Supplier contract details, pass-through analysis.", "source_ref_id": "ref1"}
                     ],
                    "notes": None
                 }
                 # ... Add Analysis 3 (e.g., FCF Conversion Sustainability) ...
                 # ... Add Analysis 4 (e.g., Capitalized Software Costs) ...
                 # ... Add Analysis 5 (e.g., Accounts Receivable Quality / DSO) ...
            ],
            "footnotes": [
                 {"id": "ref1", "document": "Buyside Financial DD Memo (Internal)", "page": "3", "section": "Key Risk Areas", "date": "Apr 2024"},
                 {"id": "ref2", "document": "Company Financial Reports (Compiled Q1'22-Q1'24)", "page": "Various", "section": "Segment Data", "date": "Various"},
                 {"id": "ref3", "document": "Peer Financial Benchmarking Report", "page": "15", "section": "Recurring Revenue", "date": "Q1 2024"},
                 {"id": "ref4", "document": "Company Audit Reports FY21-FY23", "page": "Auditor Opinion", "section": "Revenue Recognition Note", "date": "Various"},
                 {"id": "ref5", "document": "Internal Strategic Plan Update", "page": "8", "section": "Recurring Revenue Forecast", "date": "Q1 2024"},
                 # {"id": "ref6 onwards...", ...} # Add footnotes for other examples/data points
                 {"id": "ref31", "document": "Company Financial Reports (Compiled Q1'22-Q1'24)", "page": "Various", "section": "Income Statement", "date": "Various"},
                 {"id": "ref32", "document": "Peer Financial Benchmarking Report", "page": "18", "section": "Gross Margin Analysis", "date": "Q1 2024"},
                 {"id": "ref33", "document": "Internal Margin Analysis Q1 2024", "page": "5", "section": "Price vs Cost", "date": "Apr 2024"},
                 {"id": "ref34", "document": "Buyside Financial DD Memo (Internal)", "page": "8", "section": "Margin Sustainability Risk", "date": "Apr 2024"}
            ]
        }
    },
# --- END: Section 30 Definition ---

# --- START: Section 31 Definition ---
    {
        "number": 31,
        "title": "Buyside Due Diligence - Management",
        "specs": ("From a potential buyer's perspective, critically evaluate the key members of the management team (C-suite, key reports) and the Board of Directors.\n"
                  "Focus on identifying potential risks related to individual capabilities, alignment, retention, succession planning, and integration readiness.\n"
                  "For each key individual assessed (primarily C-suite and key Board members like Chair, Lead Independent Director):\n"
                  "  - Summarize role and tenure.\n"
                  "  - Critically analyze track record: Validate claimed achievements (last 24 months); identify any documented failures, setbacks, or controversies (at current or prior roles).\n"
                  "  - Assess relevance and depth of experience relative to the Company's *future* strategic needs and potential integration challenges.\n"
                  "  - Identify potential 'red flags' requiring further investigation (e.g., frequent job changes, past business failures, conflicts of interest, capability gaps).\n"
                  "  - Evaluate potential retention risks (e.g., analyze compensation structure for retention hooks like unvested equity, identify potential change-of-control payout impacts, note any signs of dissatisfaction or external opportunities).\n"
                  "Assess the overall management team's experience and track record with M&A integration, major transformations, or restructurings. Identify potential gaps in integration readiness.\n"
                  "Evaluate board effectiveness and independence from a critical perspective. Assess potential conflicts or governance weaknesses.\n"
                  "Formulate 2-3 specific, data-driven due diligence questions for each key individual or area assessed, aimed at probing risks, validating experience, and understanding retention dynamics.\n"
                  "All analysis must be supported by specific data points, quantitative examples, and source references where possible.\n"
                  "Ensure all footnotes provide precise source details: document name, date, page number, and specific section/table (Proxy Statements, Bios, News Articles if cited)."),
        "schema": {
            "overview": { # Optional overview
                "description": None, # string summarizing buyside view on management/board risks & strengths
                "description_source_ref_id": None
            },
            "key_individual_assessments": [ # List of assessments for key people
                { # Structure for ONE individual
                    "name": None, # string
                    "position": None, # string
                    "tenure_summary": None, # string (e.g., "CEO since Mar 2018")
                    "source_ref_id": None, # Source for basic info
                    "track_record_assessment": {
                        "summary": None, # string summarizing track record (buyside view)
                        "summary_source_ref_id": None,
                        "validated_achievements": [ # List confirming key achievements
                             {"achievement": None, "validation_notes": None, "source_ref_id": None}
                        ],
                        "identified_concerns_or_failures": [ # List of potential issues
                             {"concern": None, "details": None, "source_ref_id": None}
                        ],
                        "experience_fit_assessment": None, # string evaluating relevance for future/integration
                        "experience_fit_assessment_source_ref_id": None,
                        "potential_red_flags": [], # List of strings identifying flags
                        "potential_red_flags_source_ref_id": None
                    },
                    "retention_risk_analysis": {
                        "summary": None, # string assessing risk level (Low, Medium, High)
                        "summary_source_ref_id": None,
                        "factors_influencing_risk": [ # List of supporting factors
                            {
                                "factor": None, # string (e.g., "Compensation Structure", "Change of Control Provision", "Recent Departures")
                                "assessment": None, # string evaluating factor's impact on retention
                                "quantification": None, # Optional string/number (e.g., "Unvested Equity: $XM", "CoC Payout: $YM")
                                "source_ref_id": None
                            }
                        ],
                         "notes": None
                    },
                    "due_diligence_questions": [ # 2-3 specific questions for this individual
                         {"question": None, "rationale": None, "data_requested": None, "source_ref_id": None}
                    ],
                    "notes": None # Optional overall notes on individual
                }
            ],
            "team_integration_readiness": { # Assessment of team's M&A/integration experience
                 "summary": None, # string evaluating overall readiness/gaps
                 "summary_source_ref_id": None,
                 "supporting_evidence": [ # List of points supporting assessment
                      {
                           "evidence_type": None, # e.g., "Past M&A Experience", "Transformation Experience", "Identified Gaps"
                           "details": None, # string
                           "source_ref_id": None
                      }
                 ],
                 "due_diligence_questions": [
                     {"question": None, "rationale": None, "data_requested": None, "source_ref_id": None}
                 ],
                  "notes": None
            },
             "board_effectiveness_assessment": { # Critical view of board
                 "summary": None, # string evaluating independence, expertise, potential conflicts
                 "summary_source_ref_id": None,
                 "key_points": [ # List of specific observations
                      {
                           "point_type": None, # e.g., "Independence Level", "Expertise Alignment", "Potential Conflicts"
                           "observation": None, # string detailing the point
                           "implication": None, # string on potential buyside concern
                           "source_ref_id": None
                      }
                 ],
                 "due_diligence_questions": [
                     {"question": None, "rationale": None, "data_requested": None, "source_ref_id": None}
                 ],
                 "notes": None
            },
            "footnotes": [ # Top-level list for all footnotes in this section
                { # Structure definition for ONE footnote
                    "id": None, "document": None, "page": None, "section": None, "date": None 
                }
            ]
        },
        "template": { # Example data aligned with refined schema
            "overview": {
                "description": "Management team led by experienced CEO Miller appears strong operationally, but diligence required on software execution capabilities and CFO Wilson's integration experience. Board independence is adequate but founder influence warrants review. Retention risk appears moderate overall.", "description_source_ref_id": "ref1"
            },
            "key_individual_assessments": [
                { # Example Assessment 1: CEO
                    "name": "James W. Miller", "position": "Chief Executive Officer", "tenure_summary": "CEO since Mar 2018", "source_ref_id": "ref2",
                    "track_record_assessment": {
                        "summary": "Strong track record driving growth and executing strategic shifts (digital, divestiture). Prior relevant experience validated. Key concern is execution gap on software talent.", "summary_source_ref_id": "ref2",
                        "validated_achievements": [ {"achievement": "Delivered 125% TSR since appointment", "validation_notes": "Outperformed industry by 47 ppts", "source_ref_id": "ref4"} ],
                        "identified_concerns_or_failures": [ {"concern": "Missed software hiring targets", "details": "40% shortfall vs plan", "source_ref_id": "ref6"} ],
                        "experience_fit_assessment": "Relevant digital transformation experience, but needs strong tech leader.", "experience_fit_assessment_source_ref_id": "ref2",
                        "potential_red_flags": [], "potential_red_flags_source_ref_id": None
                    },
                    "retention_risk_analysis": {
                        "summary": "Medium risk. Standard CoC provisions. Significant value in unvested equity, but recent performance pressure could impact future grants.", "summary_source_ref_id": "ref7", # Assuming ref7 covers comp details
                        "factors_influencing_risk": [
                            {"factor": "Unvested Equity", "assessment": "Significant retention incentive", "quantification": "Estimated $12M value", "source_ref_id": "ref7"},
                            {"factor": "Change of Control", "assessment": "Standard double-trigger provision", "quantification": "~$25M payout", "source_ref_id": "ref7"},
                            {"factor": "External Market", "assessment": "High demand for experienced transformation CEOs", "quantification": None, "source_ref_id": None}
                        ],
                         "notes": "No obvious signs of dissatisfaction in available documents."
                    },
                    "due_diligence_questions": [
                         {"question": "What are Mr. Miller's specific plans to address the software engineering gap in the next 12 months, beyond current initiatives?", "rationale": "Assess concrete plans to fix key execution gap.", "data_requested": "Hiring plan, budget, potential M&A for talent.", "source_ref_id": "ref1"},
                         {"question": "Discuss Mr. Miller's post-acquisition integration philosophy and experience from prior roles. How would he approach integrating with [Acquirer Name]?", "rationale": "Assess integration readiness and cultural fit.", "data_requested": "Interview discussion, examples from past.", "source_ref_id": "ref1"}
                    ],
                    "notes": None
                },
                 { # Example Assessment 2: CFO
                    "name": "Sarah J. Wilson", "position": "Chief Financial Officer", "tenure_summary": "CFO since June 2020", "source_ref_id": "ref2",
                    "track_record_assessment": {
                        "summary": "Strong financial results (ROIC, FCF conversion improvement). Limited experience leading integration of large-scale acquisitions.", "summary_source_ref_id": "ref8",
                        "validated_achievements": [ {"achievement": "Improved Cash Conversion Cycle by 8.5 days", "validation_notes": "Clear trend in financials", "source_ref_id": "ref10"} ],
                        "identified_concerns_or_failures": [],
                        "experience_fit_assessment": "Excellent financial operator; large-scale integration experience less evident.", "experience_fit_assessment_source_ref_id": "ref8",
                        "potential_red_flags": [], "potential_red_flags_source_ref_id": None
                    },
                     "retention_risk_analysis": {
                         "summary": "Low-Medium risk. Appears well-compensated. CoC provisions standard.", "summary_source_ref_id": "ref7",
                         "factors_influencing_risk": [{"factor": "Compensation vs Peers", "assessment": "Total comp appears competitive (Top quartile)", "quantification": None, "source_ref_id": "ref7"}],
                         "notes": None
                    },
                    "due_diligence_questions": [
                         {"question": "Describe Ms. Wilson's specific experience managing post-merger financial integration, including challenges faced and lessons learned.", "rationale": "Probe experience relevant to potential post-acquisition integration.", "data_requested": "Interview discussion, specific deal examples.", "source_ref_id": "ref1"},
                         {"question": "What are the CFO's key priorities for improving financial systems and reporting capabilities over the next 1-2 years?", "rationale": "Understand potential system upgrade needs/costs post-acquisition.", "data_requested": "Internal finance roadmap.", "source_ref_id": "ref1"}
                    ],
                    "notes": None
                }
                 # ... Add assessments for other key individuals (e.g., Chairman, COO, CTO)...
            ],
            "team_integration_readiness": {
                 "summary": "Team has executed smaller bolt-on acquisitions and divestitures successfully. Experience with large-scale, complex integration (e.g., merging significantly different cultures or systems) appears limited based on disclosed history.", "summary_source_ref_id": "ref12",
                 "supporting_evidence": [
                      {"evidence_type": "Past M&A Experience", "details": "Completed 2 small acquisitions (<$50M) and 1 divestiture ($185M) in last 3 years. Integration reported as smooth.", "source_ref_id": "ref12"},
                      {"evidence_type": "Transformation Experience", "details": "Ongoing digital transformation presents challenges (talent gap) but demonstrates capability for change management.", "source_ref_id": "ref12"},
                      {"evidence_type": "Identified Gaps", "details": "No executive appears to have direct experience leading integration of a similar-sized or larger public company.", "source_ref_id": "ref12"}
                 ],
                 "due_diligence_questions": [
                     {"question": "Does the Company have a documented post-merger integration playbook? If so, please provide it.", "rationale": "Assess level of preparation for integration.", "data_requested": "PMI Playbook/Documentation.", "source_ref_id": "ref1"},
                     {"question": "Who on the executive team would be designated as the integration lead, and what resources would be allocated?", "rationale": "Understand integration leadership and commitment.", "data_requested": "Integration staffing plan.", "source_ref_id": "ref1"}
                 ],
                  "notes": None
            },
             "board_effectiveness_assessment": {
                 "summary": "Board appears adequately independent (73%) and includes relevant industry/tech expertise (Rodriguez, Chen). Founder/Chairman Roberts' significant ownership (15%) and board influence warrant diligence regarding alignment with potential new ownership.", "summary_source_ref_id": "ref11",
                 "key_points": [
                      {"point_type": "Independence Level", "observation": "8 of 11 directors independent.", "implication": "Generally positive, meets exchange standards.", "source_ref_id": "ref11"},
                      {"point_type": "Expertise Alignment", "observation": "Includes Tech CEO, Founder, Finance experts.", "implication": "Relevant skills appear present.", "source_ref_id": "ref11"},
                      {"point_type": "Potential Conflicts", "observation": "Chairman is Founder/major shareholder; Director Chen is spouse of another Director/Founder.", "implication": "Potential for founder interests to diverge from public shareholders/acquirer.", "source_ref_id": "ref11"}
                 ],
                 "due_diligence_questions": [
                     {"question": "Discuss the Board's process for evaluating strategic alternatives, including potential sales of the company. What were the outcomes of the 2022 strategic review regarding M&A?", "rationale": "Understand Board's historical stance on M&A and shareholder value.", "data_requested": "Board minutes extracts (if possible), discussion.", "source_ref_id": "ref1"},
                     {"question": "What are the key terms of the Governance Agreement between the Company and the Founding Families regarding board nominations and transaction approvals?", "rationale": "Clarify influence and potential blocking rights.", "data_requested": "Governance Agreement.", "source_ref_id": "ref1"}
                 ],
                 "notes": None
            },
            "footnotes": [
                {"id": "ref1", "document": "Management DD Assessment (Internal)", "page": "3", "section": "Summary", "date": "Apr 2024"},
                {"id": "ref2", "document": "Annual Proxy Statement 2024", "page": "12-18", "section": "Exec Bios", "date": "Feb 2024"},
                # {"id": "ref3", ...} # Footnotes for achievements
                {"id": "ref4", "document": "CEO Performance Metrics", "page": "8-12", "section": "TSR Analysis", "date": "Feb 2024"},
                {"id": "ref5", "document": "Legacy Components Divestiture PR", "page": "1", "section": None, "date": "Oct 12, 2023"},
                {"id": "ref6", "document": "Technical Resource Plan", "page": "15", "section": "Headcount Gap", "date": "Jan 2024"},
                {"id": "ref7", "document": "Annual Proxy Statement 2024", "page": "40-50", "section": "Compensation Details", "date": "Feb 2024"},
                {"id": "ref8", "document": "CFO Bio & Track Record Review", "page": "Internal Analysis", "section": None, "date": "Apr 2024"},
                # {"id": "ref9", ...} # Footnote for CFO prior role achievement
                {"id": "ref10", "document": "Financial Performance Analysis", "page": "Internal", "section": "CFO Tenure Impact", "date": "Apr 2024"},
                {"id": "ref11", "document": "Corporate Governance Assessment", "page": "12-18", "section": "Board Structure", "date": "Dec 2023"},
                {"id": "ref12", "document": "M&A History Review", "page": "Internal", "section": "Integration Experience", "date": "Apr 2024"}
                # ... Add all other necessary footnotes
            ]
        }
    },
# --- END: Section 31 Definition ---

# --- START: Section 32 Definition ---
    {
        "number": 32,
        "title": "Appendix - Extracted Numerical Data", # Renamed title slightly for clarity
        "specs": "Extract ALL meaningful numerical data points (integers, decimals, percentages) found within the provided source documents.\n"
                 "Exclude page numbers, section numbers, document identifiers, and purely textual dates unless part of a specific numerical data point's context.\n"
                 "For each extracted number:\n"
                 "  - Capture the numerical value itself (ideally as a number, but string is acceptable if needed for format preservation like currency symbols initially).\n"
                 "  - Identify the associated unit of measure if present (e.g., %, USD, million, shares, units, days, years, x for multiples).\n"
                 "  - Identify the time period or 'as of' date the number refers to, if mentioned nearby (e.g., FY2023, Q1 2024, As of Dec 31 2023).\n"
                 "  - Capture a short snippet of the surrounding text (e.g., the sentence or table cell header) that provides context for the number's meaning.\n"
                 "  - Identify the source document's filename.\n"
                 "  - Identify the source page number where the number was found.\n"
                 "  - Identify the source section or table name/header, if discernible.\n"
                 "  - Categorize the number broadly as 'Financial Data', 'Operating Data', or 'Other Data' (e.g., dates, counts, non-financial metrics).\n"
                 "Organize the extracted data grouped by the source document filename.\n"
                 "Include all relevant instances of numbers, even if duplicated.\n"
                 "Output ONLY the structured JSON data according to the schema. Do not perform calculations or add interpretive summaries.",
        "schema": {
            # Schema Option 2: Grouped by Document
            "extracted_data_by_document": [
                { # Structure for ONE document
                    "document_name": None, # string (Filename of the source document)
                    "document_data": [ # List of data points extracted from this document
                        { # Structure for ONE data point
                            "category": None, # string ("Financial Data", "Operating Data", or "Other Data")
                            "value": None,     # number or string (the extracted numerical value)
                            "unit": None,      # Optional string (Unit of measure e.g., "%", "USD", "million")
                            "period": None,    # Optional string (Time period e.g., "FY2023", "Q1 2024")
                            "context_text": None, # string (Surrounding text for context)
                            "source_page": None, # string or number (Page number)
                            "source_section": None # Optional string (Section/Table name)
                        }
                        # This list can contain many data point dictionaries
                    ]
                }
                # This list can contain dictionaries for each source document processed
            ]
        },
        "template": { # Example data aligned with Option 2 schema
            "extracted_data_by_document": [
                { # Data from first document
                    "document_name": "Annual Report 2023.pdf",
                    "document_data": [
                        {
                            "category": "Financial Data",
                            "value": 4572.3,
                            "unit": "million USD",
                            "period": "FY 2023",
                            "context_text": "Consolidated revenues were $4,572.3 million for the year ended December 31, 2023.",
                            "source_page": "F-5",
                            "source_section": "Consolidated Statements of Income"
                        },
                        {
                            "category": "Financial Data",
                            "value": 14.1,
                            "unit": "%",
                            "period": "FY 2023 vs FY 2022",
                            "context_text": "This represents an increase of 14.1% compared to the prior year.",
                            "source_page": "25",
                            "source_section": "MD&A - Results of Operations"
                        },
                        {
                            "category": "Financial Data",
                            "value": 1028.8,
                            "unit": "million USD",
                            "period": "FY 2023",
                            "context_text": "...resulting in EBITDA of $1,028.8 million.",
                            "source_page": "26",
                            "source_section": "MD&A - Non-GAAP Measures"
                        },
                         {
                            "category": "Operating Data",
                            "value": 85.4,
                            "unit": "%",
                            "period": "FY 2023",
                            "context_text": "Average manufacturing capacity utilization improved to 85.4%.",
                            "source_page": "32",
                            "source_section": "MD&A - Operational Performance"
                        },
                        {
                            "category": "Other Data",
                            "value": 10000,
                            "unit": "employees",
                            "period": "As of Dec 31, 2023",
                            "context_text": "We had approximately 10,000 full-time employees worldwide.",
                            "source_page": "42",
                            "source_section": "Company Overview"
                        }
                        # ... potentially hundreds more entries from this document
                    ]
                },
                { # Data from second document
                    "document_name": "Q1 2024 Earnings Release.pdf",
                    "document_data": [
                         {
                            "category": "Financial Data",
                            "value": 1248.5,
                            "unit": "million USD",
                            "period": "Q1 2024",
                            "context_text": "First quarter revenue increased 14.8% year-over-year to $1,248.5 million.",
                            "source_page": "1",
                            "source_section": "Highlights"
                        },
                         {
                            "category": "Financial Data",
                            "value": 23.0,
                            "unit": "%",
                            "period": "Q1 2024",
                            "context_text": "EBITDA margin remained strong at 23.0%.",
                            "source_page": "3",
                            "source_section": "Financial Summary Table"
                        }
                         # ... more entries from this document
                    ]
                }
                 # ... potentially more document entries
            ]
        }
    },
# --- END: Section 32 Definition ---
]