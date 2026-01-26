#include <iostream>
#include <vector>

int main () 
{
   
    std::vector<size_t> vec;
    std::vector<size_t> mask = {1, 3, 4, 6, 7, 11, 12};
    size_t src_start = mask[0];

    mask.push_back(mask.back() + 1);

    for (size_t i = 0; i < mask.size(); ) {

        while (i + 1 < mask.size() &&
               mask[i + 1] == mask[i] + 1) {
            ++i;
            ++src_start;
        }
        src_start += 1;
        i += 1;

        std::cout << src_start << " " << mask[i] << "\n";

        const size_t ref_src_start = src_start;
        while (src_start < mask[i]) {
            vec.push_back(src_start);
            src_start += 1;
        }

        i         += 1;
        src_start += 1;
    }

    for (auto el : vec) {
        std::cout << el << " ";
    }
    std::cout << "\n";

    return 0;
}




