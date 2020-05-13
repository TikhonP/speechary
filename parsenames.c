#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>


const char* filename = "names/yob2018.txt";


void lower(char str[]) {
  while (*str!='\0') {
    *str = tolower(*str);
    str++; 
  }
}

char gender(char inname[]) {
  lower(inname);
  //printf("%s\n", inname);
  FILE *in = fopen(filename, "r");
 
 char str[30];
 
 while (fscanf(in, "%s", str) == 1) {
	char *token = strtok(str, ",");
     char *name = token; 
     lower(name);
     if (strstr(inname, name)) {
       token = strtok(NULL, ",");
       char *gender = token;
       //token = strtok(NULL, ",");
       //char *p = token;
       //int popularity = atoi(p);
     //printf("%s-%s-%d\n", name, gender, popularity);
		 return *gender;
   }
  }
 return 'E';
}


int main() {
  //char nam[] = "TikHOnN";
  //char g = gender(nam);
  //printf("%c\n", g); 
  return 0;
}
