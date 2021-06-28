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

static int save_treasure(treasure_t *tr) {
	char filename[sizeof(SAVE_DIR) + 65];
	strcpy(filename, SAVE_DIR);
	strcat(filename, tr->location_name);
	int fd = open(filename, O_WRONLY | O_EXCL|O_CREAT, S_IRUSR|S_IWUSR);
	if (fd == -1) {
		if (errno == EEXIST) {
			return -2;
		}
		return -1;
	}
	size_t length = strlen(tr->description);
	if (write(fd, tr->description, length) == -1) {
		return -1;
	}

	close(fd);
	int ret = log_write_access(tr->location_name);
	if (ret != 0) {
		int tmp_errno = errno;
		remove(filename);
		errno = tmp_errno;
	}
	return ret;
}

treasure_t *load_treasure(char *name) {
	char filename[sizeof(SAVE_DIR) + 65];
	strcpy(filename, SAVE_DIR);
	strcat(filename, name);

	FILE *fp = fopen(filename, "r");
	if (fp == NULL) {
		if (errno == ENOENT) {
			return NULL;
		}
		die("fopen");
	}

	size_t len = strlen(name);

	char *location = (char *) malloc(sizeof(char) * len);
	if (location == NULL) {
		die("malloc");
	}
	strcpy(location, name);
	char *descr = (char *) malloc(sizeof(char) * 256);
	if (descr == NULL) {
		free(location);
		die("malloc");
	}
	treasure_t *tr = (treasure_t *) malloc(sizeof(treasure_t));
	if (tr == NULL) {
		free(location);
		free(descr);
		die("malloc");
	}
	if (fgets(descr, 256, fp) == NULL) {
		if (ferror(fp)) {
			free(location);
			free(descr);
			free(tr);
			die("fgets");
		}
	}
	tr->location_name = location;
	tr->description = descr;
	return tr;
}

void add_treasure(void) {
	printf("Give it a name: ");
	fflush(stdout);
	char name[64];
	char *s = fgets(name, 64, stdin);
	if (s == NULL) {
		if (feof(stdin)) {
			return;
		} else {
			die("fgets");
		}
	}
	size_t len = strlen(name);
	name[len - 1] = '\0';

	if (strchr(name, '.') != NULL || strchr(name, '/') != NULL) {
		printf("Bad characters in location name!\n");
		return;
	}

	printf("Describe it: ");
	fflush(stdout);
	char description[256];
	s = fgets(description, 256, stdin);
	if (s == NULL) {
		if (feof(stdin)) {
			return;
		} else {
			die("fgets");
		}
	}
	len = strlen(description);
	description[len - 1] = '\0';

	treasure_t tr = {name, description};
	int ret = save_treasure(&tr);
	if (ret == -1) {
		die("save_treasure");
	} else if (ret == -2) {
		printf("There already is treasure at this location!\n");
		fflush(stdout);
	} else {
		printf("Great! We'll keep this information save for you! :)\n");
		fflush(stdout);
	}
}

void view_treasure(void) {
	printf("Location name: ");
	fflush(stdout);
	char name[64];
	char *s = fgets(name, 64, stdin);
	if (s == NULL) {
		if (feof(stdin)) {
			return;
		} else {
			die("fgets");
		}
	}
	size_t len = strlen(name);
	name[len - 1] = '\0';

	if (strchr(name, '.') != NULL || strchr(name, '/') != NULL) {
		printf("Bad characters in location name!\n");
		return;
	}

	treasure_t *tr = load_treasure(name);
	if (tr == NULL) {
		printf("No treasure found at this location!\n");
		return;
	}

	printf("\n%s\n", tr->location_name);
	printf("-------------\n");
	printf("Description: %s\n", tr->description);
	fflush(stdout);
	free(tr->location_name);
	free(tr->description);
	free(tr);
}

void modify_treasure(void) {
	printf("Sorry, feature not yet implemented! \n");
	printf("Please wait for the next release.\n");
}
