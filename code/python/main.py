# флейворы +
# нампай +
# ффд +

from Balancing import *
from Metrics import *
from VM import VM
from PM import PM
from Commons import RebalanceLoads


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
