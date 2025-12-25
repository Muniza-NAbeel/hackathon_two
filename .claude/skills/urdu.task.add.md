---
name: urdu.task.add
description: اردو میں نیا کام شامل کریں (Add a task in Urdu)
arguments:
  - name: kaam
    description: کام کی تفصیل (Task description in Urdu)
    required: true
  - name: tareekh
    description: تاریخ (Due date - آج، کل، پرسوں، etc.)
    required: false
  - name: ahmiyat
    description: اہمیت (Priority - زیادہ، معمولی، کم)
    required: false
agent: urdu-language-agent
---

# Urdu Task Add Skill

اردو میں نیا کام شامل کریں

## اردو کمانڈز (Urdu Commands)

### شامل کرنے کے طریقے
- "یاد دلائیں کہ..."
- "کام لکھ لو..."
- "شامل کرو..."
- "نیا کام..."

### تاریخ کی اصطلاحات
| اردو | معنی |
|------|------|
| آج | Today |
| کل | Tomorrow |
| پرسوں | Day after tomorrow |
| اگلے ہفتے | Next week |
| مہینے کے آخر میں | End of month |
| صبح | Morning (9 AM) |
| دوپہر | Afternoon (2 PM) |
| شام | Evening (6 PM) |
| رات | Night (9 PM) |

### اہمیت کی سطح
| اردو | Level |
|------|-------|
| فوری / بہت ضروری | Urgent |
| زیادہ / اہم | High |
| معمولی | Medium |
| کم | Low |

## Output

```
✅ کام شامل ہو گیا

📋 کام: {{kaam}}
📅 تاریخ: {{tareekh | "کوئی تاریخ نہیں"}}
⭐ اہمیت: {{ahmiyat | "معمولی"}}

آپ کے کل [X] کام باقی ہیں۔
```
