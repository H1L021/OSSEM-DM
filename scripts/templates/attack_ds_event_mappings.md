# ATT&CK DS Event Mappings

|Data Source|Component|Source|Relationship|Target|EventID|Log Provider|Log Channel|Audit Category|Audit Sub-Category|Enable Commands| GPO Audit Policy|
| :---| :---| :---| :---| :---| :---| :---| :---| :---| :---| :---| :---|
{% for ds in ds_event_mappings|sort(attribute='name') %}{% for dc in ds['data_components'] %}{% for dr in dc['relationships'] %}{% for t in dr['telemetry']%}|{{ds['name']}}|{{dc['name']}}|{{dr['source_data_element']}}|{{dr['relationship']}}|{{dr['target_data_element']}}|{{t['event_id']}}|{{t['log_provider']}}|{{t['log_channel']}}|{{t['audit_category']|default('NA')}}|{{t['audit_sub_category']|default('NA')}}|{% if t['log_channel'] == "Security" %} `auditpol /set /subcategory:"{{t['audit_sub_category']}}" /success:enable /failure:enable` {% elif t['log_channel'] == "Microsoft-Windows-Sysmon/Operational" %} `<{{t['audit_category']}} onmatch="exclude" />` {% else %}NA{% endif %}|{% if t['log_channel'] == "Security" %} Computer Configuration -> Windows Settings -> Security Settings -> Advanced Audit Policy Configuration -> System Audit Policies -> {{t['audit_category']}} -> Audit {{t['audit_sub_category']}} {% else %}NA{% endif %}|
{% endfor %}{% endfor %}{% endfor %}{% endfor %}