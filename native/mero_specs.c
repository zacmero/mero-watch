#include "mero_specs.h"

int mero_read_heap_specs(struct mero_heap_specs *out)
{
    const volatile mero_u32 *free_counter = (const volatile mero_u32 *)0x0010b300;
    const volatile mero_u32 *minimum_counter = (const volatile mero_u32 *)0x0010b2fc;
    const volatile unsigned short *region_start = (const volatile unsigned short *)0x0010f38c;
    const volatile unsigned short *region_end = (const volatile unsigned short *)0x0010f38e;
    mero_u32 start, end;

    if (!out)
        return 0;
    start = *region_start;
    end = *region_end;
    out->free_bytes = *free_counter;
    out->minimum_free_bytes = *minimum_counter;
    out->allocator_region_bytes = end >= start ? (end - start) << 7 : 0;
    /* The firmware logs heap and physical-region counters separately. Do not
     * assume the heap counter is bounded by that region (virtual allocation). */
    return end > start && out->minimum_free_bytes <= out->free_bytes;
}
