#include <iostream>
#include <iomanip>
#include <vector>
#include <random>
#include "ortools/linear_solver/linear_solver.h"
#include "ortools/sat/cp_model.h"
#include "ortools/sat/model.h"


const int kNumPMs = 9;
const int kNumVMs = 14;

using Placement = std::vector<std::vector<int>>;

struct Machine {
    std::unordered_map<std::string, int64_t> traits;
};

struct PM : public Machine {
    PM() {
        std::mt19937 gen(42);
        std::uniform_int_distribution dist(1, 4);
        // вопрос не совсем понял как записывается память на хуавейклауд, взял что то своё
        traits["mem"] = 64 * dist(gen);
        traits["cpu"] = 64;
        // вопрос где взять iops? на сайте не нашёл
        traits["iops"] = 0;
        traits["pps"] = 8'500'000;
        traits["bandwidth"] = 30720;

        max_load["mem"] = 0.9;
        max_load["cpu"] = 0.9;
        max_load["iops"] = 0.8;
        max_load["pps"] = 0.8;
        max_load["bandwidth"] = 0.8;
    }

    std::unordered_map<std::string, double> max_load;
};

struct VM : public Machine {
    using DistributionParams = std::unordered_map<std::string, std::pair<double, double>>;
    using Distributions = std::unordered_map<std::string, std::normal_distribution<double>>;

    VM() {
        std::random_device rd;
        gen = std::mt19937(rd());

        set_default_traits();
        for (const auto& [trait, v] : traits) {
            dists[trait] = std::normal_distribution<double>(0.2, 0.05);
        }

        update_load();
    }

    VM(const DistributionParams& params, std::optional<std::unordered_map<std::string, double>> demands = std::nullopt) {
        std::random_device rd;
        gen = std::mt19937(rd());

        set_dists(params);
        set_default_traits();

        if (demands.has_value()) {
            for (const auto& [trait, v] : demands.value()) {
                traits[trait] = v;
            }
        }

        update_load();
    }

    void set_mem_intensive() {
        load["mem"] = std::uniform_real_distribution<double>(0.7, 1)(gen);
    }

    void update_load() {
        for (const auto&[k, v] : traits) {
            load[k] = dists[k](gen);
            if (load[k] < 0.01 || load[k] > 0.99) {
                load[k] = dists[k](gen);
            }
        }
    }

    void set_dists(const DistributionParams& d) {
        for (const auto& [trait, params] : d) {
            dists[trait] = std::normal_distribution<double>(params.first, params.second);
        }
    }

    std::unordered_map<std::string, double> load;

private:
    Distributions dists;
    std::mt19937 gen;

    void set_default_traits() {
        traits["mem"] = 42;
        traits["cpu"] = 8;
        traits["iops"] = 0;
        traits["pps"] = 750'000;
        traits["bandwidth"] = 4096;
    }
};

bool
check_trait(const std::vector<VM> &vm, size_t vm_idx, const PM &pm, const std::vector<int>& curr_placement,
            const std::string &name) {
    double available = pm.max_load.at(name) * pm.traits.at(name);
    int64_t consumption = 0;
    for (size_t t = 0; t < vm.size(); ++t) {
        consumption += (curr_placement[t] > 0) * vm[t].traits.at(name) * vm[t].load.at(name);
    }
    if (vm[vm_idx].traits.at(name) <= available - consumption) {
        return true;
    }
    return false;
}


// вопрос как сделать ffd когда так много параметров?
// пока что отсортировал по памяти
// может ли даже самый простой алгоритм выдавать плохие ответы, если все pmы имеют одинаковые capacity?
Placement FFD(std::vector<VM> vms, std::vector<PM> pms) {
    std::sort(vms.begin(), vms.end(), [](const VM& lhs, const VM& rhs) {
        return lhs.traits.at("mem") * lhs.load.at("mem") > rhs.traits.at("mem") * rhs.load.at("mem");
    });

    std::sort(pms.begin(), pms.end(), [](const PM& lhs, const PM& rhs) {
        return lhs.traits.at("mem") > rhs.traits.at("mem");
    });
    Placement result(pms.size(), std::vector<int>(vms.size(), false));

    size_t pm_idx = 1;

    for (size_t j = 0; j < vms.size(); ++j) {
        bool put = false;
        for (size_t i = 0; i < pm_idx; ++i) {
            if (check_trait(vms, j, pms[i], result[i], "mem") &&
                check_trait(vms, j, pms[i], result[i], "cpu") &&
                check_trait(vms, j, pms[i], result[i], "pps") &&
                check_trait(vms, j, pms[i], result[i], "iops") &&
                check_trait(vms, j, pms[i], result[i], "bandwidth")) {
                result[i][j] = true;
                put = true;
                break;
            }
        }

        if (!put) {
            result[pm_idx][j] = true;
            ++pm_idx;
        }
    }

    return result;
}

// как работает LL с несколькими
// как может возникнуть неоптимальная ситуация если все пороги равны
// так много вопросов и так мало ответов :(
Placement LL(std::vector<VM> vms, std::vector<PM> pms) {
    std::sort(vms.begin(), vms.end(), [](const VM& lhs, const VM& rhs) {
        return lhs.traits.at("mem") * lhs.load.at("mem") > rhs.traits.at("mem") * rhs.load.at("mem");
    });

    std::sort(pms.begin(), pms.end(), [](const PM& lhs, const PM& rhs) {
        return lhs.traits.at("mem") > rhs.traits.at("mem");
    });
    Placement result(pms.size(), std::vector<int>(vms.size(), false));

    size_t pm_idx = 1;

    for (size_t j = 0; j < vms.size(); ++j) {
        bool put = false;
        for (size_t i = 0; i < pm_idx; ++i) {
            if (check_trait(vms, j, pms[i], result[i], "mem") &&
                check_trait(vms, j, pms[i], result[i], "cpu") &&
                check_trait(vms, j, pms[i], result[i], "pps") &&
                check_trait(vms, j, pms[i], result[i], "iops") &&
                check_trait(vms, j, pms[i], result[i], "bandwidth")) {
                result[i][j] = true;
                put = true;
                break;
            }
        }

        if (!put) {
            result[pm_idx][j] = true;
            ++pm_idx;
        }
    }

    return result;
}

int main() {
    std::vector<PM> pms;
    pms.reserve(kNumPMs);
    for (size_t i = 0; i < kNumPMs; ++i) {
        pms.emplace_back();
    }

    std::vector<VM> vms;
    vms.reserve(kNumVMs);

    for (int i = 0; i < kNumVMs; ++i) {
        VM vm;
        vm.set_mem_intensive();
        vms.push_back(vm);
    }

    Placement placement = FFD(vms, pms);

    std::string out_type;

    std::cout << "What type of output do you want? (bool/int)" << std::endl;

    std::cin >> out_type;

    if (out_type != "int" && out_type != "bool") {
        throw std::out_of_range("Wrong output type");
    }

    int obj = 0;
    for (size_t i = 0; i < pms.size(); ++i) {
        int64_t sum = 0;
        for (const auto &vm: placement[i]) {
            std::cout << std::setw(out_type == "int" ? 6 : 3) << (out_type == "int" ? vm : vm > 0);
            sum += vm;
        }
        std::cout << std::setw(6) << "  Total usage: " << sum << " / " << pms[i].traits["mem"];
        std::cout << std::endl;
        if (sum > 0) {
            obj += 1;
        }
    }

    std::cout << "Objective: " << obj << std::endl;

    return 0;
}


