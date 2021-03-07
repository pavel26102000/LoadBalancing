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
