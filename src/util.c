#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <stdint.h>

#include "include/treasure.h"
#include "include/util.h"

void die(char *name) {
	printf("Well, seems like there is some kind of a problem. \n");
	printf("Please try again later.\n");
	fflush(stdout);
	perror(name);
	exit(1);
}

int log_write_access(char *name) {
	int fd;
	char filename[sizeof(SAVE_DIR) + 5];
	strcpy(filename, SAVE_DIR);
	strcat(filename, ".log");
	fd = open(filename, O_WRONLY|O_CREAT|O_APPEND, S_IRUSR|S_IWUSR);
	if (fd == -1) {
		return -1;
	}

	size_t len = strlen(name);
	if (write(fd, name, len) == -1) {
		return -1;
	}
	if (write(fd, "\n", 1) == -1) {
		return -1;
	}
	close(fd);
	return 0;
}

void print_logs(void) {
	char filename[sizeof(SAVE_DIR) + 5];
	strcpy(filename, SAVE_DIR);
	strcat(filename, ".log");
	FILE *fp_log = fopen(filename, "r");
	if (fp_log == NULL) {
		die("fopen");
	}

	char line[256];
	int pos = 0;
	while(fgets(line, 256, fp_log) != NULL) {
		size_t length = strlen(line);
		if (line[length - 1] == '\n') {
			line[length - 1] = '\0';
		}
		if (length == 1) {
			continue;
		}

		treasure_t *tr = load_treasure(line);
		if (tr == NULL) {
			continue;
		}

		printf("%d: %s - %s\n", (pos + 1), tr->location_name, tr->description);
		free(tr->location_name);
		free(tr->description);
		free(tr);

		++pos;
	}
	fclose(fp_log);
	printf("That's it!\n");
}

void print_ascii_header(void) {
	printf("  _                                       \n");
	printf(" | |                                      \n");
	printf(" | |_ _ __ ___  __ _ ___ _   _ _ __ _   _ \n");
	printf(" | __| '__/ _ \\/ _` / __| | | | '__| | | |\n");
	printf(" | |_| | |  __/ (_| \\__ \\ |_| | |  | |_| |\n");
	printf("  \\__|_|  \\___|\\__,_|___/\\__,_|_|   \\__, |\n");
	printf("                                     __/ |\n");
	printf("                                    |___/ \n");
	printf("\n");
}
