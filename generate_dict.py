import json
import re
import patch_zh

settings = patch_zh.get_settings_replacements()
chat = patch_zh.get_chat_replacements()

dict_out = {}

def extract_strings(s_eng, s_zh):
    # Regex to find text between quotes (either " or ')
    eng_matches = re.findall(r'["\'](.*?)["\']', s_eng)
    zh_matches = re.findall(r'["\'](.*?)["\']', s_zh)
    
    if len(eng_matches) == len(zh_matches):
        for e, z in zip(eng_matches, zh_matches):
            if e and z and e != z and not e.startswith('${'):
                dict_out[e.strip()] = z.strip()

for e, z in settings:
    extract_strings(e, z)
for e, z in chat:
    extract_strings(e, z)

# Add some dynamic prefixes manually so our observer can use them
dict_out["Thinking for "] = "思考中 "
dict_out["Thought for "] = "思考了 "
dict_out["Changes Overview"] = "更改概览"

with open('zh_dictionary.json', 'w', encoding='utf-8') as f:
    json.dump(dict_out, f, ensure_ascii=False, indent=2)

print(f"Extracted {len(dict_out)} translation pairs to zh_dictionary.json!")
