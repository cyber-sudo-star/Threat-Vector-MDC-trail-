import json
import os
import random
import copy

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_CACHE = {}

MODULES_METADATA = [
    {
        "id": 1,
        "title": "Computer Fundamentals",
        "icon": "desktop",
        "description": "Understand the basic components of a computer, how hardware and software work, and the role of operating systems in managing computer resources.",
        "topics": [
            "Introduction to computers",
            "Hardware and software",
            "CPU and its functions",
            "RAM and ROM",
            "Storage devices",
            "Input and output devices",
            "Operating systems",
            "Files and folders",
            "Basic computer operations",
            "Internet and cloud storage basics"
        ]
    },
    {
        "id": 2,
        "title": "Networking Fundamentals",
        "icon": "network-wired",
        "description": "Learn how computers communicate with each other, how networks are structured, and how different protocols help transfer information.",
        "topics": [
            "Introduction to computer networks",
            "LAN and WAN",
            "Routers and switches",
            "IP and MAC addresses",
            "DNS and DHCP",
            "Ports",
            "TCP and UDP",
            "OSI model",
            "TCP/IP model",
            "Common network protocols"
        ]
    },
    {
        "id": 3,
        "title": "Operating Systems & Linux",
        "icon": "terminal",
        "description": "Understand how operating systems work, explore the basics of Linux, and become familiar with commands, files, permissions, and processes.",
        "topics": [
            "Introduction to operating systems",
            "Windows and Linux",
            "Linux distributions",
            "File systems",
            "Linux terminal",
            "Basic Linux commands",
            "Users and permissions",
            "Processes",
            "Package management",
            "System logs"
        ]
    },
    {
        "id": 4,
        "title": "Cybersecurity Fundamentals",
        "icon": "shield-alt",
        "description": "Explore the basic principles of cybersecurity, understand common security terminology, and learn how information and systems are protected.",
        "topics": [
            "Introduction to cybersecurity",
            "CIA triad",
            "Assets, threats, vulnerabilities, and risks",
            "Authentication and authorization",
            "Multi-factor authentication",
            "Encryption and hashing",
            "Digital signatures",
            "Security controls",
            "Data protection and privacy"
        ]
    },
    {
        "id": 5,
        "title": "Cyber Threats & Attacks",
        "icon": "bug",
        "description": "Discover common cyber threats and attack techniques, understand how attackers operate, and learn how to identify suspicious activities.",
        "topics": [
            "Malware",
            "Viruses, worms, and Trojans",
            "Ransomware",
            "Phishing",
            "Social engineering",
            "Brute-force attacks",
            "Dictionary attacks",
            "DoS and DDoS attacks",
            "Insider threats",
            "Attack vectors"
        ]
    },
    {
        "id": 6,
        "title": "Network & Web Security",
        "icon": "globe",
        "description": "Learn how networks and websites are protected, explore common web vulnerabilities, and understand the security mechanisms used to prevent attacks.",
        "topics": [
            "Firewalls",
            "IDS and IPS",
            "VPNs",
            "HTTP and HTTPS",
            "TLS",
            "Web application basics",
            "SQL injection",
            "Cross-site scripting (XSS)",
            "OWASP Top 10",
            "Secure browsing"
        ]
    },
    {
        "id": 7,
        "title": "Security Tools & Practical Skills",
        "icon": "tools",
        "description": "Become familiar with commonly used cybersecurity tools and understand how they help security professionals examine networks, analyse traffic, and identify potential vulnerabilities.",
        "topics": [
            "Nmap",
            "Wireshark",
            "tcpdump",
            "Network scanning",
            "Packet analysis",
            "Log analysis",
            "Vulnerability assessment",
            "Basic security testing",
            "Security monitoring",
            "Safe introductory security labs"
        ]
    },
    {
        "id": 8,
        "title": "Security Operations & GRC",
        "icon": "user-shield",
        "description": "Understand how organisations manage cybersecurity, monitor security events, respond to incidents, assess risks, and maintain security policies and compliance.",
        "topics": [
            "Security Operations Centre (SOC)",
            "SIEM",
            "Security alerts",
            "Threat detection",
            "Incident response",
            "Risk assessment",
            "Security policies",
            "Access control",
            "Compliance",
            "NIST Cybersecurity Framework",
            "Governance, Risk, and Compliance (GRC)"
        ]
    }
]

def load_module(module_id):
    if module_id in _CACHE:
        return _CACHE[module_id]
    
    json_path = os.path.join(_BASE_DIR, f"module{module_id}.json")
    if not os.path.exists(json_path):
        return None
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        _CACHE[module_id] = data
        return data

def get_all_modules():
    return MODULES_METADATA

def get_module_meta(module_id):
    for m in MODULES_METADATA:
        if m["id"] == module_id:
            return m
    return None

def get_quiz_questions(module_id, difficulty, shuffle_questions=True, shuffle_options=True, **kwargs):
    if "shuffle" in kwargs:
        shuffle_questions = kwargs["shuffle"]
        shuffle_options = kwargs["shuffle"]
    mod = load_module(module_id)
    if not mod:
        return []
    
    difficulty = difficulty.lower()
    matching = [q for q in mod.get("questions", []) if q.get("difficulty", "").lower() == difficulty]
    
    # Deep copy to ensure shuffling does not mutate cached data
    questions_copy = copy.deepcopy(matching)
    
    if shuffle_questions:
        random.shuffle(questions_copy)
    
    # Interleave subtopics so consecutive questions don't share the same topic
    if len(questions_copy) > 1:
        interleaved = []
        topic_buckets = {}
        for q in questions_copy:
            top = q.get("topic", "General")
            topic_buckets.setdefault(top, []).append(q)
        
        while any(topic_buckets.values()):
            for top in list(topic_buckets.keys()):
                if topic_buckets[top]:
                    interleaved.append(topic_buckets[top].pop(0))
        questions_copy = interleaved
    
    # Shuffle options safely without breaking correct answer mapping
    if shuffle_options:
        for q in questions_copy:
            orig_options = q.get("options", [])
            orig_correct = q.get("correct", [])
            
            # Map original option texts that are correct
            correct_texts = {orig_options[i] for i in orig_correct if i < len(orig_options)}
            
            shuffled_opts = list(orig_options)
            random.shuffle(shuffled_opts)
            
            # Recompute new correct indices
            new_correct = [idx for idx, opt in enumerate(shuffled_opts) if opt in correct_texts]
            
            q["options"] = shuffled_opts
            q["correct"] = new_correct
    
    return questions_copy
