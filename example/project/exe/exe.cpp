#include <dep.hpp>

int main(int argc, char *argv[]) {
    for(int i = 1; i < argc; ++i) {
        dep_print_string(argv[1]);
    }
    return 0;
}
