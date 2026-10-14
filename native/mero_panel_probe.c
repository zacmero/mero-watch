/* First native-code probe for the exact inspected PID76 stock application.
 * Temporarily use the Music text widget; do not replace its media controls.
 * Binding provenance and patch boundaries: docs/native-panel-probe.md.
 */
typedef unsigned char u8;
typedef unsigned int u32;

extern void *mero_get_element(u32 id);
extern int mero_redraw(void *element);
extern int mero_set_text(void *element, const char *format,
                         const char *text, int length, int mode);

void mero_panel_probe(void)
{
    u8 *element = mero_get_element(0x143002);
    if (!element)
        return;
    mero_set_text(element, (const char *)0x0608451f,
                  (const char *)0x06084ed4, 10, 2);
    if (!(element[32] & 4))
        mero_redraw(element);
}
