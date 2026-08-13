# -*- coding: utf-8 -*-
"""CompTIA Security+ SY0-701 — practitioner pack.

Split out of the old combined `security` pack on 2026-08-11. Security+ sits
between CC and CISSP and is the odd one out in *kind*, not just depth: it is
the only one of the three with performance-based questions, and the only one
that expects the candidate to name specific tooling and acronyms rather than
reason about them abstractly. A CISSP-depth "which option would a security
leader choose" answer misses most of what this exam actually asks.

So the persona here is a hands-on practitioner: given this situation, which
control, tool or technique do you deploy, and what does its output look like.

Blueprint (SY0-701 Exam Objectives v5.0; SY0-801 previews ~2026-10-20 with
the same five-domain shape, so the structure below should survive the
refresh):
    D1 General Security Concepts                12%
    D2 Threats, Vulnerabilities and Mitigations 22%
    D3 Security Architecture                    18%
    D4 Security Operations                      28%
    D5 Security Program Management and Oversight 20%

Section numbers 01-28 map 1:1 to the 28 official sub-objectives (1.1-5.6).
Verified 2026-08-11 against the official SY0-701 Exam Objectives v5.0 PDF,
line by line -- the topic list already tracked the blueprint closely; the
verification pass added the dozen or so explicitly-named items that were
missing (blockchain/key stretching, downgrade/collision/birthday crypto
attacks, GPO/SELinux hardening, UBA, jump/proxy servers, SD-WAN/SASE,
802.1X/EAP) rather than a rewrite.

Shares NOTEBOOK_ID_SECURITY with the CC and CISSP packs: one uploaded source
library covers all three blueprints. Note the one consequence -- slides_v2.py's
lock is per cert, not per notebook, so do not run slide cycles for two
security packs at the same time.

Only slide.pdf is downloaded: the reader site uses the PDF, so generating
.pptx would double the time and disk for a file nothing reads.
"""
from certs._security_shared import (
    security_slide_instructions,
    security_summary_prompt,
)

EXAM_NAME = "CompTIA Security+ SY0-701"
OUTPUT_DIR = "secplus/output"
SITE_DIR = "secplus"       # index.html sits beside its own output/
DIST_DIR = "secplus/dist"
NOTEBOOK_ENV = "NOTEBOOK_ID_SECURITY"   # shared library, see module docstring
SLIDE_FORMATS = ("pdf",)

SECTION_TITLES = {
    "01": "Security Controls",
    "02": "Fundamental Security Concepts",
    "03": "Change Management",
    "04": "Cryptographic Solutions",
    "05": "Threat Actors and Motivations",
    "06": "Threat Vectors and Attack Surfaces",
    "07": "Vulnerability Types",
    "08": "Malicious Activity and Indicators",
    "09": "Mitigation Techniques",
    "10": "Architecture Models and Cloud",
    "11": "Enterprise Infrastructure Security",
    "12": "Data Protection",
    "13": "Resilience and Recovery",
    "14": "Secure Computing Techniques",
    "15": "Asset Management",
    "16": "Vulnerability Management",
    "17": "Alerting and Monitoring",
    "18": "Enterprise Security Capabilities",
    "19": "Identity and Access Management",
    "20": "Automation and Orchestration",
    "21": "Incident Response",
    "22": "Investigation Data Sources",
    "23": "Security Governance",
    "24": "Risk Management",
    "25": "Third-Party Risk",
    "26": "Compliance",
    "27": "Audits and Assessments",
    "28": "Security Awareness",
}

TOPICS = [
    # -- 01: Security Controls (D1.1) --
    {"id": "01_01", "topic": "Technical, Managerial, Operational and Physical Control Categories"},
    {"id": "01_02", "topic": "Preventive Controls and Where They Sit"},
    {"id": "01_03", "topic": "Deterrent and Detective Controls"},
    {"id": "01_04", "topic": "Corrective and Compensating Controls"},
    {"id": "01_05", "topic": "Directive Controls and Policy as a Control"},
    {"id": "01_06", "topic": "Matching a Control Type to a Given Scenario"},

    # -- 02: Fundamental Security Concepts (D1.2) --
    {"id": "02_01", "topic": "The CIA Triad in Practical Terms"},
    {"id": "02_02", "topic": "Non-Repudiation and Its Technical Basis"},
    {"id": "02_03", "topic": "Authentication, Authorisation and Accounting (AAA)"},
    {"id": "02_04", "topic": "Authenticating People Versus Authenticating Systems"},
    {"id": "02_05", "topic": "Gap Analysis and Measuring Against a Standard"},
    {"id": "02_06", "topic": "Zero Trust: Control Plane and Data Plane"},
    {"id": "02_07", "topic": "Policy Engine, Policy Administrator and Policy Enforcement Point"},
    {"id": "02_08", "topic": "Adaptive Identity and Implicit Trust Zones"},
    {"id": "02_09", "topic": "Physical Security Controls for the Practitioner"},
    {"id": "02_10", "topic": "Deception Technology: Honeypots, Honeynets and Honeytokens"},

    # -- 03: Change Management (D1.3) --
    {"id": "03_01", "topic": "Why Change Management Is a Security Process"},
    {"id": "03_02", "topic": "Approval Process, Ownership and Stakeholders"},
    {"id": "03_03", "topic": "Impact Analysis, Test Results and Backout Plans"},
    {"id": "03_04", "topic": "Maintenance Windows and Standard Operating Procedures"},
    {"id": "03_05", "topic": "Technical Implications: Allow Lists, Restarts and Dependencies"},

    # -- 04: Cryptographic Solutions (D1.4) --
    {"id": "04_01", "topic": "Symmetric Encryption and Key Distribution"},
    {"id": "04_02", "topic": "Asymmetric Encryption and Key Pairs"},
    {"id": "04_03", "topic": "Key Length and What Actually Makes a Key Strong"},
    {"id": "04_04", "topic": "Public Key Infrastructure: CA, RA and Trust Chains"},
    {"id": "04_05", "topic": "Certificates, CSRs and Certificate Attributes"},
    {"id": "04_06", "topic": "Certificate Revocation: CRL and OCSP Stapling"},
    {"id": "04_07", "topic": "Hashing, Salting and Password Storage"},
    {"id": "04_08", "topic": "Digital Signatures and What They Prove"},
    {"id": "04_09", "topic": "Key Exchange and Perfect Forward Secrecy"},
    {"id": "04_10", "topic": "Full-Disk, Partition, File and Database Encryption"},
    {"id": "04_11", "topic": "TPM, HSM, Key Management Systems and Secure Enclaves"},
    {"id": "04_12", "topic": "Obfuscation: Steganography, Tokenisation and Data Masking"},
    {"id": "04_13", "topic": "Key Stretching and Slowing Down Brute Force"},
    {"id": "04_14", "topic": "Blockchain and the Open Public Ledger"},

    # -- 05: Threat Actors and Motivations (D2.1) --
    {"id": "05_01", "topic": "Nation-State Actors and Advanced Persistent Threats"},
    {"id": "05_02", "topic": "Organised Crime and Financially Driven Attackers"},
    {"id": "05_03", "topic": "Hacktivists and Ideological Motivation"},
    {"id": "05_04", "topic": "Insider Threats: Malicious, Negligent and Compromised"},
    {"id": "05_05", "topic": "Unskilled Attackers and Commodity Tooling"},
    {"id": "05_06", "topic": "Shadow IT as an Unintentional Threat Source"},
    {"id": "05_07", "topic": "Actor Attributes: Resources, Sophistication and Internal Access"},

    # -- 06: Threat Vectors and Attack Surfaces (D2.2) --
    {"id": "06_01", "topic": "Message-Based Vectors: Email, SMS and Instant Messaging"},
    {"id": "06_02", "topic": "Phishing, Spear Phishing, Whaling and Business Email Compromise"},
    {"id": "06_03", "topic": "Vishing, Smishing and Voice-Based Social Engineering"},
    {"id": "06_04", "topic": "Pretexting, Impersonation and Watering Hole Attacks"},
    {"id": "06_05", "topic": "Image, File and Removable Device Vectors"},
    {"id": "06_06", "topic": "Vulnerable Software as a Vector: Client-Based Versus Agentless"},
    {"id": "06_07", "topic": "Unsupported Systems and End-of-Life Applications"},
    {"id": "06_08", "topic": "Unsecure Networks: Wireless, Wired and Bluetooth"},
    {"id": "06_09", "topic": "Open Service Ports and Default Credentials"},
    {"id": "06_10", "topic": "Supply Chain Vectors: Vendors, Suppliers and MSPs"},
    {"id": "06_11", "topic": "Human Vectors and Why Social Engineering Still Wins"},

    # -- 07: Vulnerability Types (D2.3) --
    {"id": "07_01", "topic": "Application Vulnerabilities: Memory Injection and Buffer Overflow"},
    {"id": "07_02", "topic": "Race Conditions: TOC and TOU"},
    {"id": "07_03", "topic": "Malicious Update and Compromised Software Delivery"},
    {"id": "07_04", "topic": "Operating System Vulnerabilities"},
    {"id": "07_05", "topic": "Web Vulnerabilities: SQL Injection"},
    {"id": "07_06", "topic": "Web Vulnerabilities: Cross-Site Scripting"},
    {"id": "07_07", "topic": "Hardware Vulnerabilities: Firmware and End-of-Life Devices"},
    {"id": "07_08", "topic": "Legacy Hardware and Why It Cannot Simply Be Patched"},
    {"id": "07_09", "topic": "Virtualisation Vulnerabilities: VM Escape and Resource Reuse"},
    {"id": "07_10", "topic": "Cloud-Specific Vulnerabilities and Misconfiguration"},
    {"id": "07_11", "topic": "Supply Chain Vulnerabilities in Service and Hardware Providers"},
    {"id": "07_12", "topic": "Cryptographic Vulnerabilities and Weak Implementations"},
    {"id": "07_13", "topic": "Misconfiguration and Zero-Day Vulnerabilities"},

    # -- 08: Malicious Activity and Indicators (D2.4) --
    {"id": "08_01", "topic": "Ransomware: Behaviour and Indicators"},
    {"id": "08_02", "topic": "Trojans, Worms and Viruses Distinguished"},
    {"id": "08_03", "topic": "Spyware, Keyloggers and Bloatware"},
    {"id": "08_04", "topic": "Rootkits and Logic Bombs"},
    {"id": "08_05", "topic": "Physical Attacks: Brute Force, RFID Cloning and Environmental"},
    {"id": "08_06", "topic": "Denial of Service, Distributed DoS and Amplification"},
    {"id": "08_07", "topic": "DNS Attacks and Domain Hijacking"},
    {"id": "08_08", "topic": "On-Path Attacks and Session Replay"},
    {"id": "08_09", "topic": "Credential Replay and Privilege Escalation"},
    {"id": "08_10", "topic": "Password Attacks: Brute Force, Spraying and Dictionary"},
    {"id": "08_11", "topic": "Application Attacks: Directory Traversal and Request Forgery"},
    {"id": "08_12", "topic": "Reading Indicators: Account Lockouts, Impossible Travel and Log Anomalies"},
    {"id": "08_13", "topic": "Cryptographic Attacks: Downgrade, Collision and Birthday"},

    # -- 09: Mitigation Techniques (D2.5) --
    {"id": "09_01", "topic": "Segmentation and Access Control as Mitigations"},
    {"id": "09_02", "topic": "Application Allow Lists and Isolation"},
    {"id": "09_03", "topic": "Patching and Configuration Enforcement"},
    {"id": "09_04", "topic": "Decommissioning and Removing Attack Surface"},
    {"id": "09_05", "topic": "Encryption, Monitoring and Least Privilege as Mitigations"},
    {"id": "09_06", "topic": "Host-Based Firewalls and Intrusion Prevention"},
    {"id": "09_07", "topic": "Choosing the Right Mitigation for a Given Attack"},

    # -- 10: Architecture Models and Cloud (D3.1) --
    {"id": "10_01", "topic": "Cloud Responsibility Matrix and the Shared Model"},
    {"id": "10_02", "topic": "Hybrid Considerations and Third-Party Vendor Risk"},
    {"id": "10_03", "topic": "Infrastructure as Code and Its Security Impact"},
    {"id": "10_04", "topic": "Serverless and Microservices Architectures"},
    {"id": "10_05", "topic": "Network Infrastructure: Physical, Software-Defined and Virtual"},
    {"id": "10_06", "topic": "On-Premises Versus Centralised Versus Decentralised"},
    {"id": "10_07", "topic": "Containerisation and Virtualisation Compared"},
    {"id": "10_08", "topic": "IoT, ICS and SCADA Security Considerations"},
    {"id": "10_09", "topic": "Embedded Systems and Real-Time Operating Systems"},
    {"id": "10_10", "topic": "Architecture Trade-Offs: Cost, Responsiveness and Patch Availability"},

    # -- 11: Enterprise Infrastructure Security (D3.2) --
    {"id": "11_01", "topic": "Device Placement and Security Zones"},
    {"id": "11_02", "topic": "Attack Surface and Connectivity Decisions"},
    {"id": "11_03", "topic": "Failure Modes: Fail-Open Versus Fail-Closed"},
    {"id": "11_04", "topic": "Active Versus Passive Device Deployment"},
    {"id": "11_05", "topic": "Inline Versus Tap and Monitor Deployment"},
    {"id": "11_06", "topic": "Firewall Types: Layer 4, Layer 7 and Next-Generation"},
    {"id": "11_07", "topic": "Web Application Firewalls and Unified Threat Management"},
    {"id": "11_08", "topic": "IDS and IPS: Signature Versus Trend Based"},
    {"id": "11_09", "topic": "Secure Communication: VPN, Tunnelling and Remote Access"},
    {"id": "11_10", "topic": "Selection of Effective Controls for a Given Infrastructure"},
    {"id": "11_11", "topic": "Network Appliances: Jump Servers, Proxies, Load Balancers and Sensors"},
    {"id": "11_12", "topic": "Port Security: 802.1X and EAP"},
    {"id": "11_13", "topic": "SD-WAN and Secure Access Service Edge (SASE)"},

    # -- 12: Data Protection (D3.3) --
    {"id": "12_01", "topic": "Data Types: Regulated, Trade Secret, Intellectual Property and Legal"},
    {"id": "12_02", "topic": "Data Classifications: Sensitive, Confidential, Public and Restricted"},
    {"id": "12_03", "topic": "Data States: At Rest, In Transit and In Use"},
    {"id": "12_04", "topic": "Data Sovereignty and Geolocation Requirements"},
    {"id": "12_05", "topic": "Geographic Restrictions and Permission Restrictions"},
    {"id": "12_06", "topic": "Encryption, Hashing and Masking as Protection Methods"},
    {"id": "12_07", "topic": "Tokenisation and Obfuscation in Data Protection"},
    {"id": "12_08", "topic": "Data Loss Prevention and Where It Is Enforced"},

    # -- 13: Resilience and Recovery (D3.4) --
    {"id": "13_01", "topic": "High Availability and Load Balancing"},
    {"id": "13_02", "topic": "Site Considerations: Hot, Cold, Warm and Geographic Dispersion"},
    {"id": "13_03", "topic": "Platform Diversity and Multi-Cloud Resilience"},
    {"id": "13_04", "topic": "Continuity of Operations and Capacity Planning"},
    {"id": "13_05", "topic": "Testing: Tabletop Exercises, Failover and Simulation"},
    {"id": "13_06", "topic": "Backups: Onsite, Offsite, Frequency, Encryption and Snapshots"},
    {"id": "13_07", "topic": "Replication and Journaling"},
    {"id": "13_08", "topic": "Power Resilience: Generators and Uninterruptible Power Supplies"},

    # -- 14: Secure Computing Techniques (D4.1) --
    {"id": "14_01", "topic": "Secure Baselines: Establish, Deploy and Maintain"},
    {"id": "14_02", "topic": "Hardening Workstations and Servers"},
    {"id": "14_03", "topic": "Hardening Mobile Devices and Embedded Systems"},
    {"id": "14_04", "topic": "Wireless Device Installation and Site Surveys"},
    {"id": "14_05", "topic": "Mobile Solutions: MDM, BYOD, COPE and CYOD"},
    {"id": "14_06", "topic": "Wireless Security Settings: WPA3, AAA and RADIUS"},
    {"id": "14_07", "topic": "Application Security: Input Validation and Secure Cookies"},
    {"id": "14_08", "topic": "Sandboxing and Application Monitoring"},

    # -- 15: Asset Management (D4.2) --
    {"id": "15_01", "topic": "Acquisition, Procurement and Assignment of Assets"},
    {"id": "15_02", "topic": "Asset Inventory, Ownership and Classification"},
    {"id": "15_03", "topic": "Monitoring and Asset Tracking Throughout Life"},
    {"id": "15_04", "topic": "Sanitisation, Destruction and Certification"},
    {"id": "15_05", "topic": "Data Retention and Disposal Decisions"},

    # -- 16: Vulnerability Management (D4.3) --
    {"id": "16_01", "topic": "Vulnerability Scanning: Credentialed and Non-Credentialed"},
    {"id": "16_02", "topic": "Application Security Testing: Static and Dynamic Analysis"},
    {"id": "16_03", "topic": "Package Monitoring and Software Composition Analysis"},
    {"id": "16_04", "topic": "Threat Feeds, OSINT and Information Sharing"},
    {"id": "16_05", "topic": "Penetration Testing and Responsible Disclosure Programmes"},
    {"id": "16_06", "topic": "Analysing Results: False Positives and False Negatives"},
    {"id": "16_07", "topic": "Prioritisation and CVSS Scoring"},
    {"id": "16_08", "topic": "CVE, Exposure Factor and Environmental Variables"},
    {"id": "16_09", "topic": "Remediation: Patching, Insurance, Segmentation and Exceptions"},
    {"id": "16_10", "topic": "Validation of Remediation and Ongoing Reporting"},

    # -- 17: Alerting and Monitoring (D4.4) --
    {"id": "17_01", "topic": "Monitoring Systems, Applications and Infrastructure"},
    {"id": "17_02", "topic": "Log Aggregation and Archiving"},
    {"id": "17_03", "topic": "Alerting, Alert Tuning and Reducing Noise"},
    {"id": "17_04", "topic": "Scanning, Reporting and Quarantine Responses"},
    {"id": "17_05", "topic": "SIEM: What It Correlates and Why"},
    {"id": "17_06", "topic": "Antivirus, DLP and SNMP Traps as Monitoring Tools"},
    {"id": "17_07", "topic": "NetFlow and Network Telemetry"},
    {"id": "17_08", "topic": "Benchmarks and Security Content Automation Protocol"},

    # -- 18: Enterprise Security Capabilities (D4.5) --
    {"id": "18_01", "topic": "Firewall Rules, Access Control Lists and Ports"},
    {"id": "18_02", "topic": "Screened Subnets and Perimeter Design"},
    {"id": "18_03", "topic": "IDS and IPS Trends, Signatures and Tuning"},
    {"id": "18_04", "topic": "Web Filtering: URL Scanning, Content Categorisation and Agents"},
    {"id": "18_05", "topic": "DNS Filtering and Reputation Services"},
    {"id": "18_06", "topic": "Email Security: DMARC, DKIM, SPF and Gateways"},
    {"id": "18_07", "topic": "File Integrity Monitoring"},
    {"id": "18_08", "topic": "Data Loss Prevention Deployment in the Enterprise"},
    {"id": "18_09", "topic": "Network Access Control and Posture Checking"},
    {"id": "18_10", "topic": "Endpoint Detection and Response and Extended Detection and Response"},
    {"id": "18_11", "topic": "Operating System Hardening: Group Policy and SELinux"},
    {"id": "18_12", "topic": "User Behaviour Analytics"},

    # -- 19: Identity and Access Management (D4.6) --
    {"id": "19_01", "topic": "Provisioning and Deprovisioning User Accounts"},
    {"id": "19_02", "topic": "Permission Assignments and Identity Proofing"},
    {"id": "19_03", "topic": "Federation and Single Sign-On"},
    {"id": "19_04", "topic": "LDAP, SAML, OAuth and OpenID Connect"},
    {"id": "19_05", "topic": "Interoperability and Attestation"},
    {"id": "19_06", "topic": "Access Control Models: MAC, DAC, RBAC and ABAC"},
    {"id": "19_07", "topic": "Rule-Based and Time-of-Day Access Restrictions"},
    {"id": "19_08", "topic": "Multi-Factor Authentication Implementations and Factors"},
    {"id": "19_09", "topic": "Password Concepts: Complexity, Age, Reuse and Managers"},
    {"id": "19_10", "topic": "Privileged Access Management: Just-in-Time and Password Vaulting"},

    # -- 20: Automation and Orchestration (D4.7) --
    {"id": "20_01", "topic": "Use Cases: Provisioning, Guard Rails and Ticket Creation"},
    {"id": "20_02", "topic": "Automating Security Groups and Access Approval"},
    {"id": "20_03", "topic": "Continuous Integration and Testing in Security"},
    {"id": "20_04", "topic": "Benefits: Efficiency, Baseline Enforcement and Reaction Time"},
    {"id": "20_05", "topic": "Other Considerations: Complexity, Cost and Single Point of Failure"},

    # -- 21: Incident Response (D4.8) --
    {"id": "21_01", "topic": "Incident Response Process: Preparation and Detection"},
    {"id": "21_02", "topic": "Analysis, Containment and Eradication"},
    {"id": "21_03", "topic": "Recovery and Lessons Learned"},
    {"id": "21_04", "topic": "Training and Testing the Response Plan"},
    {"id": "21_05", "topic": "Tabletop Exercises and Simulations"},
    {"id": "21_06", "topic": "Root Cause Analysis"},
    {"id": "21_07", "topic": "Threat Hunting as a Proactive Activity"},
    {"id": "21_08", "topic": "Digital Forensics: Legal Hold and Chain of Custody"},
    {"id": "21_09", "topic": "Acquisition, Preservation, Reporting and E-Discovery"},

    # -- 22: Investigation Data Sources (D4.9) --
    {"id": "22_01", "topic": "Firewall Logs and What They Reveal"},
    {"id": "22_02", "topic": "Application and Endpoint Logs"},
    {"id": "22_03", "topic": "OS-Specific Security Logs and IPS/IDS Logs"},
    {"id": "22_04", "topic": "Network, Metadata and Vulnerability Scan Outputs"},
    {"id": "22_05", "topic": "Dashboards, Automated Reports and Packet Captures"},

    # -- 23: Security Governance (D5.1) --
    {"id": "23_01", "topic": "Guidelines, Policies and Their Hierarchy"},
    {"id": "23_02", "topic": "Acceptable Use Policy and Information Security Policies"},
    {"id": "23_03", "topic": "Business Continuity and Incident Response Policies"},
    {"id": "23_04", "topic": "Standards: Password, Access Control, Encryption and Physical"},
    {"id": "23_05", "topic": "Procedures: Change Management, Onboarding and Playbooks"},
    {"id": "23_06", "topic": "External Considerations: Regulatory, Legal and Industry"},
    {"id": "23_07", "topic": "Governance Structures: Boards, Committees and Government Entities"},
    {"id": "23_08", "topic": "Roles and Responsibilities: Owners, Controllers, Processors and Custodians"},

    # -- 24: Risk Management (D5.2) --
    {"id": "24_01", "topic": "Risk Identification and the Risk Register"},
    {"id": "24_02", "topic": "Key Risk Indicators, Risk Owners and Risk Threshold"},
    {"id": "24_03", "topic": "Ad Hoc, Recurring, One-Time and Continuous Assessment"},
    {"id": "24_04", "topic": "Qualitative Risk Analysis"},
    {"id": "24_05", "topic": "Quantitative Risk Analysis: SLE, ARO and ALE"},
    {"id": "24_06", "topic": "Probability, Likelihood, Exposure Factor and Impact"},
    {"id": "24_07", "topic": "Risk Management Strategies: Transfer, Accept, Avoid and Mitigate"},
    {"id": "24_08", "topic": "Risk Appetite, Tolerance and Exemptions"},
    {"id": "24_09", "topic": "Risk Reporting and Business Impact Analysis"},

    # -- 25: Third-Party Risk (D5.3) --
    {"id": "25_01", "topic": "Vendor Assessment: Penetration Testing and Right to Audit"},
    {"id": "25_02", "topic": "Evidence of Internal Audits and Independent Assessments"},
    {"id": "25_03", "topic": "Supply Chain Analysis and Vendor Selection"},
    {"id": "25_04", "topic": "Due Diligence and Conflict of Interest"},
    {"id": "25_05", "topic": "Agreements: SLA, MOU, MOA, MSA, WO/SOW, NDA and BPA"},
    {"id": "25_06", "topic": "Vendor Monitoring and Questionnaires"},
    {"id": "25_07", "topic": "Rules of Engagement With Third Parties"},

    # -- 26: Compliance (D5.4) --
    {"id": "26_01", "topic": "Compliance Reporting: Internal and External"},
    {"id": "26_02", "topic": "Consequences of Non-Compliance: Fines and Sanctions"},
    {"id": "26_03", "topic": "Reputational Damage and Loss of Licence"},
    {"id": "26_04", "topic": "Compliance Monitoring: Due Diligence and Attestation"},
    {"id": "26_05", "topic": "Internal and External Compliance Monitoring"},
    {"id": "26_06", "topic": "Privacy: Legal Implications and Data Subject Rights"},
    {"id": "26_07", "topic": "Data Roles: Controller Versus Processor and Data Inventory"},

    # -- 27: Audits and Assessments (D5.5) --
    {"id": "27_01", "topic": "Internal Audits and the Audit Committee"},
    {"id": "27_02", "topic": "Self-Assessments and Compliance Checks"},
    {"id": "27_03", "topic": "External Audits, Regulatory and Examinations"},
    {"id": "27_04", "topic": "Penetration Testing: Physical, Offensive and Defensive"},
    {"id": "27_05", "topic": "Integrated Testing and Known, Partially Known and Unknown Environments"},
    {"id": "27_06", "topic": "Reconnaissance: Passive and Active"},

    # -- 28: Security Awareness (D5.6) --
    {"id": "28_01", "topic": "Phishing Campaigns and Recognising Attempts"},
    {"id": "28_02", "topic": "Anomalous Behaviour Recognition: Risky and Unexpected"},
    {"id": "28_03", "topic": "User Guidance and Training Topics"},
    {"id": "28_04", "topic": "Reporting, Monitoring and Development of Awareness Programmes"},
    {"id": "28_05", "topic": "Execution and Measurement of an Awareness Programme"},
]

# Security+ is the hands-on exam of the three, and the only one with
# performance-based questions: it asks which tool, setting or technique you
# deploy, and what its output looks like. The old combined pack answered
# everything as a CISSP-style management decision, which is the wrong shape
# for most of this blueprint.
_PERSONA = (
    "ตอบในมุมของ practitioner ที่ลงมือทำจริง (hands-on) — ต้องรู้ว่า 'ในสถานการณ์นี้เลือกใช้เครื่องมือ/ค่า config/เทคนิคตัวไหน' "
    "และผลลัพธ์ที่ได้หน้าตาเป็นยังไง ไม่ใช่ตอบแบบผู้บริหารที่ชั่งงบอย่างเดียว "
    "ถ้ามีชื่อเครื่องมือ โปรโตคอล หรือ acronym ที่ข้อสอบชอบถาม ให้ระบุชื่อจริงเสมอ"
)

_WORKED_EXAMPLE = (
    "ตัวอย่างการใช้งานจริงเชิงปฏิบัติ (practical scenario) อย่างน้อย 1 สถานการณ์เต็ม — "
    "ตั้งโจทย์แบบที่ข้อสอบ performance-based ชอบออก แล้วเดินให้ดูทีละขั้นว่าเลือกเครื่องมือ/ค่า setting ไหน เพราะอะไร "
    "และดูผลลัพธ์ยังไงถึงรู้ว่าสำเร็จ "
    "ถ้าหัวข้อมีสูตรคำนวณ (เช่น SLE, ARO, ALE, CVSS) ให้ใส่ตัวอย่างคำนวณจริงพร้อมค่าจำลองทีละขั้นแทน"
)

_EXAM_WORDING = (
    "โดยเฉพาะ acronym ที่ข้อสอบ SY0-701 ชอบเอามาสลับกัน และตัวเลือกที่ 'ทำได้จริงแต่ไม่ใช่เครื่องมือที่ตรงที่สุด' "
    "สำหรับโจทย์นั้น"
)

_COMPARE_HINT = (
    "เน้นเทียบเครื่องมือ/เทคนิค/โปรโตคอลที่ทำงานคล้ายกัน ว่าตัวไหนเหมาะกับสถานการณ์แบบไหน"
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
