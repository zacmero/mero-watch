#ifndef MERO_SPECS_H
#define MERO_SPECS_H

typedef unsigned int mero_u32;

struct mero_heap_specs {
    mero_u32 free_bytes;
    mero_u32 minimum_free_bytes;
    mero_u32 allocator_region_bytes;
};

/* Stock 1.0.0.4 bindings traced from its mem_stats routine. Returns zero for
 * an inconsistent snapshot. allocator_region_bytes is not total chip RAM. */
int mero_read_heap_specs(struct mero_heap_specs *out);

#endif
