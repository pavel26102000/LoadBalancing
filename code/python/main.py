# флейворы +
# нампай +
# ффд +

import numpy as np


def gen_load(loc, scale):
    load = np.random.normal(loc, scale)
    if load < 0.05 or load > 0.99:
        load = np.random.normal(loc, scale)
    return load


class VM:
    def __init__(self, traits_=None, load_dis_=None, load_=None, flavour=None):
        if flavour is None or flavour in [1, 2, 3, 4]:
            self.traits = {
                "cpu": 1,
                "bw": 1,
                "ram": 1,
                "iops": 1
            }

        if load_dis_ is None and flavour is None:
            self.load_dis = {
                "cpu": (0.2, 0.1),
                "bw": (0.2, 0.1),
                "ram": (0.2, 0.1),
                "iops": (0.2, 0.1)
            }
        elif flavour == 1:
            self.load_dis = {
                "cpu": (0.6, 0.2),
                "bw": (0.2, 0.1),
                "ram": (0.4, 0.15),
                "iops": (0.4, 0.15)
            }
        elif flavour == 2:
            self.load_dis = {
                "cpu": (0.4, 0.15),
                "bw": (0.6, 0.2),
                "ram": (0.2, 0.1),
                "iops": (0.4, 0.15)
            }
        elif flavour == 3:
            self.load_dis = {
                "cpu": (0.4, 0.15),
                "bw": (0.4, 0.15),
                "ram": (0.6, 0.15),
                "iops": (0.2, 0.1)
            }
        elif flavour == 4:
            self.load_dis = {
                "cpu": (0.2, 0.1),
                "bw": (0.4, 0.15),
                "ram": (0.4, 0.15),
                "iops": (0.6, 0.2)
            }
        else:
            self.load_dis = load_dis_

        self.load = {}
        if load_ is None:
            self.update_loads()
        else:
            self.load = load_

    def update_loads(self, load_dis_=None):
        if load_dis_ is not None:
            self.load_dis = load_dis_

        for tr, [loc, sc] in self.load_dis.items():
            self.load[tr] = gen_load(loc, sc)


class PM:
    def __init__(self, traits_=None, flavour=None):
        if flavour is None:
            self.traits = {
                "cpu": 4,
                "bw": 4,
                "ram": 4,
                "iops": 4
            }

            self.max_load = {
                "cpu": 0.9,
                "bw": 0.8,
                "ram": 0.9,
                "iops": 0.8
            }

            self.demand = {}
            for tr in self.traits:
                self.demand[tr] = 0

            self.vms = list()

    def check_vm(self, vm):
        ok = True
        for tr in self.traits:
            if self.demand[tr] + vm.traits[tr] * vm.load[tr] > self.max_load[tr] * self.traits[tr]:
                ok = False
                break
        return ok

    def place_vm(self, vm, idx=-1):
        self.vms.append((vm, idx))
        for tr in vm.traits:
            self.demand[tr] += vm.traits[tr] * vm.load[tr]

    def update_vm(self, vm, idx):
        curr_vm, ar_idx = self.vms[idx]
        for tr in vm.traits:
            self.demand[tr] -= curr_vm.traits[tr] * curr_vm.load[tr]

        for tr in vm.traits:
            self.demand[tr] += vm.traits[tr] * vm.load[tr]
        self.vms[idx] = (vm, ar_idx)

    def mean_load(self):
        sum_loads = 0
        for trait in self.traits:
            sum_loads += self.demand[trait] / self.traits[trait]
        return sum_loads / len(self.traits)

    def clear(self):
        for tr in self.traits:
            self.demand[tr] = 0
        self.vms = list()


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


def CountFreePMS(placement):
    num_free = 0
    for i in range(len(placement)):
        if (placement[i] == 0).all():
            num_free += 1
    return num_free


def RebalanceLoads(pms, vms):
    for i in range(len(vms)):
        vms[i].update_loads()

    for i in range(len(pms)):
        for j in range(len(pms[i].vms)):
            _, idx = pms[i].vms[j]
            pms[i].update_vm(vms[idx], j)


def CountOverloaded(pms):
    num_overloaded = 0
    for pm in pms:
        for trait in pm.traits:
            if pm.demand[trait] > pm.traits[trait] * pm.max_load[trait]:
                num_overloaded += 1
    return num_overloaded


def CountStdResourceUsage(pms):
    usage = []
    for pm in pms:
        pm_usage = pm.mean_load()
        if pm_usage != 0:
            usage.append(pm_usage)
    return np.std(usage)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    pms = list()
    for i in range(60):
        pms.append(PM())

    vms = list()
    for i in range(300):
        flavour = np.random.randint(1, 4)
        vms.append(VM(flavour=flavour))

    table = np.zeros((len(pms), len(vms)))
    table, vms = RoundRobin(pms, vms, table)  # to check if all vms can be placed
    print("Number of vms:", len(table[0]))
    print("Std usage after round robin:", CountStdResourceUsage(pms))

    table, _ = FFD(pms, vms, table)  # first mapping
    vms = vms[:len(table[0])]
    free = CountFreePMS(table)
    # print(*table.tolist(), sep="\n")
    print("\n")

    std_usage = CountStdResourceUsage(pms)
    RebalanceLoads(pms, vms)  # rebalancing loads

    overloaded = CountOverloaded(pms)  # first mapping stats
    print("Before balancing:")
    print("Overloaded:", overloaded)
    print("Std usage:", std_usage)
    print("Number of free hosts:", free)
    print("----------------------")

    table, n_m = FFD(pms, vms, table)
    free = CountFreePMS(table)
    print("After balancing:")  # second mapping stats
    print("Number of free hosts:", free)
    print("Std usage:", CountStdResourceUsage(pms))
    print("Number of migrations:", n_m)
    # print( *table.tolist(), sep="\n")
    overloaded = CountOverloaded(pms)
    print("Overloaded:", overloaded)
    print("\n\n")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
