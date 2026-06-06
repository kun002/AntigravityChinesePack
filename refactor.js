const fs = require('fs');
const path = require('path');

function extractStrings() {
    const extCode = fs.readFileSync('extension.js', 'utf-8');
    const dict = {};

    // Helper to extract string from between quotes
    function getInsideQuotes(s) {
        const match = s.match(/(?:children|label|title|placeholder|description|text|tooltip|tooltipText|aria-label):(?:`([^`]+)`|"([^"]+)"|'([^']+)')/);
        if (match) {
            return match[1] || match[2] || match[3];
        }
        
        // Match pure strings like '"English"', '"\u4e2d\u6587"'
        const pureMatch = s.match(/^"([^"]+)"$/);
        if (pureMatch) return pureMatch[1];
        
        return null;
    }

    // We look for arrays like ['...','...']
    const regex = /\[\s*'([^']*)'\s*,\s*'([^']*)'\s*\]/g;
    let match;
    let count = 0;
    while ((match = regex.exec(extCode)) !== null) {
        let engRaw = match[1];
        let zhRaw = match[2];
        
        // Handle escaped quotes in python/js string representation
        engRaw = engRaw.replace(/\\"/g, '"');
        zhRaw = zhRaw.replace(/\\"/g, '"');
        zhRaw = zhRaw.replace(/\\u([0-9a-fA-F]{4})/g, (m, c) => String.fromCharCode(parseInt(c, 16)));
        
        let eng = getInsideQuotes(engRaw);
        let zh = getInsideQuotes(zhRaw);
        
        if (!eng && engRaw.startsWith('{') && engRaw.includes('label:"')) {
            eng = engRaw.match(/label:"([^"]+)"/)?.[1];
            zh = zhRaw.match(/label:"([^"]+)"/)?.[1];
        }

        // If we still didn't find the key, just try generic quote extraction
        if (!eng) {
            eng = engRaw.match(/"([^"]+)"/)?.[1];
            zh = zhRaw.match(/"([^"]+)"/)?.[1];
        }
        
        if (eng && zh && eng !== zh && !eng.startsWith('${') && !eng.includes('"+')) {
            dict[eng.trim()] = zh.trim();
            count++;
        }
    }
    
    // Add missing/dynamic manual entries
    dict["Thinking for "] = "思考中 ";
    dict["Thought for "] = "思考了 ";
    dict["Changes Overview"] = "更改概览";
    dict["Settings - "] = "设置 - ";

    console.log(`Extracted ${count} items into dictionary.`);
    fs.writeFileSync('zh_dictionary.json', JSON.stringify(dict, null, 2), 'utf-8');
}

extractStrings();
