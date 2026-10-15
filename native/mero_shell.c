#include "mero_specs.h"

typedef unsigned char u8;

/* Bindings are supplied by the stock-specific linker, not SDK structs. */
extern void *mero_ui_alloc(mero_u32 size);
extern void mero_ui_free(void *memory);
extern int mero_ui_text(void *element, const char *code, const char *text,
                        int length, int mode);
extern void *mero_ui_element(mero_u32 id);
extern int mero_ui_redraw(void *element);
extern int mero_ui_window(mero_u32 id);
extern int mero_ui_menu(void);

#define SHELL_PAGE 119u
#define SHELL_WINDOW ((SHELL_PAGE << 17) | 0x800u | SHELL_PAGE)
#define SHELL_TEXT ((SHELL_PAGE << 17) | 0x3000u)
#define STATE_MAGIC 0x4d535031u

struct text_state {
    mero_u32 magic;
    char text[64];
};

static char *literal(char *out, const char *value)
{
    while (*value)
        *out++ = *value++;
    return out;
}

static char *decimal(char *out, mero_u32 value)
{
    char digits[10];
    unsigned count = 0;
    do {
        digits[count++] = '0' + value % 10;
        value /= 10;
    } while (value);
    while (count)
        *out++ = digits[--count];
    return out;
}

static char **text_pointer(void *element)
{
    /* Traced native text setter writes attrs.str at element byte 112. */
    return (char **)((u8 *)element + 112);
}

static struct text_state *state(void *element)
{
    char *text = *text_pointer(element);
    struct text_state *value;
    /* INIT clears the template pointer before storing only an owned buffer.
     * Do not assume a physical/virtual allocator address range. */
    if (!text)
        return 0;
    value = (struct text_state *)(text - sizeof(mero_u32));
    return value->magic == STATE_MAGIC ? value : 0;
}

static void update(void *element)
{
    struct text_state *value = state(element);
    struct mero_heap_specs heap;
    mero_u32 row = *(mero_u32 *)((u8 *)element + 4) & 0x3ffu;
    char *out;
    int available;
    if (!value)
        return;
    out = value->text;
    available = mero_read_heap_specs(&heap);
    if (row == 0)
        out = literal(out, "mero-shell");
    else if (row >= 1 && row <= 3) {
        out = literal(out, row == 1 ? "free heap: " : row == 2 ? "low heap: " : "physical pool: ");
        if (available) {
            out = decimal(out, row == 1 ? heap.free_bytes : row == 2 ? heap.minimum_free_bytes : heap.allocator_region_bytes);
            out = literal(out, " B");
        } else
            out = literal(out, "unavailable");
    } else if (row == 4)
        out = literal(out, "ISA: PI32v2/r3");
    else
        out = literal(out, row == 5 ? "Refresh" : "Back");
    *out = 0;
    mero_ui_text(element, "ascii", value->text, out - value->text, 0);
}

int mero_shell_text_change(void *element, int event, void *private_data)
{
    struct text_state *value;
    (void)private_data;
    if (event == 1) {
        /* Clear the template's non-owned pointer before allocating. */
        mero_ui_text(element, "ascii", 0, 0, 0);
        value = mero_ui_alloc(sizeof(*value));
        if (value) {
            value->magic = STATE_MAGIC;
            mero_ui_text(element, "ascii", value->text, 0, 0);
            update(element);
        }
    } else if (event == 10) {
        value = state(element);
        mero_ui_text(element, "ascii", 0, 0, 0);
        if (value) {
            value->magic = 0;
            mero_ui_free(value);
        }
    }
    return 0;
}

int mero_shell_touch(void *element, const mero_u32 *event)
{
    mero_u32 row, index;
    void *item;
    if (!event || event[0] != 7)
        return 0;
    row = *(mero_u32 *)((u8 *)element + 4) & 0x3ffu;
    if (row == 6) {
        mero_ui_menu();
        return 1;
    }
    if (row != 5)
        return 0;
    for (index = 0; index < 5; ++index) {
        item = mero_ui_element(SHELL_TEXT | index);
        if (item) {
            update(item);
            if (!(((u8 *)item)[32] & 4))
                mero_ui_redraw(item);
        }
    }
    return 1;
}

int mero_menu_touch(void *element, const mero_u32 *event)
{
    (void)element;
    if (!event || event[0] != 7)
        return 0;
    mero_ui_window(SHELL_WINDOW);
    return 1;
}

int mero_menu_text_change(void *element, int event, void *private_data)
{
    (void)private_data;
    if (event == 1)
        mero_ui_text(element, "ascii", "Mero", 4, 0);
    return 0;
}
