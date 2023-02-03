import semanticscholar as sch

paper = sch.paper('arXiv:1612.08083', timeout=4)

for i,k in paper.items():
    print(i,"\n",k)

print(len(paper.get("references")))
