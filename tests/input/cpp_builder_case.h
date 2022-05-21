#include <iostream>

namespace ns1 {
namespace ns2 {

class A {

    void foo() {
        auto i = 0;
        ++i;
    }

    void bar();
};
} // namespace ns2
} // namespace ns1

class B {
    void b_foo() {
        auto b_f = 0;
        ++ b_f;
    }
};

namespace ns3 {
namespace ns4 {
class C {
    void c_foo() {
        auto c = 0;
    }
};
}

void baaaa() {
    auto bbb = 0;
}
}
