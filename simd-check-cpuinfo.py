#!/usr/bin/env python

import os
import sys

cpuinfofp = "/proc/cpuinfo"

f = open(cpuinfofp,"r")
lines = f.readlines()
f.close()

flagsln = ""

for line in lines:
  if line.startswith("flags\t\t:"):
    flagsln = line
    break

if not flagsln:
  print("line with flags not found. lines:")
  print(lines)
  sys.exit(1)

flags = flagsln.split(':')[1].strip().split()
#print("found flags:")
print(flags)

sys.stdout.write("SSE: ")
if 'sse' in flags:
  sys.stdout.write("yes\n")
else:
  sys.stdout.write("no\n")

sys.stdout.write("SSE2: ")
if 'sse2' in flags:
  sys.stdout.write("yes\n")
else:
  sys.stdout.write("no\n")

sys.stdout.write("SSE3: ")
if 'sse3' in flags:
  sys.stdout.write("yes\n")
else:
  sys.stdout.write("no\n")

sys.stdout.write("sSSE3: ")
if 'ssse3' in flags:
  sys.stdout.write("yes\n")
else:
  sys.stdout.write("no\n")

sys.stdout.write("SSE4.1: ")
if 'sse4_1' in flags:
  sys.stdout.write("yes\n")
else:
  sys.stdout.write("no\n")

sys.stdout.write("SSE4.2: ")
if 'sse4_2' in flags:
  sys.stdout.write("yes\n")
else:
  sys.stdout.write("no\n")

sys.stdout.write("AVX: ")
if 'avx' in flags:
  sys.stdout.write("yes\n")
else:
  sys.stdout.write("no\n")

sys.stdout.write("AVX2: ")
if 'avx2' in flags:
  sys.stdout.write("yes\n")
else:
  sys.stdout.write("no\n")

sys.stdout.write("AVX512f: ")
if 'avx512f' in flags:
  sys.stdout.write("yes\n")
else:
  sys.stdout.write("no\n")

sys.stdout.write("AVX512vl: ")
if 'avx512vl' in flags:
  sys.stdout.write("yes\n")
else:
  sys.stdout.write("no\n")

sys.stdout.write("AVX512dq: ")
if 'avx512dq' in flags:
  sys.stdout.write("yes\n")
else:
  sys.stdout.write("no\n")

sys.stdout.write("AVX512bw: ")
if 'avx512bw' in flags:
  sys.stdout.write("yes\n")
else:
  sys.stdout.write("no\n")

sys.stdout.write("FMA: ")
if 'fma' in flags:
  sys.stdout.write("yes\n")
else:
  sys.stdout.write("no\n")

sys.stdout.write("F16C: ")
if 'f16c' in flags:
  sys.stdout.write("yes\n")
else:
  sys.stdout.write("no\n")

sys.stdout.write("BMI1: ")
if 'bmi1' in flags:
  sys.stdout.write("yes\n")
else:
  sys.stdout.write("no\n")

sys.stdout.write("BMI2: ")
if 'bmi2' in flags:
  sys.stdout.write("yes\n")
else:
  sys.stdout.write("no\n")
