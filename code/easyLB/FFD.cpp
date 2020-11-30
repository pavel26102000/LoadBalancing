#include <iostream>
#include <iomanip>
#include <vector>
#include <random>

using Placement = std::vector<std::vector<int>>;

struct PM {
    int64_t mem_capacity;
    int64_t mem_reserved;
};

const int kNumPMs = 8;
const int kNumVMs = 20;
const int kBigPMMem = 4096;
const int kBigVMMem = 1024;

Placement FFD(const std::vector<int64_t> &vm, const std::vector<PM> &pms, double l_m = 1, double r = 0) {
    Placement result(pms.size(), std::vector<int>(vm.size(), false));

    for (size_t j = 0; j < vm.size(); ++j) {
        for (size_t i = 0; i < pms.size(); ++i) {
            int64_t mem_available = pms[i].mem_capacity - pms[i].mem_reserved;
            double msla = l_m * mem_available;
            int64_t mem_consumption = 0;
            for (size_t t = 0; t < vm.size(); ++t) {
                mem_consumption += (result[i][t] > 0) * vm[t];
            }
            if (vm[j] <= msla * (1 + r) - mem_consumption) {
                result[i][j] = vm[j];
                break;
            }
        }
    }

    return result;
}

int main() {
    std::vector<PM> pms;
    pms.reserve(kNumPMs);
    for (size_t i = 0; i < kNumPMs / 8; ++i) {
        pms.push_back({kBigPMMem, kBigPMMem / 32});
    }

    for (size_t i = 0; i < kNumPMs / 2; ++i) {
        pms.push_back({kBigPMMem / 2, kBigPMMem / 32});
    }

    for (size_t i = 0; i < 3 * kNumPMs / 8; ++i) {
        pms.push_back({kBigPMMem / 4, kBigPMMem / 32});
    }

    std::vector<int64_t> vms;
    vms.reserve(kNumVMs);

    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<int> dist(1, kNumVMs / 2);

    int num_big = dist(gen);
    int num_medium = dist(gen);
    int num_small = kNumVMs - num_medium - num_big;

    for (int i = 0; i < num_big; ++i) {
        vms.push_back(kBigVMMem);
    }

    for (int i = 0; i < num_medium; ++i) {
        vms.push_back(kBigVMMem / 2);
    }

    for (int i = 0; i < num_small; ++i) {
        vms.push_back(kBigVMMem / 4);
    }

    Placement placement = FFD(vms, pms);

    std::string out_type;

    std::cin >> out_type;

    if (out_type != "int" && out_type != "bool") {
        throw std::out_of_range("Wrong output type");
    }

    for (size_t i = 0; i < pms.size(); ++i) {
        int64_t sum = 0;
        for (const auto& vm: placement[i]) {
            std::cout << std::setw(out_type == "int" ? 4 : 2) << (out_type == "int" ? vm : vm > 0) << "\t";
            sum += vm;
        }
        std::cout << std::setw(4) << "Total usage: " << sum << " / " << pms[i].mem_capacity - pms[i].mem_reserved;
        std::cout << std::endl;
    }

    return 0;
}
