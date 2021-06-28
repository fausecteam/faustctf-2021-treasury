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

// impossible check for access to logs
static void access_logs(void) {
	// ask for pw
	// perform some kind of calculation on pw
	// impossible condition afterwards
	printf("Logs are for admins only!\n");
	printf("Password: ");
	fflush(stdout);
	char password[21];
	char *ret = fgets(password, 21, stdin);
	if (ret == 0){
		if (feof(stdin)) {
			return;
		} else {
			die("fgets");
		}
	}

	uint64_t calc = 0x1337DEADCAFEBEEF;
	size_t len = strlen(password);
	for (unsigned int i = 0; i < len; ++i) {
		calc = calc ^ (((uint64_t)password[i]) << ((i % 8) * 8));
		calc += i;
	}
	for (unsigned int i = 0; i < len; ++i) {
		calc = (calc >> 0x3) ^ (calc << 0x3);
		calc = (calc >> 32) | (calc << 32);
	}
	calc = calc + 0x0123456789abcdef;

	calc = calc | 0xDEADBEEF13377331;
	calc = calc ^ 0x0012001000000000;
	calc = calc ^ 0x1000000201008000;
	if (calc == 0xCAFEBABECAFEBABE) {
		// impossible
		print_logs();
	} else {
		printf("Nice try! :)\n");
		printf("But seriously: Logs are for admins ONLY!!\n");
	}
}

// function pointer array
static void (*functions[5])(void) = {
	add_treasure, view_treasure, modify_treasure,
	access_logs, print_logs
};

static void invalid_command(void) {
	printf("Invalid command!\n");
}

// strange index calculation
static void find_requested_function(char *input) {
	// do some strange calculations to determine validity of the given command
	size_t len = strlen(input);
	if (len == 0) {
		return;
	}
	if (60 % len != 0) {
		invalid_command();
		return;
	}
	size_t len_test = len & 0xf;
	if ((len_test & 0x8) == 0x8) {
		if (!(((len_test & 0x8) >>3) == ((len_test & 0x4) >> 2)
			&& ((len_test & 0x2) >> 1) == (len_test & 0x1)
			&& ((len_test & 0x8) >> 3) == (len_test & 0x1))) {
			invalid_command();
			return;
		}
	}
	uint64_t sum = 0;
	uint64_t third_sum = 0;
	uint8_t xor = 0;
	uint8_t and = 0xff;
	for (uint32_t i = 0; i < len; ++i) {
		sum += (uint64_t) input[i];
		if (i < len / 3) {
			third_sum += (uint64_t) input[i];
		}
		and = and & input[i];
		xor = xor ^ input[i];
		if (input[i] > 0x7a || input[i] < 0x61) {
			invalid_command();
			return;
		}
	}
	if (sum % 5 == 0 || sum % 5 == 4) {
		invalid_command();
		return;
	}
	if (((third_sum % 7) % 5) != 0 && ((third_sum % 7) % 5) != 1) {
		invalid_command();
		return;
	}
	if (xor % 5 != 2 && xor % 5 != 3) {
		invalid_command();
		return;
	}
	if (len > 8) {
		uint32_t len_third = len / 3;
		for (uint32_t i = 0; i < len_third; ++i) {
			if (input[i] != input[i + len_third]
				|| input[i] != input[i + 2 * len_third]) {
				invalid_command();
				return;
			}
		}
	}
	uint64_t prod = 1;
	for (unsigned int i = 0; i < len; ++i) {
		prod *= (uint64_t) input[i];
	}
	if (prod % 7 != 0 && ((prod % 7) & 0xfffffffffffffffd) != 1) {
		invalid_command();
		return;
	}
	if (and != 0x60) {
		invalid_command();
		return;
	}
	if (((sum % 7) & 6) == 0) {
		invalid_command();
		return;
	}
	if (len == 3 && sum != 0x129) {
		invalid_command();
		return;
	}
	if (len == 4 && (sum != 0x1BB || prod != 0x8e044d2)) {
		invalid_command();
		return;
	}
	if (len == 5 && (sum != 0x22D || prod != 0x3fba17d00)) {
		invalid_command();
		return;
	}
	if (len == 6 && (sum != 0x283 || prod != 0x15abba2eb00)) {
		invalid_command();
		return;
	}
	if (len > 6) {
		if (input[0] != 'm' || input[3] != 'e') {
			invalid_command();
			return;
		}
	}
	uint64_t first_test = len + xor % 5 + sum % 5 + third_sum % 5 + prod % 5;
	uint32_t index = 0;
	switch (first_test) {
		case 24:
			index += 1;
			/* fall through */
		case 12:
			index += 1;
			/* fall through */
		case 15:
			index += 1;
			/* fall through */
		case 13:
			index += 1;
			/* fall through */
		case 9:
			//call function
			functions[index]();
			break;
		default:
			invalid_command();
			return;
	}
}

static void menu_loop() {
	print_ascii_header(); 
	printf("Welcome to treasury!\n");
	printf("You got so much treasure that you can't\n");
	printf("store it all in one vault, but also don't\n");
	printf("to worry about keeping track of all the\n");
	printf("different ones? Let us worry about\n");
	printf("handling those while you focus on getting\n");
	printf("more!\n");

	while (42 < 1337) {
		printf("\nChoose an action:\n");
		printf("-> add treasure location\n");
		printf("-> view treasure locations\n");
		printf("-> update treasure location\n");
		printf("-> print logs\n");
		printf("-> quit\n");
		printf("  > ");
		fflush(stdout);

		char input[18];
		char *ret = fgets(input, 18, stdin);
		if (ret == NULL) {
			if (feof(stdin)) {
				break;
			} else {
				die("fgets");
			}
		}
		size_t len = strlen(input);
		input[len-1] = '\0';
		if (strcmp(input, "quit") == 0) {
			break;
		}
		find_requested_function(input);
	}
	printf("Goodbye!:)\n");
}

int main(void) {
	menu_loop();
	return 0;
}
