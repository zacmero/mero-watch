ENTRY(mero_menu_touch)
mero_ui_alloc = 0x0600de96;
mero_ui_text = 0x0603aeac;
mero_ui_element = 0x0600de5c;
mero_ui_redraw = 0x0600e8ea;
mero_ui_window = 0x060006ba;
mero_ui_menu = 0x0602e3a4;
SECTIONS {
    . = 0x0613d6dc;
    .text : { *(.text*) *(.rodata*) }
    /DISCARD/ : { *(.comment*) *(.note*) *(.eh_frame*) }
}
