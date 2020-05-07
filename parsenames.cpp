#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>

const char* filename = "names/yob2018.txt";


int gender(std::string inname) {
  inname.lower();
  printf("%s\n", inname);
 //  FILE *in = fopen(filename, "r");
 //
 //  char str[30];
 //
 //  while (fscanf(in, "%s", str) == 1) {
 //    char *token = strtok(str, ",");
 //    char *name = token;
 //    lower_string(name);
 //    if (strstr(inname, name)) {
 //      token = strtok(NULL, ",");
 //      char *gender = token;
 //      token = strtok(NULL, ",");
 //      char *p = token;
 //      int popularity = atoi(p);
 //    printf("%s-%s-%d\n", name, gender, popularity);
 //  }
 // }
 return 0;
}


int main() {
  gender("Tikhon");
  return 0;
}
