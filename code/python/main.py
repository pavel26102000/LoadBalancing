# флейворы +
# нампай +
# ффд +

from Balancing import *
from Metrics import *
from VM import VM
from PM import PM
from Commons import RebalanceLoads


def TEST(num_pms: int, num_vms: int, first_algo, second_algo, num_runs: int = 1):
    avg_num_vms_total = 0
    avg_use_rr = 0
    avg_ovl_fst = 0
    avg_ovl_snd = 0
    avg_free_hosts_first_algo = 0
    avg_free_hosts_diff = 0
    avg_usage_fst = 0
    avg_usage_snd = 0
    avg_num_migrations = 0

    for run in range(num_runs):
        pms = list()
        for i in range(num_pms):
            pms.append(PM())

        vms = list()
        for i in range(num_vms):
            flavour = np.random.randint(1, 4)
            vms.append(VM(flavour=flavour))

        table = np.zeros((len(pms), len(vms)))
        table, vms = RoundRobin(pms, vms, table)  # to check if all vms can be placed
        avg_num_vms_total = (avg_num_vms_total * run + len(table[0])) / (run + 1)
        rsrc_usage = CountStdResourceUsage(pms)
        avg_use_rr = (avg_use_rr * run + rsrc_usage) / (run + 1)

        table, _ = first_algo(pms, vms, table)  # first mapping
        vms = vms[:len(table[0])]
        free = CountFreePMS(table)
        avg_free_hosts_first_algo = (avg_free_hosts_first_algo * run + free) / (run + 1)

        std_usage = CountStdResourceUsage(pms)
        avg_usage_fst = (avg_usage_fst * run + std_usage) / (run + 1)
        pms, vms = RebalanceLoads(pms, vms)  # rebalancing loads

        avg_ovl_fst = (avg_ovl_fst * run + CountOverloaded(pms)) / (run + 1)  # first mapping stats

        table, n_m = second_algo(pms, vms, table)
        avg_num_migrations = (avg_num_migrations * run + n_m) / (run + 1)

        free_diff = CountFreePMS(table) - free
        avg_free_hosts_diff = (avg_free_hosts_diff * run + free_diff) / (run + 1)

        std_usage = CountStdResourceUsage(pms)
        avg_usage_snd = (avg_usage_snd * run + std_usage) / (run + 1)
        # print( *table.tolist(), sep="\n")
        overloaded = CountOverloaded(pms)
        avg_ovl_snd = (avg_ovl_snd * run + overloaded) / (run + 1)

    print("Average total number of vms: ", avg_num_vms_total)
    print("Average std usage after the Round Robin", avg_use_rr)

    print("\n----------------------------------------\n")
    print("First algorithm and Rebalancing happened")
    print("\n----------------------------------------\n")

    print("Average number of overloaded hosts: ", avg_ovl_fst)
    print("Average std usage after First Algorithm: ", avg_usage_fst)
    print("Average free hosts after First Algorithm: ", avg_free_hosts_first_algo)

    print("\n----------------------------------------\n")
    print("Rebalancing happened")
    print("\n----------------------------------------\n")

    print("Average number of overloaded hosts: ", avg_ovl_snd)
    print("Average std usage after Second Algorithm: ", avg_usage_snd)
    print("Average free hosts difference after Second Algorithm: ", avg_free_hosts_diff)
    print("Average number of migrations: ", avg_num_migrations)



if __name__ == '__main__':
    # test function args:
    # num_pms : number of servers
    # num_vms : number of Virtual Machines to Place
    # first_algo : the algorithm to make initial mapping
    # second_algo : the algorithm to rebalance load
    # num_runs : number of times to run rebalancing algorithm (from scratch)
    TEST(100, 500, FFD, MyAlgorithm, 100)
