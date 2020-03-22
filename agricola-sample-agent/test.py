import subprocess

popen = subprocess.Popen(["python", "sample_agent.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf-8')
popen.stdin.write("??????\n")
popen.stdin.flush()
popen.stdout.flush()
print(popen.stdout.readline())