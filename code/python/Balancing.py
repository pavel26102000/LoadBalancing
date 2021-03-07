import numpy as np


def FFD(pms, vms, placement, sort_key=lambda x: -x.traits["ram"] * x.load["ram"]):
    for pm in pms:
        pm.clear()
    sorted_vms = list(enumerate(vms))
    sorted_vms.sort(key=lambda x: sort_key(x[1]))
    num_migrations = 0

    for i in range(len(sorted_vms)):
        vm_idx = sorted_vms[i][0]
        for j in range(len(pms)):
            if pms[j].check_vm(vms[vm_idx]):
                pms[j].place_vm(vms[vm_idx])

                if placement[j][vm_idx] != 1:
                    num_migrations += 1
                    for t in range(len(placement)):
                        placement[t][vm_idx] = 0
                    placement[j][vm_idx] = 1
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
