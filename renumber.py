# -*- coding: utf-8 -*-
"""One-time renumber of output/ folders for the 90 -> 109 topic expansion.

Two-phase rename (old_id -> TMP__new_id -> new_id) so that overlapping
id ranges (e.g. old 01_09 -> new 01_11, while old 01_11 also exists) never
collide mid-rename.

Run once. Safe to re-run (idempotent: skips ids already matching the map).
"""
import os

OUTPUT_DIR = "output"

# old_id -> new_id, only for topics whose numeric id actually changes.
# Sections 03, 04, 08 are untouched. Section 07 only gets a pure append
# (07_19), so no existing folder in 07 needs renaming.
MAPPING = {
    # Section 01
    "01_08": "01_09",  # VLAN and Inter-VLAN Routing
    "01_09": "01_11",  # RSTP, MSTP, PortFast, BPDUGuard, Root Guard
    "01_10": "01_14",  # Layer 2 EtherChannel
    "01_11": "01_16",  # HSRP and VRRP
    "01_12": "01_17",  # Policy-Based Routing (PBR)
    # Section 02
    "02_03": "02_04",  # Implementing OSPFv2
    "02_04": "02_05",  # Implementing OSPFv3 (IPv6)
    "02_05": "02_06",  # Optimizing OSPF
    "02_06": "02_07",  # OSPF Area Types and Summarization
    "02_07": "02_10",  # Enterprise Internet Connectivity
    "02_08": "02_11",  # Implementing NAT and PAT
    "02_09": "02_12",  # Exploring eBGP
    "02_10": "02_13",  # BGP Best Path Selection Algorithm
    # Section 05
    "05_03": "05_06",  # Introducing QoS
    "05_04": "05_07",  # Interpret QoS Configurations
    "05_05": "05_09",  # NTP and PTP
    "05_06": "05_10",  # Syslog, SNMP, NetFlow and FNF
    "05_07": "05_13",  # Configuring Cisco IOS EEM Applet
    "05_08": "05_14",  # Network Troubleshooting Tools and Concepts
    "05_09": "05_15",  # Ping, Traceroute, Debug and Conditional Debug
    "05_10": "05_16",  # Cisco IOS IP SLAs
    "05_11": "05_17",  # SPAN, RSPAN and ERSPAN
    # Section 06
    "06_10": "06_12",  # Endpoint Security
    "06_11": "06_13",  # Firewall and NGFW Concepts
    "06_12": "06_14",  # REST API Security
    "06_13": "06_15",  # MACSec and TrustSec Overview
    "06_14": "06_18",  # 802.1X for Wired and Wireless
    "06_15": "06_19",  # MAC Authentication Bypass (MAB)
    "06_16": "06_20",  # Web Authentication
}


def main():
    folders = sorted(os.listdir(OUTPUT_DIR))
    renames = []
    for folder in folders:
        old_id = folder[:5]
        if old_id in MAPPING:
            new_id = MAPPING[old_id]
            rest = folder[5:]  # keeps the leading "_" + slug
            renames.append((folder, f"TMP__{new_id}{rest}", f"{new_id}{rest}"))

    print(f"{len(renames)} folders to renumber")

    # Phase 1: old -> temp
    for old, tmp, _final in renames:
        src = os.path.join(OUTPUT_DIR, old)
        dst = os.path.join(OUTPUT_DIR, tmp)
        if os.path.exists(src):
            os.rename(src, dst)

    # Phase 2: temp -> final
    for old, tmp, final in renames:
        src = os.path.join(OUTPUT_DIR, tmp)
        dst = os.path.join(OUTPUT_DIR, final)
        if os.path.exists(src):
            os.rename(src, dst)
            print(f"  {old}  ->  {final}")

    remaining_tmp = [f for f in os.listdir(OUTPUT_DIR) if f.startswith("TMP__")]
    if remaining_tmp:
        print(f"WARNING: {len(remaining_tmp)} temp folders left over: {remaining_tmp}")
    else:
        print("Renumber complete, no leftover temp folders.")

    total = len(os.listdir(OUTPUT_DIR))
    print(f"Total folders in output/: {total} (expect 90)")


if __name__ == "__main__":
    main()
