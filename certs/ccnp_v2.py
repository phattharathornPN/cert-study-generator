# -*- coding: utf-8 -*-
"""CCNP ENCOR 350-401 -- redesigned topic list (v2).

Why a rewrite: measuring the v1 pack found 44 topic pairs whose summaries
shared 55-85% of their technical vocabulary. The cause was scope collision,
not prompt wording -- "RSTP, MSTP, PortFast, BPDUGuard, Root Guard" cannot
avoid overlapping "RSTP and MSTP Fundamentals" no matter how the prompt is
phrased, and four separate campus-design topics all had licence to explain
the same three-layer model.

Design rules applied here:

* One topic teaches one mechanism. No title carries a list.
* No two topics may cover the same mechanism. Where v1 had an overview plus
  a deep dive of the same subject, the overview is gone and the subject is
  split by mechanism instead.
* Split further wherever real depth exists. OSPF LSA types, PIM modes, BGP
  attributes and the SD-WAN planes each get a topic per item rather than one
  topic per family.
* Teaching order within a section: concept, then mechanism, then
  configuration, then troubleshooting.

Sections are finer than the exam's six domains so that each one is a
coherent study block.
"""

EXAM_NAME = "CCNP ENCOR 350-401"
# The generated files must sit *inside* SITE_DIR, the way CCNA's do. The site
# builder writes asset links as "output/..." relative to index.html, and
# build_dist copies OUTPUT_DIR to its path relative to SITE_DIR -- so an
# output directory outside SITE_DIR (the original "output_v2") produced an
# index pointing at a directory that was never packaged, and a dist holding
# nothing but index.html.
OUTPUT_DIR = "v2/output"
SITE_DIR = "v2"      # index.html sits beside its own output/
DIST_DIR = "v2/dist"
# Its own notebook, not v1's. Sharing v1's meant sharing v1's artifact
# backlog -- LIST_ARTIFACTS times out once a notebook accumulates enough
# of them, which breaks wait_for_completion for every new generation --
# and sharing its daily quota. A separate notebook fixes both.
NOTEBOOK_ENV = "NOTEBOOK_ID_CCNP_V2"
SLIDE_FORMATS = ("pdf", "pptx")

SECTION_TITLES = {
    "01": "Enterprise Architecture and Design",
    "02": "Switching Hardware and Forwarding",
    "03": "VLANs and Trunking",
    "04": "Spanning Tree",
    "05": "EtherChannel",
    "06": "Routing Fundamentals and Path Control",
    "07": "EIGRP",
    "08": "OSPF",
    "09": "BGP",
    "10": "First Hop Redundancy and Internet Edge",
    "11": "Tunnels and Network Overlays",
    "12": "Compute Virtualization",
    "13": "Wireless",
    "14": "Multicast",
    "15": "Quality of Service",
    "16": "Network Assurance and Monitoring",
    "17": "Infrastructure Security",
    "18": "Identity and Access Control",
    "19": "Security Architecture",
    "20": "Cisco SD-Access",
    "21": "Cisco SD-WAN",
    "22": "Automation and Programmability",
}


from certs._shared import networking_slide_instructions, networking_summary_prompt


def SLIDE_INSTRUCTIONS(topic: str) -> str:
    return networking_slide_instructions(EXAM_NAME, topic)


def SUMMARY_PROMPT(topic: str) -> str:
    return networking_summary_prompt(EXAM_NAME, topic)


TOPICS = [
    # -- 01: Enterprise Architecture and Design --
    # v1 had four topics (01_01/03/04/05) all free to explain the three-layer
    # model; they overlapped 67-85%. Split by layer and by design choice.
    {"id": "01_01", "topic": "Hierarchical Network Design and Why Layers Exist"},
    {"id": "01_02", "topic": "The Access Layer: Role and Design Requirements"},
    {"id": "01_03", "topic": "The Distribution Layer: Role and Design Requirements"},
    {"id": "01_04", "topic": "The Core Layer and When a Network Needs One"},
    {"id": "01_05", "topic": "Two-Tier Collapsed Core Design"},
    {"id": "01_06", "topic": "Three-Tier Design and What Justifies the Extra Layer"},
    {"id": "01_07", "topic": "Spine-Leaf Fabric Design"},
    {"id": "01_08", "topic": "Cisco Enterprise Architecture Model and Network Modules"},
    {"id": "01_09", "topic": "Layer 2 Access Design and Its Dependence on STP"},
    {"id": "01_10", "topic": "Routed Access Design: Moving Layer 3 to the Edge"},
    {"id": "01_11", "topic": "Comparing Layer 2 Access and Routed Access Trade-offs"},
    {"id": "01_12", "topic": "Switch Stacking with StackWise"},
    {"id": "01_13", "topic": "VSS and StackWise Virtual"},
    {"id": "01_14", "topic": "Multichassis EtherChannel in Campus Design"},
    {"id": "01_15", "topic": "High Availability: Stateful Switchover (SSO)"},
    {"id": "01_16", "topic": "High Availability: Nonstop Forwarding and Graceful Restart"},
    {"id": "01_17", "topic": "On-Premises versus Cloud Deployment Models"},
    {"id": "01_18", "topic": "Cloud Service Models: IaaS, PaaS and SaaS"},

    # -- 02: Switching Hardware and Forwarding --
    # v1 spread CEF across 01_07/01_08/01_24 with 67-72% overlap. One
    # mechanism per topic instead.
    {"id": "02_01", "topic": "Control Plane, Data Plane and Management Plane"},
    {"id": "02_02", "topic": "Process Switching and Why It Is Slow"},
    {"id": "02_03", "topic": "Fast Switching and the Route Cache"},
    {"id": "02_04", "topic": "Cisco Express Forwarding: The Forwarding Model"},
    {"id": "02_05", "topic": "The CEF Forwarding Information Base"},
    {"id": "02_06", "topic": "The CEF Adjacency Table"},
    {"id": "02_07", "topic": "TCAM: How Ternary Matching Works in Hardware"},
    {"id": "02_08", "topic": "TCAM Allocation and SDM Templates"},
    {"id": "02_09", "topic": "Exception Punting: When Traffic Reaches the CPU"},
    {"id": "02_10", "topic": "Diagnosing Hardware Forwarding and Performance Limits"},

    # -- 03: VLANs and Trunking --
    {"id": "03_01", "topic": "VLAN Fundamentals and Broadcast Domain Design"},
    {"id": "03_02", "topic": "Configuring VLANs and Access Ports"},
    {"id": "03_03", "topic": "802.1Q Trunk Encapsulation and Frame Tagging"},
    {"id": "03_04", "topic": "Native VLAN Behaviour and Mismatch Risks"},
    {"id": "03_05", "topic": "Dynamic Trunking Protocol and Trunk Negotiation"},
    {"id": "03_06", "topic": "VTP Modes, Versions and Revision Number Risks"},
    {"id": "03_07", "topic": "Inter-VLAN Routing with Switched Virtual Interfaces"},
    {"id": "03_08", "topic": "Routed Ports on Layer 3 Switches"},
    {"id": "03_09", "topic": "Troubleshooting VLAN and Trunk Connectivity"},

    # -- 04: Spanning Tree --
    # v1's 01_11 bundled five features and overlapped 01_12/01_14 by 75%.
    {"id": "04_01", "topic": "Layer 2 Loops and the Problem Spanning Tree Solves"},
    {"id": "04_02", "topic": "The Bridge ID and Root Bridge Election"},
    {"id": "04_03", "topic": "Root Port Selection and Path Cost"},
    {"id": "04_04", "topic": "Designated Port Selection"},
    {"id": "04_05", "topic": "Classic STP Port States and Timers"},
    {"id": "04_06", "topic": "RSTP Port Roles and Port States"},
    {"id": "04_07", "topic": "The RSTP Proposal and Agreement Handshake"},
    {"id": "04_08", "topic": "RSTP Topology Change Handling"},
    {"id": "04_09", "topic": "MSTP Instances and Region Configuration"},
    {"id": "04_10", "topic": "MSTP Boundary Behaviour with RSTP and PVST+"},
    {"id": "04_11", "topic": "PortFast and Edge Ports"},
    {"id": "04_12", "topic": "BPDU Guard"},
    {"id": "04_13", "topic": "BPDU Filter"},
    {"id": "04_14", "topic": "Root Guard"},
    {"id": "04_15", "topic": "Loop Guard and UDLD"},
    {"id": "04_16", "topic": "Troubleshooting Spanning Tree Convergence"},

    # -- 05: EtherChannel --
    {"id": "05_01", "topic": "EtherChannel Concepts and Bundling Requirements"},
    {"id": "05_02", "topic": "LACP Negotiation and Modes"},
    {"id": "05_03", "topic": "PAgP Negotiation and Modes"},
    {"id": "05_04", "topic": "Static On Mode and the Risks of Skipping Negotiation"},
    {"id": "05_05", "topic": "EtherChannel Load Balancing Hash Algorithms"},
    {"id": "05_06", "topic": "Traffic Polarization and Hash Tuning"},
    {"id": "05_07", "topic": "Layer 3 EtherChannel"},
    {"id": "05_08", "topic": "Troubleshooting EtherChannel Bundling Failures"},

    # -- 06: Routing Fundamentals and Path Control --
    {"id": "06_01", "topic": "The Routing Table and Route Selection Order"},
    {"id": "06_02", "topic": "Administrative Distance"},
    {"id": "06_03", "topic": "Longest Prefix Match"},
    {"id": "06_04", "topic": "Comparing Routing Protocol Metrics"},
    {"id": "06_05", "topic": "Static Routes, Default Routes and Floating Statics"},
    {"id": "06_06", "topic": "Route Redistribution Fundamentals"},
    {"id": "06_07", "topic": "Route Maps: Structure and Processing Logic"},
    {"id": "06_08", "topic": "Prefix Lists for Route Filtering"},
    {"id": "06_09", "topic": "Policy-Based Routing"},
    {"id": "06_10", "topic": "VRF-Lite: Separating Routing Tables on One Device"},

    # -- 07: EIGRP --
    {"id": "07_01", "topic": "EIGRP Neighbor Discovery and Adjacency Requirements"},
    {"id": "07_02", "topic": "EIGRP Metric Components and K-Values"},
    {"id": "07_03", "topic": "The DUAL Algorithm"},
    {"id": "07_04", "topic": "Feasible Distance, Reported Distance and the Feasibility Condition"},
    {"id": "07_05", "topic": "Successors and Feasible Successors"},
    {"id": "07_06", "topic": "The EIGRP Query Process and Stuck-In-Active"},
    {"id": "07_07", "topic": "EIGRP Summarization and Stub Routing"},
    {"id": "07_08", "topic": "Configuring and Verifying EIGRP"},
    {"id": "07_09", "topic": "Troubleshooting EIGRP Neighbor and Route Problems"},

    # -- 08: OSPF --
    # v1 collapsed all LSA types into one topic; each gets its own here.
    {"id": "08_01", "topic": "OSPF Link-State Operation and the Link-State Database"},
    {"id": "08_02", "topic": "OSPF Router ID Selection"},
    {"id": "08_03", "topic": "OSPF Areas and Router Roles"},
    {"id": "08_04", "topic": "OSPF Hello Packets and Neighbor Requirements"},
    {"id": "08_05", "topic": "OSPF Neighbor States and Adjacency Formation"},
    {"id": "08_06", "topic": "OSPF Network Types"},
    {"id": "08_07", "topic": "DR and BDR Election on Multi-Access Networks"},
    {"id": "08_08", "topic": "OSPF Cost and Reference Bandwidth"},
    {"id": "08_09", "topic": "LSA Type 1: Router LSA"},
    {"id": "08_10", "topic": "LSA Type 2: Network LSA"},
    {"id": "08_11", "topic": "LSA Type 3 and Inter-Area Route Propagation"},
    {"id": "08_12", "topic": "LSA Type 4 and Type 5: External Routes and the ASBR"},
    {"id": "08_13", "topic": "LSA Type 7 and NSSA Translation"},
    {"id": "08_14", "topic": "Stub and Totally Stubby Areas"},
    {"id": "08_15", "topic": "OSPF Summarization at the ABR and ASBR"},
    {"id": "08_16", "topic": "SPF Calculation and Throttle Timers"},
    {"id": "08_17", "topic": "OSPFv3 for IPv6"},
    {"id": "08_18", "topic": "Troubleshooting OSPF Adjacency Failures"},

    # -- 09: BGP --
    {"id": "09_01", "topic": "BGP Fundamentals: eBGP versus iBGP"},
    {"id": "09_02", "topic": "The BGP Finite State Machine"},
    {"id": "09_03", "topic": "BGP Message Types"},
    {"id": "09_04", "topic": "BGP Neighbor Establishment and Troubleshooting"},
    {"id": "09_05", "topic": "Well-Known and Optional Path Attributes"},
    {"id": "09_06", "topic": "Weight and Local Preference"},
    {"id": "09_07", "topic": "AS Path and Origin"},
    {"id": "09_08", "topic": "MED and Community Attributes"},
    {"id": "09_09", "topic": "The BGP Best Path Selection Algorithm"},
    {"id": "09_10", "topic": "Influencing Inbound and Outbound Path Selection"},
    {"id": "09_11", "topic": "Configuring and Verifying eBGP"},

    # -- 10: First Hop Redundancy and Internet Edge --
    {"id": "10_01", "topic": "First Hop Redundancy Concepts"},
    {"id": "10_02", "topic": "HSRP Operation, Priority and Preemption"},
    {"id": "10_03", "topic": "VRRP Operation and How It Differs from HSRP"},
    {"id": "10_04", "topic": "GLBP and Active Load Sharing"},
    {"id": "10_05", "topic": "FHRP Object Tracking"},
    {"id": "10_06", "topic": "NAT Concepts and Address Terminology"},
    {"id": "10_07", "topic": "Static and Dynamic NAT"},
    {"id": "10_08", "topic": "PAT and Port Translation"},
    {"id": "10_09", "topic": "Enterprise Internet Edge Design"},
    {"id": "10_10", "topic": "DHCP Server, Client and Relay Operation"},

    # -- 11: Tunnels and Network Overlays --
    # v1's VXLAN overview and deep dive overlapped 70%; split by mechanism.
    {"id": "11_01", "topic": "GRE Tunnel Operation and Configuration"},
    {"id": "11_02", "topic": "Tunnel MTU, Fragmentation and MSS Adjustment"},
    {"id": "11_03", "topic": "IPsec Fundamentals: AH and ESP"},
    {"id": "11_04", "topic": "IKE Phases and Diffie-Hellman Groups"},
    {"id": "11_05", "topic": "GRE over IPsec"},
    {"id": "11_06", "topic": "Comparing Site-to-Site VPN Technologies"},
    {"id": "11_07", "topic": "LISP Architecture and Component Roles"},
    {"id": "11_08", "topic": "The LISP Map-Request and Map-Reply Flow"},
    {"id": "11_09", "topic": "LISP Map Cache and PxTR Interworking"},
    {"id": "11_10", "topic": "VXLAN Encapsulation Format and the VNI"},
    {"id": "11_11", "topic": "VXLAN VTEPs and Data Plane Forwarding"},
    {"id": "11_12", "topic": "VXLAN MTU Impact and Anycast Gateway"},

    # -- 12: Compute Virtualization --
    {"id": "12_01", "topic": "Server Virtualization Fundamentals"},
    {"id": "12_02", "topic": "Type-1 and Type-2 Hypervisors"},
    {"id": "12_03", "topic": "Virtual Machines and Resource Allocation"},
    {"id": "12_04", "topic": "Virtual Switching and VM Connectivity"},
    {"id": "12_05", "topic": "Containers versus Virtual Machines"},
    {"id": "12_06", "topic": "Network Functions Virtualization"},
    {"id": "12_07", "topic": "Virtualization Overhead and Hardware Abstraction"},

    # -- 13: Wireless --
    {"id": "13_01", "topic": "RF Fundamentals and Signal Behaviour"},
    {"id": "13_02", "topic": "802.11 Standards and Modulation"},
    {"id": "13_03", "topic": "Channel Planning and Interference Management"},
    {"id": "13_04", "topic": "Antenna Types and Coverage Patterns"},
    {"id": "13_05", "topic": "Autonomous, Cloud and Split-MAC Architectures"},
    {"id": "13_06", "topic": "CAPWAP Control and Data Tunnels"},
    {"id": "13_07", "topic": "Access Point Modes and Deployment Options"},
    {"id": "13_08", "topic": "The AP Join Process and WLC Discovery"},
    {"id": "13_09", "topic": "Intra-Controller Roaming"},
    {"id": "13_10", "topic": "Inter-Controller Layer 2 and Layer 3 Roaming"},
    {"id": "13_11", "topic": "Location Services and Client Tracking"},
    {"id": "13_12", "topic": "Wireless Client Authentication Methods"},
    {"id": "13_13", "topic": "WPA2 and WPA3 Security"},
    {"id": "13_14", "topic": "Troubleshooting Wireless Client Connectivity"},

    # -- 14: Multicast --
    # v1's 05_02 listed six mechanisms in one title; one each here.
    {"id": "14_01", "topic": "Multicast Addressing and Layer 2 MAC Mapping"},
    {"id": "14_02", "topic": "IGMPv2 Operation"},
    {"id": "14_03", "topic": "IGMPv3 and Source-Specific Multicast"},
    {"id": "14_04", "topic": "IGMP Snooping"},
    {"id": "14_05", "topic": "The Reverse Path Forwarding Check"},
    {"id": "14_06", "topic": "PIM Dense Mode"},
    {"id": "14_07", "topic": "PIM Sparse Mode and the Rendezvous Point"},
    {"id": "14_08", "topic": "The PIM Register Process and SPT Switchover"},
    {"id": "14_09", "topic": "PIM Designated Router Election"},
    {"id": "14_10", "topic": "The PIM Assert Mechanism"},
    {"id": "14_11", "topic": "Bidirectional PIM"},
    {"id": "14_12", "topic": "MSDP and Inter-Domain Multicast"},
    {"id": "14_13", "topic": "RP Discovery: Static, Auto-RP and BSR"},

    # -- 15: Quality of Service --
    {"id": "15_01", "topic": "QoS Requirements: Delay, Jitter and Loss"},
    {"id": "15_02", "topic": "Traffic Classification and NBAR"},
    {"id": "15_03", "topic": "Marking with DSCP, IP Precedence and CoS"},
    {"id": "15_04", "topic": "Trust Boundaries"},
    {"id": "15_05", "topic": "Queuing and Class-Based Weighted Fair Queuing"},
    {"id": "15_06", "topic": "Low Latency Queuing for Voice"},
    {"id": "15_07", "topic": "Policing and the Token Bucket Algorithm"},
    {"id": "15_08", "topic": "Traffic Shaping and Contract Enforcement"},
    {"id": "15_09", "topic": "Congestion Avoidance with WRED"},
    {"id": "15_10", "topic": "QoS Models: IntServ and DiffServ"},
    {"id": "15_11", "topic": "Interpreting an MQC QoS Configuration"},

    # -- 16: Network Assurance and Monitoring --
    # v1 bundled Syslog/SNMP/NetFlow/FNF into one topic and Ping/Traceroute/
    # Debug into another; both overlapped their deep dives.
    {"id": "16_01", "topic": "Syslog Severity Levels and Message Structure"},
    {"id": "16_02", "topic": "SNMP Versions and Security Models"},
    {"id": "16_03", "topic": "NetFlow Concepts and Flow Records"},
    {"id": "16_04", "topic": "Flexible NetFlow Configuration"},
    {"id": "16_05", "topic": "Model-Driven Telemetry and gRPC"},
    {"id": "16_06", "topic": "IPFIX and Telemetry Data Formats"},
    {"id": "16_07", "topic": "NTP Operation and Stratum Hierarchy"},
    {"id": "16_08", "topic": "PTP and Precision Timing"},
    {"id": "16_09", "topic": "IP SLA Operations and Thresholds"},
    {"id": "16_10", "topic": "SPAN and RSPAN"},
    {"id": "16_11", "topic": "ERSPAN"},
    {"id": "16_12", "topic": "EEM Applets and Event Detectors"},
    {"id": "16_13", "topic": "EEM Actions and AAA Command Authorization Interaction"},
    {"id": "16_14", "topic": "Debug and Conditional Debug"},
    {"id": "16_15", "topic": "Interpreting Ping and Traceroute Output"},
    {"id": "16_16", "topic": "A Structured Troubleshooting Methodology"},

    # -- 17: Infrastructure Security --
    {"id": "17_01", "topic": "Standard and Extended Access Control Lists"},
    {"id": "17_02", "topic": "Named and Time-Based ACLs"},
    {"id": "17_03", "topic": "ACL Placement and Troubleshooting"},
    {"id": "17_04", "topic": "Control Plane Policing Concepts"},
    {"id": "17_05", "topic": "Configuring CoPP Policies"},
    {"id": "17_06", "topic": "Device Access Hardening"},
    {"id": "17_07", "topic": "Line Configuration and Local User Authentication"},
    {"id": "17_08", "topic": "Password Management and Encryption Types"},

    # -- 18: Identity and Access Control --
    # v1's AAA Framework and RADIUS/TACACS+ topics overlapped 70%.
    {"id": "18_01", "topic": "The AAA Framework: Authentication, Authorization and Accounting"},
    {"id": "18_02", "topic": "RADIUS Operation and Message Flow"},
    {"id": "18_03", "topic": "TACACS+ Operation and How It Differs from RADIUS"},
    {"id": "18_04", "topic": "802.1X Components and the EAP Exchange"},
    {"id": "18_05", "topic": "Comparing EAP Methods"},
    {"id": "18_06", "topic": "MAC Authentication Bypass"},
    {"id": "18_07", "topic": "Web Authentication"},
    {"id": "18_08", "topic": "RADIUS Change of Authorization"},
    {"id": "18_09", "topic": "FlexAuth and the Access Session Manager"},
    {"id": "18_10", "topic": "Cisco ISE Architecture and Personas"},
    {"id": "18_11", "topic": "ISE Policy Sets and Authorization Profiles"},

    # -- 19: Security Architecture --
    {"id": "19_01", "topic": "Threat Landscape and Attack Categories"},
    {"id": "19_02", "topic": "Layer 2 Attacks and Their Mitigations"},
    {"id": "19_03", "topic": "Firewall Types and NGFW Capabilities"},
    {"id": "19_04", "topic": "IPS and Threat Detection"},
    {"id": "19_05", "topic": "Endpoint Security and EDR"},
    {"id": "19_06", "topic": "Zero Trust Principles"},
    {"id": "19_07", "topic": "SASE Architecture"},
    {"id": "19_08", "topic": "MACsec Operation and Frame Format"},
    {"id": "19_09", "topic": "MACsec Key Agreement and AES-GCM Encryption"},
    {"id": "19_10", "topic": "TrustSec Security Group Tags"},
    {"id": "19_11", "topic": "SGT Propagation: Inline Tagging and SXP"},
    {"id": "19_12", "topic": "TrustSec Policy Enforcement"},
    {"id": "19_13", "topic": "REST API Security Considerations"},

    # -- 20: Cisco SD-Access --
    {"id": "20_01", "topic": "SD-Access Solution Overview and Value"},
    {"id": "20_02", "topic": "Fabric Roles: Edge, Border and Control Plane Nodes"},
    {"id": "20_03", "topic": "LISP as the SD-Access Control Plane"},
    {"id": "20_04", "topic": "VXLAN as the SD-Access Data Plane"},
    {"id": "20_05", "topic": "TrustSec as the SD-Access Policy Plane"},
    {"id": "20_06", "topic": "Underlay Design and LAN Automation"},
    {"id": "20_07", "topic": "Virtual Networks and Macro-Segmentation"},
    {"id": "20_08", "topic": "SGT-Based Micro-Segmentation Inside the Fabric"},
    {"id": "20_09", "topic": "Wireless Integration in SD-Access"},
    {"id": "20_10", "topic": "Interoperating with a Traditional Campus"},
    {"id": "20_11", "topic": "Catalyst Center Architecture"},
    {"id": "20_12", "topic": "Catalyst Center Assurance and Analytics"},
    {"id": "20_13", "topic": "Catalyst Center Workflows and Provisioning"},

    # -- 21: Cisco SD-WAN --
    # v1 had eleven SD-WAN topics overlapping 65-72%; one plane per topic.
    {"id": "21_01", "topic": "SD-WAN Solution Overview and Benefits"},
    {"id": "21_02", "topic": "The Four Planes of Cisco SD-WAN"},
    {"id": "21_03", "topic": "vBond and the Orchestration Plane"},
    {"id": "21_04", "topic": "vSmart and the Control Plane"},
    {"id": "21_05", "topic": "vManage and the Management Plane"},
    {"id": "21_06", "topic": "WAN Edge Routers and the Data Plane"},
    {"id": "21_07", "topic": "OMP Route Advertisement"},
    {"id": "21_08", "topic": "TLOC Structure and Colors"},
    {"id": "21_09", "topic": "Zero-Touch Provisioning"},
    {"id": "21_10", "topic": "NAT Traversal and DTLS Tunnel Establishment"},
    {"id": "21_11", "topic": "SD-WAN Control Policies"},
    {"id": "21_12", "topic": "SD-WAN Data Policies"},
    {"id": "21_13", "topic": "Application-Aware Routing"},
    {"id": "21_14", "topic": "SD-WAN Design Limitations and Considerations"},

    # -- 22: Automation and Programmability --
    {"id": "22_01", "topic": "Python Data Types for Network Automation"},
    {"id": "22_02", "topic": "Python Control Flow and Functions"},
    {"id": "22_03", "topic": "JSON Structure and Parsing"},
    {"id": "22_04", "topic": "XML and YAML Compared to JSON"},
    {"id": "22_05", "topic": "YANG Data Models and Module Structure"},
    {"id": "22_06", "topic": "NETCONF Operations and Datastores"},
    {"id": "22_07", "topic": "RESTCONF and Its HTTP Mapping"},
    {"id": "22_08", "topic": "REST API Methods and Idempotency"},
    {"id": "22_09", "topic": "HTTP Response Codes and Error Handling"},
    {"id": "22_10", "topic": "API Authentication: Basic, Token and Session"},
    {"id": "22_11", "topic": "Catalyst Center API Structure"},
    {"id": "22_12", "topic": "SD-WAN Manager API Structure"},
    {"id": "22_13", "topic": "Ansible for Network Configuration"},
    {"id": "22_14", "topic": "Puppet, Chef and Agent-Based Tools"},
    {"id": "22_15", "topic": "CI/CD Concepts for Network Configuration"},
]
