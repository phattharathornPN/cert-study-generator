# -*- coding: utf-8 -*-
"""Security certification pack: ISC2 CC, CompTIA Security+ SY0-701 and ISC2 CISSP.

One pack, not three. The three exams are largely nested -- almost everything
CC tests is tested again by Security+, and almost everything Security+ tests
is tested again by CISSP at greater depth. Generating them separately would
produce three near-identical summaries of the CIA triad, three of RBAC, three
of PKI, and would triple a slide backlog that is already the bottleneck.

So each mechanism is taught once, at the depth the *hardest* exam needs
(CISSP: what a security leader decides), which subsumes what the other two
ask. Topics that only one exam reaches -- CISSP's formal security models and
legal depth, Security+'s tooling acronyms -- are simply included; a CC
candidate can stop at the sections they need.

Blueprint coverage this pack is built against:

  CC (refreshed outline effective 2026-09-01)
      Security Principles 26% | BC/DR/IR 10% | Access Controls 22%
      Network Security 24% | Security Operations 18%   -- AI folded throughout
  Security+ SY0-701 (SY0-801 previews ~2026-10-20, same five-domain shape)
      General Concepts 12% | Threats/Vulns/Mitigations 22% | Architecture 18%
      Operations 28% | Program Management and Oversight 20%
  CISSP (exam outline effective 2024-04-15, still current)
      1 Security and Risk Management 16% | 2 Asset Security 10%
      3 Security Architecture and Engineering 13% | 4 Comms and Network 13%
      5 IAM 13% | 6 Assessment and Testing 12% | 7 Operations 13%
      8 Software Development Security 10%

Design rules, same as the other packs here: one topic teaches one mechanism,
no title carries a list, and sections run in teaching order -- concepts before
controls, controls before operations, operations before assessment.

Only slide.pdf is downloaded: the reader site uses the PDF, so generating
.pptx would double the time and disk for a file nothing reads.
"""

EXAM_NAME = "Security: CC + Security+ SY0-701 + CISSP"
OUTPUT_DIR = "security/output"
SITE_DIR = "security"      # index.html sits beside its own output/
DIST_DIR = "security/dist"
NOTEBOOK_ENV = "NOTEBOOK_ID_SECURITY"
SLIDE_FORMATS = ("pdf",)

SECTION_TITLES = {
    "01": "Core Security Concepts",
    "02": "Security Governance",
    "03": "Legal, Regulatory and Privacy",
    "04": "Risk Management",
    "05": "Third-Party and Supply Chain Risk",
    "06": "Security Control Types",
    "07": "Personnel Security and Awareness",
    "08": "Business Continuity and Disaster Recovery",
    "09": "Asset Management and Classification",
    "10": "Data Protection and Lifecycle",
    "11": "Cryptography Fundamentals",
    "12": "Applied Cryptography and PKI",
    "13": "Physical and Environmental Security",
    "14": "Network Fundamentals",
    "15": "Network Attacks",
    "16": "Network Defence and Segmentation",
    "17": "Secure Architecture and Cloud",
    "18": "Systems, Virtualisation and Endpoints",
    "19": "Identity Management",
    "20": "Access Control and Federation",
    "21": "Threat Actors and Attack Surfaces",
    "22": "Vulnerabilities, Malware and Indicators",
    "23": "Secure Baselines and Hardening",
    "24": "Vulnerability and Patch Management",
    "25": "Monitoring, Logging and SIEM",
    "26": "Security Assessment and Testing",
    "27": "Incident Response",
    "28": "Digital Forensics and Investigations",
    "29": "Secure Software Development",
    "30": "Application Security Controls",
    "31": "Automation and Orchestration",
    "32": "AI Security",
}

TOPICS = [
    # -- 01: Core Security Concepts (all three exams) --
    {"id": "01_01", "topic": "Confidentiality: What It Protects and How It Fails"},
    {"id": "01_02", "topic": "Integrity: Detecting and Preventing Unauthorised Change"},
    {"id": "01_03", "topic": "Availability: Uptime as a Security Property"},
    {"id": "01_04", "topic": "Identification and Authentication as Separate Steps"},
    {"id": "01_05", "topic": "The Three Authentication Factors and Why They Differ"},
    {"id": "01_06", "topic": "Authorisation: Deciding What an Identity May Do"},
    {"id": "01_07", "topic": "Accounting, Auditability and Accountability"},
    {"id": "01_08", "topic": "Non-Repudiation and Its Technical Basis"},
    {"id": "01_09", "topic": "Authenticity and Trust in Security Design"},
    {"id": "01_10", "topic": "Privacy as Distinct from Confidentiality"},
    {"id": "01_11", "topic": "Defence in Depth and Layered Controls"},
    {"id": "01_12", "topic": "Least Privilege and Need to Know"},
    {"id": "01_13", "topic": "Separation of Duties, Job Rotation and Mandatory Vacation"},
    {"id": "01_14", "topic": "Fail Securely, Secure Defaults and Economy of Mechanism"},
    {"id": "01_15", "topic": "Zero Trust: Never Trust, Always Verify"},
    {"id": "01_16", "topic": "Zero Trust Planes: Policy Engine, Administrator and Enforcement Point"},
    {"id": "01_17", "topic": "Adaptive Identity and Implicit Trust Zones"},

    # -- 02: Security Governance (CISSP D1, Sec+ D5) --
    {"id": "02_01", "topic": "Security Governance and Alignment to Business Strategy"},
    {"id": "02_02", "topic": "Policies, Standards, Baselines, Guidelines and Procedures"},
    {"id": "02_03", "topic": "Acceptable Use Policy and What It Must Cover"},
    {"id": "02_04", "topic": "Governance Structures: Boards, Committees and Steering Groups"},
    {"id": "02_05", "topic": "Organisational Roles: Owner, Custodian, Processor and User"},
    {"id": "02_06", "topic": "Due Care versus Due Diligence"},
    {"id": "02_07", "topic": "Control Frameworks: ISO 27001, NIST CSF and COBIT"},
    {"id": "02_08", "topic": "Gap Analysis and Measuring Against a Standard"},
    {"id": "02_09", "topic": "The ISC2 Code of Professional Ethics"},
    {"id": "02_10", "topic": "Organisational Ethics and Conflict of Interest"},
    {"id": "02_11", "topic": "Change Management: Approval, Ownership and Stakeholders"},
    {"id": "02_12", "topic": "Impact Analysis, Test Results and Backout Plans"},
    {"id": "02_13", "topic": "Maintenance Windows and Standard Operating Procedures"},
    {"id": "02_14", "topic": "Version Control and Documentation of Change"},

    # -- 03: Legal, Regulatory and Privacy (CISSP D1, Sec+ D5) --
    {"id": "03_01", "topic": "Criminal, Civil, Administrative and Regulatory Law"},
    {"id": "03_02", "topic": "Intellectual Property: Patent, Copyright, Trademark and Trade Secret"},
    {"id": "03_03", "topic": "Licensing, Import and Export Controls"},
    {"id": "03_04", "topic": "Transborder Data Flow and Data Localisation"},
    {"id": "03_05", "topic": "GDPR Principles and Data Subject Rights"},
    {"id": "03_06", "topic": "HIPAA, PCI DSS, SOX and GLBA Obligations"},
    {"id": "03_07", "topic": "Computer Crime Law and Breach Notification"},
    {"id": "03_08", "topic": "Compliance Reporting: Internal and External"},
    {"id": "03_09", "topic": "Consequences of Non-Compliance: Fines, Sanctions and Licence Loss"},
    {"id": "03_10", "topic": "Attestation, Acknowledgement and Compliance Monitoring"},

    # -- 04: Risk Management (all three) --
    {"id": "04_01", "topic": "Assets, Threats, Vulnerabilities and Exposure Defined"},
    {"id": "04_02", "topic": "Asset Valuation as the Basis of Risk"},
    {"id": "04_03", "topic": "How Likelihood and Impact Combine into Risk"},
    {"id": "04_04", "topic": "Risk Identification and the Risk Register"},
    {"id": "04_05", "topic": "Key Risk Indicators, Risk Owners and Risk Threshold"},
    {"id": "04_06", "topic": "Qualitative Risk Analysis and Risk Matrices"},
    {"id": "04_07", "topic": "Quantitative Risk Analysis: AV, EF, SLE, ARO and ALE"},
    {"id": "04_08", "topic": "Risk Treatment: Mitigate, Transfer, Avoid and Accept"},
    {"id": "04_09", "topic": "Residual Risk, Risk Appetite and Risk Tolerance"},
    {"id": "04_10", "topic": "Countermeasure Selection and Total Cost of Ownership"},
    {"id": "04_11", "topic": "Continuous Monitoring and Risk Reporting"},
    {"id": "04_12", "topic": "Risk Frameworks: NIST RMF and ISO 27005"},
    {"id": "04_13", "topic": "Threat Modelling: STRIDE, PASTA and DREAD"},

    # -- 05: Third-Party and Supply Chain Risk (CISSP D1, Sec+ D5) --
    {"id": "05_01", "topic": "Supply Chain Risk and Where It Enters"},
    {"id": "05_02", "topic": "Vendor Selection, Due Diligence and Questionnaires"},
    {"id": "05_03", "topic": "Right to Audit, Penetration Testing and Evidence of Control"},
    {"id": "05_04", "topic": "Agreements: SLA, MOU, MSA, SOW, NDA and BPA"},
    {"id": "05_05", "topic": "Ongoing Vendor Monitoring and Offboarding"},
    {"id": "05_06", "topic": "SOC 1, SOC 2 and SOC 3 Reports"},

    # -- 06: Security Control Types (all three) --
    {"id": "06_01", "topic": "Control Categories: Technical, Managerial, Operational and Physical"},
    {"id": "06_02", "topic": "Preventive, Detective and Corrective Controls"},
    {"id": "06_03", "topic": "Deterrent, Directive and Compensating Controls"},
    {"id": "06_04", "topic": "Control Selection, Scoping and Tailoring"},
    {"id": "06_05", "topic": "Honeypots, Honeynets, Honeyfiles and Honeytokens"},

    # -- 07: Personnel Security and Awareness (CISSP D1, Sec+ D5, CC D1) --
    {"id": "07_01", "topic": "Candidate Screening, Background Checks and Onboarding"},
    {"id": "07_02", "topic": "Employment Agreements and Policy Acknowledgement"},
    {"id": "07_03", "topic": "Transfers, Termination and Offboarding Controls"},
    {"id": "07_04", "topic": "Contractor, Consultant and Vendor Personnel Controls"},
    {"id": "07_05", "topic": "Security Awareness, Training and Education Compared"},
    {"id": "07_06", "topic": "Phishing Simulation Campaigns and Recognising Attacks"},
    {"id": "07_07", "topic": "Anomalous Behaviour Recognition and Reporting"},
    {"id": "07_08", "topic": "Role-Based Training and Programme Effectiveness Metrics"},

    # -- 08: Business Continuity and Disaster Recovery (all three) --
    {"id": "08_01", "topic": "Business Continuity versus Disaster Recovery"},
    {"id": "08_02", "topic": "Business Impact Analysis and Critical Function Ranking"},
    {"id": "08_03", "topic": "MTD, RTO, RPO and Work Recovery Time"},
    {"id": "08_04", "topic": "MTBF, MTTR and Availability Targets"},
    {"id": "08_05", "topic": "Backup Types: Full, Incremental and Differential"},
    {"id": "08_06", "topic": "Backup Strategy: 3-2-1, Offsite Storage and Encryption"},
    {"id": "08_07", "topic": "Snapshots, Replication, Journaling and Electronic Vaulting"},
    {"id": "08_08", "topic": "Hot, Warm and Cold Recovery Sites"},
    {"id": "08_09", "topic": "Geographic Dispersion and Multiple Processing Sites"},
    {"id": "08_10", "topic": "High Availability, Clustering and Load Balancing"},
    {"id": "08_11", "topic": "Power Resilience: UPS, Generators and Capacity Planning"},
    {"id": "08_12", "topic": "Plan Testing: Read-Through, Tabletop, Simulation and Full Interruption"},
    {"id": "08_13", "topic": "Restoration Order and Returning to Normal Operations"},
    {"id": "08_14", "topic": "Plan Approval, Distribution and Maintenance"},

    # -- 09: Asset Management and Classification (CISSP D2, Sec+ D4) --
    {"id": "09_01", "topic": "Identifying and Inventorying Information Assets"},
    {"id": "09_02", "topic": "Classification Schemes: Government and Commercial"},
    {"id": "09_03", "topic": "Labelling, Marking and Handling Requirements"},
    {"id": "09_04", "topic": "Asset Ownership, Assignment and Accountability"},
    {"id": "09_05", "topic": "Tangible and Intangible Asset Valuation"},
    {"id": "09_06", "topic": "Acquisition, Provisioning and Asset Tracking"},
    {"id": "09_07", "topic": "Decommissioning, Disposal and Certification of Destruction"},

    # -- 10: Data Protection and Lifecycle (all three) --
    {"id": "10_01", "topic": "The Data Lifecycle from Creation to Destruction"},
    {"id": "10_02", "topic": "Data Roles: Owner, Controller, Processor, Custodian and Subject"},
    {"id": "10_03", "topic": "Data Types: PII, PHI, Financial and Intellectual Property"},
    {"id": "10_04", "topic": "Data at Rest, In Transit and In Use"},
    {"id": "10_05", "topic": "Data Sovereignty and Geolocation Requirements"},
    {"id": "10_06", "topic": "Data Retention Policy and Legal Hold"},
    {"id": "10_07", "topic": "Data Remanence and Media Sanitisation"},
    {"id": "10_08", "topic": "Clearing, Purging, Degaussing and Physical Destruction"},
    {"id": "10_09", "topic": "Data Loss Prevention Deployment and Policy"},
    {"id": "10_10", "topic": "Obfuscation: Tokenisation, Masking and Steganography"},
    {"id": "10_11", "topic": "Digital Rights Management"},

    # -- 11: Cryptography Fundamentals (all three) --
    {"id": "11_01", "topic": "Cryptographic Goals and the Cryptosystem Lifecycle"},
    {"id": "11_02", "topic": "Symmetric Encryption and the Key Distribution Problem"},
    {"id": "11_03", "topic": "Symmetric Algorithms: DES, 3DES and AES"},
    {"id": "11_04", "topic": "Block Cipher Modes and Initialisation Vectors"},
    {"id": "11_05", "topic": "Stream Ciphers and Key Stream Reuse"},
    {"id": "11_06", "topic": "Asymmetric Encryption and the Key Pair"},
    {"id": "11_07", "topic": "Asymmetric Algorithms: RSA, ECC and Diffie-Hellman"},
    {"id": "11_08", "topic": "Hybrid Cryptography and Session Key Exchange"},
    {"id": "11_09", "topic": "Perfect Forward Secrecy"},
    {"id": "11_10", "topic": "Hash Functions and Collision Resistance"},
    {"id": "11_11", "topic": "Salting, Key Stretching and Password Storage"},
    {"id": "11_12", "topic": "Message Authentication Codes and HMAC"},
    {"id": "11_13", "topic": "Digital Signatures: Signing versus Encrypting"},
    {"id": "11_14", "topic": "Key Length and What Actually Makes a Cipher Strong"},

    # -- 12: Applied Cryptography and PKI (all three) --
    {"id": "12_01", "topic": "Certificate Authorities and the Chain of Trust"},
    {"id": "12_02", "topic": "Root of Trust, Intermediate CAs and Cross-Certification"},
    {"id": "12_03", "topic": "Certificate Signing Requests and Enrolment"},
    {"id": "12_04", "topic": "Certificate Revocation Lists and OCSP Stapling"},
    {"id": "12_05", "topic": "Wildcard, SAN and Self-Signed Certificates"},
    {"id": "12_06", "topic": "Key Management: Generation, Escrow, Rotation and Destruction"},
    {"id": "12_07", "topic": "Trusted Platform Modules and Hardware Security Modules"},
    {"id": "12_08", "topic": "Secure Enclaves and Key Management Systems"},
    {"id": "12_09", "topic": "Full-Disk, Volume, File and Database Encryption"},
    {"id": "12_10", "topic": "Transport Encryption and TLS Handshake Security"},
    {"id": "12_11", "topic": "Cryptanalytic Attacks: Brute Force, Birthday and Side Channel"},
    {"id": "12_12", "topic": "Downgrade Attacks and Deprecated Algorithms"},
    {"id": "12_13", "topic": "Blockchain and the Open Public Ledger"},
    {"id": "12_14", "topic": "Quantum Computing and Post-Quantum Cryptography"},

    # -- 13: Physical and Environmental Security (all three) --
    {"id": "13_01", "topic": "Site and Facility Design: CPTED Principles"},
    {"id": "13_02", "topic": "Perimeter Defence: Fences, Bollards, Lighting and Signage"},
    {"id": "13_03", "topic": "Secure Areas: Wiring Closets, Server Rooms and Vaults"},
    {"id": "13_04", "topic": "Badge Systems, Turnstiles and Access Vestibules"},
    {"id": "13_05", "topic": "Tailgating and Piggybacking as Attack Techniques"},
    {"id": "13_06", "topic": "Locks, Guards, Surveillance and Alarm Systems"},
    {"id": "13_07", "topic": "Sensors: Infrared, Pressure, Microwave and Ultrasonic"},
    {"id": "13_08", "topic": "Power Problems: Brownouts, Surges, Sags and Blackouts"},
    {"id": "13_09", "topic": "HVAC, Humidity and Environmental Monitoring"},
    {"id": "13_10", "topic": "Fire Detection, Fire Classes and Suppression Agents"},
    {"id": "13_11", "topic": "Personnel Safety as the Overriding Priority"},

    # -- 14: Network Fundamentals (CC D4, Sec+ D3, CISSP D4) --
    {"id": "14_01", "topic": "The OSI Model as a Security Reference"},
    {"id": "14_02", "topic": "The TCP/IP Model and Protocol Weaknesses"},
    {"id": "14_03", "topic": "IP Addressing, Subnets and Private Address Space"},
    {"id": "14_04", "topic": "IPv6 Addressing and Its Security Implications"},
    {"id": "14_05", "topic": "TCP versus UDP and the Three-Way Handshake"},
    {"id": "14_06", "topic": "Ports and Services You Must Recognise"},
    {"id": "14_07", "topic": "DNS Resolution and Where It Is Abused"},
    {"id": "14_08", "topic": "DNSSEC and Protecting Name Resolution"},
    {"id": "14_09", "topic": "DHCP and the Risk of Rogue Servers"},
    {"id": "14_10", "topic": "Transmission Media: Copper, Fibre and Interference"},
    {"id": "14_11", "topic": "Wireless Standards and Terminology"},
    {"id": "14_12", "topic": "Bluetooth, Zigbee, NFC and Cellular Security"},
    {"id": "14_13", "topic": "Converged Protocols: FCoE, iSCSI and VoIP"},
    {"id": "14_14", "topic": "Content Distribution Networks and Edge Caching"},

    # -- 15: Network Attacks (all three) --
    {"id": "15_01", "topic": "Denial of Service, Distributed DoS and Amplification"},
    {"id": "15_02", "topic": "On-Path (Man-in-the-Middle) Attacks"},
    {"id": "15_03", "topic": "Spoofing: MAC, IP and ARP"},
    {"id": "15_04", "topic": "DNS Poisoning, Hijacking and Domain Fronting"},
    {"id": "15_05", "topic": "Session Hijacking and Replay Attacks"},
    {"id": "15_06", "topic": "Eavesdropping, Sniffing and Traffic Analysis"},
    {"id": "15_07", "topic": "Wireless Attacks: Evil Twin, Rogue AP and Deauthentication"},
    {"id": "15_08", "topic": "VLAN Hopping and Switch Attacks"},
    {"id": "15_09", "topic": "Covert Channels and Data Exfiltration Paths"},

    # -- 16: Network Defence and Segmentation (all three) --
    {"id": "16_01", "topic": "Firewalls: Packet Filter, Stateful and Proxy"},
    {"id": "16_02", "topic": "Next-Generation Firewalls and Layer 7 Inspection"},
    {"id": "16_03", "topic": "Web Application Firewalls and Unified Threat Management"},
    {"id": "16_04", "topic": "Intrusion Detection versus Intrusion Prevention"},
    {"id": "16_05", "topic": "Sensor Placement: Inline versus Tap, Active versus Passive"},
    {"id": "16_06", "topic": "Fail-Open versus Fail-Closed Device Behaviour"},
    {"id": "16_07", "topic": "Network Segmentation, Security Zones and Screened Subnets"},
    {"id": "16_08", "topic": "VLANs and Microsegmentation as Controls"},
    {"id": "16_09", "topic": "Air Gaps and Physical Isolation"},
    {"id": "16_10", "topic": "Network Access Control and Device Posture"},
    {"id": "16_11", "topic": "Port Security, 802.1X and EAP Methods"},
    {"id": "16_12", "topic": "Jump Servers, Bastion Hosts and Proxy Servers"},
    {"id": "16_13", "topic": "VPN Types: Remote Access, Site-to-Site and Always-On"},
    {"id": "16_14", "topic": "IPsec Modes and What a Tunnel Actually Protects"},
    {"id": "16_15", "topic": "Split Tunnelling and Remote Access Risk"},
    {"id": "16_16", "topic": "Wireless Security: WPA2, WPA3 and Enterprise Authentication"},
    {"id": "16_17", "topic": "Secure Access Service Edge and SD-WAN"},
    {"id": "16_18", "topic": "Email Security: SPF, DKIM and DMARC"},
    {"id": "16_19", "topic": "Email Gateways, Filtering and Attachment Inspection"},
    {"id": "16_20", "topic": "URL, Content and DNS Filtering"},

    # -- 17: Secure Architecture and Cloud (Sec+ D3, CISSP D3) --
    {"id": "17_01", "topic": "On-Premises, Cloud and Hybrid Trade-Offs"},
    {"id": "17_02", "topic": "Cloud Service Models and the Shared Responsibility Model"},
    {"id": "17_03", "topic": "Cloud Deployment Models: Public, Private, Community and Hybrid"},
    {"id": "17_04", "topic": "Cloud-Specific Vulnerabilities and Misconfiguration"},
    {"id": "17_05", "topic": "Infrastructure as Code and Serverless Architecture"},
    {"id": "17_06", "topic": "Microservices and the Attack Surface They Create"},
    {"id": "17_07", "topic": "Software-Defined Networking and Centralised Control"},
    {"id": "17_08", "topic": "Distributed Systems, Edge and Fog Computing Risk"},
    {"id": "17_09", "topic": "Industrial Control Systems, SCADA and Embedded Devices"},
    {"id": "17_10", "topic": "Internet of Things and Constrained Device Security"},
    {"id": "17_11", "topic": "Real-Time Operating Systems and Availability Constraints"},
    {"id": "17_12", "topic": "Architecture Trade-Offs: Cost, Scalability and Patch Availability"},

    # -- 18: Systems, Virtualisation and Endpoints (Sec+ D3/D4, CISSP D3) --
    {"id": "18_01", "topic": "CPU Modes, Protection Rings and Process Isolation"},
    {"id": "18_02", "topic": "Memory Protection and Address Space Layout Randomisation"},
    {"id": "18_03", "topic": "The Trusted Computing Base and Reference Monitor"},
    {"id": "18_04", "topic": "Secure Boot, Measured Boot and Hardware Root of Trust"},
    {"id": "18_05", "topic": "Hypervisor Types and Virtual Machine Escape"},
    {"id": "18_06", "topic": "Container Security and Resource Reuse"},
    {"id": "18_07", "topic": "Database Security: Aggregation, Inference and Polyinstantiation"},
    {"id": "18_08", "topic": "Mobile Deployment Models: BYOD, COPE and CYOD"},
    {"id": "18_09", "topic": "Mobile Device Management and Connection Methods"},
    {"id": "18_10", "topic": "Mobile Threats: Sideloading, Jailbreaking and Rooting"},
    {"id": "18_11", "topic": "Endpoint Protection, Antimalware and EDR"},
    {"id": "18_12", "topic": "Host-Based Firewalls and Host-Based IPS"},
    {"id": "18_13", "topic": "File Integrity Monitoring"},

    # -- 19: Identity Management (all three) --
    {"id": "19_01", "topic": "Identity Proofing and Registration"},
    {"id": "19_02", "topic": "Provisioning, Review and Deprovisioning of Accounts"},
    {"id": "19_03", "topic": "Password Policy: Length, Complexity and Rotation"},
    {"id": "19_04", "topic": "Password Managers and Passwordless Authentication"},
    {"id": "19_05", "topic": "Password Attacks: Brute Force, Spraying and Dictionary"},
    {"id": "19_06", "topic": "Biometrics: FAR, FRR and Crossover Error Rate"},
    {"id": "19_07", "topic": "Hard Tokens, Soft Tokens and Security Keys"},
    {"id": "19_08", "topic": "One-Time Passwords: HOTP and TOTP"},
    {"id": "19_09", "topic": "Multi-Factor and Adaptive Authentication"},
    {"id": "19_10", "topic": "Session Management, Timeouts and Session Attacks"},
    {"id": "19_11", "topic": "Privileged Access Management and Just-in-Time Access"},
    {"id": "19_12", "topic": "Service Accounts and Machine Identity"},
    {"id": "19_13", "topic": "Directory Services: LDAP and Active Directory"},

    # -- 20: Access Control and Federation (all three) --
    {"id": "20_01", "topic": "Subjects, Objects and Access Rules"},
    {"id": "20_02", "topic": "Discretionary Access Control"},
    {"id": "20_03", "topic": "Mandatory Access Control and Security Labels"},
    {"id": "20_04", "topic": "Role-Based Access Control"},
    {"id": "20_05", "topic": "Rule-Based and Time-of-Day Restrictions"},
    {"id": "20_06", "topic": "Attribute-Based and Risk-Based Access Control"},
    {"id": "20_07", "topic": "Access Control Matrices, Capability Tables and ACLs"},
    {"id": "20_08", "topic": "Single Sign-On and Its Risks"},
    {"id": "20_09", "topic": "Kerberos: Tickets, KDC and Known Weaknesses"},
    {"id": "20_10", "topic": "SAML and Federated Identity"},
    {"id": "20_11", "topic": "OAuth 2.0 and OpenID Connect"},
    {"id": "20_12", "topic": "RADIUS, TACACS+ and Diameter"},
    {"id": "20_13", "topic": "Access Review, Recertification and Entitlement Creep"},
    {"id": "20_14", "topic": "Formal Models: Bell-LaPadula and Biba"},
    {"id": "20_15", "topic": "Formal Models: Clark-Wilson and Brewer-Nash"},

    # -- 21: Threat Actors and Attack Surfaces (Sec+ D2, CC D1) --
    {"id": "21_01", "topic": "Nation-State Actors and Advanced Persistent Threats"},
    {"id": "21_02", "topic": "Organised Crime, Hacktivists and Unskilled Attackers"},
    {"id": "21_03", "topic": "Insider Threats, Intentional and Accidental"},
    {"id": "21_04", "topic": "Shadow IT and Unmanaged Assets"},
    {"id": "21_05", "topic": "Actor Attributes: Resources, Sophistication and Motivation"},
    {"id": "21_06", "topic": "Message Vectors: Email, SMS, Instant Message and Voice"},
    {"id": "21_07", "topic": "Removable Media and Malicious USB Devices"},
    {"id": "21_08", "topic": "Open Ports, Default Credentials and Unsecure Networks"},
    {"id": "21_09", "topic": "Phishing, Spear Phishing, Vishing and Smishing"},
    {"id": "21_10", "topic": "Business Email Compromise and Watering Hole Attacks"},
    {"id": "21_11", "topic": "Pretexting, Impersonation and Typosquatting"},
    {"id": "21_12", "topic": "Why Social Engineering Works: Authority, Urgency and Scarcity"},

    # -- 22: Vulnerabilities, Malware and Indicators (Sec+ D2) --
    {"id": "22_01", "topic": "Zero-Day Vulnerabilities and Why They Are Different"},
    {"id": "22_02", "topic": "Unsupported Systems, Legacy Hardware and End of Life"},
    {"id": "22_03", "topic": "Memory Injection and Buffer Overflow"},
    {"id": "22_04", "topic": "Race Conditions: Time of Check and Time of Use"},
    {"id": "22_05", "topic": "Malware Families: Virus, Worm, Trojan and Rootkit"},
    {"id": "22_06", "topic": "Ransomware: How It Spreads and How to Survive It"},
    {"id": "22_07", "topic": "Spyware, Bloatware, Logic Bombs and Keyloggers"},
    {"id": "22_08", "topic": "Privilege Escalation and Credential Replay"},
    {"id": "22_09", "topic": "Indicators: Account Lockouts, Impossible Travel and Concurrent Sessions"},
    {"id": "22_10", "topic": "Indicators: Resource Consumption, Blocked Content and Missing Logs"},
    {"id": "22_11", "topic": "Mitigation Techniques: Isolation, Allow Lists and Configuration Enforcement"},

    # -- 23: Secure Baselines and Hardening (Sec+ D4, CISSP D7) --
    {"id": "23_01", "topic": "Establishing, Deploying and Maintaining a Secure Baseline"},
    {"id": "23_02", "topic": "Hardening Workstations and Servers"},
    {"id": "23_03", "topic": "Hardening Switches, Routers and Network Appliances"},
    {"id": "23_04", "topic": "Hardening ICS, SCADA, Embedded and IoT Devices"},
    {"id": "23_05", "topic": "Operating System Security: Group Policy and SELinux"},
    {"id": "23_06", "topic": "Secure Protocol Selection and Insecure Protocol Removal"},
    {"id": "23_07", "topic": "Wireless Installation: Site Surveys and Heat Maps"},
    {"id": "23_08", "topic": "Configuration Management and Drift Detection"},

    # -- 24: Vulnerability and Patch Management (Sec+ D4, CISSP D7) --
    {"id": "24_01", "topic": "The Vulnerability Management Lifecycle"},
    {"id": "24_02", "topic": "Credentialed versus Non-Credentialed Scanning"},
    {"id": "24_03", "topic": "CVSS Scoring and the CVE Database"},
    {"id": "24_04", "topic": "False Positives, False Negatives and Confirmation"},
    {"id": "24_05", "topic": "Prioritisation by Exposure, Exploitability and Risk Tolerance"},
    {"id": "24_06", "topic": "Patch Management and Emergency Patching"},
    {"id": "24_07", "topic": "Compensating Controls When Patching Is Impossible"},
    {"id": "24_08", "topic": "Validation of Remediation and Rescanning"},
    {"id": "24_09", "topic": "Threat Feeds, OSINT and Dark Web Monitoring"},
    {"id": "24_10", "topic": "Package Monitoring and Software Bill of Materials"},
    {"id": "24_11", "topic": "Bug Bounties and Responsible Disclosure"},

    # -- 25: Monitoring, Logging and SIEM (all three) --
    {"id": "25_01", "topic": "What to Monitor: Systems, Applications and Infrastructure"},
    {"id": "25_02", "topic": "What Belongs in a Log and What Must Never"},
    {"id": "25_03", "topic": "Log Aggregation, Protection and Retention"},
    {"id": "25_04", "topic": "SIEM Architecture and Correlation Rules"},
    {"id": "25_05", "topic": "Alerting, Alert Tuning and Alert Fatigue"},
    {"id": "25_06", "topic": "Quarantine and Automated Alert Response"},
    {"id": "25_07", "topic": "SNMP Traps, NetFlow and Packet Capture as Sources"},
    {"id": "25_08", "topic": "User and Entity Behaviour Analytics"},
    {"id": "25_09", "topic": "Threat Hunting and Proactive Detection"},
    {"id": "25_10", "topic": "Reporting, Archiving and Compliance Evidence"},

    # -- 26: Security Assessment and Testing (CISSP D6, Sec+ D5) --
    {"id": "26_01", "topic": "Designing an Assessment, Test and Audit Strategy"},
    {"id": "26_02", "topic": "Internal Audits, Self-Assessments and Audit Committees"},
    {"id": "26_03", "topic": "External Audits and Regulatory Examinations"},
    {"id": "26_04", "topic": "Vulnerability Assessment Methodology"},
    {"id": "26_05", "topic": "Penetration Testing Phases and Rules of Engagement"},
    {"id": "26_06", "topic": "Known, Partially Known and Unknown Environment Testing"},
    {"id": "26_07", "topic": "Passive and Active Reconnaissance"},
    {"id": "26_08", "topic": "Red, Blue and Purple Team Exercises"},
    {"id": "26_09", "topic": "Breach and Attack Simulation"},
    {"id": "26_10", "topic": "Log Review and Synthetic Transaction Monitoring"},
    {"id": "26_11", "topic": "Misuse Case Testing, Interface Testing and Coverage Analysis"},
    {"id": "26_12", "topic": "Account Management and Access Review Data Collection"},
    {"id": "26_13", "topic": "Backup Verification and Recovery Testing"},
    {"id": "26_14", "topic": "Analysing and Reporting Results to Management"},
    {"id": "26_15", "topic": "Remediation Tracking, Exceptions and Key Performance Indicators"},

    # -- 27: Incident Response (all three) --
    {"id": "27_01", "topic": "Event, Alert and Incident: Why the Distinction Matters"},
    {"id": "27_02", "topic": "The Incident Response Plan and Team Composition"},
    {"id": "27_03", "topic": "Preparation and Detection"},
    {"id": "27_04", "topic": "Analysis, Triage and Severity Classification"},
    {"id": "27_05", "topic": "Containment Strategies and Their Trade-Offs"},
    {"id": "27_06", "topic": "Eradication and Recovery"},
    {"id": "27_07", "topic": "Lessons Learned and Root Cause Analysis"},
    {"id": "27_08", "topic": "Incident Reporting and Stakeholder Communication"},
    {"id": "27_09", "topic": "Tabletop Exercises, Simulations and Response Training"},

    # -- 28: Digital Forensics and Investigations (CISSP D7, Sec+ D4) --
    {"id": "28_01", "topic": "Investigation Types: Criminal, Civil, Regulatory and Internal"},
    {"id": "28_02", "topic": "Evidence Types and the Best Evidence Rule"},
    {"id": "28_03", "topic": "Chain of Custody and Evidence Admissibility"},
    {"id": "28_04", "topic": "Order of Volatility and Acquisition Priority"},
    {"id": "28_05", "topic": "Media, Network and Software Forensics"},
    {"id": "28_06", "topic": "Legal Hold, Preservation and eDiscovery"},
    {"id": "28_07", "topic": "Entrapment versus Enticement"},
    {"id": "28_08", "topic": "Forensic Reporting and Expert Testimony"},

    # -- 29: Secure Software Development (CISSP D8, Sec+ D4) --
    {"id": "29_01", "topic": "Development Methodologies: Waterfall, Agile and Spiral"},
    {"id": "29_02", "topic": "DevOps, DevSecOps and Shifting Security Left"},
    {"id": "29_03", "topic": "Maturity Models: CMMI and SAMM"},
    {"id": "29_04", "topic": "Security in Each Phase of the SDLC"},
    {"id": "29_05", "topic": "Source Code Repositories and Version Control Security"},
    {"id": "29_06", "topic": "Continuous Integration and Continuous Delivery Pipelines"},
    {"id": "29_07", "topic": "Assessing Acquired and Commercial Off-the-Shelf Software"},
    {"id": "29_08", "topic": "Open Source Components and Dependency Risk"},

    # -- 30: Application Security Controls (CISSP D8, Sec+ D2/D4) --
    {"id": "30_01", "topic": "Secure Coding Standards and Guidelines"},
    {"id": "30_02", "topic": "Input Validation and Output Encoding"},
    {"id": "30_03", "topic": "SQL, Command and LDAP Injection"},
    {"id": "30_04", "topic": "Cross-Site Scripting"},
    {"id": "30_05", "topic": "Cross-Site Request Forgery and Directory Traversal"},
    {"id": "30_06", "topic": "Authentication and Session Flaws in Applications"},
    {"id": "30_07", "topic": "API Security and Web Service Protection"},
    {"id": "30_08", "topic": "Static and Dynamic Application Security Testing"},
    {"id": "30_09", "topic": "Fuzzing, Sandboxing and Manual Code Review"},
    {"id": "30_10", "topic": "Code Signing and Software Integrity"},
    {"id": "30_11", "topic": "Cookies, Secure Headers and Client-Side Controls"},

    # -- 31: Automation and Orchestration (Sec+ D4) --
    {"id": "31_01", "topic": "Automating User and Resource Provisioning"},
    {"id": "31_02", "topic": "Guard Rails, Security Groups and Ticket Creation"},
    {"id": "31_03", "topic": "SOAR: Orchestration of Incident Response"},
    {"id": "31_04", "topic": "Benefits: Baseline Enforcement, Reaction Time and Workforce Multiplier"},
    {"id": "31_05", "topic": "Costs: Complexity, Single Point of Failure and Technical Debt"},
    {"id": "31_06", "topic": "Ongoing Supportability of Automation"},

    # -- 32: AI Security (CC 2026 refresh, Security+ SY0-801 direction) --
    {"id": "32_01", "topic": "AI Assets: Models, Training Data and Prompts"},
    {"id": "32_02", "topic": "Large Language Models and Where They Enter the Enterprise"},
    {"id": "32_03", "topic": "Prompt Injection and Insecure Output Handling"},
    {"id": "32_04", "topic": "Training Data Poisoning and Model Theft"},
    {"id": "32_05", "topic": "AI-Generated Phishing, Deepfakes and Voice Cloning"},
    {"id": "32_06", "topic": "Shadow AI and Data Leakage Through Public Models"},
    {"id": "32_07", "topic": "AI in Defence: Detection, Triage and Its Limits"},
    {"id": "32_08", "topic": "AI Governance, Acceptable Use and Human Oversight"},
]
