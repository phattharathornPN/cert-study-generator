# -*- coding: utf-8 -*-
"""CCNA 200-301 study pack.

Design rule: one topic teaches one thing. A title like "OSI and TCP/IP
Models, Encapsulation and Decapsulation" reads fine on a syllabus but
generates a summary that skims all three, so the OSI layers never actually
get taught. Every entry below names a single mechanism, and anything that
needed an "and" got split.

Ordering is teaching order, not the exam blueprint's order: concepts before
configuration, addressing before routing, Layer 2 before Layer 3. Sections
build on the ones before them, so working straight down the list never
requires knowledge that has not been covered yet.

Only slide.pdf is downloaded: the reader site uses the PDF, so generating
.pptx would double the time and disk for a file nothing reads.
"""

EXAM_NAME = "CCNA 200-301"
OUTPUT_DIR = "CCNA/output"
SITE_DIR = "CCNA"    # index.html sits beside its own output/
DIST_DIR = "CCNA/dist"
NOTEBOOK_ENV = "NOTEBOOK_ID_CCNA"
SLIDE_FORMATS = ("pdf",)

SECTION_TITLES = {
    "01": "Networking Concepts",
    "02": "Physical Layer and Cabling",
    "03": "Ethernet and Layer 2 Switching",
    "04": "Cisco IOS and Device Basics",
    "05": "IPv4 Addressing and Subnetting",
    "06": "IPv6 Addressing",
    "07": "Transport and Application Layer",
    "08": "VLANs and Trunking",
    "09": "Spanning Tree and EtherChannel",
    "10": "Routing Fundamentals and Static Routing",
    "11": "OSPF",
    "12": "Redundancy and WAN Connectivity",
    "13": "NAT and Access Control Lists",
    "14": "IP Services and Network Management",
    "15": "Quality of Service",
    "16": "Wireless Networking",
    "17": "Architecture and Virtualization",
    "18": "Security Fundamentals",
    "19": "Secure Access and Device Hardening",
    "20": "Automation and Programmability",
}


from certs._shared import networking_slide_instructions, networking_summary_prompt


def SLIDE_INSTRUCTIONS(topic: str) -> str:
    return networking_slide_instructions(EXAM_NAME, topic)


def SUMMARY_PROMPT(topic: str) -> str:
    return networking_summary_prompt(EXAM_NAME, topic)


TOPICS = [
    # -- 01: Networking Concepts --
    {"id": "01_01", "topic": "What a Network Is: Components, Topologies and Terminology"},
    {"id": "01_02", "topic": "The OSI Seven-Layer Model: What Each Layer Does"},
    {"id": "01_03", "topic": "The TCP/IP Model and How It Maps to OSI"},
    {"id": "01_04", "topic": "Encapsulation and De-encapsulation as Data Crosses the Layers"},
    {"id": "01_05", "topic": "Protocol Data Units: Bits, Frames, Packets and Segments"},
    {"id": "01_06", "topic": "Hubs, Switches and Routers: What Each Device Decides"},
    {"id": "01_07", "topic": "Firewalls and Next-Generation Firewalls"},
    {"id": "01_08", "topic": "Intrusion Prevention and Detection Systems"},
    {"id": "01_09", "topic": "Access Points, Wireless LAN Controllers and Endpoints"},
    {"id": "01_10", "topic": "LAN, WAN and Small Office Network Types"},

    # -- 02: Physical Layer and Cabling --
    {"id": "02_01", "topic": "Copper Cabling: UTP Categories and Ethernet Standards"},
    {"id": "02_02", "topic": "Straight-Through versus Crossover Cables and Auto-MDIX"},
    {"id": "02_03", "topic": "Fiber Optic Cabling: Single-Mode versus Multimode"},
    {"id": "02_04", "topic": "Choosing a Transmission Medium for a Given Requirement"},
    {"id": "02_05", "topic": "Interface Speed, Duplex and Auto-Negotiation"},
    {"id": "02_06", "topic": "Duplex Mismatch: Symptoms and Diagnosis"},
    {"id": "02_07", "topic": "Reading Interface Error Counters: Collisions, Runts, Giants and CRC"},

    # -- 03: Ethernet and Layer 2 Switching --
    {"id": "03_01", "topic": "The Ethernet Frame: Fields and Their Purpose"},
    {"id": "03_02", "topic": "MAC Addresses: Format, OUI and Address Types"},
    {"id": "03_03", "topic": "How a Switch Builds Its MAC Address Table"},
    {"id": "03_04", "topic": "Switch Forwarding Decisions: Forward, Filter and Flood"},
    {"id": "03_05", "topic": "Collision Domains versus Broadcast Domains"},
    {"id": "03_06", "topic": "The ARP Process: Resolving an IP Address to a MAC Address"},
    {"id": "03_07", "topic": "Cisco Discovery Protocol: Operation and Verification"},
    {"id": "03_08", "topic": "Link Layer Discovery Protocol and How It Differs from CDP"},

    # -- 04: Cisco IOS and Device Basics --
    {"id": "04_01", "topic": "Cisco IOS Command Modes and Navigating Between Them"},
    {"id": "04_02", "topic": "IOS Context-Sensitive Help, Editing and Command Shortcuts"},
    {"id": "04_03", "topic": "Initial Switch Setup: Hostname, Passwords and Management IP"},
    {"id": "04_04", "topic": "Initial Router Setup and Bringing Up Interfaces"},
    {"id": "04_05", "topic": "Running Configuration versus Startup Configuration"},
    {"id": "04_06", "topic": "Backing Up and Restoring Device Configurations"},
    {"id": "04_07", "topic": "The Cisco Device Boot Process and Configuration Register"},
    {"id": "04_08", "topic": "Upgrading Cisco IOS Images with TFTP and FTP"},
    {"id": "04_09", "topic": "Password Recovery on a Cisco Device"},

    # -- 05: IPv4 Addressing and Subnetting --
    {"id": "05_01", "topic": "The IPv4 Header and Its Key Fields"},
    {"id": "05_02", "topic": "IPv4 Address Structure: Network and Host Portions"},
    {"id": "05_03", "topic": "IPv4 Address Classes and Classful Addressing"},
    {"id": "05_04", "topic": "Public, Private and Reserved IPv4 Address Ranges"},
    {"id": "05_05", "topic": "Subnet Masks and Prefix Length Notation"},
    {"id": "05_06", "topic": "Binary Conversion for Subnetting"},
    {"id": "05_07", "topic": "Finding the Network Address, Broadcast Address and Host Range"},
    {"id": "05_08", "topic": "Calculating How Many Subnets and Hosts a Mask Provides"},
    {"id": "05_09", "topic": "Subnetting Shortcuts for Working Under Exam Time Pressure"},
    {"id": "05_10", "topic": "VLSM: Sizing Each Subnet to Its Actual Need"},
    {"id": "05_11", "topic": "Route Summarization and CIDR Notation"},
    {"id": "05_12", "topic": "Verifying IP Configuration on Windows, macOS and Linux"},

    # -- 06: IPv6 Addressing --
    {"id": "06_01", "topic": "Why IPv6 Exists: The Limits of IPv4"},
    {"id": "06_02", "topic": "IPv6 Address Format and Compression Rules"},
    {"id": "06_03", "topic": "IPv6 Global Unicast Addresses and Prefix Structure"},
    {"id": "06_04", "topic": "IPv6 Link-Local Addresses and Their Role"},
    {"id": "06_05", "topic": "IPv6 Unique Local Addresses"},
    {"id": "06_06", "topic": "IPv6 Multicast and Solicited-Node Addresses"},
    {"id": "06_07", "topic": "IPv6 Anycast Addressing"},
    {"id": "06_08", "topic": "Configuring Static IPv6 Addresses on Cisco Devices"},
    {"id": "06_09", "topic": "SLAAC and EUI-64 Address Generation"},
    {"id": "06_10", "topic": "DHCPv6: Stateless versus Stateful"},
    {"id": "06_11", "topic": "IPv6 Neighbor Discovery Protocol"},
    {"id": "06_12", "topic": "Running IPv4 and IPv6 Together with Dual Stack"},

    # -- 07: Transport and Application Layer --
    {"id": "07_01", "topic": "The TCP Header and How Reliability Works"},
    {"id": "07_02", "topic": "The TCP Three-Way Handshake and Connection Teardown"},
    {"id": "07_03", "topic": "TCP Windowing and Flow Control"},
    {"id": "07_04", "topic": "UDP and When Speed Matters More Than Reliability"},
    {"id": "07_05", "topic": "Port Numbers, Sockets and Well-Known Services"},
    {"id": "07_06", "topic": "DNS: Record Types and the Resolution Process"},
    {"id": "07_07", "topic": "DHCP: The DORA Process and Lease Lifecycle"},

    # -- 08: VLANs and Trunking --
    {"id": "08_01", "topic": "VLAN Concepts: Segmenting a Switched Network"},
    {"id": "08_02", "topic": "Creating VLANs and Assigning Access Ports"},
    {"id": "08_03", "topic": "Voice VLANs and Connecting IP Phones"},
    {"id": "08_04", "topic": "802.1Q Trunking and How Frames Are Tagged"},
    {"id": "08_05", "topic": "The Native VLAN and Why It Matters"},
    {"id": "08_06", "topic": "Controlling Which VLANs Cross a Trunk"},
    {"id": "08_07", "topic": "Dynamic Trunking Protocol and Why It Is Usually Disabled"},
    {"id": "08_08", "topic": "Troubleshooting VLAN and Trunk Connectivity"},

    # -- 09: Spanning Tree and EtherChannel --
    {"id": "09_01", "topic": "Layer 2 Loops and Broadcast Storms: The Problem STP Solves"},
    {"id": "09_02", "topic": "The Bridge ID and Root Bridge Election"},
    {"id": "09_03", "topic": "STP Port Roles: Root, Designated and Blocking"},
    {"id": "09_04", "topic": "STP Port States and Timers"},
    {"id": "09_05", "topic": "STP Path Cost and Selecting the Root Port"},
    {"id": "09_06", "topic": "Influencing STP with Priority and Cost Tuning"},
    {"id": "09_07", "topic": "Rapid PVST+ and Faster Convergence"},
    {"id": "09_08", "topic": "PortFast: Skipping the Listening and Learning States"},
    {"id": "09_09", "topic": "BPDU Guard and Protecting the Edge"},
    {"id": "09_10", "topic": "Troubleshooting a Spanning Tree Topology"},
    {"id": "09_11", "topic": "EtherChannel Concepts and Configuration Requirements"},
    {"id": "09_12", "topic": "Negotiating EtherChannel with LACP"},
    {"id": "09_13", "topic": "Negotiating EtherChannel with PAgP and Static On Mode"},
    {"id": "09_14", "topic": "EtherChannel Load Balancing and Verification"},

    # -- 10: Routing Fundamentals and Static Routing --
    {"id": "10_01", "topic": "How a Router Forwards a Packet"},
    {"id": "10_02", "topic": "Reading the IP Routing Table"},
    {"id": "10_03", "topic": "Connected Routes, Local Routes and Route Sources"},
    {"id": "10_04", "topic": "Longest Prefix Match in Practice"},
    {"id": "10_05", "topic": "Administrative Distance: Choosing Between Route Sources"},
    {"id": "10_06", "topic": "Routing Metrics and Best Path Selection"},
    {"id": "10_07", "topic": "Configuring IPv4 Static Routes"},
    {"id": "10_08", "topic": "Default Routes and the Gateway of Last Resort"},
    {"id": "10_09", "topic": "Host Routes and Fully Specified Static Routes"},
    {"id": "10_10", "topic": "Floating Static Routes for Backup Paths"},
    {"id": "10_11", "topic": "Configuring IPv6 Static Routes"},
    {"id": "10_12", "topic": "Troubleshooting Static Routing and Recursive Lookups"},
    {"id": "10_13", "topic": "Inter-VLAN Routing with Router-on-a-Stick"},
    {"id": "10_14", "topic": "Inter-VLAN Routing with Layer 3 Switch SVIs"},

    # -- 11: OSPF --
    {"id": "11_01", "topic": "Link-State Routing and the OSPF Link-State Database"},
    {"id": "11_02", "topic": "OSPF Areas and Router Roles"},
    {"id": "11_03", "topic": "How OSPF Chooses Its Router ID"},
    {"id": "11_04", "topic": "OSPF Cost and Reference Bandwidth"},
    {"id": "11_05", "topic": "OSPF Hello Packets and Neighbor Requirements"},
    {"id": "11_06", "topic": "OSPF Neighbor States and Reaching Full Adjacency"},
    {"id": "11_07", "topic": "OSPF Network Types: Broadcast and Point-to-Point"},
    {"id": "11_08", "topic": "DR and BDR Election on Multi-Access Networks"},
    {"id": "11_09", "topic": "Configuring Single-Area OSPFv2 with the network Command"},
    {"id": "11_10", "topic": "Configuring OSPF with Interface-Level Commands"},
    {"id": "11_11", "topic": "OSPF Passive Interfaces"},
    {"id": "11_12", "topic": "Tuning OSPF Hello and Dead Timers"},
    {"id": "11_13", "topic": "Verifying OSPF with show Commands"},
    {"id": "11_14", "topic": "Troubleshooting OSPF Adjacency Failures"},

    # -- 12: Redundancy and WAN Connectivity --
    {"id": "12_01", "topic": "Why Default Gateway Redundancy Is Needed"},
    {"id": "12_02", "topic": "HSRP Roles, Virtual IP and Virtual MAC"},
    {"id": "12_03", "topic": "HSRP Priority, Preemption and Failover Behavior"},
    {"id": "12_04", "topic": "Configuring and Verifying HSRP"},
    {"id": "12_05", "topic": "WAN Technologies: Leased Lines, MPLS and Broadband"},
    {"id": "12_06", "topic": "Site-to-Site VPN Concepts"},
    {"id": "12_07", "topic": "Remote Access VPN Concepts"},
    {"id": "12_08", "topic": "Provider-Managed MPLS VPN Services"},

    # -- 13: NAT and Access Control Lists --
    {"id": "13_01", "topic": "Why NAT Exists and the Inside/Outside Terminology"},
    {"id": "13_02", "topic": "Configuring Static NAT"},
    {"id": "13_03", "topic": "Configuring Dynamic NAT with an Address Pool"},
    {"id": "13_04", "topic": "Configuring PAT and How Port Translation Works"},
    {"id": "13_05", "topic": "Verifying and Troubleshooting NAT Translations"},
    {"id": "13_06", "topic": "How an ACL Processes Traffic: Order and Implicit Deny"},
    {"id": "13_07", "topic": "Wildcard Masks: Reading and Writing Them"},
    {"id": "13_08", "topic": "Configuring Standard ACLs"},
    {"id": "13_09", "topic": "Configuring Extended ACLs by Protocol and Port"},
    {"id": "13_10", "topic": "Named ACLs and Editing Existing Entries"},
    {"id": "13_11", "topic": "Where to Place an ACL and in Which Direction"},
    {"id": "13_12", "topic": "Troubleshooting Traffic Blocked by an ACL"},

    # -- 14: IP Services and Network Management --
    {"id": "14_01", "topic": "NTP and Keeping Device Clocks Synchronized"},
    {"id": "14_02", "topic": "Configuring a Cisco Router as a DHCP Server"},
    {"id": "14_03", "topic": "DHCP Relay with ip helper-address"},
    {"id": "14_04", "topic": "Syslog Severity Levels and Log Destinations"},
    {"id": "14_05", "topic": "SNMP Components, Versions and Security"},
    {"id": "14_06", "topic": "Configuring SSH for Secure Device Management"},
    {"id": "14_07", "topic": "Using ping and traceroute to Isolate Problems"},
    {"id": "14_08", "topic": "Using debug Safely on Production Devices"},
    {"id": "14_09", "topic": "A Structured Troubleshooting Methodology"},

    # -- 15: Quality of Service --
    {"id": "15_01", "topic": "What QoS Solves: Bandwidth, Delay, Jitter and Loss"},
    {"id": "15_02", "topic": "Traffic Classification"},
    {"id": "15_03", "topic": "Marking with DSCP, IP Precedence and CoS"},
    {"id": "15_04", "topic": "Trust Boundaries and Where to Mark Traffic"},
    {"id": "15_05", "topic": "Queuing and Congestion Management"},
    {"id": "15_06", "topic": "Traffic Shaping versus Policing"},
    {"id": "15_07", "topic": "Congestion Avoidance and WRED"},
    {"id": "15_08", "topic": "QoS Models: Best Effort, IntServ and DiffServ"},
    {"id": "15_09", "topic": "Designing End-to-End QoS Policy"},

    # -- 16: Wireless Networking --
    {"id": "16_01", "topic": "Radio Frequency Fundamentals and Signal Behavior"},
    {"id": "16_02", "topic": "802.11 Standards and Their Data Rates"},
    {"id": "16_03", "topic": "The 2.4 GHz and 5 GHz Bands Compared"},
    {"id": "16_04", "topic": "Wireless Channels and Non-Overlapping Channel Planning"},
    {"id": "16_05", "topic": "SSID, BSS and ESS Explained"},
    {"id": "16_06", "topic": "The Wireless Client Association Process"},
    {"id": "16_07", "topic": "Autonomous versus Controller-Based Wireless Architectures"},
    {"id": "16_08", "topic": "CAPWAP Tunnels and the Split-MAC Model"},
    {"id": "16_09", "topic": "Access Point Modes and When to Use Each"},
    {"id": "16_10", "topic": "WLC Ports and Interface Types"},
    {"id": "16_11", "topic": "Creating a WLAN on the Wireless LAN Controller GUI"},
    {"id": "16_12", "topic": "Configuring a Dynamic Interface and Mapping It to a VLAN"},
    {"id": "16_13", "topic": "Configuring a DHCP Scope for Wireless Clients"},
    {"id": "16_14", "topic": "Wireless Roaming Between Access Points"},
    {"id": "16_15", "topic": "Troubleshooting Wireless Client Connectivity"},

    # -- 17: Architecture and Virtualization --
    {"id": "17_01", "topic": "Three-Tier Hierarchical Campus Design"},
    {"id": "17_02", "topic": "Two-Tier Collapsed Core Design"},
    {"id": "17_03", "topic": "Spine-Leaf Data Center Design"},
    {"id": "17_04", "topic": "The Cisco Enterprise Architecture Model"},
    {"id": "17_05", "topic": "Cloud Service Models: IaaS, PaaS and SaaS"},
    {"id": "17_06", "topic": "Cloud Deployment Models: Public, Private and Hybrid"},
    {"id": "17_07", "topic": "Server Virtualization and Hypervisor Types"},
    {"id": "17_08", "topic": "Virtual Machines versus Containers"},
    {"id": "17_09", "topic": "Virtual Switching and How VMs Reach the Network"},
    {"id": "17_10", "topic": "Virtual Routing and Forwarding (VRF)"},
    {"id": "17_11", "topic": "Switch Stacking with StackWise"},
    {"id": "17_12", "topic": "VSS and StackWise Virtual"},

    # -- 18: Security Fundamentals --
    {"id": "18_01", "topic": "Threats, Vulnerabilities, Exploits and Mitigations Defined"},
    {"id": "18_02", "topic": "Malware Types and How They Spread"},
    {"id": "18_03", "topic": "Denial of Service and Distributed Denial of Service Attacks"},
    {"id": "18_04", "topic": "Spoofing Attacks: MAC, IP and DHCP"},
    {"id": "18_05", "topic": "Social Engineering and Phishing"},
    {"id": "18_06", "topic": "Man-in-the-Middle Attacks"},
    {"id": "18_07", "topic": "Reconnaissance and Common Attack Tools"},
    {"id": "18_08", "topic": "Hashing and Verifying Data Integrity"},
    {"id": "18_09", "topic": "Symmetric versus Asymmetric Encryption"},
    {"id": "18_10", "topic": "Digital Certificates and Public Key Infrastructure"},
    {"id": "18_11", "topic": "IPsec Services and Tunnel versus Transport Mode"},
    {"id": "18_12", "topic": "SSL/TLS and Securing Web Traffic"},
    {"id": "18_13", "topic": "Wireless Security Evolution: WEP, WPA, WPA2 and WPA3"},
    {"id": "18_14", "topic": "TKIP and AES Encryption in Wireless Networks"},
    {"id": "18_15", "topic": "Wireless Authentication: Pre-Shared Key versus Enterprise"},

    # -- 19: Secure Access and Device Hardening --
    {"id": "19_01", "topic": "Securing Console Access"},
    {"id": "19_02", "topic": "Securing VTY Lines for Remote Access"},
    {"id": "19_03", "topic": "Enable Secret and Privilege Levels"},
    {"id": "19_04", "topic": "Local User Accounts and Password Encryption"},
    {"id": "19_05", "topic": "Password Policy: Complexity, Rotation and Alternatives"},
    {"id": "19_06", "topic": "Configuring Login Banners"},
    {"id": "19_07", "topic": "The AAA Framework: Authentication, Authorization and Accounting"},
    {"id": "19_08", "topic": "RADIUS and TACACS+ Compared"},
    {"id": "19_09", "topic": "802.1X Port-Based Authentication"},
    {"id": "19_10", "topic": "Port Security: Limiting MAC Addresses on a Port"},
    {"id": "19_11", "topic": "Port Security Violation Modes and Err-Disabled Recovery"},
    {"id": "19_12", "topic": "DHCP Snooping and Trusted Ports"},
    {"id": "19_13", "topic": "Dynamic ARP Inspection"},
    {"id": "19_14", "topic": "Disabling Unused Services, Interfaces and Protocols"},

    # -- 20: Automation and Programmability --
    {"id": "20_01", "topic": "Why Networks Are Being Automated"},
    {"id": "20_02", "topic": "Traditional Device-by-Device Management versus Controller-Based"},
    {"id": "20_03", "topic": "Separating the Control Plane from the Data Plane"},
    {"id": "20_04", "topic": "Software-Defined Networking Architecture and Controllers"},
    {"id": "20_05", "topic": "Northbound and Southbound APIs"},
    {"id": "20_06", "topic": "REST API Fundamentals: CRUD and HTTP Verbs"},
    {"id": "20_07", "topic": "HTTP Response Codes and API Authentication"},
    {"id": "20_08", "topic": "Reading and Interpreting JSON"},
    {"id": "20_09", "topic": "XML and YAML Compared to JSON"},
    {"id": "20_10", "topic": "YANG Data Models"},
    {"id": "20_11", "topic": "NETCONF"},
    {"id": "20_12", "topic": "RESTCONF"},
    {"id": "20_13", "topic": "Ansible and Agentless Automation"},
    {"id": "20_14", "topic": "Puppet, Chef and Agent-Based Automation"},
    {"id": "20_15", "topic": "Cisco Catalyst Center (DNA Center)"},
    {"id": "20_16", "topic": "Cisco SD-Access: Fabric, Underlay and Overlay"},
    {"id": "20_17", "topic": "Cisco SD-WAN Components and Architecture"},
]
