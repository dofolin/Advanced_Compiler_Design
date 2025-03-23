// From https://www.programiz.com/c-programming/examples/power-recursion
int power(int n1, int n2);
int main() {
  int base, a, result;
  base = 123;
  a = 456;
  result = power(base, a);
  return result;
}

int power(int base, int a) {
  if (a != 0)
    return (base * power(base, a - 1));
  else
    return 1;
}
