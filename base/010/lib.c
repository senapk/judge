#include "lib.h"
Res soma(int a, int b){
    Res r;
    return (Res) {a + b, a - b};
}