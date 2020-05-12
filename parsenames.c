#include <stdlib.h>
#include <stdio.h>
#include <string.h>


const char* filename = "names/yob2018.txt";


char gender(char* inname) {
 // printf("%s\n", inname);
  FILE *in = fopen(filename, "r");
 
 char str[30];
 
 while (fscanf(in, "%s", str) == 1) {
	char *token = strtok(str, ",");
     char *name = token; 
     if (strstr(inname, name)) {
       token = strtok(NULL, ",");
       char *gender = token;
       token = strtok(NULL, ",");
       char *p = token;
       int popularity = atoi(p);
     //printf("%s-%s-%d\n", name, gender, popularity);
		 return *gender;
   }
  }
 return 'E';
}


int main() {
  //char g = gender("Tikhon");
  //printf("%c\n", g); 
  return 0;
}
