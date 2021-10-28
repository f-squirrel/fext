#include <iostream>

namespace ns1 {
namespace ns2 {

class A {
public:
    virtual void virtual_method (){}
};

class B : public A {
public:
    void foo(int a, bool b) { ++a; }
    template<typename T>
    void bar(T t) {t++; }
    static void zzz() {  }
    inline static void aaa() {  }
    void only_decl();
    void const_method() const {}
    void virtual_method () override {}
    auto auto_method() {
        return 42;
    }

    class C {
        void c_method() {}
    };
};

struct S {
    void f() {}
};
}
}

template<typename T>
class F {
    public:
        void foo(T v) { ++v; --v; T sum = v + v; }
};

inline void free_function() { int a = 0; ++a; }

template<typename T>
inline void free_function(T t) { int a = 0; ++a; }

inline void free_inline_function(int a) { a++; a = a + 1; free_function(a); }

void free_funciton_only_decl();

