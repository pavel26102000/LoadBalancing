import numpy as np

import heapq


class Heap(object):
    def __init__(self, initial=None, key=lambda x: x):
        self.key = key
        self.index = 0
        if initial:
            self._data = [(key(item), i, item) for i, item in enumerate(initial)]
            self.index = len(self._data)
            heapq.heapify(self._data)
        else:
            self._data = []

    def push(self, item, index=None):
        if index is None:
            heapq.heappush(self._data, (self.key(item), self.index, item))
            self.index += 1
        else:
            heapq.heappush(self._data, (self.key(item), index, item))

    def pop(self):
        return heapq.heappop(self._data)[1:]

    def empty(self):
        return len(self._data) == 0


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
                pms[j].place_vm(vms[vm_idx], vm_idx)

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


def HottestToColdest(pms, vms, placement, sort_vm_key=lambda x: x.traits["ram"] * x.load["ram"],
                     sort_pm_key=lambda x: x.mean_load() + x.is_overloaded()):
    pms_heap = Heap(pms, sort_pm_key)
    num_migrations = 0

    for i in range(len(pms)):
        if pms[i].is_overloaded():
            pms[i].vms.sort(key=lambda x: sort_vm_key(x[0]))

            to_insert_back = []
            curr_vm = -1
            while pms[i].is_overloaded():
                _, vm_idx = pms[i].vms[curr_vm]
                if pms_heap.empty():
                    for idx in to_insert_back:
                        pms_heap.push(pms[idx], idx)
                    to_insert_back = []
                    curr_vm -= 1
                    if curr_vm == -len(pms[i].vms):
                        print("Its Impossible for pm", i)
                        break
                    else:
                        continue
                target, _ = pms_heap.pop()
                to_insert_back.append(target)

                if pms[target].check_vm(vms[vm_idx]):
                    pms[i].remove_vm(vm_idx)
                    pms[target].place_vm(vms[vm_idx], vm_idx)
                    placement[i][vm_idx] = 0
                    placement[target][vm_idx] = 1
                    num_migrations += 1
                    for idx in to_insert_back:
                        pms_heap.push(pms[idx], idx)
                    to_insert_back = []
                    curr_vm = -1

    return placement, num_migrations


def MyAlgorithm(pms, vms, placement, sort_vm_key=lambda x: x.mean_demand(),
                sort_pm_key=lambda x: x.mean_load() + x.is_overloaded(), max_migrations_to_free=2):
    have_to_migrate = Heap(key=sort_vm_key)
    dirty = [False] * len(pms)
    num_migrations = 0

    for i in range(len(pms)):
        if pms[i].is_overloaded():
            pms[i].vms.sort(key=lambda x: sort_vm_key(x[0]))
            while pms[i].is_overloaded():
                vm, vm_idx = pms[i].vms[-1]
                pms[i].remove_vm(vm_idx)
                have_to_migrate.push(vm, vm_idx)
        elif len(pms[i].vms) <= max_migrations_to_free:
            dirty[i] = True

    sorted_pms = sorted(enumerate(pms), key=lambda x: sort_pm_key(x[1]) + 4 * (len(x[1].vms) == 0) + 2 * dirty[x[0]])

    while not have_to_migrate.empty():
        vm_idx, vm = have_to_migrate.pop()
        for i in range(len(sorted_pms)):
            pm_idx = sorted_pms[i][0]
            if pms[pm_idx].check_vm(vm):
                pms[pm_idx].place_vm(vm, vm_idx)

                for t in range(len(pms)):
                    placement[t][vm_idx] = 0
                placement[pm_idx][vm_idx] = 1
                num_migrations += 1
                dirty[pm_idx] = False
                break

    sorted_pms = sorted(enumerate(pms), key=lambda x: sort_pm_key(x[1]) + 4 * (len(x[1].vms) == 0) + 2 * dirty[x[0]])

    for i in range(len(dirty)):
        if dirty[i]:
            new_pm_idxes = []
            can_be_placed = True
            for vm, vm_idx in pms[i].vms:
                if can_be_placed:
                    for i in range(len(sorted_pms)):
                        pm_idx = sorted_pms[i][0]
                        if dirty[pm_idx]:
                            can_be_placed = False
                            break
                        if pms[pm_idx].check_vm(vm):
                            pms[pm_idx].place_vm(vm, vm_idx)
                            new_pm_idxes.append((pm_idx, vm_idx))
                            dirty[pm_idx] = False
                            break
            if can_be_placed:
                pms[i].clear()

                for pm_idx, vm_idx in new_pm_idxes:
                    for t in range(len(pms)):
                        placement[t][vm_idx] = 0
                    placement[pm_idx][vm_idx] = 1
                num_migrations += 1
            else:
                for pm_idx, vm_idx in new_pm_idxes:
                    pms[pm_idx].remove_vm(vm_idx)

    return placement, num_migrations
