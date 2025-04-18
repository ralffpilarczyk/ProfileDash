"""
Section definitions for ProfileDash
Contains descriptions of all profile sections
(Simplified Schemas - Attempt 2 - Focusing on Structure + Text)
"""
import json # Added for schema conversion in prompts later

# --- Helper function to add standard fields ---
def add_standard_fields(schema_dict):
    """Adds standard analysis_text and footnotes to a schema."""
    if 'properties' not in schema_dict:
        schema_dict['properties'] = {}
        
    schema_dict['properties']['analysis_text'] = {
        "type": ["string", "null"],
        "description": "Detailed analysis, discussion, context, and any extracted information that doesn't fit into other structured fields for this section. Should contain the core narrative and findings."
    }
    schema_dict['properties']['footnotes'] = {
        "type": "array",
        "description": "List of sources cited in the analysis_text or other fields.",
        "items": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Unique reference ID (e.g., 'ref1')."},
                "document": {"type": "string", "description": "Source document name/description."},
                "page": {"type": ["string", "integer", "null"], "description": "Page number(s) or identifier."},
                "section": {"type": ["string", "null"], "description": "Specific section/table within the document."}
            },
            "required": ["id", "document"] # Make page optional as it might not always apply
        }
    }
    # Add analysis_text and footnotes to required fields if it should always be present (even if null/empty string)
    if 'required' in schema_dict:
         # Avoid adding duplicates if already present
         if 'analysis_text' not in schema_dict['required']:
             schema_dict['required'].append('analysis_text')
         if 'footnotes' not in schema_dict['required']:
            schema_dict['required'].append('footnotes')
    else:
         schema_dict['required'] = ['analysis_text', 'footnotes']

    # Add optional 'notes' field at the top level for general section notes
    schema_dict['properties']['notes'] = {
        "type": ["string", "null"],
        "description": "Optional general notes for the entire section."
    }

    return schema_dict

# --- Function to add Optional Notes field recursively ---
# We might not need this if we add notes manually only where needed,
# but keeping it here as an option for broader application.
def _add_optional_notes_recursively(schema_node):
    """Adds an optional 'notes' field to object properties recursively."""
    if isinstance(schema_node, dict):
        if schema_node.get("type") == "object" and "properties" in schema_node:
            # Add notes to the object itself if not already present
            if "notes" not in schema_node["properties"]:
                 schema_node["properties"]["notes"] = {
                     "type": ["string", "null"],
                     "description": "Optional notes or context for this specific item."
                 }
            # Recurse into properties
            for key, prop_schema in schema_node["properties"].items():
                 _add_optional_notes_recursively(prop_schema)
        elif schema_node.get("type") == "array" and "items" in schema_node:
            # Recurse into array items
            _add_optional_notes_recursively(schema_node["items"])
    elif isinstance(schema_node, list): # Handle schemas defined as list (less common)
        for item_schema in schema_node:
            _add_optional_notes_recursively(item_schema)

# --- Section Definitions ---
sections = [
# --- Section 1: Operating Footprint (Simplified) ---
    {
        "number": 1,
        "title": "Operating Footprint",
        "specs": "Extract data on the total number of employees and their locations, including any available breakdowns (e.g., by region, function). Specify the 'as of' date for employee counts.\n"
                 "Extract data on main operating assets, including their categories (e.g., Manufacturing Plants, Offices, R&D Centers), specific asset names/descriptions, locations (city and country), and ownership status (owned or leased). Specify the 'as of' date for asset information.\n"
                 "Include any relevant quantitative metrics for assets (e.g., production capacity, square footage, book value), clearly specifying units and the 'as of' date.\n"
                 "Provide the detailed analysis and findings in the 'analysis_text' field. Use footnotes for specific sources.",
        "schema": add_standard_fields({
            "type": "object",
            "properties": {
                "employee_summary": {
                    "type": ["object", "null"],
                    "description": "High-level summary of employee data if easily extractable.",
                    "properties": {
                         "total_employees": {"type": ["integer", "string", "null"]}, # Allow string for approx values
                         "as_of_date": {"type": ["string", "null"]},
                         "_source_ref_id": {"type": ["string", "null"]},
                         "notes": {"type": ["string", "null"], "description": "Optional notes for employee summary."}
                    },
                    "additionalProperties": False
                },
                "key_asset_categories": {
                     "type": "array",
                     "description": "List of major asset categories identified by name.",
                     "items": {"type": "string"}
                },
            },
            "additionalProperties": False # Discourage extra top-level keys
        }),
        "template": {
            "employee_summary": {"total_employees": 10000, "as_of_date": "December 31, 2023", "_source_ref_id": "ref1", "notes": "Includes full-time equivalents."},
            "key_asset_categories": ["Manufacturing Plants", "R&D Centers", "Distribution Hubs"],
            "analysis_text": "The company employed approximately 10,000 people as of Dec 31, 2023 [ref1], with major hubs in North America. Key assets include Manufacturing Plants, notably the primary facility in Detroit (owned, 500k sq ft capacity 50k units/yr) [ref1], and R&D Centers like the leased Palo Alto hub focusing on software [ref2]. The European Assembly Plant in Frankfurt is leased until 2028 [ref3]. Specific employee breakdowns by region or function were not detailed in the reviewed documents.",
            "footnotes": [
                 {"id": "ref1", "document": "Annual Report 2023", "page": "42", "section": "Operations Overview"},
                 {"id": "ref2", "document": "Investor Presentation Q2 2023", "page": "15", "section": "Global Footprint"},
                 {"id": "ref3", "document": "Annual Report 2023", "page": "F-18", "section": "Note 7: Leases"}
            ],
            "notes": None
        }
    },
# --- Section 2: Products and Services (Simplified) ---
    {
        "number": 2,
        "title": "Products and Services",
        "specs": "Extract a list of key product/service categories and individual products/services within each category.\n"
                 "For each major category and product, extract its value proposition from the customer perspective and any stated competitive advantages.\n"
                 "Capture available performance metrics (e.g., revenue contribution percentage, market share, growth rate) for major categories and products, specifying the 'as of' date or period for each metric.\n"
                 "Extract information on product lifecycle stage (e.g., Growth, Mature, Decline) and market positioning (e.g., Premium, Mid-Market, Low-Cost) if available.\n"
                 "Provide the detailed analysis and findings in the 'analysis_text' field. Use footnotes for specific sources.",
        "schema": add_standard_fields({
            "type": "object",
            "properties": {
                 "key_product_categories": {
                     "type": "array",
                     "description": "List of major product/service category names identified.",
                     "items": {"type": "string"}
                 },
                 "key_products": {
                      "type": "array",
                      "description": "List of specific key product/service names identified.",
                      "items": {"type": "string"}
                 }
            },
             "additionalProperties": False
        }),
        "template": {
            "key_product_categories": ["Cloud Infrastructure Services", "Software Solutions", "Legacy Hardware"],
            "key_products": ["Enterprise Compute Engine", "Data Analytics Suite", "Model X Controller"],
            "analysis_text": "The company's main offerings fall into Cloud Infrastructure Services and Software Solutions, with a declining Legacy Hardware segment. Cloud Infrastructure (40% revenue FY23 [ref1], 22.5% YoY growth [ref2]) is described as scalable and secure, positioned as Premium [ref1]. Its key product, Enterprise Compute Engine [ref4], offers high performance and claims a 30% better price-performance ratio [ref4]; it's considered Mature [ref4]. Software Solutions focus on data analytics... [details extracted and summarized here]. Market share for Cloud Infrastructure was 18% in Q4 2023 [ref3].",
            "footnotes": [
                {"id": "ref1", "document": "Annual Report 2023", "page": "15", "section": "Business Segments"},
                {"id": "ref2", "document": "Q4 2023 Earnings Call Transcript", "page": "3", "section": "CEO Opening Remarks"},
                {"id": "ref3", "document": "Market Analysis Slide Deck", "page": "8", "section": "Competitive Landscape"},
                {"id": "ref4", "document": "Product Catalog 2023", "page": "22", "section": "Cloud Solutions"}
            ],
            "notes": None
        }
    },
# --- Section 3: Key Customers (Simplified) ---
    {
        "number": 3,
        "title": "Key Customers",
        "specs": "Extract data on customer concentration (% revenue from top 1, 5, 10 customers) with dates.\n"
                 "Extract the Company's stated position in the value chain.\n"
                 "Extract a list of the largest customers identified by name.\n"
                 "For key customers, extract relationship details, revenue contribution, products purchased, and segmentation if available.\n"
                 "Provide the detailed analysis and findings in the 'analysis_text' field. Use footnotes for specific sources.",
        "schema": add_standard_fields({
            "type": "object",
            "properties": {
                "customer_concentration_summary": {
                    "type": ["string", "null"],
                    "description": "A brief summary of customer concentration metrics found (e.g., 'Top 10 customers account for 68.2% of revenue (FY23)')."
                },
                 "identified_key_customers": {
                      "type": "array",
                      "description": "List of names of key customers identified.",
                      "items": {"type": "string"}
                 },
                 "value_chain_position_summary": {
                     "type": ["string", "null"],
                     "description": "Brief summary of the company's stated position (e.g., 'Tier 1 Supplier')."
                 }
            },
             "additionalProperties": False
        }),
        "template": {
            "customer_concentration_summary": "Top customer accounted for 15.3%, Top 5 for 42.7%, Top 10 for 68.2% of revenue in FY 2023 [ref1].",
            "identified_key_customers": ["Volkswagen Group", "Toyota Motor Corporation", "General Motors"],
            "value_chain_position_summary": "Tier 1 Supplier to automotive OEMs [ref2].",
            "analysis_text": "The company operates as a Tier 1 Supplier to automotive OEMs [ref2]. Significant customer concentration exists [ref1]. Volkswagen Group is the largest customer (15.3% revenue, 18.7% profit contribution FY23), with a relationship spanning 15+ years [ref3]. They purchase ECUs ($120.5M FY23 revenue [ref1]) and Infotainment Systems [ref1]. Toyota is the second largest (12.8% revenue FY23) [ref1] purchasing Powertrain Components ($95.2M FY23 revenue [ref1]). Customer satisfaction for VW was 4.2/5 [ref4]. Segmentation details were limited, but key customers are primarily global automotive OEMs in Europe and Asia-Pacific [ref1].",
            "footnotes": [
                {"id": "ref1", "document": "Annual Report 2023", "page": "37", "section": "Customer Relationships"},
                {"id": "ref2", "document": "Investor Presentation Q4 2023", "page": "15", "section": "Value Chain Position"},
                {"id": "ref3", "document": "Annual Report 2023", "page": "38", "section": "Key Account Management"},
                {"id": "ref4", "document": "Customer Satisfaction Survey 2023", "page": "5", "section": "OEM Responses"}
            ],
            "notes": None
        }
    },
# --- Section 4: Key Suppliers (Simplified) ---
     {
        "number": 4,
        "title": "Key Suppliers",
        "specs": "Extract data on supplier concentration (% COGS from top 1, 5, 10 suppliers) with dates.\n"
                 "Identify specific supplier risks mentioned and mitigation efforts.\n"
                 "Extract the Company's stated business model and value chain position/margin capture.\n"
                 "Extract a list of the largest suppliers identified by name.\n"
                 "For key suppliers, extract relationship details, COGS contribution, materials provided, and segmentation if available.\n"
                 "Provide the detailed analysis and findings in the 'analysis_text' field. Use footnotes for specific sources.",
        "schema": add_standard_fields({
            "type": "object",
            "properties": {
                 "supplier_concentration_summary": {
                     "type": ["string", "null"],
                     "description": "A brief summary of supplier concentration metrics found (e.g., 'Top supplier accounts for 18.2% of COGS (FY23)')."
                 },
                 "identified_key_suppliers": {
                      "type": "array",
                      "description": "List of names of key suppliers identified.",
                      "items": {"type": "string"}
                 },
                 "identified_supplier_risks": {
                      "type": "array",
                      "description": "List of key supplier risks mentioned (e.g., 'Single-source dependency for semiconductors').",
                      "items": {"type": "string"}
                 },
                 "business_model_summary": {
                     "type": ["string", "null"],
                     "description": "Brief summary of the business model (e.g., 'B2B2C') and value chain position."
                 }
            },
            "additionalProperties": False
        }),
        "template": {
            "supplier_concentration_summary": "Top supplier contributed 18.2% of COGS, Top 5 45.6%, Top 10 72.3% in FY 2023 [ref1].",
            "identified_key_suppliers": ["TSMC", "Foxconn", "Bosch"],
            "identified_supplier_risks": ["Single-source dependency for critical semiconductors from TSMC [ref2]", "Geographic concentration in Asia-Pacific (47% of suppliers) [ref2]"],
            "business_model_summary": "B2B2C model, Tier 1 Supplier with mid-range margin capture (Gross Margin 38.5% FY23) [ref3].",
            "analysis_text": "The company operates a B2B2C model [ref3]. Significant supplier concentration exists [ref1]. TSMC is the largest supplier (18.2% COGS FY23) providing Custom ICs [ref1], posing a single-source risk mitigated by developing a secondary source (Samsung qualification ongoing [ref2]). Foxconn (12.5% COGS FY23) provides PCB assemblies [ref1]. Mitigation for geographic risk involves expanding supplier base in Americas/Europe [ref2]. TSMC performance metrics (Defect Rate 0.05%, OTD 98.7% FY23) exceed targets [ref5]. Supplier segmentation appears focused on Semiconductor Mfg and EMS providers [ref1].",
            "footnotes": [
                 {"id": "ref1", "document": "Annual Report 2023", "page": "42", "section": "Supply Chain Overview"},
                 {"id": "ref2", "document": "Risk Management Assessment 2023", "page": "15", "section": "Supply Chain Risks"},
                 {"id": "ref3", "document": "Investor Presentation Q4 2023", "page": "18", "section": "Value Chain Analysis"},
                 {"id": "ref4", "document": "Annual Report 2023", "page": "43", "section": "Strategic Supplier Relationships"},
                 {"id": "ref5", "document": "Supplier Performance Report 2023", "page": "7", "section": "Top Tier Suppliers"}
            ],
            "notes": None
        }
    },
# --- Section 5: Key Competitors (Simplified) ---
    {
        "number": 5,
        "title": "Key Competitors",
        "specs": "Extract market overview data (size, growth, company share) with dates.\n"
                 "Identify key market segments and company/competitor share within them.\n"
                 "Extract a list of key competitors by name.\n"
                 "For each competitor, extract overview details, market share/trends, positioning, areas of competition/strength, and recent strategic moves.\n"
                 "Provide the detailed analysis and findings in the 'analysis_text' field. Use footnotes for specific sources.",
        "schema": add_standard_fields({
            "type": "object",
            "properties": {
                 "market_overview_summary": {
                     "type": ["string", "null"],
                     "description": "A brief summary of market size, growth, and company share found (e.g., 'Total market $85.7B (FY23), growing 4.8%, company share 15.3%')."
                 },
                 "identified_key_competitors": {
                      "type": "array",
                      "description": "List of names of key competitors identified.",
                      "items": {"type": "string"}
                 }
            },
            "additionalProperties": False
        }),
        "template": {
            "market_overview_summary": "The total addressable market was $85.7B in FY23, growing at 4.8%. The company held a 15.3% overall market share [ref1].",
            "identified_key_competitors": ["Competitor A", "Competitor B", "Competitor C"],
            "analysis_text": "The company primarily competes in the Premium Industrial Automation segment ($32.4B size, 5.7% growth), holding 18.9% share [ref1], and the Mid-Market Process Control segment ($28.6B size), holding 12.7% share [ref1]. Competitor A (HQ Munich, Public, $18.7B rev FY23) leads the premium segment (22.5% share, increasing) [ref1] with strong R&D (8.7% revenue) [ref2]. They recently acquired Smart Robotics Inc. ($350M Q3 2023) [ref3]. Competitor B (HQ Osaka, Public, $12.3B rev FY23) focuses on mid-market value solutions (14.8% overall share, stable) [ref2], strong mainly in Asia-Pacific [ref2].",
            "footnotes": [
                 {"id": "ref1", "document": "Industry Market Report 2023", "page": "25", "section": "Competitive Landscape"},
                 {"id": "ref2", "document": "Annual Report 2023", "page": "48", "section": "Competitive Environment"},
                 {"id": "ref3", "document": "Quarterly Investor Presentation Q4 2023", "page": "12", "section": "Market Developments"}
            ],
            "notes": None
        }
    },
# --- Section 6: Operational KPIs (More Structured - Keep as previous draft) ---
    {
        "number": 6,
        "title": "Operational KPIs",
        "specs": "Extract operational KPIs contributing to cash flow (market share, volumes, prices, customer activity, industry-specific metrics).\n"
                 "Provide data for last 3 years + recent YTD if available.\n"
                 "Include company forecasts/guidance for these KPIs.\n"
                 "Include competitor benchmarks if available.\n"
                 "Extract relevant MDNA (trends, achievements, challenges, disconnects) specifically about these KPIs.\n"
                 "Provide detailed findings in 'analysis_text'. Present key KPIs in a structured list.",
        "schema": add_standard_fields({
            "type": "object",
            "properties": {
                "key_kpi_data": {
                    "type": "array",
                    "description": "List of key operational KPIs with their recent data points.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "category": {"type": ["string", "null"]},
                            "description": {"type": ["string", "null"]},
                            "recent_value": {"type": ["number", "string", "null"]},
                            "unit": {"type": ["string", "null"]},
                            "period": {"type": ["string", "null"]},
                            "yoy_change": {"type": ["number", "string", "null"]},
                            "trend_summary": {"type": ["string", "null"], "description": "Brief summary like 'Increasing', 'Stable', 'Declining'"},
                            "_source_ref_id": {"type": ["string", "null"]},
                            "notes": {"type": ["string", "null"]}
                        },
                        "required": ["name", "recent_value", "unit", "period"],
                        "additionalProperties": False
                    }
                },
                "kpi_guidance_summary": {
                    "type": ["string", "null"],
                    "description": "Brief summary of any company guidance found for operational KPIs (e.g., 'Market share guided to 16.0-16.5% for FY24')."
                },
                "competitor_benchmark_summary": {
                    "type": ["string", "null"],
                    "description": "Brief summary of any direct competitor benchmark data found for operational KPIs."
                },
            },
            "required": ["key_kpi_data", "analysis_text", "footnotes"],
            "additionalProperties": False
        }),
        "template": {
            "key_kpi_data": [
                {"name": "Market Share", "category": "Market Position", "description": "Overall market share", "recent_value": 15.7, "unit": "%", "period": "Q1 2024", "yoy_change": "+0.4 ppts vs Q1 2023", "trend_summary": "Increasing", "_source_ref_id": "ref2", "notes": None},
                {"name": "Production Volume", "category": "Operational", "description": "Total units produced", "recent_value": 0.88, "unit": "million units", "period": "Q1 2024", "yoy_change": "+5.5% vs Q1 2023", "trend_summary": "Increasing", "_source_ref_id": "ref2", "notes": None},
                {"name": "Average Selling Price", "category": "Pricing", "description": "Avg revenue per unit", "recent_value": 1340, "unit": "USD", "period": "Q1 2024", "yoy_change": "+1.9% vs Q1 2023", "trend_summary": "Increasing", "_source_ref_id": "ref2", "notes": "Slightly lagging input cost inflation."},
                {"name": "Capacity Utilization", "category": "Operational", "description": "Mfg capacity usage", "recent_value": 87.2, "unit": "%", "period": "Q1 2024", "yoy_change": "+1.8 ppts vs Q1 2023", "trend_summary": "Increasing", "_source_ref_id": "ref2", "notes": "Approaching optimal levels."}
            ],
            "kpi_guidance_summary": "Market share guided to 16.0-16.5% for FY 2024 [ref3].",
            "competitor_benchmark_summary": "Market share benchmarked vs Competitor A (22.5%) and B (14.8%) in FY23 [ref4].",
            "analysis_text": "MDNA highlights consistent improvement in operational KPIs [ref1]. Key achievements include 95.8% OTD rate [ref1] and 13% ARPU growth since FY21 [ref1]. Challenges noted are growing order backlogs (+16.8%) [ref2] and ASP increases lagging inflation [ref3]. A disconnect was observed between CEO statements on capacity ('no longer an issue' [ref5]) and rising utilization/backlog data [ref2].",
            "footnotes": [
                {"id": "ref1", "document": "Annual Report 2023", "page": "32", "section": "Operational Performance"},
                {"id": "ref2", "document": "Q1 2024 Quarterly Report", "page": "8", "section": "Key Performance Indicators"},
                {"id": "ref3", "document": "FY 2024 Guidance", "page": "4", "section": "Management Outlook"},
                {"id": "ref4", "document": "Industry Benchmarking Report 2023", "page": "15", "section": "Competitive Metrics"},
                {"id": "ref5", "document": "Q4 2023 Earnings Call Transcript", "page": "7", "section": "CEO Remarks"}
            ],
            "notes": None
        }
    },
# --- Section 7: Summary Financials (Consolidated) (More Structured - Keep as previous draft) ---
    {
        "number": 7,
        "title": "Summary Financials (Consolidated)",
        "specs": "Extract key consolidated financial metrics (Revenue, EBITDA, OpInc, NetInc, Capex, Cash Conversion) for last 3 years and recent quarters.\n"
                 "Include GAAP and adjusted measures if provided, detailing adjustments.\n"
                 "Extract forecasts/guidance for these metrics.\n"
                 "List material one-time items.\n"
                 "Include commentary on performance vs industry.\n"
                 "Extract relevant MDNA (trends, achievements, challenges, disconnects).\n"
                 "Provide detailed analysis in 'analysis_text', key figures in structured tables.",
        "schema": add_standard_fields({
            "type": "object",
            "properties": {
                "annual_financials_summary": {
                    "type": "array",
                    "description": "Summary of key annual financial metrics.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "metric_name": {"type": "string"},
                            "unit": {"type": "string"},
                            # Dynamically add years as keys e.g., "FY2023": value
                        },
                        "patternProperties": {
                             "^(FY\\d{4})$": {"type": ["number", "string", "null"]} # Key for Year
                        },
                        "required": ["metric_name", "unit"],
                         "additionalProperties": {"type": ["number", "string", "null", "object"]} # Allow _source_ref_id etc.
                    }
                },
                "quarterly_financials_summary": {
                    "type": "array",
                    "description": "Summary of key recent quarterly financial metrics.",
                     "items": {
                        "type": "object",
                        "properties": {
                            "metric_name": {"type": "string"},
                            "unit": {"type": "string"},
                        },
                        "patternProperties": {
                            "^(Q[1-4]_\\d{4})$": {"type": ["number", "string", "null"]} # Key for Quarter
                        },
                        "required": ["metric_name", "unit"],
                        "additionalProperties": {"type": ["number", "string", "null", "object"]}
                    }
                },
                "key_adjusted_metrics": {
                     "type": "array",
                     "description": "Key non-GAAP adjustments.",
                     "items": {
                         "type": "object",
                         "properties": {
                            "metric_name": {"type": "string"},
                            "period": {"type": "string"},
                            "reported_value": {"type": ["number", "null"]},
                            "adjusted_value": {"type": ["number", "null"]},
                            "adjustment_description": {"type": "string"},
                            "unit": {"type": "string"},
                            "_source_ref_id": {"type": ["string", "null"]},
                            "notes": {"type": ["string", "null"]}
                         },
                         "required": ["metric_name", "period", "adjusted_value", "adjustment_description", "unit"],
                         "additionalProperties": False
                     }
                },
                "one_time_items_summary": {
                     "type": "array",
                     "description": "List of material one-off items identified.",
                     "items": {
                          "type": "object",
                          "properties": {
                               "period": {"type": "string"},
                               "description": {"type": "string"},
                               "impact_value": {"type": ["number", "null"]},
                               "unit": {"type": ["string", "null"]},
                               "affected_metric": {"type": ["string", "null"]},
                               "_source_ref_id": {"type": ["string", "null"]},
                               "notes": {"type": ["string", "null"]}
                          },
                         "required": ["period", "description"],
                         "additionalProperties": False
                     }
                },
                "guidance_summary": {
                     "type": "array",
                     "description": "Summary of key financial guidance provided.",
                     "items": {
                         "type": "object",
                         "properties": {
                              "metric_name": {"type": "string"},
                              "period": {"type": "string"},
                              "guidance_range": {"type": "string"},
                              "unit": {"type": "string"},
                              "_source_ref_id": {"type": ["string", "null"]},
                              "notes": {"type": ["string", "null"]}
                         },
                        "required": ["metric_name", "period", "guidance_range", "unit"],
                        "additionalProperties": False
                     }
                },
            },
             "required": ["annual_financials_summary", "analysis_text", "footnotes"],
             "additionalProperties": False
        }),
        "template": {
            "annual_financials_summary": [
                 {"metric_name": "Revenue", "unit": "M USD", "FY2021": 3562.5, "FY2022": 4008.7, "FY2023": 4572.3, "_source_ref_id": "ref1"},
                 {"metric_name": "EBITDA", "unit": "M USD", "FY2021": 748.1, "FY2022": 865.9, "FY2023": 1028.8, "_source_ref_id": "ref1"},
                 {"metric_name": "Net Income", "unit": "M USD", "FY2021": 210.4, "FY2022": 285.6, "FY2023": 390.1, "_source_ref_id": "ref1"},
                 {"metric_name": "Capex", "unit": "M USD", "FY2021": 180.2, "FY2022": 205.3, "FY2023": 221.5, "_source_ref_id": "ref1"}
            ],
             "quarterly_financials_summary": [
                 {"metric_name": "Revenue", "unit": "M USD", "Q4_2023": 1213.7, "Q1_2024": 1248.5, "_source_ref_id": "ref3"},
                 {"metric_name": "EBITDA", "unit": "M USD", "Q4_2023": 283.1, "Q1_2024": 287.2, "_source_ref_id": "ref3"}
             ],
            "key_adjusted_metrics": [
                 {"metric_name": "Adjusted EBITDA", "period": "FY2023", "reported_value": 1028.8, "adjusted_value": 1042.5, "adjustment_description": "Excludes $13.7M legal settlement", "unit": "M USD", "_source_ref_id": "ref1", "notes": None},
                 {"metric_name": "Adjusted Net Income", "period": "FY2023", "reported_value": 390.1, "adjusted_value": 401.5, "adjustment_description": "Excludes legal settlement and restructuring net of tax", "unit": "M USD", "_source_ref_id": "ref1", "notes": None}
            ],
            "one_time_items_summary": [
                 {"period": "FY 2023", "description": "Legal settlement", "impact_value": -13.7, "unit": "M USD", "affected_metric": "EBITDA", "_source_ref_id": "ref1", "notes": None},
                 {"period": "FY 2021", "description": "Restructuring costs", "impact_value": -14.3, "unit": "M USD", "affected_metric": "EBITDA", "_source_ref_id": "ref1", "notes": None}
            ],
            "guidance_summary": [
                 {"metric_name": "Revenue", "period": "FY 2024", "guidance_range": "5050-5250", "unit": "M USD", "_source_ref_id": "ref4", "notes": "Midpoint implies 12.6% YoY growth."},
                 {"metric_name": "Adjusted EBITDA Margin", "period": "FY 2024", "guidance_range": "22.8%-23.5%", "unit": "%", "_source_ref_id": "ref4", "notes": None}
            ],
            "analysis_text": "MDNA: Consistent double-digit revenue growth noted [ref1]. Achievements: Record Adjusted EBITDA ($1043M FY23), improved cash conversion (87.5% FY23) [ref1]. Challenges: Slowing Capex growth (+7.9% FY23 vs +14% prior), recurring one-time items impacting GAAP results [ref1]. Disconnects: Actual FY23 revenue growth (14.1%) slightly missed target (15%) [ref1/ref5]; Restructuring charges continued into Q1 2024 despite claims of completion [ref1/ref3]. Industry Comparison: Outperforms industry revenue growth, lags top peer on EBITDA margin [ref2].",
            "footnotes": [
                {"id": "ref1", "document": "Annual Report 2023", "page": "25-32", "section": "Financial Review"},
                {"id": "ref2", "document": "FY 2023 Form 10-K", "page": "45-48", "section": "MD&A"},
                {"id": "ref3", "document": "Q1 2024 Quarterly Report", "page": "8-12", "section": "Financial Results"},
                {"id": "ref4", "document": "FY 2024 Guidance Press Release", "page": "2-3", "section": "Financial Outlook"},
                {"id": "ref5", "document": "Q3 2023 Earnings Call Transcript", "page": "6", "section": "CFO Remarks"}
            ],
            "notes": None
        }
    },
# --- Section 8: Summary Financials (Segment) (More Structured - Keep as previous draft) ---
    {
        "number": 8,
        "title": "Summary Financials (Segment)",
        "specs": "Extract segment financial performance (Revenue, OpIncome, Segment EBITDA, etc.). Use exact segment names. Data for last 3 years + recent quarters. List segment-specific one-time items. Extract segment-specific MDNA (trends, achievements, challenges, disconnects). Provide details in 'analysis_text', key figures in structured lists.",
        "schema": add_standard_fields({
            "type": "object",
            "properties": {
                 "segment_financial_summaries": {
                     "type": "array",
                     "description": "List containing financial summary for each reported segment.",
                     "items": {
                         "type": "object",
                         "properties": {
                             "segment_name": {"type": "string"},
                             "description": {"type": ["string", "null"]},
                             "key_metrics": {
                                  "type": "array",
                                  "description": "Key financial metrics for this segment.",
                                  "items": {
                                       "type": "object",
                                       "properties": {
                                           "metric_name": {"type": "string"},
                                           "unit": {"type": "string"},
                                            # Dynamically add years/quarters as keys
                                       },
                                       "patternProperties": {
                                            "^(FY\\d{4}|Q[1-4]_\\d{4})$": {"type": ["number", "string", "null"]}
                                       },
                                       "required": ["metric_name", "unit"],
                                       "additionalProperties": {"type": ["number", "string", "null", "object"]}
                                  }
                             },
                             "mdna_summary": {"type": ["string", "null"], "description": "Brief summary of MDNA specific to this segment."},
                             "one_time_items": {"type": "array", "description": "Descriptions of one-off items.", "items": {"type": "string"}},
                             "_source_ref_id": {"type": ["string", "null"]},
                             "notes": {"type": ["string", "null"]}
                         },
                         "required": ["segment_name", "key_metrics"],
                         "additionalProperties": False
                     }
                 }
            },
             "required": ["segment_financial_summaries", "analysis_text", "footnotes"],
             "additionalProperties": False
        }),
        "template": {
            "segment_financial_summaries": [
                 {
                     "segment_name": "Industrial Automation",
                     "description": "Provides control systems, robotics, and software.",
                     "key_metrics": [
                          {"metric_name": "Segment Revenue", "unit": "M USD", "FY2021": 2000.0, "FY2022": 2200.0, "FY2023": 2500.0, "Q1_2024": 670.0},
                          {"metric_name": "Segment Operating Income", "unit": "M USD", "FY2021": 300.0, "FY2022": 350.0, "FY2023": 420.0, "Q1_2024": 105.0}
                     ],
                     "mdna_summary": "Strong growth driven by X1000 adoption, outpacing market [ref4]. Challenges: pricing pressure [ref5].",
                     "one_time_items": ["Restructuring charges FY23 (-$15.0M OpInc) [ref3]"],
                     "_source_ref_id": "ref1",
                     "notes": "Largest segment by revenue."
                 },
                 {
                     "segment_name": "Process Control Systems",
                     "description": "Provides systems for continuous process industries.",
                      "key_metrics": [
                          {"metric_name": "Segment Revenue", "unit": "M USD", "FY2021": 1500.0, "FY2022": 1650.0, "FY2023": 1800.0, "Q1_2024": 460.0}
                     ],
                     "mdna_summary": "Steady growth benefiting from energy investments; longer sales cycles [ref1].",
                     "one_time_items": [],
                     "_source_ref_id": "ref1",
                     "notes": None
                 }
            ],
            "analysis_text": "Industrial Automation continues strong performance despite headwinds. Process Control remains stable. [Overall commentary comparing segments].",
            "footnotes": [
                 {"id": "ref1", "document": "Annual Report 2023", "page": "F-35", "section": "Note 15: Segment Information"},
                 {"id": "ref3", "document": "Annual Report 2023", "page": "F-36", "section": "Note 15: One-Time Items"},
                 {"id": "ref4", "document": "Annual Report 2023", "page": "30", "section": "MD&A - Segment Review"},
                 {"id": "ref5", "document": "Q4 2023 Earnings Call Transcript", "page": "9", "section": "Segment Discussion"}
            ],
            "notes": None
        }
    },
# --- Section 9: Balance Sheet (More Structured - Keep as previous draft) ---
    {
        "number": 9,
        "title": "Balance Sheet (Most Recent)",
        "specs": "Extract summarized balance sheet (key assets/liabilities). Include key metrics (Total Assets/Debt, Net Debt, Leverage, Coverage, Equity, Working Capital metrics - Current Ratio, DSO, DIO, DPO, CCC). Detail debt profile (types, maturity, covenants). List significant off-balance sheet items. Extract MDNA on balance sheet focus areas. Provide detailed analysis in 'analysis_text', key figures in structured lists.",
        "schema": add_standard_fields({
            "type": "object",
            "properties": {
                "balance_sheet_date": {"type": ["string", "null"]},
                "balance_sheet_summary": {
                    "type": "array",
                    "description": "Key balance sheet line items.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "line_item": {"type": "string"},
                            "value": {"type": ["number", "null"]},
                            "unit": {"type": "string"},
                            "percentage_total": {"type": ["number", "null"]},
                            "yoy_change_percentage": {"type": ["number", "null"]},
                            "_source_ref_id": {"type": ["string", "null"]},
                            "notes": {"type": ["string", "null"]}
                        },
                        "required": ["line_item", "value", "unit"],
                        "additionalProperties": False
                    }
                },
                "key_metrics": {
                    "type": "array",
                    "description": "Key calculated or stated balance sheet and working capital metrics.",
                    "items": {
                         "type": "object",
                        "properties": {
                            "metric_name": {"type": "string"}, # e.g., "Net Debt / EBITDA", "Current Ratio", "DSO"
                            "value": {"type": ["number", "string", "null"]},
                            "unit": {"type": ["string", "null"]}, # e.g., "x", "days"
                            "yoy_change": {"type": ["number", "string", "null"]},
                            "_source_ref_id": {"type": ["string", "null"]},
                            "notes": {"type": ["string", "null"]}
                        },
                        "required": ["metric_name", "value", "unit"],
                        "additionalProperties": False
                    }
                },
                 "debt_profile_summary": {
                     "type": ["string", "null"],
                     "description": "Narrative summary of debt types, maturity profile, and covenant status."
                 },
                 "off_balance_sheet_summary": {
                     "type": ["string", "null"],
                     "description": "Narrative summary of significant OBS items found."
                 }
            },
            "required": ["balance_sheet_date", "balance_sheet_summary", "key_metrics", "analysis_text", "footnotes"],
            "additionalProperties": False
        }),
        "template": {
            "balance_sheet_date": "March 31, 2024",
            "balance_sheet_summary": [
                {"line_item": "Cash & Equiv.", "value": 845.2, "unit": "M USD", "percentage_total": 12.7, "yoy_change_percentage": 8.6, "_source_ref_id": "ref1", "notes": None},
                {"line_item": "Net PP&E", "value": 1875.4, "unit": "M USD", "percentage_total": 28.2, "yoy_change_percentage": 5.7, "_source_ref_id": "ref1", "notes": None},
                {"line_item": "Goodwill & Intangibles", "value": 1945.2, "unit": "M USD", "percentage_total": 29.3, "yoy_change_percentage": 2.1, "_source_ref_id": "ref1", "notes": None},
                {"line_item": "Total Debt (Current+LT)", "value": 2093.8, "unit": "M USD", "percentage_total": 31.5, "yoy_change_percentage": -0.6, "_source_ref_id": "ref1", "notes": "Includes current portion."},
                {"line_item": "Total Equity", "value": 3132.0, "unit": "M USD", "percentage_total": 47.2, "yoy_change_percentage": 9.8, "_source_ref_id": "ref1", "notes": None}
            ],
            "key_metrics": [
                {"metric_name": "Net Debt / EBITDA", "value": 1.15, "unit": "x", "yoy_change": -0.25, "_source_ref_id": "ref1", "notes": "Leverage decreased."},
                {"metric_name": "Current Ratio", "value": 1.45, "unit": "x", "yoy_change": 0.12, "_source_ref_id": "ref1", "notes": "Calculated from BS lines."},
                {"metric_name": "Cash Conversion Cycle", "value": 96.3, "unit": "days", "yoy_change": -8.5, "_source_ref_id": "ref1", "notes": "Significant improvement."}
            ],
            "debt_profile_summary": "Debt includes $250M drawn on revolver and $500M Senior Notes due 2028 [ref2]. Maturity profile well-staggered. Covenants (Net Debt/EBITDA < 3.0x, Int Cov > 4.0x) comfortably met [ref2].",
            "off_balance_sheet_summary": "Main OBS item: Operating lease commitments ($185.7M) through 2032 [ref2].",
            "analysis_text": "MDNA discussion focuses on Working Capital Management (targeting CCC of 90 days) and maintaining conservative leverage (target 1.5-2.0x) to preserve capacity for strategic M&A activities [ref3]. Balance sheet remains strong.",
            "footnotes": [
                 {"id": "ref1", "document": "Q1 2024 Quarterly Report", "page": "15-18", "section": "Consolidated Balance Sheets"},
                 {"id": "ref2", "document": "Q1 2024 Quarterly Report", "page": "22-25", "section": "Notes - Note 8: Debt"},
                 {"id": "ref3", "document": "Q1 2024 Earnings Call Transcript", "page": "7-9", "section": "CFO Financial Review"}
            ],
            "notes": None
        }
    },
# --- Section 10: Top 10 Shareholders (Simplified - Keep as previous draft) ---
    {
        "number": 10,
        "title": "Top 10 Shareholders",
        "specs": "Extract ownership structure details (shares, classes, ticker, rights) with date. List top 10 shareholders (name, type, shares, %, changes, board seats). Identify shareholder groups & insider holdings. Detail activism history & agreements. Provide detailed analysis in 'analysis_text'. Identify key shareholders.",
        "schema": add_standard_fields({
            "type": "object",
            "properties": {
                 "ownership_summary": {
                     "type": ["string", "null"],
                     "description": "Brief summary of total shares, classes, and ownership date."
                 },
                 "identified_major_shareholders": { # Simplified list
                      "type": "array",
                      "description": "List of names of major shareholders (>5% or key families/insiders) identified.",
                      "items": {"type": "string"}
                 }
            },
            "additionalProperties": False
        }),
        "template": {
             "ownership_summary": "As of March 31, 2024, 125.7M Common Shares (Ticker: EXMP) were outstanding, one vote per share [ref1].",
             "identified_major_shareholders": ["Roberts Family Holdings LLC", "BlackRock, Inc.", "James Miller (CEO)"],
             "analysis_text": "Roberts Family Holdings (Founder) holds 15.0% [ref1], decreased 1.2 ppts over 12m [ref2]; holds 2 board seats via Governance Agreement [ref3]. BlackRock holds 10.0% (passive) [ref1]. All executives/directors hold 22.0% combined [ref4]. CEO Miller holds 2.0% [ref4]. Starboard Value activism occurred Q1-Q3 2022, resulted in board changes, stake exited Q1 2023 [ref5]. Governance agreement grants families board nomination rights [ref3].",
             "footnotes": [
                 {"id": "ref1", "document": "Proxy Statement 2024", "page": "24-28", "section": "Security Ownership"},
                 {"id": "ref2", "document": "SEC Form 4 Analysis", "page": "Summary", "date": "Various"},
                 {"id": "ref3", "document": "Governance Agreement Summary", "page": "Internal Memo", "date": "Jun 2018"},
                 {"id": "ref4", "document": "Proxy Statement 2024", "page": "27", "section": "Insider Holdings Table"},
                 {"id": "ref5", "document": "Investor Relations Presentation Q1 2024", "page": "32", "section": "Corporate Governance Update"}
             ],
            "notes": None
        }
    },
# --- Section 11: Material Corporate Activity (Simplified) ---
    {
        "number": 11,
        "title": "Material Corporate Activity",
        "specs": "Extract a list of material corporate activities (strategic reviews, financings, M&A) over last 3 years. Include pending/rumored/failed. Present chronologically (recent first). For each: Date, Type, Target/Counterparty, Description, Value, Structure Details, Rationale/Synergies, Status/Closing, Market Reaction, Post-transaction Impact. Provide detailed analysis in 'analysis_text'. Summarize key activities.",
        "schema": add_standard_fields({
            "type": "object",
            "properties": {
                 "key_activities_summary": {
                     "type": "array",
                     "description": "List of brief summaries for key corporate activities identified (e.g., 'Mar 2024: Pending Acquisition of TechInnovate ($450M)').",
                     "items": {"type": "string"}
                 }
            },
            "additionalProperties": False
        }),
        "template": {
            "key_activities_summary": [
                "Mar 2024: Announced Pending Acquisition of TechInnovate Solutions, Inc. ($450M, 72% cash/28% stock) [ref1]",
                "Oct 2023: Completed Divestiture of Legacy Components Division ($185M + $25M earnout) [ref3]",
                "Q3 2023: Completed $85M Share Repurchase Program [ref4]"
            ],
            "analysis_text": "Recent activity focused on acquiring digital capabilities and divesting non-core assets. The pending TechInnovate acquisition aims to add IoT capabilities with expected cost ($35M/yr) and revenue ($65M/yr) synergies [ref1]. Regulatory approval is pending, expected closing Q3 2024 [ref1]. Market reaction was positive (+3.5% stock price) [ref2]. The Legacy Components divestiture (to Industrial Partners Group) sharpened focus on core automation; proceeds used for debt reduction ($100M) and share repurchase ($85M) [ref3/ref4]. This divestiture is expected to improve consolidated margins by ~0.8 ppts [ref4]. Earlier activities included...",
            "footnotes": [
                 {"id": "ref1", "document": "TechInnovate Acquisition Press Release", "page": "1-3", "date": "March 15, 2024"},
                 {"id": "ref2", "document": "Bloomberg Financial Data", "page": None, "date": "March 15, 2024"},
                 {"id": "ref3", "document": "Legacy Components Divestiture Press Release", "page": "1-2", "date": "October 12, 2023"},
                 {"id": "ref4", "document": "Q4 2023 Earnings Call Transcript", "page": "6", "date": "February 8, 2024"}
            ],
            "notes": None
        }
    },
# --- Section 12: Key Decision Makers (Simplified) ---
    {
        "number": 12,
        "title": "Key Decision Makers",
        "specs": "Extract leadership structure (Chair/CEO roles). Overview Board comp (total members, independent, tenure). List senior execs & board members. For execs: Name, title, appt date, age, education, prior experience, detailed comp (base, bonus, LTI breakdown), ownership, key reports. For board: Name, board position, independence, appt date, age, primary affiliation, background, committee roles/expertise, relationships, attendance, comp, ownership. Detail Board Committees. Note recent leadership changes & impact. Describe decision-making structure. Provide detailed analysis in 'analysis_text'. List key individuals.",
        "schema": add_standard_fields({
            "type": "object",
            "properties": {
                "leadership_structure_summary": {
                    "type": ["string", "null"],
                    "description": "Brief summary of Chair/CEO roles and board independence."
                },
                "identified_key_executives": {
                     "type": "array",
                     "description": "List of names of key executives identified (e.g., CEO, CFO).",
                     "items": {"type": "string"}
                },
                "identified_key_board_members": {
                      "type": "array",
                      "description": "List of names of key board members identified (e.g., Chair, Lead Director).",
                      "items": {"type": "string"}
                }
            },
            "additionalProperties": False
        }),
        "template": {
            "leadership_structure_summary": "Separate Chairman (Founder Thomas Roberts) and CEO (James Miller). Lead Independent Director (Dr. Elena Rodriguez) appointed 2019. Board is 73% independent (8 of 11 members) [ref1].",
            "identified_key_executives": ["James W. Miller (CEO)", "Sarah Wilson (CFO)", "Lisa Chen (CTO)"],
            "identified_key_board_members": ["Thomas J. Roberts (Chairman)", "Dr. Elena M. Rodriguez (Lead Independent Director)", "Richard Taylor (Audit Chair)"],
            "analysis_text": "CEO James Miller (since Mar 2018, age 56, HBS MBA) has prior relevant COO experience [ref2]. FY23 total comp $9.7M (Base $1.25M, Bonus $1.97M, LTI $6.5M) [ref2]. Owns 2.0% shares [ref2], exceeds 6x salary requirement [ref2]. Recent change: Lisa Chen appointed CTO Jan 2024, replacing retired predecessor [ref3]. Chairman Roberts (Founder, age 72) holds 15.0% via family entity [ref1/ref2]. Lead Director Dr. Rodriguez (age 62) is CEO of TechSolutions Inc. and brings tech strategy expertise [ref1]. Audit Committee chaired by R. Taylor includes 2 financial experts [ref1]. Decision making involves Board approval for major M&A/budgets, CEO authority for operations [ref6]. Detailed compensation breakdowns and full board bios available in proxy [ref2].",
            "footnotes": [
                {"id": "ref1", "document": "Proxy Statement 2024", "page": "12-15", "section": "Corporate Governance"},
                {"id": "ref2", "document": "Proxy Statement 2024", "page": "35-52", "section": "Executive and Director Compensation"},
                {"id": "ref3", "document": "Press Release: CTO Appointment", "page": "1", "date": "Jan 15, 2024"},
                # {"id": "ref4", ... } # Other refs if needed
                # {"id": "ref5", ... }
                {"id": "ref6", "document": "Corporate Governance Guidelines", "page": "8", "date": "Mar 2023"}
            ],
            "notes": None
        }
    },
# --- Section 13: Strategic Objectives (Simplified - Keep as previous draft) ---
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
                 "Provide the detailed analysis and findings in the 'analysis_text' field. List key objectives/strategies.",
        "schema": add_standard_fields({
            "type": "object",
            "properties": {
                 "key_objectives_list": {
                      "type": "array",
                      "description": "List of key strategic objective titles identified.",
                      "items": {"type": "string"}
                 },
                 "key_strategies_list": {
                      "type": "array",
                      "description": "List of key strategy titles identified.",
                      "items": {"type": "string"}
                 }
            },
             "additionalProperties": False
        }),
        "template": {
             "key_objectives_list": ["Increase recurring revenue share to 40% by 2025", "Expand Asia-Pacific Market Share to 25% by 2026", "Achieve industry leadership in sustainable manufacturing solutions"],
             "key_strategies_list": ["Leverage existing customer base for subscription conversions", "Enhance software platform with industry-specific solutions", "Leverage Singapore manufacturing hub for localized production"],
             "analysis_text": "The company pivoted strategy post-2019 towards integrated solutions and recurring revenue [ref1]. Key objectives include increasing recurring revenue to 40% by 2025 (currently 28% Q1 2024) [ref2/ref3] and expanding APAC market share to 25% by 2026 (currently 18% Q1 2024) [ref2/ref3]. Strategies involve cross-selling subscriptions to the installed base (>120k units [ref6]), supported by the global service network [ref6] and enhancing the software platform via R&D ($45M/yr) and M&A ($200M budget) [ref6]. Progress is tracked via Recurring Revenue % and Subscription Conversion Rate (currently 18% vs 30% target [ref3]). Competitive context shows alignment with top peers (Competitor A at 35% recurring) [ref5].",
             "footnotes": [
                 {"id": "ref1", "document": "Strategic Review Presentation", "page": "5-8", "date": "Nov 10, 2022"},
                 {"id": "ref2", "document": "Three-Year Strategic Plan", "page": "12-28", "date": "Nov 10, 2022"},
                 {"id": "ref3", "document": "Q1 2024 Quarterly Report", "page": "8-15", "date": "Apr 25, 2024"},
                 {"id": "ref4", "document": "Annual Report 2023", "page": "24-32", "date": "Feb 15, 2024"},
                 {"id": "ref5", "document": "Industry Market Analysis Report", "page": "45-52", "date": "Jan 2024"},
                 {"id": "ref6", "document": "Capital Allocation Plan", "page": "18-24", "date": "Dec 12, 2023"}
             ],
             "notes": None
        }
    },
# --- Section 14: Strategic Constraints (Simplified) ---
     {
        "number": 14,
        "title": "Strategic Constraints",
        "specs": "Extract overview of main strategic constraints. Identify top 3 (hindering objectives). For each: Name/Category, Description/Root Causes, Affected Objective(s)/Impact, Quantitative Impact Data, Historical Evolution, Competitive Benchmarking, Mitigation Efforts/Effectiveness. Identify emerging constraints. Provide detailed analysis in 'analysis_text'. List key constraints.",
        "schema": add_standard_fields({
            "type": "object",
            "properties": {
                 "identified_constraints_list": {
                      "type": "array",
                      "description": "List of key strategic constraint titles identified.",
                      "items": {"type": "string"}
                 }
            },
            "additionalProperties": False
        }),
        "template": {
             "identified_constraints_list": ["Technical Talent Acquisition and Retention", "Manufacturing Capacity Limitations in Asia-Pacific", "Legacy System Integration Complexity"],
             "analysis_text": "Key constraints hinder strategic goals [ref1]. The most significant is the Technical Talent gap (Human Capital), with a 40% shortfall (200 engineers) vs target [ref3], impacting the recurring revenue objective by slowing digital development [ref2]. This has intensified over 24m (time-to-fill 95->110 days [ref4]) and lags competitors (18% vacancy vs 12% leader A [ref5]). Mitigation via global hubs (45 hires vs 120 target [ref6]) and planned acqui-hiring ($100M budget [ref6]) is narrowing but not closing the gap [ref6]. APAC Manufacturing Capacity (Operations) also limits share growth (7k unit/yr gap vs demand [ref7]), being addressed by facility expansion (45% complete [ref7]) and contract manufacturing (starts H2 2024 [ref7]). Emerging constraint: Increasing Regulatory Complexity (Energy/Cyber) [ref9].",
             "footnotes": [
                  {"id": "ref1", "document": "Risk Management Assessment", "page": "12-18", "date": "Feb 2024"},
                  {"id": "ref2", "document": "Three-Year Strategic Plan", "page": "30-32", "date": "Nov 10, 2022"},
                  {"id": "ref3", "document": "Q1 2024 Quarterly Report", "page": "15-16", "date": "Apr 25, 2024"},
                  {"id": "ref4", "document": "HR Talent Assessment", "page": "8-12", "date": "Jan 2024"},
                  {"id": "ref5", "document": "Industry Competitive Analysis", "page": "22-28", "date": "Mar 2024"},
                  {"id": "ref6", "document": "Talent Strategy Presentation", "page": "5-14", "date": "Mar 15, 2024"},
                  {"id": "ref7", "document": "APAC Mfg Capacity Analysis", "page": "3-8", "date": "Feb 5, 2024"},
                  {"id": "ref9", "document": "Emerging Risk Assessment", "page": "10-18", "date": "Jan 15, 2024"}
             ],
             "notes": None
        }
    },
# --- Section 15: Strengths (Simplified - Keep as previous draft) ---
    {
        "number": 15,
        "title": "Strengths",
        "specs": "Extract overview of core competitive strengths. Identify top 3 relevant strengths enabling competition. Focus on existing strengths. For each: Name/Category, Description, Development History (how built), Quantitative Evidence (substantiation, metrics vs competitors), Competitive Advantage Analysis (how it translates to performance), Current Leverage (how used now). Identify emerging strengths. Provide detailed analysis in 'analysis_text'. List key strengths.",
        "schema": add_standard_fields({
            "type": "object",
            "properties": {
                 "identified_strengths_list": {
                      "type": "array",
                      "description": "List of key strength titles identified.",
                      "items": {"type": "string"}
                 }
            },
            "additionalProperties": False
        }),
        "template": {
             "identified_strengths_list": ["Proprietary Energy Optimization Technology", "Global Manufacturing Scale & Flexibility", "Legacy & Modern System Integration Expertise"],
             "analysis_text": "Core strengths include proprietary energy optimization tech (Technology/IP) developed over 10 years ($215M investment incl. acquisition [ref2]), delivering superior efficiency (18.5% avg cost reduction vs 12.3% industry avg [ref3]) and faster ROI (14.7 vs 22.5 months avg [ref3]). This provides an 8 ppt margin premium and +18 ppts win rate advantage [ref5]. It's leveraged in premium products ($485M revenue FY23 [ref6]). Global manufacturing scale (Operations) provides a 12.5% cost advantage vs regional peers and superior OTD (95.8% vs 87.5% avg [ref7]), supporting pricing power and regional customization [ref5/ref6]. Integration Expertise (Capability) allows modernization of legacy systems (94.5% success rate vs 72% avg [ref6]), driving high-margin service revenue ($215M FY23) and retention (92% renewal) [ref7]. Emerging strength: AI Predictive Maintenance (late dev stage [ref9]).",
             "footnotes": [
                 {"id": "ref1", "document": "Competitive Positioning Assessment", "page": "8-15", "date": "Mar 2024"},
                 {"id": "ref2", "document": "Technology Portfolio Review", "page": "12-18", "date": "Feb 2024"},
                 {"id": "ref3", "document": "Product Performance Metrics", "page": "5-9", "date": "Q1 2024"},
                 {"id": "ref4", "document": "Industry Competitive Analysis", "page": "22-28", "date": "Mar 2024"},
                 {"id": "ref5", "document": "Win/Loss Analysis Report", "page": "10-18", "date": "Q4 2023"},
                 {"id": "ref6", "document": "Annual Report 2023", "page": "35-42", "date": "Feb 15, 2024"},
                 {"id": "ref7", "document": "Mfg Capabilities Review", "page": "4-15", "date": "Jan 2024"},
                 {"id": "ref9", "document": "Emerging Capabilities Report", "page": "8-12", "date": "Mar 2024"}
             ],
             "notes": None
        }
    },
# --- Section 16: Weaknesses (Simplified) ---
    {
        "number": 16,
        "title": "Weaknesses",
        "specs": "Extract overview of main weaknesses/limitations. Identify top 3 relevant weaknesses hindering performance/competition. For each: Name/Category, Description/Root Causes, Quantitative Impact Data (vs competitors), Competitive Disadvantage Analysis (how it manifests), Mitigation Efforts/Effectiveness. Identify emerging weaknesses. Provide detailed analysis in 'analysis_text'. List key weaknesses.",
        "schema": add_standard_fields({
            "type": "object",
            "properties": {
                 "identified_weaknesses_list": {
                      "type": "array",
                      "description": "List of key weakness titles identified.",
                      "items": {"type": "string"}
                 }
            },
            "additionalProperties": False
        }),
        "template": {
             "identified_weaknesses_list": ["Limited Software Development Capacity", "APAC Manufacturing Scale Gap", "Service Network Density Gaps"],
             "analysis_text": "Key weaknesses relative to competitors [ref1]. Limited software capacity (Capability/Resources) stems from late strategic pivot [ref2], resulting in a 40% engineer gap [ref3] and 50% slower time-to-market vs peers [ref3]. This manifests as lower win rates (42% loss rate cites timing [ref5]) and hinders recurring revenue goals (Est. $120-150M lost opportunity [ref3]). Mitigation (dev centers, partnerships) is insufficient near-term [ref6]. APAC Mfg Scale Gap (Operations) leads to higher costs (+12.5% vs local) and longer lead times vs regional competitors [ref7/ref4], impacting APAC share goals. Mitigation (expansion, CM) underway but completion 2025+ [ref7]. Service Network gaps exist in emerging regions...",
             "footnotes": [
                {"id": "ref1", "document": "Strategic SWOT Analysis", "page": "15-22", "date": "Mar 2024"},
                {"id": "ref2", "document": "Digital Transformation Review", "page": "8-12", "date": "Feb 2024"},
                {"id": "ref3", "document": "Technical Resource Plan", "page": "15-20", "date": "Jan 2024"},
                # {"id": "ref4", ...}
                {"id": "ref5", "document": "Win/Loss Analysis Report", "page": "22-30", "date": "Q4 2023"},
                {"id": "ref6", "document": "Software Talent Strategy Update", "page": "3-10", "date": "Mar 15, 2024"},
                # {"id": "ref7", ...}
             ],
             "notes": None
        }
    },
# --- Section 17: Opportunities (Simplified) ---
    {
        "number": 17,
        "title": "Opportunities",
        "specs": "Extract overview of promising near-term (12-24m) opportunities. Identify top 3 actionable opportunities leveraging existing strengths. For each: Name/Description, Enabling Strength(s), Market Potential/Size, Implementation Plan/Timeframe/Investment, Quantified Financial Impact (Revenue, Profit, ROI), Key Risks. Provide detailed analysis in 'analysis_text'. List key opportunities.",
        "schema": add_standard_fields({
            "type": "object",
            "properties": {
                 "identified_opportunities_list": {
                      "type": "array",
                      "description": "List of key opportunity titles identified.",
                      "items": {"type": "string"}
                 }
            },
            "additionalProperties": False
        }),
        "template": {
             "identified_opportunities_list": ["Expansion of Energy Optimization Services to Existing Base", "Asia-Pacific Service Network Expansion", "Cross-selling Integrated Solutions"],
             "analysis_text": "Key opportunities leverage existing strengths [ref1]. Expanding Energy Optimization Services to the 68% of existing customers not using it [ref3] leverages proprietary tech & relationships [ref2]. Plan involves targeted outreach over 18m ($12.5M cost [ref4]) with potential +$80.7M cumulative revenue and 85% 3Y IRR [ref5]. Risk is low (conversion rate) [ref6]. APAC Service Network Expansion leverages Singapore hub [ref2] to improve response times and target 45% attach rate (from 28%) [ref3]. Plan involves hiring 80 techs over 24m ($18.5M cost [ref4]) for +$55.3M cumulative revenue potential (58% 3Y IRR [ref5]). Medium risk (execution) [ref6]. Cross-selling...",
             "footnotes": [
                 {"id": "ref1", "document": "Strategic Opportunities Assessment", "page": "5-12", "date": "Mar 2024"},
                 {"id": "ref2", "document": "Competitive Positioning Assessment", "page": "8-15", "date": "Mar 2024"},
                 {"id": "ref3", "document": "Market Analysis Report", "page": "18-25", "date": "Q1 2024"},
                 {"id": "ref4", "document": "Strategic Initiative Planning", "page": "10-22", "date": "Feb 2024"},
                 {"id": "ref5", "document": "Financial Projections", "page": "15-28", "date": "Mar 2024"},
                 {"id": "ref6", "document": "Risk Assessment Report", "page": "8-14", "date": "Q1 2024"}
             ],
             "notes": None
        }
    },
# --- Section 18: Threats (Simplified) ---
    {
        "number": 18,
        "title": "Threats",
        "specs": "Extract overview of significant external threats. Identify top 3 threats (Competitive, Tech, Regulatory, Supply Chain etc.) impacting performance in next 12-24m. For each: Name/Category, Description/Drivers, Quantified Potential Negative Impact (Revenue, Margin, Share), Likelihood/Timeframe/Velocity Assessment, Mitigation Efforts/Effectiveness, Related Competitor Context. Provide detailed analysis in 'analysis_text'. List key threats.",
        "schema": add_standard_fields({
            "type": "object",
            "properties": {
                 "identified_threats_list": {
                      "type": "array",
                      "description": "List of key threat titles identified.",
                      "items": {"type": "string"}
                 }
            },
            "additionalProperties": False
        }),
        "template": {
             "identified_threats_list": ["Accelerating Price Erosion in Core Hardware", "Digital Capabilities Gap vs. Software-Natives", "Supply Chain Disruptions (Semiconductors)"],
             "analysis_text": "Key external threats exist [ref1]. Price Erosion (Competitive/Market) driven by Asian competitors and commoditization [ref2] risks 2.5-4.0 ppts margin compression in hardware ($75-120M annual revenue impact potential by FY25) [ref3]. Likelihood High, Velocity Accelerating (Price realization down 1.0ppt Q1'24) [ref3]. Mitigation (value pricing, cost reduction) only partially effective (~$10-15M EBITDA offset expected) [ref4]. Digital Gap (Tech/Comp) vs software natives risks recurring revenue goals (potential miss 32% vs 40% target by 2025) and valuation (-0.5-1.2x EV/EBITDA impact) [ref3]. Likelihood High, Velocity Increasing (Win rate vs natives down) [ref4]. Mitigation (partnerships, dev centers) lags investment of leaders [ref4/ref5]. Semiconductor supply chain risks remain...",
             "footnotes": [
                  {"id": "ref1", "document": "Strategic Risk Assessment", "page": "8-15", "date": "Mar 2024"},
                  {"id": "ref2", "document": "Competitive Landscape Analysis", "page": "15-25", "date": "Feb 2024"},
                  {"id": "ref3", "document": "Financial Impact Analysis - Threats", "page": "5-12", "date": "Feb 2024"},
                  {"id": "ref4", "document": "Mitigation Plan Review", "page": "10-18", "date": "Mar 2024"},
                  {"id": "ref5", "document": "Competitive Intelligence Report", "page": "8-20", "date": "Q1 2024"}
             ],
             "notes": None
        }
    },
# --- Section 19: Sellside Positioning - Macro (Simplified) ---
    {
        "number": 19,
        "title": "Sellside Positioning - Macro",
        "specs": "Extract overview summarizing positive macro trends. Identify top 3 positive macro trends (economic indicators, broad forces). Focus only on macro. For each: Name/Category, Description, Quantitative Data (recent history + forecast, indicators like GDP/capex/labor/trade/energy/rates), Regional/Sector Breakdowns, How it benefits Company (quantitative link if possible). Provide detailed analysis in 'analysis_text'. List key trends.",
        "schema": add_standard_fields({
            "type": "object",
            "properties": {
                 "identified_trends_list": {
                      "type": "array",
                      "description": "List of key positive macro trend titles identified.",
                      "items": {"type": "string"}
                 }
            },
            "additionalProperties": False
        }),
        "template": {
            "identified_trends_list": ["Robust Manufacturing Capex Growth (Automation Focus)", "Rising Manufacturing Labor Costs & Shortages", "Reshoring/Supply Chain Regionalization"],
            "analysis_text": "Positive macro tailwinds support the investment thesis [ref1]. Robust Mfg Capex Growth (Investment Trend), particularly in automation (forecast +14.8% 2025F vs +6.8% overall mfg capex) [ref2], directly boosts demand as company revenue correlates ~0.85x with automation capex [ref3]. Rising Mfg Labor Costs (Labor Trend), forecast +6.2% globally in 2025F [ref3], increases automation ROI, shortening payback periods by ~35% (2024 vs 2022) [ref3] and driving demand. Reshoring Initiatives (Trade Pattern), esp. in N.America (+1580 projects announced 2024, +$225B investment [ref4]), favors the company's geographic footprint (80% rev N.Am/Europe) as new facilities have ~35% higher automation content [ref4].",
            "footnotes": [
                 {"id": "ref1", "document": "Macroeconomic Impact Analysis", "page": "3-4", "date": "Mar 2025"},
                 {"id": "ref2", "document": "Global Manufacturing Investment Outlook", "page": "12-18", "date": "Feb 2025"},
                 {"id": "ref3", "document": "Manufacturing Labor Market Report", "page": "22-28", "date": "Jan 2025"},
                 {"id": "ref4", "document": "Supply Chain Restructuring Analysis", "page": "15-24", "date": "Mar 2025"}
            ],
            "notes": None
        }
    },
# --- Section 20: Sellside Positioning - Industry (Simplified) ---
    {
        "number": 20,
        "title": "Sellside Positioning - Industry",
        "specs": "Extract overview summarizing positive industry dynamics/trends (relevant sectors). Identify top 3 positive industry trends (tech adoption, business models, segment growth, competitive shifts, industry regulation). Focus only on industry. For each: Name/Category, Description, Quantitative Data (recent history + forecast, indicators like segment size/growth, tech penetration, pricing, consolidation), Segment/Product Breakdowns, How it benefits Company (alignment/outperformance). Provide detailed analysis in 'analysis_text'. List key trends.",
        "schema": add_standard_fields({
            "type": "object",
            "properties": {
                 "identified_trends_list": {
                      "type": "array",
                      "description": "List of key positive industry trend titles identified.",
                      "items": {"type": "string"}
                 }
            },
            "additionalProperties": False
        }),
        "template": {
             "identified_trends_list": ["Accelerating Industrial Digitalization & IIoT Adoption", "Industry Shift from Hardware to Integrated Solutions", "Prioritization of Energy Optimization Technologies"],
             "analysis_text": "Favorable industry dynamics include accelerating digitalization [ref1]. The Industrial Automation Software market grew 20% in 2024 to $34.2B and is forecast +21.3% in 2025F [ref2]. Smart Mfg Platforms (+28.5% CAGR) and Analytics (+32.4% CAGR) are key sub-segments [ref2]. This benefits the company as its Connected Product revenue grew 32.8% YoY FY23, outpacing the market [ref3]. The shift from hardware to integrated solutions (52.5% adoption forecast 2025F vs 45.2% 2024 [ref3]) aligns with the company's strategy and supports margin expansion [ref3]. Prioritization of Energy Optimization (market forecast $51.2B 2025F, +20.5% CAGR [ref4]) directly plays to the company's core tech strength, driving share gains (+2.5 ppts FY23) and premium pricing [ref5].",
             "footnotes": [
                 {"id": "ref1", "document": "Industry Analysis Report", "page": "3-5", "date": "Mar 2025"},
                 {"id": "ref2", "document": "Industrial Digitalization Trends", "page": "12-18", "date": "Feb 2025"},
                 {"id": "ref3", "document": "Automation Business Models Analysis", "page": "8-15", "date": "Jan 2025"},
                 {"id": "ref4", "document": "Industrial Energy Management Report", "page": "22-30", "date": "Mar 2025"},
                 {"id": "ref5", "document": "Company Performance Metrics Q1 2024", "page": "Internal", "date": "Apr 2024"}
             ],
             "notes": None
        }
    },
# --- Section 21: Sellside Positioning - Competitive Positioning (Simplified) ---
    {
        "number": 21,
        "title": "Sellside Positioning - Competitive Positioning",
        "specs": "Extract overview summarizing key competitive advantages & market standing. Identify top 3 specific advantages impacting economic performance (next 12m). For each: Name/Category, Description, Quantitative Evidence (performance vs competitors, share, cost advantage, pricing premium), How it translates to Financial Performance/Market Outcomes (margins, growth, win rates, retention), Customer Validation (retention, satisfaction, testimonials). Provide detailed analysis in 'analysis_text'. List key advantages.",
        "schema": add_standard_fields({
            "type": "object",
            "properties": {
                 "identified_advantages_list": {
                      "type": "array",
                      "description": "List of key competitive advantage titles identified.",
                      "items": {"type": "string"}
                 }
            },
            "additionalProperties": False
        }),
        "template": {
            "identified_advantages_list": ["Proprietary Energy Optimization Technology", "Global Manufacturing Scale & Flexibility", "Legacy & Modern System Integration Expertise"],
            "analysis_text": "Key advantages support premium positioning [ref1]. Energy Optimization Tech (Tech Diff) provides superior efficiency (+4.2 ppts vs Competitor A [ref2]) and faster ROI (7.8 months vs avg [ref2]), driving higher margins (+8 ppts vs standard hardware) and win rates (+18 ppts) [ref3]. Global Mfg Scale (Ops Excellence) yields 12.5% cost advantage vs regional peers [ref4] and better OTD (+8.3 ppts vs avg [ref4]), supporting pricing flexibility and share gains [ref5]. Integration Expertise (Capability) enables faster, more successful integration (44% faster, +22.5 ppts success rate vs avg [ref6]), driving high-margin services ($215M FY23 rev) and customer retention (92% renewal vs 78% avg) [ref7]. Customer validation includes 95.8% retention for energy solutions [ref3].",
            "footnotes": [
                 {"id": "ref1", "document": "Competitive Positioning Assessment", "page": "8-15", "date": "Mar 2025"},
                 {"id": "ref2", "document": "Energy Management Solutions Performance", "page": "12-18", "date": "Feb 2025"},
                 {"id": "ref3", "document": "Financial Performance Review FY2023", "page": "Internal", "date": "Jan 2025"},
                 {"id": "ref4", "document": "Manufacturing Capabilities Report", "page": "5-15", "date": "Dec 2024"},
                 {"id": "ref5", "document": "Win/Loss Analysis Report", "page": "10-18", "date": "Q4 2023"},
                 {"id": "ref6", "document": "Integration Capabilities Assessment", "page": "22-30", "date": "Dec 2023"},
                 {"id": "ref7", "document": "Service Segment Performance Report", "page": "10-18", "date": "Jan 2025"}
            ],
            "notes": None
        }
    },
# --- Section 22: Sellside Positioning - Operating Performance (Simplified) ---
    {
        "number": 22,
        "title": "Sellside Positioning - Operating Performance",
        "specs": "Extract overview highlighting exceptional operating performance/execution (last 24m). Identify top 3 operating metrics/achievements demonstrating strength (beyond standard financials: e.g., share gains, volume growth, price realization, ARPU growth, efficiency gains like utilization/OTD). For each: Name/Category, Description, Quantitative Trend Data (last 24m, quarterly?), Comparison vs Benchmarks (emphasize outperformance), Key Drivers, Link to Financial Outcomes, Sustainability Commentary. Provide detailed analysis in 'analysis_text'. List key highlights.",
        "schema": add_standard_fields({
            "type": "object",
            "properties": {
                 "identified_highlights_list": {
                      "type": "array",
                      "description": "List of key operating performance highlight titles identified.",
                      "items": {"type": "string"}
                 }
            },
            "additionalProperties": False
        }),
        "template": {
            "identified_highlights_list": ["Premium Segment Market Share Expansion", "Significant Revenue Per Customer Expansion", "Manufacturing Efficiency and Output Gains"],
            "analysis_text": "Exceptional operating execution demonstrated [ref1]. Premium Segment Share expanded +3.1 ppts (to 18.9%) over 24m, outpacing key competitors significantly [ref2], driven by new product success (X1000) [ref2]. This contributed ~65% of FY23 revenue growth [ref3]. Avg Revenue Per Customer grew 4.8% YoY FY23, nearly 2x peer avg [ref4], driven by solution selling and customer success programs, boosting sales efficiency [ref5]. Mfg Efficiency improved with utilization up +5.1 ppts (to 87.2%) and cost/unit index down -5.5% over 9 quarters [ref6], contributing ~0.7 ppts to FY23 Gross Margin improvement [ref7]. Performance trends expected to continue near-term [ref3/ref5/ref7].",
            "footnotes": [
                 {"id": "ref1", "document": "Operational Performance Assessment", "page": "3-6", "date": "Mar 2025"},
                 {"id": "ref2", "document": "Market Share Analysis Report", "page": "10-15", "date": "Feb 2025"},
                 {"id": "ref3", "document": "Strategic Growth Analysis", "page": "22-28", "date": "Jan 2025"},
                 {"id": "ref4", "document": "Customer Metrics Analysis", "page": "8-16", "date": "Mar 2025"},
                 {"id": "ref5", "document": "Revenue Growth Drivers Report", "page": "15-22", "date": "Feb 2025"},
                 {"id": "ref6", "document": "Manufacturing Performance Report", "page": "5-18", "date": "Jan 2025"},
                 {"id": "ref7", "document": "Operational Efficiency Analysis", "page": "12-20", "date": "Mar 2025"}
            ],
            "notes": None
        }
    },
# --- Section 23: Sellside Positioning - Financial Performance (Simplified) ---
    {
        "number": 23,
        "title": "Sellside Positioning - Financial Performance",
        "specs": "Extract overview highlighting exceptional financial performance (last 24m). Identify top 3 financial achievements/metrics demonstrating strength (Growth+Profitability, Cash Generation, Capital Efficiency like ROIC). For each: Name/Category, Description, Quantitative Trend Data (last 24m, quarterly?), Comparison vs Benchmarks/Competitors (quantify outperformance), Key Drivers (link to ops/strategy), Link to Shareholder Value/Strategic Flexibility. Provide detailed analysis in 'analysis_text'. List key highlights.",
        "schema": add_standard_fields({
            "type": "object",
            "properties": {
                 "identified_highlights_list": {
                      "type": "array",
                      "description": "List of key financial performance highlight titles identified.",
                      "items": {"type": "string"}
                 }
            },
            "additionalProperties": False
        }),
        "template": {
            "identified_highlights_list": ["Accelerating Revenue Growth with Margin Expansion", "Superior Cash Flow Generation and Conversion", "Industry-Leading Return on Invested Capital (ROIC)"],
            "analysis_text": "Exceptional financial strength demonstrated [ref1]. Revenue growth accelerated to 14.8% YoY (Q1'24) while EBITDA margin expanded +1.0 ppt over 4 qtrs (to 23.0%) [ref2], significantly outpacing peers (+5.8 ppts rev growth, +1.2 ppts margin expansion vs avg FY23) [ref3], driven by mix shift and premium segment gains [ref3]. Superior Cash Conversion (87.5% OCF/EBITDA FY23, +9.3 ppts vs peer avg) and FCF Margin (13.1% FY23, +3.6 ppts vs peer avg) [ref4/ref5] fuel balanced capital allocation (growth, debt paydown, shareholder returns) [ref5]. Industry-leading ROIC (19.8% FY23, +6.3 ppts vs peer avg) [ref6/ref7] reflects efficient capital deployment and justifies premium valuation [ref7].",
            "footnotes": [
                 {"id": "ref1", "document": "Financial Performance Summary", "page": "3-5", "date": "Mar 2025"},
                 {"id": "ref2", "document": "Q1 2024 Earnings Release", "page": "5-8", "date": "Apr 25, 2024"},
                 {"id": "ref3", "document": "Growth Analysis Report", "page": "10-15", "date": "Feb 2024"},
                 {"id": "ref4", "document": "Cash Flow Performance Analysis", "page": "8-12", "date": "Mar 2024"},
                 {"id": "ref5", "document": "Working Capital Mgmt Report", "page": "15-22", "date": "Jan 2024"},
                 {"id": "ref6", "document": "Capital Efficiency Analysis", "page": "5-12", "date": "Feb 2024"},
                 {"id": "ref7", "document": "Competitive Financial Benchmarking", "page": "18-25", "date": "Mar 2024"}
            ],
            "notes": None
        }
    },
# --- Section 24: Sellside Positioning - Management (Simplified) ---
    {
        "number": 24,
        "title": "Sellside Positioning - Management",
        "specs": "Extract overview positioning management/board as experienced, capable, aligned. Identify top 3 facts/achievements related to management/board strength (last 24m). Focus on quantifiable achievements (TSR, successful strategy execution, financial improvements). Highlight relevant background/experience of key individuals (CEO, CFO, Chair). Emphasize successful execution of specific initiatives with data. Include positive governance aspects. Provide detailed analysis in 'analysis_text'. List key strengths/achievements.",
        "schema": add_standard_fields({
            "type": "object",
            "properties": {
                 "identified_strengths_list": {
                      "type": "array",
                      "description": "List of key management/board strength/achievement titles identified.",
                      "items": {"type": "string"}
                 }
            },
            "additionalProperties": False
        }),
        "template": {
             "identified_strengths_list": ["CEO Miller: Proven Digital Transformation Leader Delivering Value", "CFO Wilson: Driving Financial Discipline & Superior Cash Generation", "Experienced Board with Strong Independent Oversight"],
             "analysis_text": "Experienced leadership team with strong execution track record [ref1]. CEO Miller (since 2018, prior relevant COO experience [ref2]) delivered 125% TSR vs +78% industry [ref4], successfully pivoted strategy (+6 ppts recurring revenue share [ref3]) and executed divestiture ($185M proceeds [ref5]). CFO Wilson (since 2020) drove financial discipline leading to superior FCF conversion (87.5% FY23 vs 78.2% peer avg) and ROIC (19.8% FY23 vs 13.5% peer avg) [ref10/ref6]. Board (73% independent [ref11]) includes Founder Chairman Roberts (40+ yrs experience [ref2]) and Tech CEO Lead Director Rodriguez [ref11], providing effective strategic oversight, evidenced by successful 2022 strategic review [ref10].",
             "footnotes": [
                 {"id": "ref1", "document": "Management Assessment Report", "page": "3-5", "date": "Mar 2024"},
                 {"id": "ref2", "document": "Proxy Statement 2024", "page": "12-18", "date": "Feb 2024"},
                 {"id": "ref3", "document": "CEO Performance Review", "page": "5-10", "date": "Jan 2024"},
                 {"id": "ref4", "document": "CEO Performance Metrics", "page": "8-12", "date": "Feb 2024"},
                 {"id": "ref5", "document": "Legacy Components Divestiture PR", "page": "1", "date": "Oct 12, 2023"},
                 {"id": "ref6", "document": "CFO Performance Assessment", "page": "3-8", "date": "Jan 2024"},
                 {"id": "ref10", "document": "Board Effectiveness Review", "page": "8-15", "date": "Jan 2024"}, # Used for CFO ROIC/FCF link, Board review
                 {"id": "ref11", "document": "Corporate Governance Assessment", "page": "12-18", "date": "Dec 2023"}
             ],
             "notes": None
        }
    },
# --- Section 25: Sellside Positioning - Potential Investor Concerns and Mitigants (Simplified - Keep as previous draft) ---
    {
        "number": 25,
        "title": "Sellside Positioning - Potential Investor Concerns and Mitigants",
        "specs": "Identify top 5 potential investor concerns (fundamental business or valuation). For each: Name/Category, Description, Supporting Data Points. Immediately follow with 1-2 compelling Mitigants: Description, Supporting Data/Evidence showing how concern is addressed/reduced. Provide detailed analysis in 'analysis_text'. List key concerns.",
        "schema": add_standard_fields({
            "type": "object",
            "properties": {
                 "identified_concerns_list": {
                      "type": "array",
                      "description": "List of key potential investor concern titles identified.",
                      "items": {"type": "string"}
                 }
            },
            "additionalProperties": False
        }),
        "template": {
             "identified_concerns_list": ["Software Development Capability Gap", "Asia-Pacific Manufacturing Constraints", "Premium Valuation Relative to Peers", "Hardware Margin Pressure", "Associate Performance Volatility"],
             "analysis_text": "Potential concerns acknowledged but mitigated [ref1]. 1) Software Gap (40% engineer shortfall [ref2]): Mitigated by tech partnerships (+15% capacity boost via cloud services [ref3]) and focus on existing high-value IP driving recurring revenue (+22.5% YoY FY23 [ref3]). 2) APAC Capacity Constraints (lagging demand): Mitigated by facility expansion (on track, +65% capacity by Q3'25 [ref5]) and secured contract manufacturing (+5k units/yr from H2'24 [ref5]). 3) Premium Valuation (14.5x EV/EBITDA vs 11.9x avg [ref14]): Justified by superior financials (+5.8 ppts rev growth, +6.3 ppts ROIC vs peers [ref15]) and mix shift to higher-multiple software/services (28% recurring vs 15% peer avg [ref15]). 4) Hardware Margin Pressure... 5) Associate Volatility...",
             "footnotes": [
                 {"id": "ref1", "document": "Investor Concerns Analysis", "page": "3-4", "date": "Mar 2024"},
                 {"id": "ref2", "document": "Technical Resource Gap Assessment", "page": "8-12", "date": "Feb 2024"},
                 {"id": "ref3", "document": "Strategic Technology Partnership Report", "page": "5-10", "date": "Jan 2024"},
                 {"id": "ref5", "document": "APAC Mfg Capacity Analysis", "page": "3-8", "date": "Feb 5, 2024"}, # Reused ref
                 {"id": "ref14", "document": "Valuation Analysis Report", "page": "5-10", "date": "Mar 2024"},
                 {"id": "ref15", "document": "Financial Performance Benchmarking", "page": "12-18", "date": "Mar 2024"}
             ],
             "notes": None
        }
    },
# --- Section 26: Buyside Due Diligence - Macro (Simplified) ---
    {
        "number": 26,
        "title": "Buyside Due Diligence - Macro",
        "specs": "From buyside view, analyze top 3 macro risk trends (next 12-24m). Focus on downside (slowing growth, rates, inflation, labor, supply chain, FX, geopolitical). For each: Name/Category, Risk Description, Company Sensitivity Analysis (quantify negative impact scenarios), Competitive Benchmarking (relative vulnerability), Mitigation Assessment (effectiveness/limitations), Formulate 2-3 DD Questions. Provide detailed analysis in 'analysis_text'. List key risks.",
        "schema": add_standard_fields({
            "type": "object",
            "properties": {
                 "identified_risks_list": {
                      "type": "array",
                      "description": "List of key macro risk titles identified for diligence.",
                      "items": {"type": "string"}
                 },
                 "key_dd_questions": { # Consolidate questions
                      "type": "array",
                      "description": "Consolidated list of key buyside due diligence questions related to macro risks.",
                      "items": {"type": "string"}
                 }
            },
            "additionalProperties": False
        }),
        "template": {
             "identified_risks_list": ["Interest Rate Sensitivity / Capex Cycle Downturn Risk", "Input Cost Inflation & Margin Pressure", "Foreign Exchange Exposure"],
             "key_dd_questions": [
                 "Provide detailed backlog data (aging, book-to-bill by segment, cancellation rates) for the past 8 quarters to assess forward visibility under potential slowdown.",
                 "Quantify fixed vs. variable costs by segment and detail specific cost reduction levers available under a 5% revenue decline scenario.",
                 "Provide detailed breakdown of input cost inflation by major category and the effectiveness of specific pass-through mechanisms over the past 8 quarters.",
                 "What percentage of COGS is covered by long-term supplier agreements (>12 months) with fixed pricing or defined escalators?",
                 "What is the current currency hedging strategy, percentage of exposure hedged by currency, and sensitivity of EBITDA/Net Income to a 10% adverse movement in key FX rates?"
             ],
             "analysis_text": "Buyside DD should focus on macro risks [ref1]. 1) Capex Cycle Risk: Company revenue highly correlated (0.85x beta) to industrial capex [ref3]. Downturn scenario (capex growth slows 3ppts) implies ~-2.6 ppts revenue impact and -0.7 ppts EBITDA margin impact [ref3]. Company appears slightly more sensitive than Competitor A [ref4]. Mitigation (recurring revenue shift) helps but hardware mix remains high [ref5]. DD questions focus on backlog visibility and cost flexibility. 2) Inflation Risk: Negative price/cost gap emerged Q1'24 (-2.2 ppts) [ref8]. High exposure to electronics (38% direct costs) [ref8]. Pass-through ability lags Competitor A [ref9]. Mitigation (hedging, value pricing) partially effective [ref10]. DD questions focus on granular price/cost pass-through and supplier contracts. 3) FX Exposure: Significant impact on associate earnings (e.g., Telkomsel -18% post-tax contribution impact FY23 partly due to IDR depreciation [ref5]). Hedging policy exists but doesn't cover translation risk fully [ref10]. DD questions focus on hedging specifics and sensitivity.",
             "footnotes": [], # Fixed placeholder
             "notes": None
        }
    },
# --- Section 27: Buyside Due Diligence - Industry (Simplified) ---
    {
        "number": 27,
        "title": "Buyside Due Diligence - Industry",
        "specs": "From buyside view, analyze top 3 industry risk trends (next 12-24m). Focus on downside (disruptive tech, competition, customer shifts, industry regulation, biz model obsolescence). For each: Name/Category, Risk Description/Why risk to Company, Company Vulnerability Analysis (quantify exposure/gap/scenario impact), Competitive Benchmarking (positioning/response vs peers), Company Response Assessment (adequacy/limitations), Formulate 2-3 DD Questions. Provide detailed analysis in 'analysis_text'. List key risks.",
        "schema": add_standard_fields({
            "type": "object",
            "properties": {
                 "identified_risks_list": {
                      "type": "array",
                      "description": "List of key industry risk titles identified for diligence.",
                      "items": {"type": "string"}
                 },
                 "key_dd_questions": {
                      "type": "array",
                      "description": "Consolidated list of key buyside due diligence questions related to industry risks.",
                      "items": {"type": "string"}
                 }
            },
            "additionalProperties": False
        }),
        "template": {
            "identified_risks_list": ["Software-Centric Disruption by New Entrants", "Hardware Commoditization & Price Pressure", "Regulatory Hurdles (Cybersecurity/Energy)"],
            "key_dd_questions": [
                 "Provide the detailed cloud platform roadmap, including plans and resources needed to achieve feature parity with Competitor A and key software natives.",
                 "What is the customer churn rate specifically for customers who evaluated but did not select the Company's digital/subscription offerings in the past 12 months?",
                 "Provide gross margin analysis by product SKU for standard hardware lines over 8 quarters, isolating price, volume, mix, and cost impacts.",
                 "What is the competitive pricing intelligence process and response plan for further potential price cuts from Asian competitors?",
                 "Detail the compliance roadmap and associated costs for upcoming cybersecurity (e.g., EU CRA) and energy efficiency regulations in key markets."
            ],
            "analysis_text": "Industry risks require diligence [ref1]. 1) Software Disruption: Risk from software-natives (e.g., SoftwareAutomation Inc) challenging traditional models [ref2]. Company vulnerable due to lagging capabilities (win rate vs natives 42% down from 52% [ref3], cloud platform score 6.2/10 [ref4]), risking recurring revenue goals (potential miss $85-140M by 2025 [ref3]). Competitor A investing more ($350M/yr vs $150M/yr est.) [ref4]. Company response (partnerships, dev centers) lacks scale [ref5]. DD Qs focus on platform roadmap and digital deal churn. 2) Hardware Commoditization: Accelerating price erosion (-3.2% Q1'24 [ref8]) in standard hardware (~42% revenue) driven by Asian competitors [ref7]. Risks margin compression (potential -1.5 ppts EBITDA impact scenario [ref8]). Company more exposed than Competitor A (42% vs 35% revenue [ref9]). Mitigation (bundling, cost reduction) partially effective [ref10]. DD Qs focus on SKU-level margins and pricing response plans. 3) Regulatory Hurdles...",
            "footnotes": [], # Fixed placeholder
            "notes": None
        }
    },
# --- Section 28: Buyside Due Diligence - Competitive Positioning (Simplified) ---
    {
        "number": 28,
        "title": "Buyside Due Diligence - Competitive Positioning",
        "specs": "From buyside view, critically evaluate competitive positioning. Analyze market share trends (overall, segment, geo; last 24-36m; rate of change vs competitors). Assess defensibility/sustainability of product differentiation (use objective metrics, validate claims, identify erosion). Evaluate actual pricing power (realization, discounting, premium/discount vs competitors, cost pass-through). Analyze relative cost position (benchmark COGS%, SG&A%, Mfg cost/unit, R&D efficiency vs peers). Critically assess claimed advantages (validate magnitude, sustainability, economic contribution). Identify key disadvantages/vulnerabilities. Formulate 2-3 DD questions per topic area. Provide detailed analysis in 'analysis_text'.",
        "schema": add_standard_fields({
            "type": "object",
            "properties": {
                 "positioning_summary": {
                     "type": ["string", "null"],
                     "description": "Overall buyside summary of competitive strengths and weaknesses."
                 },
                 "key_dd_questions": {
                      "type": "array",
                      "description": "Consolidated list of key buyside due diligence questions related to competitive positioning.",
                      "items": {"type": "string"}
                 }
            },
            "additionalProperties": False
        }),
        "template": {
             "positioning_summary": "Buyside view: Holds advantages in energy tech and integration, but market share trend is mixed (gaining in premium auto, losing vs digital natives), differentiation eroding in standard hardware, pricing power softening (realization down), and cost position needs deeper validation vs specific peers [ref1].",
             "key_dd_questions": [
                  "Provide cohort analysis of market share showing gains/losses by customer acquisition year and segment.",
                  "Detail win rates specifically against software-native competitors over the past 8 quarters.",
                  "What is the detailed technical roadmap and investment plan ($ and FTEs) for the digital platform to achieve feature parity?",
                  "Provide SKU-level pricing analysis (ASP, discounts) for standard hardware lines over 8 quarters.",
                  "Provide a detailed manufacturing cost benchmark study comparing Company's cost per unit against Competitors A, B, and C by major product line.",
                  "What is the multi-year plan and budget to sustain the competitive advantage in energy optimization technology?",
                  "Provide customer cohort analysis showing financials for standard hardware vs. integrated solution customers."
             ],
             "analysis_text": "Market Share: Overall stable (+0.7 ppts 24m) but mix shift - gaining in premium auto (+3.1 ppts) but losing vs digital/software natives [ref2]. Win rate down 2.5 ppts overall [ref2]. Differentiation: Strong in energy tech (+4.2 ppts efficiency vs Comp A [ref5]), weak in digital features (score 72 vs 82.5 Comp A [ref5]). Pricing Power: Realization rate softening (82.7% FY23 vs 84.4% FY22), premium vs Comp A narrowed [ref8]. Cost: Favorable Gross Margin (+1.2 ppts vs avg) and SG&A (-0.7 ppts vs avg) [ref10], but Mfg Cost/Unit potentially lags key peers [ref10]. Advantage Validation: Energy tech & integration advantages seem real [ref12]. Risks: Digital gap, hardware commoditization are key vulnerabilities [ref12].",
             "footnotes": [], # Fixed placeholder
             "notes": None
        }
    },
# --- Section 29: Buyside Due Diligence - Operating Performance (Simplified) ---
    {
        "number": 29,
        "title": "Buyside Due Diligence - Operating Performance",
        "specs": "From buyside view, critically analyze top 3 operating metrics impacting value/risk (last 24m). Focus beyond financials (e.g., share trends, volume/price drivers, unit economics, CAC, CLTV/CAC, churn/retention by cohort, asset utilization). For each: Definition/Relevance, Historical Trend/Volatility, Benchmark vs Peers (esp. underperformance/sustainability), Driver Analysis (sustainability/quality), Sustainability Assessment (risks/headwinds), Potential Financial Impact of Risks, Formulate 2-3 DD Questions.",
        "schema": add_standard_fields({
            "type": "object",
            "properties": {
                 "identified_metrics_for_dd": {
                      "type": "array",
                      "description": "List of key operating metric titles identified for diligence.",
                      "items": {"type": "string"}
                 },
                 "key_dd_questions": {
                      "type": "array",
                      "description": "Consolidated list of key buyside due diligence questions related to operating performance.",
                      "items": {"type": "string"}
                 }
            },
            "additionalProperties": False
        }),
        "template": {
             "identified_metrics_for_dd": ["Premium Segment Market Share Trend", "Customer Churn Rate (Annualized)", "Manufacturing Capacity Utilization Trend"],
             "key_dd_questions": [
                 "Provide market share data broken down by product generation (e.g., X1000 vs older models) and customer cohort (new vs existing) for the premium automation segment.",
                 "What is management's competitive response plan to Competitor A's increased investment and Competitor B's anticipated new product launch in the premium segment?",
                 "Provide customer churn data segmented by customer size, geography, product line, and acquisition cohort for the past 36 months.",
                 "What is the quantitative impact of the Customer Success program on churn reduction and upsell rates? Provide supporting data and cost analysis.",
                 "Provide detailed historical data and forward projections for manufacturing capacity utilization by facility, alongside demand forecasts and backlog aging.",
                 "What are the specific contingency plans and associated costs if capacity utilization significantly exceeds or falls below optimal levels (e.g., >90% or <75%)?"
             ],
             "analysis_text": "Key operating metrics require diligence [ref1]. 1) Premium Segment Share: Strong gains (+3.1 ppts over 24m to 18.9% [ref2]) outpaced peers [ref3]. Drivers: X1000 launch, Competitor B issues [ref2]. Sustainability Risk: Competitor response, launch boost fading [ref1]. Potential Impact: Slowing gains could hit FY25 revenue growth by -1.5 ppts [ref1]. DD Qs probe gain sources & competitive response. 2) Customer Churn: Improved significantly (8.2% Q1'22 -> 6.0% Q1'24 [ref5]), better than industry avg (9.0%) [ref6]. Drivers: Product reliability, Customer Success program, subscription adoption [ref5]. Sustainability Risk: Further reduction difficult, relies on scaling Customer Success [ref1]. Potential Impact: Reversion to 8% churn could cost ~$35M ARR [ref1]. DD Qs probe cohort churn & Customer Success ROI. 3) Capacity Utilization: Increased steadily (82.1% FY22 -> 87.2% Q1'24 [ref6 from Sec 22]), well above industry (75.5%) [ref6 from Sec 22]. Driver: Strong demand, efficiency initiatives [ref7 from Sec 22]. Sustainability Risk: Approaching ceiling, potential bottleneck despite CEO comments [ref5 from Sec 6]. Potential Impact: Limits growth, increases lead times. DD Qs probe facility-level data and contingency plans.",
             "footnotes": [], # Fixed placeholder
             "notes": None
        }
    },
# --- Section 30: Buyside Due Diligence - Financial Performance (Simplified) ---
    {
        "number": 30,
        "title": "Buyside Due Diligence - Financial Performance",
        "specs": "From buyside view, critically analyze 5-7 key financial metrics (quality/sustainability risks). Focus beyond headlines (earnings quality, margins, cash flows, returns). For each: Definition/Relevance, Historical Trend/Benchmark, Quality Assessment (accounting, one-timers, adjustments, mgmt indicators), Sustainability Assessment (drivers, risks, headwinds), Potential Financial Impact (normalization, risk quantification), Formulate 2-3 DD Questions. Note forensic flags.",
        "schema": add_standard_fields({
            "type": "object",
            "properties": {
                 "identified_metrics_for_dd": {
                      "type": "array",
                      "description": "List of key financial metric titles identified for diligence.",
                      "items": {"type": "string"}
                 },
                 "key_dd_questions": {
                      "type": "array",
                      "description": "Consolidated list of key buyside due diligence questions related to financial performance.",
                      "items": {"type": "string"}
                 }
            },
            "additionalProperties": False
        }),
        "template": {
             "identified_metrics_for_dd": ["Recurring Revenue Quality", "Gross Margin Sustainability", "Free Cash Flow Conversion Quality", "Capitalized Software Development Costs", "Accounts Receivable / DSO Trend"],
             "key_dd_questions": [
                  "Provide a detailed cohort analysis of recurring revenue customers showing retention rates, expansion revenue (upsell/cross-sell), and ARPU trends by cohort.",
                  "What percentage of recurring revenue is tied to multi-year contracts versus month-to-month or annual renewals?",
                  "Provide a detailed gross margin bridge analysis for the past 8 quarters, quantifying the impact of volume, price, mix, input costs, manufacturing efficiencies, and FX.",
                  "What are the specific contractual protections or pass-through mechanisms for key input cost categories (electronics, metals)?",
                  "Provide a quality of free cash flow analysis, reconciling Net Income to FCF and detailing working capital changes and non-cash adjustments for 8 quarters.",
                  "What is the company's policy for capitalizing software development costs? Provide details on capitalized amounts, amortization periods, and impairment testing results for the past 3 years.",
                  "Provide an aging analysis of accounts receivable for the past 8 quarters and detail the methodology for calculating the allowance for doubtful accounts."
             ],
             "analysis_text": "Financial diligence areas [ref1]. 1) Recurring Revenue Quality: Growing (22%->28.5% mix Q1'22-Q1'24 [ref2]) but lags leader A (35%) [ref3]. Quality seems high (60% subscription) [ref4], but sustainability depends on closing software gap [ref5]. DD Qs probe cohort retention/expansion and contract lengths. 2) Gross Margin Sustainability: Declined from 43.8% (Q1'22) to 41.3% (Q1'24), now below industry avg (43.1%) [ref31/ref32]. High risk of further compression from hardware price erosion (-3.2% Q1'24 [ref8]) and input costs [ref34]. DD Qs focus on margin bridge and cost pass-through. 3) FCF Conversion: Strong (87.5% OCF/EBITDA FY23) but aided by lower capex recently [ref5 from Sec 23]. Sustainability requires maintaining WC improvements [ref5 from Sec 23]. DD Qs probe WC details. 4) Capitalized Software Costs: Need review of policy, amortization, potential impairment risk given tech shifts. DD Qs request policy & testing details. 5) Accounts Receivable: Check quality via aging/allowance adequacy. DD Qs ask for aging/allowance methodology.",
             "footnotes": [], # Fixed placeholder
             "notes": None
        }
    },
# --- Section 31: Buyside Due Diligence - Management (Simplified) ---
    {
        "number": 31,
        "title": "Buyside Due Diligence - Management",
        "specs": "From buyside view, critically evaluate key management (C-suite, key reports) & Board (Chair, Lead Ind. Director). Focus on risks: individual capabilities, alignment, retention, succession, integration readiness. For key individuals: Role/Tenure, Track Record Analysis (validate achievements, identify failures/controversies), Experience Fit (future strategy/integration), Red Flags, Retention Risk Analysis (comp hooks, CoC, satisfaction). Assess team M&A/integration track record & readiness gaps. Evaluate board effectiveness/independence/conflicts. Formulate 2-3 DD questions per key individual/area.",
        "schema": add_standard_fields({
            "type": "object",
            "properties": {
                 "key_individuals_assessed": {
                      "type": "array",
                      "description": "List of names of key individuals assessed.",
                      "items": {"type": "string"}
                 },
                 "key_dd_questions": {
                      "type": "array",
                      "description": "Consolidated list of key buyside due diligence questions related to management and board.",
                      "items": {"type": "string"}
                 }
            },
            "additionalProperties": False
        }),
        "template": {
             "key_individuals_assessed": ["James W. Miller (CEO)", "Sarah Wilson (CFO)", "Thomas J. Roberts (Chairman)"],
             "key_dd_questions": [
                  "What are CEO Miller's specific plans to address the software engineering gap in the next 12 months?",
                  "Describe CEO Miller's post-acquisition integration philosophy and specific experience from prior roles.",
                  "Describe CFO Wilson's specific experience managing post-merger financial integration, including challenges faced.",
                  "What are the CFO's key priorities for improving financial systems and reporting capabilities over the next 1-2 years?",
                  "Does the Company have a documented post-merger integration playbook? Provide details.",
                  "Discuss the Board's process for evaluating strategic alternatives, including potential sales of the company.",
                  "What are the key terms of the Governance Agreement between the Company and the Founding Families regarding board nominations and transaction approvals?"
             ],
             "analysis_text": "Buyside view of management [ref1]. CEO Miller: Strong track record on growth/strategy shifts (+125% TSR vs +78% industry [ref4]), relevant prior COO experience [ref2]. Concern: Software execution gap [ref6]. Retention risk medium (Std CoC, good unvested equity [$12M est] [ref7]). CFO Wilson: Strong financial operator (improved FCF/ROIC [ref10]), but limited large-scale integration experience cited [ref8]. Retention risk low-medium (comp competitive [ref7]). Chairman Roberts: Founder influence/ownership (15% [ref2]) needs assessment re: alignment [ref11]. Team Integration Readiness: Experience limited to smaller bolt-ons/divestitures; large-scale integration readiness gap likely [ref12]. Board: Appears adequately independent (73% [ref11]), relevant expertise present, but founder influence/family relationships noted [ref11]. DD Qs focus on software gap plan, integration experience/playbook, Board M&A stance, and Founder governance agreement.",
             "footnotes": [], # Fixed placeholder
             "notes": None
        }
    },
# --- Section 32: Appendix (Simplified - Keep as previous draft) ---
    {
        "number": 32,
        "title": "Appendix - Extracted Numerical Data Snippets",
        "specs": "Extract sentences or short text snippets containing meaningful numerical data points (integers, decimals, percentages) from the documents. Include source document and page number for each snippet.",
        "schema": {
            "type": "object",
            "properties": {
                "extracted_snippets": {
                    "type": "array",
                    "description": "List of text snippets containing numerical data.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "text_snippet": {"type": "string", "description": "The extracted text containing the number."},
                            "document_name": {"type": "string", "description": "Source document filename."},
                            "source_page": {"type": ["string", "integer", "null"], "description": "Page number."},
                            "source_section": {"type": ["string", "null"], "description": "Optional section/table identifier."}
                        },
                        "required": ["text_snippet", "document_name", "source_page"],
                         "additionalProperties": False
                    }
                }
            },
            "required": ["extracted_snippets"],
             "additionalProperties": False # No analysis_text or footnotes needed here
        },
        "template": {
            "extracted_snippets": [
                {"text_snippet": "Consolidated revenues were $4,572.3 million for the year ended December 31, 2023.", "document_name": "Annual Report 2023.pdf", "source_page": "F-5", "source_section": "Consolidated Statements of Income"},
                {"text_snippet": "This represents an increase of 14.1% compared to the prior year.", "document_name": "Annual Report 2023.pdf", "source_page": "25", "source_section": "MD&A - Results of Operations"},
                {"text_snippet": "Average manufacturing capacity utilization improved to 85.4%.", "document_name": "Annual Report 2023.pdf", "source_page": "32", "source_section": "MD&A - Operational Performance"},
                {"text_snippet": "First quarter revenue increased 14.8% year-over-year to $1,248.5 million.", "document_name": "Q1 2024 Earnings Release.pdf", "source_page": "1", "source_section": "Highlights"}
            ]
        }
    },
] # Added missing closing bracket for the main 'sections' list

# Function to get schema or template for prompts (can be used in section_processor)
def get_section_schema_string(section_number):
    for section in sections:
        if section["number"] == section_number:
            try:
                # Ensure using the updated schema which includes standard fields
                schema_to_dump = section.get('schema', {})
                # Optional: Add notes recursively if desired globally
                # _add_optional_notes_recursively(schema_to_dump)
                return json.dumps(schema_to_dump, indent=2)
            except Exception as e:
                print(f"Error dumping schema for section {section_number}: {e}")
                return "{}"
    return "{}"

def get_section_template_string(section_number):
     for section in sections:
        if section["number"] == section_number:
             try:
                template_to_dump = section.get('template', {})
                # Ensure template also reflects standard fields for clarity
                if 'analysis_text' not in template_to_dump: template_to_dump['analysis_text'] = "..."
                if 'footnotes' not in template_to_dump: template_to_dump['footnotes'] = []
                if 'notes' not in template_to_dump: template_to_dump['notes'] = None
                # Optional: Add notes recursively if desired globally
                # _add_optional_notes_recursively(template_to_dump) # Usually not needed for templates
                return json.dumps(template_to_dump, indent=2)
             except Exception as e:
                print(f"Error dumping template for section {section_number}: {e}")
                return "{}"
     return "{}"

# --- END OF COMPLETE section_definitions.py ---