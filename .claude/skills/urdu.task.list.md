---
name: urdu.task.list
description: اردو میں کاموں کی فہرست دیکھیں (View tasks in Urdu)
arguments:
  - name: filter
    description: فلٹر (باقی، مکمل، آج، ہفتہ)
    required: false
agent: urdu-language-agent
---

# Urdu Task List Skill

اردو میں کاموں کی فہرست

## فلٹر کی اقسام

| اردو | Filter |
|------|--------|
| سب کام | All tasks |
| باقی کام | Pending |
| مکمل | Completed |
| آج کے کام | Due today |
| اس ہفتے | This week |
| زیادہ اہم | High priority |
| تاخیر شدہ | Overdue |

## کمانڈز

- "میرے کام دکھاؤ"
- "آج کیا کرنا ہے؟"
- "باقی کام کتنے ہیں؟"
- "ضروری کام دکھاؤ"

## Output

```
📋 آپ کے کام

🔴 تاخیر شدہ
━━━━━━━━━━━━━━
۱. [کام] - گزشتہ کل تک

📍 آج کے کام
━━━━━━━━━━━━━━
۲. [کام] - شام تک
۳. [کام] - رات تک

📆 اس ہفتے
━━━━━━━━━━━━━━
۴. [کام] - جمعرات
۵. [کام] - جمعہ

━━━━━━━━━━━━━━
کل: [X] کام | باقی: [Y] | مکمل: [Z]
```
