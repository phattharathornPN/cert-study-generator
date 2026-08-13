# -*- coding: utf-8 -*-
"""ISC2 Certified in Cybersecurity (CC) — entry-level pack.

Split out of the old combined `security` pack on 2026-08-11. That pack taught
every mechanism once at CISSP depth on the theory that the three exams are
nested; in practice a CC candidate reading a CISSP-depth answer gets a
management decision essay where the exam only asks them to recognise a
definition. Three packs, three depths.

CC is the shallowest of the three and the only one that is purely
recall/recognition: no performance-based items, no risk arithmetic beyond
naming the terms. Topics here stop where the exam stops.

Blueprint, verified 2026-08-11 against the official ISC2 exam outline
(isc2.org/certifications/cc/cc-certification-exam-outline, current version;
domain weights match the 2026-09-01 refresh ISC2 has announced):
    D1 Security Principles                      26%  (5 sub-objectives)
    D2 Business Continuity, DR and Incident Response  10%  (3 sub-objectives)
    D3 Access Controls Concepts                 22%  (2 sub-objectives)
    D4 Network Security                         24%  (3 sub-objectives)
    D5 Security Operations                      18%  (4 sub-objectives)

Section numbers below map 1:1 to the 17 official sub-objectives (1.1-5.4), not
to a topic count -- each section's topic list is built directly from that
sub-objective's bullet points, nothing added. The first version of this pack
padded CC with CISSP/Security+-depth material the exam doesn't cover (ABAC,
rule-based access control, digital signatures/PKI, biometric FAR/FRR/CER
math) -- recognisable as the same depth-mismatch bug the split was meant to
fix, just smaller. This version stops where the outline stops.

Shares NOTEBOOK_ID_SECURITY with the Security+ and CISSP packs: one uploaded
source library covers all three blueprints, and re-uploading it three times
would only burn quota. Note the one consequence -- slides_v2.py's lock is per
cert, not per notebook, so do not run slide cycles for two security packs at
the same time.

Only slide.pdf is downloaded: the reader site uses the PDF, so generating
.pptx would double the time and disk for a file nothing reads.
"""
from certs._security_shared import (
    security_slide_instructions,
    security_summary_prompt,
)

EXAM_NAME = "ISC2 Certified in Cybersecurity (CC)"
OUTPUT_DIR = "cc/output"
SITE_DIR = "cc"            # index.html sits beside its own output/
DIST_DIR = "cc/dist"
NOTEBOOK_ENV = "NOTEBOOK_ID_SECURITY"   # shared library, see module docstring
SLIDE_FORMATS = ("pdf",)

SECTION_TITLES = {
    "01": "Information Assurance Concepts",       # 1.1
    "02": "Risk Management Process",              # 1.2
    "03": "Security Controls",                     # 1.3
    "04": "ISC2 Code of Ethics",                    # 1.4
    "05": "Governance Processes",                   # 1.5
    "06": "Business Continuity",                    # 2.1
    "07": "Disaster Recovery",                      # 2.2
    "08": "Incident Response",                      # 2.3
    "09": "Physical Access Controls",               # 3.1
    "10": "Logical Access Controls",                # 3.2
    "11": "Computer Networking",                    # 4.1
    "12": "Network Threats and Attacks",            # 4.2
    "13": "Network Security Infrastructure",        # 4.3
    "14": "Data Security",                          # 5.1
    "15": "System Hardening",                       # 5.2
    "16": "Best Practice Security Policies",        # 5.3
    "17": "Security Awareness Training",            # 5.4
}

TOPICS = [
    # -- 01: Information Assurance Concepts (1.1) --
    {"id": "01_01", "topic": "Confidentiality: What It Protects and How It Fails"},
    {"id": "01_02", "topic": "Integrity: Detecting and Preventing Unauthorised Change"},
    {"id": "01_03", "topic": "Availability: Uptime as a Security Property"},
    {"id": "01_04", "topic": "Authentication Methods and Multi-Factor Authentication (MFA)"},
    {"id": "01_05", "topic": "Non-Repudiation and Why It Needs More Than a Password"},
    {"id": "01_06", "topic": "Privacy as Distinct from Confidentiality"},

    # -- 02: Risk Management Process (1.2) --
    {"id": "02_01", "topic": "Risk Management Priorities and Risk Tolerance"},
    {"id": "02_02", "topic": "Risk Identification: Assets, Threats and Vulnerabilities"},
    {"id": "02_03", "topic": "Risk Assessment: Qualitative and Quantitative"},
    {"id": "02_04", "topic": "Risk Treatment: Accept, Avoid, Mitigate and Transfer"},

    # -- 03: Security Controls (1.3) --
    {"id": "03_01", "topic": "Technical Controls"},
    {"id": "03_02", "topic": "Administrative Controls"},
    {"id": "03_03", "topic": "Physical Controls"},

    # -- 04: ISC2 Code of Ethics (1.4) --
    {"id": "04_01", "topic": "The ISC2 Code of Professional Ethics: The Four Canons"},
    {"id": "04_02", "topic": "Canon Order and Why It Decides Conflicts"},
    {"id": "04_03", "topic": "Reporting Ethics Violations"},

    # -- 05: Governance Processes (1.5) --
    {"id": "05_01", "topic": "Policies, Procedures and Standards"},
    {"id": "05_02", "topic": "Regulations and Laws Versus Internal Policy"},
    {"id": "05_03", "topic": "Why Governance Documents Form a Hierarchy"},

    # -- 06: Business Continuity (2.1) --
    {"id": "06_01", "topic": "Business Continuity: Purpose and Importance"},
    {"id": "06_02", "topic": "Business Continuity Plan Components"},
    {"id": "06_03", "topic": "The Business Impact Analysis"},

    # -- 07: Disaster Recovery (2.2) --
    {"id": "07_01", "topic": "Disaster Recovery: Purpose and Importance"},
    {"id": "07_02", "topic": "Disaster Recovery Plan Components"},
    {"id": "07_03", "topic": "Recovery Sites and Backup Strategies"},

    # -- 08: Incident Response (2.3) --
    {"id": "08_01", "topic": "Incident Response: Purpose and Importance"},
    {"id": "08_02", "topic": "Incident Response Plan Components"},
    {"id": "08_03", "topic": "Incident Response Team Roles"},

    # -- 09: Physical Access Controls (3.1) --
    {"id": "09_01", "topic": "Physical Security Controls: Badges, Gates and Environmental Design"},
    {"id": "09_02", "topic": "Monitoring: Guards, CCTV, Alarms and Logs"},
    {"id": "09_03", "topic": "Authorised Versus Unauthorised Personnel"},

    # -- 10: Logical Access Controls (3.2) --
    {"id": "10_01", "topic": "Principle of Least Privilege"},
    {"id": "10_02", "topic": "Segregation of Duties"},
    {"id": "10_03", "topic": "Discretionary Access Control (DAC)"},
    {"id": "10_04", "topic": "Mandatory Access Control (MAC)"},
    {"id": "10_05", "topic": "Role-Based Access Control (RBAC)"},

    # -- 11: Computer Networking (4.1) --
    {"id": "11_01", "topic": "The OSI Model as a Security Vocabulary"},
    {"id": "11_02", "topic": "The TCP/IP Model, IPv4 and IPv6"},
    {"id": "11_03", "topic": "Ports and Common Applications"},
    {"id": "11_04", "topic": "Wi-Fi Basics and Why Wireless Changes Risk"},

    # -- 12: Network Threats and Attacks (4.2) --
    {"id": "12_01", "topic": "Distributed Denial-of-Service (DDoS) Attacks"},
    {"id": "12_02", "topic": "Viruses, Worms and Trojans"},
    {"id": "12_03", "topic": "On-Path (Man-in-the-Middle) Attacks"},
    {"id": "12_04", "topic": "Side-Channel Attacks"},
    {"id": "12_05", "topic": "Intrusion Detection: Host-Based (HIDS) and Network-Based (NIDS)"},
    {"id": "12_06", "topic": "Prevention: Antivirus, Scans, Firewalls and IPS"},

    # -- 13: Network Security Infrastructure (4.3) --
    {"id": "13_01", "topic": "On-Premises Infrastructure: Power, Data Centres and HVAC"},
    {"id": "13_02", "topic": "Redundancy, Fire Suppression and MOU/MOA"},
    {"id": "13_03", "topic": "Network Segmentation: DMZ, VLAN, VPN and Micro-Segmentation"},
    {"id": "13_04", "topic": "Defence in Depth and Network Access Control (NAC)"},
    {"id": "13_05", "topic": "Cloud Basics: SLA, MSP, SaaS, IaaS and PaaS"},
    {"id": "13_06", "topic": "Hybrid Cloud Considerations"},

    # -- 14: Data Security (5.1) --
    {"id": "14_01", "topic": "Encryption Basics: Symmetric, Asymmetric and Hashing"},
    {"id": "14_02", "topic": "Data Handling: Destruction and Retention"},
    {"id": "14_03", "topic": "Data Classification and Labelling"},
    {"id": "14_04", "topic": "Logging and Monitoring Security Events"},

    # -- 15: System Hardening (5.2) --
    {"id": "15_01", "topic": "Configuration Management and Baselines"},
    {"id": "15_02", "topic": "Updates and Patches"},

    # -- 16: Best Practice Security Policies (5.3) --
    {"id": "16_01", "topic": "Data Handling Policy"},
    {"id": "16_02", "topic": "Password Policy"},
    {"id": "16_03", "topic": "Acceptable Use Policy (AUP)"},
    {"id": "16_04", "topic": "Bring Your Own Device (BYOD) Policy"},
    {"id": "16_05", "topic": "Change Management Policy"},
    {"id": "16_06", "topic": "Privacy Policy"},

    # -- 17: Security Awareness Training (5.4) --
    {"id": "17_01", "topic": "Social Engineering Awareness"},
    {"id": "17_02", "topic": "Password Protection Practices"},
    {"id": "17_03", "topic": "Why Awareness Training Matters"},
]

# CC is a recognition exam: the candidate must name the concept and pick the
# textbook-correct definition, not defend a budget. Asking for a management
# decision scenario here (as the old combined pack did) produced answers the
# exam never tests.
_PERSONA = (
    "ตอบในมุมของผู้เริ่มต้นสายความมั่นคงปลอดภัย (entry level) ที่ต้อง 'จำนิยามให้แม่นและแยกแยะศัพท์ใกล้เคียงให้ออก' "
    "ไม่ต้องตอบแบบผู้บริหารที่ต้องชั่งงบประมาณหรือเลือกกลยุทธ์องค์กร เพราะข้อสอบ CC ไม่ได้ถามระดับนั้น"
)

_WORKED_EXAMPLE = (
    "ตัวอย่างสถานการณ์ในที่ทำงานจริงแบบเข้าใจง่าย 1 สถานการณ์ — "
    "เล่าว่าแนวคิดนี้ถูกใช้หรือถูกละเมิดอย่างไรในองค์กรทั่วไป แล้วชี้ว่าจุดไหนคือแนวคิดที่กำลังเรียนอยู่ "
    "(เน้นให้เห็นภาพและจำได้ ไม่ต้องวิเคราะห์ความคุ้มค่าเชิงงบประมาณ)"
)

_EXAM_WORDING = (
    "โดยเฉพาะศัพท์ที่ข้อสอบ CC ชอบเอามาสลับกันจนสับสน เช่น identification กับ authentication, "
    "threat กับ vulnerability, BC กับ DR — ให้ชี้ชัดว่าต่างกันตรงไหน"
)

_COMPARE_HINT = (
    "เน้นเทียบ 'นิยาม' ให้ชัดเป็นคู่ ๆ ว่าคำไหนหมายถึงอะไรและใช้ตอนไหน"
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
