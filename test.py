import pdfplumber
pdf = pdfplumber.open('varkapp/static/การสร้างสื่อดิจิทัล/บทที่ 1  รู้จักกับการตัดต่อภาพยนตร์/A_แบบทดสอบก่อนเรียน/AnsPreCh1.pdf')
text = []
for page in range(0, len(pdf.pages)):
  
    page = pdf.pages[page].extract_text().splitlines()
    for p in page:
        text.append(p)
pdf.close()

for t in text:
    print(t)