
struct treasure {
	// maximal length: 64
	char *location_name;
	char *description;
};

typedef struct treasure treasure_t;

treasure_t *load_treasure(char *name);

void add_treasure(void);

void view_treasure(void);

void modify_treasure(void);
