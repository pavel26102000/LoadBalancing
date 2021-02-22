import numpy as np

def FFD(pms, vms, placement, trait="ram"):
    for pm in pms:
        pm.clear()
    vms.sort(key=lambda x: -x.traits[trait] * x.load[trait])
    num_migrations = 0

    for i in range(len(vms)):
        for j in range(len(pms)):
            if pms[j].check_vm(vms[i]):
                pms[j].place_vm(vms[i])

                if placement[j][i] != 1:
                    num_migrations += 1
                    for t in range(len(placement)):
                        placement[t][i] = 0
                    placement[j][i] = 1
                break

    return placement, num_migrations

def RoundRobin(pms, vms, placement):
    idx = np.random.randint(0, len(pms) - 1)
    for i in range(len(vms)):
        temp = idx
        while True:
            if pms[idx].check_vm(vms[i]):
                placement[idx][i] = 1
                pms[idx].place_vm(vms[i], i)
                break
            idx += 1
            idx %= len(pms)
            if idx == temp:
                return placement[:, :i], vms[:i]
        idx = temp + 1
        idx %= len(pms)
    return placement, vms