import random
import subprocess
import os

INPUT = "input.txt"
VCD = "cla_4bit.vcd"
OUT = "sim.out"
TB = "cla_4bit_tb.v"
DUT = "cla_4bit.v"

vectors = []
with open(INPUT, "w") as f:
    for _ in range(20):
        a = random.randint(0, 15)
        b = random.randint(0, 15)
        cin = random.randint(0, 1)
        vectors.append((a, b, cin))
        f.write(f"{a} {b} {cin}\n")

for p in (OUT, VCD):
    if os.path.exists(p):
        os.remove(p)
subprocess.run(["iverilog", "-o", OUT, TB, DUT], check=True)
subprocess.run(["vvp", OUT], check=True)

name2sym = {}
snapshots = []
current = {}

with open(VCD, "r") as f:
    in_defs = True
    for line in f:
        line = line.strip()
        if not line:
            continue
        if in_defs:
            if line.startswith("$var"):
                parts = line.split()
                if len(parts) >= 6:
                    sym = parts[3]
                    name = parts[4].split('[')[0]
                    if name in ("a", "b", "cin", "sum", "cout"):
                        name2sym[name] = sym
            elif line.startswith("$enddefinitions"):
                in_defs = False
            continue

        if line.startswith('#'):
            if all(k in current for k in ("a", "b", "cin", "sum", "cout")):
                snapshots.append(dict(current))
            continue

        if line[0] in 'bB':
            try:
                _, rest = line.split('b', 1)
                val, sym = rest.split()
            except ValueError:
                continue
            for n, s in name2sym.items():
                if s == sym:
                    val = ''.join('0' if ch in 'xXzZ' else ch for ch in val)
                    current[n] = int(val or '0', 2)
                    break
        else:
            val = 1 if line[0] == '1' else 0
            sym = line[1:]
            for n, s in name2sym.items():
                if s == sym:
                    current[n] = val
                    break

if all(k in current for k in ("a", "b", "cin", "sum", "cout")):
    if not snapshots or snapshots[-1] != current:
        snapshots.append(dict(current))

if len(snapshots) >= len(vectors):
    snapshots = snapshots[-len(vectors):]

ok = 0
for i, (vec, samp) in enumerate(zip(vectors, snapshots)):
    a, b, cin = vec
    total = a + b + cin
    exp_sum = total & 0xF
    exp_cout = (total >> 4) & 1
    got_sum = samp.get("sum")
    got_cout = samp.get("cout")
    if got_sum == exp_sum and got_cout == exp_cout:
        ok += 1
    else:
        print(f"mismatch[{i}]: a={a} b={b} cin={cin} -> exp sum={exp_sum} cout={exp_cout}, got sum={got_sum} cout={got_cout}")

print(f"Passed {ok}/{len(vectors)} cases.")