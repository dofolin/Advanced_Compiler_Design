int add4(int x) {
  int y = 0;
  for (int i = 0; i < 1000000000; i++) {
    int z = i + i;
  }
  return x + 4;
}

int main() { return add4(38); }
