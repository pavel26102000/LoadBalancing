from numpy import random

def gen_load(loc, scale):
    load = random.normal(loc, scale)
    if load < 0.05 or load > 0.99:
        load = random.normal(loc, scale)
    return load

def RebalanceLoads(pms, vms):
    for i in range(len(vms)):
        vms[i].update_loads()

    for i in range(len(pms)):
        for j in range(len(pms[i].vms)):
            _, idx = pms[i].vms[j]
            pms[i].update_vm(vms[idx], j)