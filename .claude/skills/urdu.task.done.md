---
name: urdu.task.done
description: اردو میں کام مکمل کریں (Mark task complete in Urdu)
arguments:
  - name: kaam
    description: کام کا نام یا نمبر
    required: true
agent: urdu-language-agent
---

# Urdu Task Done Skill

کام مکمل کریں

## کمانڈز

- "[کام] ہو گیا"
- "[نمبر] مکمل"
- "ختم کرو [کام]"
- "[کام] کر لیا"

## تصدیق کے لیے

جب کام واضح نہ ہو:

```
کون سا کام مکمل ہوا؟

۱. دودھ لانا
۲. ڈاکٹر کی اپائنٹمنٹ
۳. بل جمع کرانا

براہ کرم نمبر بتائیں۔
```

## Output

```
🎉 مبارک ہو!

✅ مکمل شدہ کام: {{kaam}}
🕐 مکمل: ابھی

━━━━━━━━━━━━━━
آج کے باقی کام: [X]
کل مکمل: [Y]

{{remaining > 0 ? "اگلا کام: [next task]" : "آج کے سب کام ہو گئے! 🌟"}}
```
