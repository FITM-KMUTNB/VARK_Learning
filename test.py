from pythainlp import word_tokenize
import PyPDF2
text = "ทดสอบการตัดตำภาษาไทย"
proc = word_tokenize(text, engine='newmm')
print(proc)