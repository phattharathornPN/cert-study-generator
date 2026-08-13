# -*- coding: utf-8 -*-
"""ISC2 CISSP — manager/advisor pack.

Split out of the old combined `security` pack on 2026-08-11. The combined pack
was already written at CISSP depth, so this is the one whose *content* changes
least -- but the topic list is rebuilt against the eight CISSP domains rather
than a merged 32-section outline, so section weight now tracks the real exam.

CISSP is explicitly a management exam ("think like a manager, CEO or owner"):
the candidate is expected to pick the answer that best reduces organisational
risk for the money, not the most technically thorough one. The MOST/BEST/FIRST
qualifier is usually what separates the right answer from three plausible ones,
so every summary is asked to address it directly.

Blueprint (exam outline effective 2024-04-15, still current):
    D1 Security and Risk Management            16%
    D2 Asset Security                          10%
    D3 Security Architecture and Engineering   13%
    D4 Communication and Network Security      13%
    D5 Identity and Access Management          13%
    D6 Security Assessment and Testing         12%
    D7 Security Operations                     13%
    D8 Software Development Security           10%

Shares NOTEBOOK_ID_SECURITY with the CC and Security+ packs: one uploaded
source library covers all three blueprints. Note the one consequence --
slides_v2.py's lock is per cert, not per notebook, so do not run slide cycles
for two security packs at the same time.

Verified 2026-08-11 against the official ISC2 CISSP Exam Outline PDF
(effective 2024-04-15), domain by domain. The topic list already tracked the
blueprint closely -- two real gaps were added rather than a rewrite: 1.2's
"CIA, authenticity and non-repudiation" fundamentals (01_11) had no dedicated
topic, and 1.6/1.7's Business Impact Analysis was only ever implied, never
named (03_15). BC/DR also appears a second time under Domain 7 (section 24)
as operational implementation -- that duplication is intentional, matching
how the outline itself tests BC/DR from both a risk-planning and an
operations angle.

D4 is the one place this pack legitimately touches networking, but it is still
tested as architecture and risk, never as device configuration -- the
no-network-config guard in certs/_security_shared.py applies here too.

Only slide.pdf is downloaded: the reader site uses the PDF, so generating
.pptx would double the time and disk for a file nothing reads.
"""
from certs._security_shared import (
    security_slide_instructions,
    security_summary_prompt,
)

EXAM_NAME = "ISC2 CISSP"
OUTPUT_DIR = "cissp/output"
SITE_DIR = "cissp"         # index.html sits beside its own output/
DIST_DIR = "cissp/dist"
NOTEBOOK_ENV = "NOTEBOOK_ID_SECURITY"   # shared library, see module docstring
SLIDE_FORMATS = ("pdf",)

SECTION_TITLES = {
    "01": "Professional Ethics and Governance",
    "02": "Compliance, Legal and Privacy",
    "03": "Risk Management",
    "04": "Personnel Security and Awareness",
    "05": "Asset Classification and Ownership",
    "06": "Data Lifecycle and Retention",
    "07": "Data Protection Methods",
    "08": "Security Models and Architecture",
    "09": "Cryptography",
    "10": "Physical and Environmental Security",
    "11": "Vulnerabilities in Systems and Architectures",
    "12": "Network Architecture and Protocols",
    "13": "Network Components and Attacks",
    "14": "Secure Communication Channels",
    "15": "Identity Management",
    "16": "Access Control Models and Mechanisms",
    "17": "Federation and Identity Lifecycle",
    "18": "Assessment and Test Strategies",
    "19": "Security Testing Techniques",
    "20": "Audit and Security Reporting",
    "21": "Investigations and Digital Forensics",
    "22": "Operational Controls and Logging",
    "23": "Incident Management",
    "24": "Business Continuity and Disaster Recovery",
    "25": "Software Development Lifecycle Security",
    "26": "Secure Coding and Application Controls",
    "27": "Software Security Assessment",
}

TOPICS = [
    # -- 01: Professional Ethics and Governance (D1) --
    {"id": "01_01", "topic": "The ISC2 Code of Professional Ethics and Canon Precedence"},
    {"id": "01_02", "topic": "Organisational Ethics and Conflict of Interest"},
    {"id": "01_03", "topic": "Security Governance and Alignment to Business Strategy"},
    {"id": "01_04", "topic": "Organisational Roles: Owner, Custodian, Processor and User"},
    {"id": "01_05", "topic": "Governance Structures: Boards, Committees and Steering Groups"},
    {"id": "01_06", "topic": "Due Care Versus Due Diligence"},
    {"id": "01_07", "topic": "Policies, Standards, Baselines, Guidelines and Procedures"},
    {"id": "01_08", "topic": "Acceptable Use Policy and What It Must Cover"},
    {"id": "01_09", "topic": "Control Frameworks: ISO 27001, NIST CSF and COBIT"},
    {"id": "01_10", "topic": "Gap Analysis and Measuring Against a Standard"},
    {"id": "01_11", "topic": "The Five Pillars: Confidentiality, Integrity, Availability, Authenticity and Non-Repudiation"},

    # -- 02: Compliance, Legal and Privacy (D1) --
    {"id": "02_01", "topic": "Criminal, Civil, Administrative and Regulatory Law"},
    {"id": "02_02", "topic": "Intellectual Property: Patent, Copyright, Trademark and Trade Secret"},
    {"id": "02_03", "topic": "Licensing, Import and Export Controls"},
    {"id": "02_04", "topic": "Transborder Data Flow and Data Localisation"},
    {"id": "02_05", "topic": "GDPR Principles and Data Subject Rights"},
    {"id": "02_06", "topic": "HIPAA, PCI DSS, SOX and GLBA Obligations"},
    {"id": "02_07", "topic": "Computer Crime Law and Breach Notification"},
    {"id": "02_08", "topic": "Contractual, Legal and Industry Compliance Requirements"},
    {"id": "02_09", "topic": "Privacy Requirements and Privacy by Design"},
    {"id": "02_10", "topic": "Consequences of Non-Compliance: Fines, Sanctions and Licence Loss"},
    {"id": "02_11", "topic": "Compliance Reporting: Internal and External"},
    {"id": "02_12", "topic": "Investigation Types: Criminal, Civil, Regulatory and Administrative"},

    # -- 03: Risk Management (D1) --
    {"id": "03_01", "topic": "Assets, Threats, Vulnerabilities and Exposure Defined"},
    {"id": "03_02", "topic": "Asset Valuation as the Basis of Risk"},
    {"id": "03_03", "topic": "Risk Identification and the Risk Register"},
    {"id": "03_04", "topic": "Qualitative Risk Analysis and Risk Matrices"},
    {"id": "03_05", "topic": "Quantitative Risk Analysis: AV, EF, SLE, ARO and ALE"},
    {"id": "03_06", "topic": "Risk Treatment: Mitigate, Transfer, Avoid and Accept"},
    {"id": "03_07", "topic": "Residual Risk, Risk Appetite and Risk Tolerance"},
    {"id": "03_08", "topic": "Countermeasure Selection and Total Cost of Ownership"},
    {"id": "03_09", "topic": "Control Types and Control Selection"},
    {"id": "03_10", "topic": "Continuous Monitoring and Risk Reporting"},
    {"id": "03_11", "topic": "Risk Frameworks: NIST RMF and ISO 27005"},
    {"id": "03_12", "topic": "Threat Modelling: STRIDE, PASTA and DREAD"},
    {"id": "03_13", "topic": "Supply Chain Risk and Where It Enters"},
    {"id": "03_14", "topic": "Third-Party Agreements: SLA, MOU, MSA, SOW, NDA and BPA"},
    {"id": "03_15", "topic": "The Business Impact Analysis and External Dependencies"},

    # -- 04: Personnel Security and Awareness (D1) --
    {"id": "04_01", "topic": "Candidate Screening, Background Checks and Vetting"},
    {"id": "04_02", "topic": "Employment Agreements and Policy Acknowledgement"},
    {"id": "04_03", "topic": "Onboarding, Transfers and Termination Processes"},
    {"id": "04_04", "topic": "Separation of Duties, Job Rotation and Mandatory Vacation"},
    {"id": "04_05", "topic": "Least Privilege and Need to Know in Personnel Terms"},
    {"id": "04_06", "topic": "Vendor, Consultant and Contractor Controls"},
    {"id": "04_07", "topic": "Security Awareness, Training and Education Distinguished"},
    {"id": "04_08", "topic": "Social Engineering Awareness and Phishing Simulation"},
    {"id": "04_09", "topic": "Measuring Programme Effectiveness"},
    {"id": "04_10", "topic": "Building a Reporting Culture"},

    # -- 05: Asset Classification and Ownership (D2) --
    {"id": "05_01", "topic": "Identifying and Inventorying Information Assets"},
    {"id": "05_02", "topic": "Data Classification Schemes: Government and Commercial"},
    {"id": "05_03", "topic": "Asset Classification Versus Data Classification"},
    {"id": "05_04", "topic": "Data Owner, Data Custodian and Data Steward Roles"},
    {"id": "05_05", "topic": "Data Controller Versus Data Processor"},
    {"id": "05_06", "topic": "Labelling, Marking and Handling Requirements"},
    {"id": "05_07", "topic": "Asset Ownership and Accountability"},
    {"id": "05_08", "topic": "Tangible and Intangible Asset Valuation"},
    {"id": "05_09", "topic": "Provisioning and Tracking Assets Through Their Life"},

    # -- 06: Data Lifecycle and Retention (D2) --
    {"id": "06_01", "topic": "The Data Lifecycle From Creation to Destruction"},
    {"id": "06_02", "topic": "Data Collection Limitation and Minimisation"},
    {"id": "06_03", "topic": "Data Location and Where It Legally Resides"},
    {"id": "06_04", "topic": "Data Maintenance and Data Quality"},
    {"id": "06_05", "topic": "Retention Policy and Why Keeping Everything Is a Liability"},
    {"id": "06_06", "topic": "Legal Hold and Its Effect on Retention"},
    {"id": "06_07", "topic": "Media Sanitisation: Clearing, Purging and Destruction"},
    {"id": "06_08", "topic": "Degaussing, Cryptographic Erase and Physical Destruction"},
    {"id": "06_09", "topic": "Remanence and Why Deletion Is Not Enough"},
    {"id": "06_10", "topic": "End-of-Life and Decommissioning Decisions"},

    # -- 07: Data Protection Methods (D2) --
    {"id": "07_01", "topic": "Data States: At Rest, In Transit and In Use"},
    {"id": "07_02", "topic": "Data Loss Prevention Strategy and Placement"},
    {"id": "07_03", "topic": "Digital Rights Management and Information Rights Management"},
    {"id": "07_04", "topic": "Cloud Access Security Brokers"},
    {"id": "07_05", "topic": "Tokenisation and Data Masking"},
    {"id": "07_06", "topic": "Anonymisation, Pseudonymisation and Re-Identification Risk"},
    {"id": "07_07", "topic": "Scoping and Tailoring a Baseline to the Organisation"},
    {"id": "07_08", "topic": "Selecting Standards and Applying Them to Assets"},
    {"id": "07_09", "topic": "Data Security Controls and Compliance Requirements"},
    {"id": "07_10", "topic": "Protecting Data in Shared and Multi-Tenant Environments"},

    # -- 08: Security Models and Architecture (D3) --
    {"id": "08_01", "topic": "Secure Design Principles: Least Privilege and Defence in Depth"},
    {"id": "08_02", "topic": "Fail Securely, Secure Defaults and Economy of Mechanism"},
    {"id": "08_03", "topic": "Zero Trust and Trust But Verify Compared"},
    {"id": "08_04", "topic": "Privacy by Design and Security by Design"},
    {"id": "08_05", "topic": "The Bell-LaPadula Model and Confidentiality"},
    {"id": "08_06", "topic": "The Biba Model and Integrity"},
    {"id": "08_07", "topic": "Clark-Wilson and Well-Formed Transactions"},
    {"id": "08_08", "topic": "Brewer-Nash (Chinese Wall) and Conflict of Interest"},
    {"id": "08_09", "topic": "Reference Monitor, Security Kernel and the TCB"},
    {"id": "08_10", "topic": "Common Criteria, Evaluation Assurance Levels and Certification"},

    # -- 09: Cryptography (D3) --
    {"id": "09_01", "topic": "Cryptographic Goals and What Each Primitive Provides"},
    {"id": "09_02", "topic": "Symmetric Cryptography and Key Distribution Problems"},
    {"id": "09_03", "topic": "Block Ciphers, Stream Ciphers and Modes of Operation"},
    {"id": "09_04", "topic": "Asymmetric Cryptography and Trapdoor Functions"},
    {"id": "09_05", "topic": "Hybrid Cryptography and Why Both Are Used"},
    {"id": "09_06", "topic": "Hash Functions, Collisions and Integrity"},
    {"id": "09_07", "topic": "Message Authentication Codes and Digital Signatures"},
    {"id": "09_08", "topic": "Public Key Infrastructure: CA, RA, CRL and OCSP"},
    {"id": "09_09", "topic": "Certificate Lifecycle and Trust Models"},
    {"id": "09_10", "topic": "Key Management: Generation, Escrow, Rotation and Destruction"},
    {"id": "09_11", "topic": "Cryptanalytic Attacks: Brute Force, Birthday and Chosen Plaintext"},
    {"id": "09_12", "topic": "Side-Channel, Fault Injection and Implementation Attacks"},
    {"id": "09_13", "topic": "Ransomware and Cryptography Used Against the Organisation"},
    {"id": "09_14", "topic": "Quantum Computing and Post-Quantum Considerations"},

    # -- 10: Physical and Environmental Security (D3) --
    {"id": "10_01", "topic": "Site and Facility Design Principles"},
    {"id": "10_02", "topic": "Crime Prevention Through Environmental Design (CPTED)"},
    {"id": "10_03", "topic": "Perimeter Controls: Fencing, Lighting, Bollards and Gates"},
    {"id": "10_04", "topic": "Interior Controls: Mantraps, Turnstiles and Badge Systems"},
    {"id": "10_05", "topic": "Data Centre and Wiring Closet Security"},
    {"id": "10_06", "topic": "Power: UPS, Generators, Brownouts and Surges"},
    {"id": "10_07", "topic": "HVAC, Humidity and Environmental Monitoring"},
    {"id": "10_08", "topic": "Fire Classes, Detection and Suppression Choices"},

    # -- 11: Vulnerabilities in Systems and Architectures (D3) --
    {"id": "11_01", "topic": "Client-Based and Server-Based System Vulnerabilities"},
    {"id": "11_02", "topic": "Database Vulnerabilities: Aggregation and Inference"},
    {"id": "11_03", "topic": "Virtualisation and Hypervisor Vulnerabilities"},
    {"id": "11_04", "topic": "Cloud Deployment Models and Their Risk Profiles"},
    {"id": "11_05", "topic": "IoT, ICS, SCADA and Embedded System Weaknesses"},
    {"id": "11_06", "topic": "Distributed Systems, Edge and Containerisation Risk"},

    # -- 12: Network Architecture and Protocols (D4) --
    {"id": "12_01", "topic": "The OSI Model as a Security Reasoning Tool"},
    {"id": "12_02", "topic": "TCP/IP Model and Protocol Layering Risk"},
    {"id": "12_03", "topic": "IPv4, IPv6 and Addressing Security Implications"},
    {"id": "12_04", "topic": "Secure Protocols Versus Their Insecure Predecessors"},
    {"id": "12_05", "topic": "DNS Security and DNSSEC"},
    {"id": "12_06", "topic": "Network Segmentation as a Risk Control"},
    {"id": "12_07", "topic": "VLANs, Subnetting and Microsegmentation"},
    {"id": "12_08", "topic": "Software-Defined Networking and Network Function Virtualisation"},
    {"id": "12_09", "topic": "Converged Protocols and Their Added Attack Surface"},
    {"id": "12_10", "topic": "Wireless Standards and Enterprise Wireless Security"},
    {"id": "12_11", "topic": "Cellular, Satellite and Li-Fi Considerations"},
    {"id": "12_12", "topic": "Content Distribution Networks and Edge Delivery"},
    {"id": "12_13", "topic": "Network Architecture Decisions From a Risk Standpoint"},

    # -- 13: Network Components and Attacks (D4) --
    {"id": "13_01", "topic": "Firewalls: Types, Placement and Limitations"},
    {"id": "13_02", "topic": "Proxies, Reverse Proxies and Gateways"},
    {"id": "13_03", "topic": "IDS and IPS Placement and Tuning"},
    {"id": "13_04", "topic": "Network Access Control and Endpoint Posture"},
    {"id": "13_05", "topic": "Transmission Media and Physical Interception Risk"},
    {"id": "13_06", "topic": "Denial of Service and Distributed Denial of Service"},
    {"id": "13_07", "topic": "On-Path Attacks and Session Hijacking"},
    {"id": "13_08", "topic": "Spoofing, Poisoning and Cache Attacks"},
    {"id": "13_09", "topic": "Wireless Attacks: Evil Twin, Deauthentication and Jamming"},
    {"id": "13_10", "topic": "Bluetooth, NFC and Proximity Attacks"},
    {"id": "13_11", "topic": "Covert Channels in Networks"},
    {"id": "13_12", "topic": "Network Monitoring and Traffic Analysis for Defence"},
    {"id": "13_13", "topic": "Selecting Network Controls That Match the Risk"},

    # -- 14: Secure Communication Channels (D4) --
    {"id": "14_01", "topic": "Designing Secure Voice and Collaboration Channels"},
    {"id": "14_02", "topic": "Email Security: Encryption, Signing and Gateway Controls"},
    {"id": "14_03", "topic": "Remote Access Architecture and Its Risks"},
    {"id": "14_04", "topic": "VPN Types: Site-to-Site and Remote Access"},
    {"id": "14_05", "topic": "IPsec: AH, ESP, Transport and Tunnel Modes"},
    {"id": "14_06", "topic": "TLS and What It Does and Does Not Protect"},
    {"id": "14_07", "topic": "Virtual Desktop Infrastructure and Remote Desktop Risk"},
    {"id": "14_08", "topic": "Third-Party Connectivity and Extranet Controls"},
    {"id": "14_09", "topic": "Multimedia Collaboration and Conferencing Security"},
    {"id": "14_10", "topic": "Data Communications in Multi-Cloud Environments"},
    {"id": "14_11", "topic": "Virtualised Networks and Their Trust Boundaries"},
    {"id": "14_12", "topic": "Zero Trust Network Access Compared to VPN"},

    # -- 15: Identity Management (D5) --
    {"id": "15_01", "topic": "Identification, Authentication and Authorisation Distinguished"},
    {"id": "15_02", "topic": "Identity Proofing and Registration"},
    {"id": "15_03", "topic": "Knowledge, Ownership and Characteristic Factors"},
    {"id": "15_04", "topic": "Multi-Factor Authentication Design Decisions"},
    {"id": "15_05", "topic": "Biometrics: FAR, FRR, CER and User Acceptance"},
    {"id": "15_06", "topic": "Password Policy, Storage and Attack Resistance"},
    {"id": "15_07", "topic": "Passwordless Authentication and FIDO2"},
    {"id": "15_08", "topic": "Session Management and Timeout Decisions"},
    {"id": "15_09", "topic": "Device Authentication and Machine Identity"},
    {"id": "15_10", "topic": "Service Accounts and Non-Human Identity"},
    {"id": "15_11", "topic": "Credential Management Systems and Vaults"},
    {"id": "15_12", "topic": "Just-in-Time and Privileged Access Management"},

    # -- 16: Access Control Models and Mechanisms (D5) --
    {"id": "16_01", "topic": "Discretionary Access Control and Its Weaknesses"},
    {"id": "16_02", "topic": "Mandatory Access Control and Labels"},
    {"id": "16_03", "topic": "Role-Based Access Control Design"},
    {"id": "16_04", "topic": "Rule-Based and Attribute-Based Access Control"},
    {"id": "16_05", "topic": "Risk-Based and Adaptive Access Control"},
    {"id": "16_06", "topic": "Access Control Matrices, Capability Tables and ACLs"},
    {"id": "16_07", "topic": "Choosing an Access Control Model for a Given Organisation"},
    {"id": "16_08", "topic": "Authorisation Creep and Access Review"},
    {"id": "16_09", "topic": "Segregation of Duties Enforced Through Access Control"},
    {"id": "16_10", "topic": "Access Control Attacks: Escalation and Credential Theft"},
    {"id": "16_11", "topic": "Physical and Logical Access Control Integration"},
    {"id": "16_12", "topic": "Accountability Through Audit Trails"},
    {"id": "16_13", "topic": "Managing the Access Control Lifecycle"},

    # -- 17: Federation and Identity Lifecycle (D5) --
    {"id": "17_01", "topic": "Single Sign-On Benefits and Concentrated Risk"},
    {"id": "17_02", "topic": "Kerberos: Tickets, KDC and Its Failure Modes"},
    {"id": "17_03", "topic": "SAML and Assertion-Based Federation"},
    {"id": "17_04", "topic": "OAuth 2.0 Versus OpenID Connect"},
    {"id": "17_05", "topic": "RADIUS, TACACS+ and Diameter"},
    {"id": "17_06", "topic": "Directory Services and LDAP"},
    {"id": "17_07", "topic": "Identity as a Service and Third-Party Identity"},
    {"id": "17_08", "topic": "Federated Trust Relationships and Their Risks"},
    {"id": "17_09", "topic": "Provisioning, Modification and Deprovisioning"},
    {"id": "17_10", "topic": "Account Access Review and Recertification"},
    {"id": "17_11", "topic": "Privileged Account Monitoring"},
    {"id": "17_12", "topic": "Identity Governance and Administration"},
    {"id": "17_13", "topic": "Orphaned Accounts and Offboarding Failures"},

    # -- 18: Assessment and Test Strategies (D6) --
    {"id": "18_01", "topic": "Designing an Assessment and Test Strategy"},
    {"id": "18_02", "topic": "Internal, External and Third-Party Assessments"},
    {"id": "18_03", "topic": "Assessment Scope, Rules of Engagement and Authorisation"},
    {"id": "18_04", "topic": "Audit Strategies for Regulated Environments"},
    {"id": "18_05", "topic": "Right to Audit and Evidence of Vendor Control"},
    {"id": "18_06", "topic": "SOC 1, SOC 2 and SOC 3 Reports"},
    {"id": "18_07", "topic": "Type I Versus Type II Reports"},
    {"id": "18_08", "topic": "Continuous Assessment Versus Point-in-Time Testing"},
    {"id": "18_09", "topic": "Assessment Frequency and Trigger Events"},
    {"id": "18_10", "topic": "Choosing What to Test With Limited Resources"},

    # -- 19: Security Testing Techniques (D6) --
    {"id": "19_01", "topic": "Vulnerability Assessment and Its Limits"},
    {"id": "19_02", "topic": "Penetration Testing Phases and Methodology"},
    {"id": "19_03", "topic": "Black Box, White Box and Grey Box Testing"},
    {"id": "19_04", "topic": "Red Team, Blue Team and Purple Team Exercises"},
    {"id": "19_05", "topic": "Log Review as a Testing Technique"},
    {"id": "19_06", "topic": "Synthetic Transactions and Real User Monitoring"},
    {"id": "19_07", "topic": "Code Review and Static Application Security Testing"},
    {"id": "19_08", "topic": "Dynamic Testing and Fuzzing"},
    {"id": "19_09", "topic": "Misuse Case Testing and Abuse Cases"},
    {"id": "19_10", "topic": "Test Coverage Analysis and Interface Testing"},
    {"id": "19_11", "topic": "Breach and Attack Simulation"},
    {"id": "19_12", "topic": "Compliance Checks and Configuration Verification"},
    {"id": "19_13", "topic": "Interpreting Results and Avoiding False Assurance"},

    # -- 20: Audit and Security Reporting (D6) --
    {"id": "20_01", "topic": "Collecting Security Process Data"},
    {"id": "20_02", "topic": "Account Management Metrics and Review Data"},
    {"id": "20_03", "topic": "Management Review and Approval Cycles"},
    {"id": "20_04", "topic": "Key Performance Indicators and Key Risk Indicators"},
    {"id": "20_05", "topic": "Backup Verification Data"},
    {"id": "20_06", "topic": "Training and Awareness Metrics"},
    {"id": "20_07", "topic": "Disaster Recovery and Continuity Metrics"},
    {"id": "20_08", "topic": "Writing Reports for Technical Versus Executive Audiences"},
    {"id": "20_09", "topic": "Remediation Tracking and Exception Handling"},
    {"id": "20_10", "topic": "Ethical Disclosure of Findings"},
    {"id": "20_11", "topic": "Audit Findings, Severity Rating and Follow-Up"},
    {"id": "20_12", "topic": "Presenting Risk to the Board"},

    # -- 21: Investigations and Digital Forensics (D7) --
    {"id": "21_01", "topic": "Evidence Types and Admissibility"},
    {"id": "21_02", "topic": "The Best Evidence Rule and Hearsay"},
    {"id": "21_03", "topic": "Chain of Custody and Its Documentation"},
    {"id": "21_04", "topic": "Evidence Collection and Order of Volatility"},
    {"id": "21_05", "topic": "Forensic Imaging and Write Blocking"},
    {"id": "21_06", "topic": "Media, Network and Software Forensics"},
    {"id": "21_07", "topic": "Artefact Analysis and Timeline Reconstruction"},
    {"id": "21_08", "topic": "E-Discovery and Electronic Records"},
    {"id": "21_09", "topic": "Reporting and Documenting Investigations"},
    {"id": "21_10", "topic": "Working With Law Enforcement and Legal Counsel"},

    # -- 22: Operational Controls and Logging (D7) --
    {"id": "22_01", "topic": "Need to Know and Least Privilege in Operations"},
    {"id": "22_02", "topic": "Privileged Account Operational Controls"},
    {"id": "22_03", "topic": "Configuration and Change Management in Operations"},
    {"id": "22_04", "topic": "Patch and Vulnerability Management Operations"},
    {"id": "22_05", "topic": "Resource Protection and Media Management"},
    {"id": "22_06", "topic": "Logging Strategy and What Must Be Logged"},
    {"id": "22_07", "topic": "Log Protection, Integrity and Retention"},
    {"id": "22_08", "topic": "SIEM, Correlation and Continuous Monitoring"},
    {"id": "22_09", "topic": "Egress Monitoring and Data Exfiltration Detection"},
    {"id": "22_10", "topic": "Threat Intelligence and Its Operational Use"},

    # -- 23: Incident Management (D7) --
    {"id": "23_01", "topic": "Incident Management Lifecycle Overview"},
    {"id": "23_02", "topic": "Detection and Triage"},
    {"id": "23_03", "topic": "Response, Escalation and Communication"},
    {"id": "23_04", "topic": "Mitigation and Containment Decisions"},
    {"id": "23_05", "topic": "Reporting Obligations and Notification Timing"},
    {"id": "23_06", "topic": "Recovery and Restoration of Service"},
    {"id": "23_07", "topic": "Remediation and Root Cause Analysis"},
    {"id": "23_08", "topic": "Lessons Learned and Feeding Back Into Controls"},
    {"id": "23_09", "topic": "Preventive Measures: Firewalls, Sandboxing and Anti-Malware"},

    # -- 24: Business Continuity and Disaster Recovery (D7) --
    {"id": "24_01", "topic": "Business Impact Analysis and Criticality Ranking"},
    {"id": "24_02", "topic": "MTD, RTO, RPO and Work Recovery Time"},
    {"id": "24_03", "topic": "Recovery Strategies and Their Cost Trade-Offs"},
    {"id": "24_04", "topic": "Alternate Sites: Hot, Warm, Cold, Mobile and Reciprocal"},
    {"id": "24_05", "topic": "Backup Strategy, Storage and Offsite Considerations"},
    {"id": "24_06", "topic": "System Resilience, Fault Tolerance and High Availability"},
    {"id": "24_07", "topic": "Disaster Recovery Plan Development and Maintenance"},
    {"id": "24_08", "topic": "DR Testing: Read-Through, Walkthrough, Simulation and Parallel"},
    {"id": "24_09", "topic": "Personnel Safety and Duty of Care During a Disaster"},

    # -- 25: Software Development Lifecycle Security (D8) --
    {"id": "25_01", "topic": "Security in the Software Development Lifecycle"},
    {"id": "25_02", "topic": "Waterfall, Spiral and Agile From a Security Standpoint"},
    {"id": "25_03", "topic": "DevOps and DevSecOps"},
    {"id": "25_04", "topic": "Maturity Models: CMMI and SAMM"},
    {"id": "25_05", "topic": "Requirements Gathering and Security Requirements"},
    {"id": "25_06", "topic": "Threat Modelling During Design"},
    {"id": "25_07", "topic": "Change Management in Development"},
    {"id": "25_08", "topic": "Integrated Product Teams and Shared Ownership"},
    {"id": "25_09", "topic": "Development Environment Security and Toolchain Risk"},
    {"id": "25_10", "topic": "Configuration Management and Versioning of Code"},

    # -- 26: Secure Coding and Application Controls (D8) --
    {"id": "26_01", "topic": "Secure Coding Standards and Guidelines"},
    {"id": "26_02", "topic": "Input Validation and Output Encoding"},
    {"id": "26_03", "topic": "Injection Flaws and How They Are Prevented"},
    {"id": "26_04", "topic": "Cross-Site Scripting and Request Forgery"},
    {"id": "26_05", "topic": "Buffer Overflow and Memory Safety"},
    {"id": "26_06", "topic": "Race Conditions and TOC/TOU"},
    {"id": "26_07", "topic": "Error Handling, Logging and Information Disclosure"},
    {"id": "26_08", "topic": "Authentication and Session Handling in Applications"},
    {"id": "26_09", "topic": "API Security and Service-Oriented Architecture"},
    {"id": "26_10", "topic": "Database Security: Concurrency, Integrity and Views"},

    # -- 27: Software Security Assessment (D8) --
    {"id": "27_01", "topic": "Auditing and Logging of Code Changes"},
    {"id": "27_02", "topic": "Risk Analysis and Mitigation in Software"},
    {"id": "27_03", "topic": "Assessing the Security of Acquired Software"},
    {"id": "27_04", "topic": "Commercial Off-the-Shelf and Open Source Risk"},
    {"id": "27_05", "topic": "Third-Party and Outsourced Development Controls"},
    {"id": "27_06", "topic": "Software Composition Analysis and Dependency Risk"},
    {"id": "27_07", "topic": "Software Escrow and Vendor Failure Planning"},
    {"id": "27_08", "topic": "Malicious Code and Application Attack Recognition"},
    {"id": "27_09", "topic": "Secure Software Deployment and Runtime Protection"},
]

# CISSP is explicitly a management exam: the candidate is asked what a
# security leader should do, and the MOST/BEST/FIRST qualifier is usually what
# separates the correct answer from three technically-plausible ones.
_PERSONA = (
    "ตอบในมุมของผู้บริหาร/ที่ปรึกษาความมั่นคงปลอดภัย (manager, CEO หรือ owner) ที่ต้องตัดสินใจเพื่อ "
    "'ลดความเสี่ยงให้องค์กรอย่างคุ้มค่าที่สุด' ไม่ใช่มุมช่างเทคนิคที่เลือกทางที่ลึกที่สุด "
    "เมื่อมีหลายทางที่ถูกทางเทคนิค ให้ชี้ว่าทางไหนคือทางที่ CISSP ควรเลือกและเพราะอะไร"
)

_WORKED_EXAMPLE = (
    "สถานการณ์จำลองระดับผู้บริหาร (management scenario) อย่างน้อย 1 สถานการณ์เต็ม — "
    "ตั้งสถานการณ์ที่ต้องเลือกระหว่างตัวเลือกที่เป็นไปได้จริง 2-3 ทาง แล้วอธิบายว่าทางไหนคือคำตอบที่ CISSP "
    "ควรเลือกและเพราะอะไร (มองจากมุมลดความเสี่ยงให้องค์กรอย่างคุ้มค่า ไม่ใช่มุมเทคนิคล้วน) "
    "ถ้าหัวข้อมีตัวเลขหรือสูตรคำนวณ (เช่น ALE, RTO/RPO, CVSS) ให้ใส่ตัวอย่างคำนวณจริงพร้อมค่าจำลองทีละขั้นแทน"
)

_EXAM_WORDING = (
    "โดยเฉพาะคำที่ข้อสอบมักใช้ (MOST, BEST, FIRST) เทียบกับตัวเลือกอื่นที่ดูถูกแต่ไม่ใช่คำตอบที่ดีที่สุด "
    "และลำดับก่อนหลังที่ข้อสอบชอบถาม (เช่น ต้องทำอะไรก่อนเสมอ)"
)

_COMPARE_HINT = (
    "เน้นเทียบว่าในสถานการณ์ไหนควรเลือกแนวคิดไหน และเพราะเหตุผลเชิงบริหารความเสี่ยงอะไร"
)


def SLIDE_INSTRUCTIONS(topic: str) -> str:
    return security_slide_instructions(
        EXAM_NAME, topic,
        persona=_PERSONA,
        worked_example=_WORKED_EXAMPLE,
        exam_wording=_EXAM_WORDING,
    )


def SUMMARY_PROMPT(topic: str) -> str:
    return security_summary_prompt(
        EXAM_NAME, topic,
        persona=_PERSONA,
        worked_example=_WORKED_EXAMPLE,
        exam_wording=_EXAM_WORDING,
        compare_hint=_COMPARE_HINT,
    )
