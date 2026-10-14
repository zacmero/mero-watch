ENTRY(mero_panel_probe)
mero_get_element = 0x0600de5c;
mero_redraw = 0x0600e8ea;
mero_set_text = 0x0603aeac;
SECTIONS {
    . = 0x0603f01a;
    .text : { *(.text*) }
    /DISCARD/ : { *(.comment*) *(.note*) *(.eh_frame*) }
}
