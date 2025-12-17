import sys
import os
sys.path.append(os.path.abspath("/src/"))
import input_gen as ipt
import fuzzer_modules.r1 as fm

csv = ipt.parse_csv("data/r1/seeds.csv")
csv = ipt.parse_message_sequence(csv)

row = csv.iloc[0]
variants = fm.fuzz_r1(row, k=30)
print(variants[0])


