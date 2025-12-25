---
name: urdu.remind
description: اردو میں یاد دہانی لگائیں (Set reminder in Urdu)
arguments:
  - name: kaam
    description: کس چیز کی یاد دہانی
    required: true
  - name: waqt
    description: کب یاد دلانا ہے
    required: true
agent: urdu-language-agent
---

# Urdu Remind Skill

اردو میں یاد دہانی

## وقت کی اصطلاحات

| اردو | Time |
|------|------|
| ابھی | Now |
| تھوڑی دیر میں | In 15 minutes |
| آدھے گھنٹے میں | In 30 minutes |
| ایک گھنٹے میں | In 1 hour |
| کل صبح | Tomorrow morning |
| کل شام | Tomorrow evening |
| پرسوں | Day after tomorrow |
| جمعہ کو | On Friday |
| مہینے کی پہلی تاریخ | 1st of month |

## کمانڈز

- "کل صبح یاد دلانا کہ..."
- "۵ بجے یاد کروانا..."
- "[وقت] پر بتانا کہ..."
- "جمعہ کو یاد دلائیو..."

## Output

```
🔔 یاد دہانی لگ گئی

📋 کام: {{kaam}}
⏰ وقت: {{waqt}}

میں آپ کو [تاریخ] کو [وقت] پر یاد دلاؤں گا۔

━━━━━━━━━━━━━━
آپ کی آنے والی یاد دہانیاں: [X]
```

## یاد دہانی کا پیغام

```
🔔 یاد دہانی!

آپ نے کہا تھا:
"{{kaam}}"

⏰ مقررہ وقت: {{waqt}}

کیا آپ نے یہ کام کر لیا؟
[ہاں، ہو گیا] [بعد میں یاد دلاؤ] [منسوخ]
```
