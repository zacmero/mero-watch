typedef unsigned char u8;

void mero_ui_free(void *memory)
{
    /* Native window_show allocation failure dispatches platform free through
     * global 0x0010b448, byte offset 16 (0x0600f63a..0x0600f646). */
    u8 *api = *(u8 **)0x0010b448;
    void (*release)(void *);
    if (!memory || !api)
        return;
    release = *(void (**)(void *))(api + 16);
    if (release)
        release(memory);
}
