import pdfplumber

file = 'varkapp/static/การสร้างสื่อดิจิทัล/บทที่ 5  การตัดต่อบน Timeline/C_5.2 การตัดต่อคลิปวิดีโอบนพาเนล Timeline/Exercise 5.2/Exer5.2.pdf'


pdf = pdfplumber.open(file)
out = pdf.pages[0].extract_text().splitlines()

q_number = []
for num in range(1,8):
    q_number.append(str(num))
    q_number.append(str(num)+'.')
    for num2 in range(1,11):
        for num3 in range(1,11):
            q_number.append(str(num)+"."+str(num2)+"."+str(num3))
            print(str(num)+"."+str(num2)+"."+str(num3))