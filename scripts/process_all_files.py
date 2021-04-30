#!/usr/bin/env python

# Author: Jose Rodriguez (@Cyb3rPandaH)
# License: GNU General Public License v3 (GPLv3)

import yaml
import copy
import glob
from os import path
import json
from jinja2 import Template

# ******** Process aat&ck yaml Files ****************

# Aggregating all data sources yaml files
print("[+] Opening ATT&CK data sources yaml files..")
attack_ds_files = glob.glob(path.join(path.dirname(__file__), "..", "docs/mitre_attack/data_sources", "[!_]*.yml"))
all_ds_files = []

print("[+] Creating python lists (ATT&CK data sources) with yaml files content..")
for ds_file in attack_ds_files:
    all_ds_files.append(yaml.safe_load(open(ds_file).read()))
    
print("[+] Creating aggregated yaml file with ATT&CK data sources..")
with open(f'../docs/mitre_attack/all_attack_ds.yml', 'w') as file:
    yaml.dump(all_ds_files, file, sort_keys=False, width=4096)

# Creating data sources definition readme file
print(f"[+] Creating ATT&CK data sources definitions readme file..")
data_sources_template = Template(open('templates/attack_ds_definitions.md').read())
data_sources_render = copy.deepcopy(all_ds_files)
data_sources_markdown = data_sources_template.render(data_sources=data_sources_render)
open('../docs/mitre_attack/data_sources_definition.md', 'w').write(data_sources_markdown)

# ******** Process Relationships yaml Files ****************

# Aggregating relationships yaml files (all relationships and ATT&CK)

print("[+] Opening relationships yaml files..")
relationships_files = glob.glob(path.join(path.dirname(__file__), "..", "relationships", "[!_]*.yml"))
all_relationships_files = []
attack_relationships_files = []

print("[+] Creating python lists (all relationships and ATT&CK) with yaml files content..")
for relationship_file in relationships_files:
    relationship_yaml = yaml.safe_load(open(relationship_file).read())
    all_relationships_files.append(relationship_yaml)
    if relationship_yaml['attack'] != None:
        attack_relationships_files.append(relationship_yaml)

print("[+] Creating aggregated yaml file with all relationships..")
with open(f'../relationships/_all_ossem_relationships.yml', 'w') as file:
    yaml.dump(all_relationships_files, file, sort_keys = False)

print("[+] Creating aggregated yaml file with relationships mapped to ATT&CK..")
with open(f'../docs/mitre_attack/attack_relationships.yml', 'w') as file:
    yaml.dump(attack_relationships_files, file, sort_keys = False)

# Creating ATT&CK data source event mappings readme file
print(f"[+] Creating ATT&CK data source event mappings readme file..")
data_sources_event_mappings_template = Template(open('templates/attack_ds_event_mappings.md').read())
data_sources_event_mappings_render = copy.deepcopy(attack_relationships_files)
data_sources_event_mappings_markdown = data_sources_event_mappings_template.render(ds_event_mappings=data_sources_event_mappings_render)
open('../docs/mitre_attack/attack_events_mappings.md', 'w').write(data_sources_event_mappings_markdown)

# Creating all relationships (OSSEM) readme file
print(f"[+] Creating OSSEM Relationships readme file..")
relationships = []
for dr in all_relationships_files:
    redict = dict()
    redict['source'] = dr['behavior']['source']
    redict['relationship'] = dr['behavior']['relationship']
    redict['target'] = dr['behavior']['target']
    if redict not in relationships:
        relationships.append(redict)
data_model_relationships_template = Template(open('templates/ossem_relationships.md').read())
data_model_relationships_render = copy.deepcopy(relationships)
data_model_relationships_markdown = data_model_relationships_template.render(all_relationships=data_model_relationships_render)
open('../docs/data_model/ossem_relationships.md', 'w').write(data_model_relationships_markdown)

# Creating ATT&CK data source event mappings cvs file
print(f"[+] Creating ATT&CK data source event mappings CSV file..")
import csv 

processed_dr = []

for dr in attack_relationships_files:
    for t in dr['security_events']:
        record = dict()
        record['Data Source'] = dr['attack']['data_source']
        record['Component'] = dr['attack']['data_component']
        record['Source'] = dr['behavior']['source']
        record['Relationship'] = dr['behavior']['relationship']
        record['Target'] = dr['behavior']['target']
        record['EventID'] = t['event_id']
        record['Event Name'] = t['name']
        record['Event Platform'] = t['platform']
        record['Log Provider'] = t['log_provider']
        record['Log Channel'] = t['log_channel']
        record['Audit Category'] = t.get('audit_category', None)
        record['Audit Sub-Category'] = t.get('audit_sub_category', None)
        if t['log_channel'] == "Security":
            record['Enable Commands'] = f"auditpol /set /subcategory:{t['audit_sub_category']} /success:enable /failure:enable"
        elif t['log_channel'] == "Microsoft-Windows-Sysmon/Operational":
            record['Enable Commands'] = f"<{t['audit_category']} onmatch='exclude' />"
        else:
            record['Enable Commands'] = None
        if t['log_channel'] == "Security":
            record['GPO Audit Policy'] = f"Computer Configuration -> Windows Settings -> Security Settings -> Advanced Audit Policy Configuration -> System Audit Policies -> {t['audit_category']} -> Audit {t['audit_sub_category']}"
        else:
            record['GPO Audit Policy'] = None
        processed_dr.append(record)

header_fields = ['Data Source', 'Component', 'Source', 'Relationship', 'Target', 'EventID', 'Event Name', 'Event Platform', 'Log Provider', 'Log Channel', 'Audit Category', 'Audit Sub-Category', 'Enable Commands',  'GPO Audit Policy' ]
with open('../docs/mitre_attack/attack_events_mapping.csv', 'w', newline='')  as output_file:
    dict_writer = csv.DictWriter(output_file, header_fields)
    dict_writer.writeheader()
    dict_writer.writerows(processed_dr)