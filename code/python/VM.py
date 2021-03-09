from Commons import gen_load


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

    def mean_demand(self):
        demand = 0
        for tr in self.traits:
            demand += self.traits[tr] * self.load[tr]
        return demand / len(self.traits)
