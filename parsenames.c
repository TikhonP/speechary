#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>


const char* filename = "names/yob2018.txt";
char seps[]   = ",";

void lower(char []);

typedef struct genderName {
    char *name;
    char gender;
    int popularity;
    struct genderName *next;
} genderName;

typedef struct splittedwords {
    char *name;
    struct spittedwords *next;
} splittedwords;

genderName *readdata() {
    FILE *in = fopen(filename, "r");
    char str[30];
    genderName *start = NULL;
    genderName *i = NULL;

    while (fscanf(in, "%s", str) == 1) {
        genderName *next = malloc(sizeof(genderName));
        char *next_token = NULL;
        char *name = strtok_r(str, seps, &next_token);
        lower(name);
        next->name = strdup(name);
        next->gender = *(strtok_r(NULL, seps, &next_token));
        next->popularity = atoi(strtok_r(NULL, seps, &next_token));
        if (i != NULL)
            i->next = next;
        else if (start==NULL)
            start = next;
        i=next;
        // printf("%s-%c-%d\n", i->name, i->gender, i->popularity);
    }
    fclose(in);
    return start;
}

void releasesplt(splittedwords *i) {
    while (i != NULL) {
		splittedwords *next = i->next;
		free(i->name);
		free(i);
		i = next;
	}
}

splittedwords *split(char *word) {
    splittedwords *i = NULL;
	splittedwords *start = NULL;

    char sep[] = "_.- 1234567890";
    char *nexttok = NULL;
    char *w = strtok_r(word, sep, &nexttok);

    while (w != NULL) {
		splittedwords *next = malloc(sizeof(splittedwords));
        next->name = strdup(w);
        if (i != NULL)
            i->next = next;
		else if (start==NULL)
		    start = next;
        i=next;
        w = strtok_r(NULL, sep, &nexttok);
    }
    return start;
}


char gender(genderName *i, char *name, double* score) {
    int maleS = 0;
    int femaleS = 0;
    splittedwords *s = split(name);
    splittedwords *j = s;
    while (j!=NULL) {
        name = j->name;
        lower(name);
        while (i!=NULL) {
            char *curname = i->name;
            if (strstr(name, curname)) {
                char gender = i->gender;
                int popularity = i->popularity;
                if (gender == 'M') {
                    maleS += popularity;
                }
                else if (gender == 'F') {
                    femaleS += popularity;
                }

                // printf("%s-%c-%d\n", name, gender, popularity);
            }

            i = i->next;
        }
        j = j->next;
    }
    releasesplt(s);
    if (maleS>femaleS) {
        *score = 1-(float)femaleS/maleS;
        // printf("Answer is 'M', score %.2f\n", *score);
        return 'M';
    }
    else if (femaleS>maleS) {
        *score = 1-(float)maleS/femaleS;
        // printf("Answer is 'F', score %.2f\n", *score);
        return 'F';
    }
    else if ((maleS==femaleS) && (maleS!=0)) {
        *score = 0.5;
        // printf("Answer is 'none', score 0.5\n");
        return 'E';
    }
    else {
        *score = 0;
        // printf("Answer is 'none', matches did not found\n");
        return 'E';
    }
}

void lower(char str[]) {
    while (*str!='\0') {
        *str = tolower(*str);
        str++;
    }
}

void release(genderName *i) {
    while(i != NULL) {
        genderName *next = i->next;
        free(i->name);
        free(i);
        i = next;
    }
}

/*
void prints(genderName *i) {
	while (i != NULL) {
			printf("--------------------\nPointer - %p\nName - %s (%p)\nGender - %c\nPopularity - %d\nNext - %p\n", i, i->name, i->name, i->gender, i->popularity, i->next);
			i = i->next;
	}
	puts("-----------------");
}
*/

int main() {
    genderName *s = readdata();
    char name[30];
    double score;
    while(fscanf(stdin, "%s", name) == 1) {
        if (*name=='e') {
            break;
        }
        char a = gender(s, name, &score);
        printf("Returned is '%c', score %.2f\n", a, (float)score);
    }
    //prints(s);
    release(s);
    return 0;
}
