"""Build additional Mero launch controls and window from observed stock records.

Existing non-menu windows are byte-identical. The three proven menu variants
retain their controls and get an independent footer outside their fixed grids.
No Bluetooth or package writes are performed here.
"""
import binascii
import hashlib
import struct

from .native_style_inventory import inventory
from .native_control_tree import trees, control_tree

STOCK_SHA256 = "5778aea7b8cdaa01ebf7342b94cc277c2d6468c06547162b1d6a1447c9c45d93"
MENU_PAGES = (3, 7, 118)
SHELL_PAGE = 119
MENU_IMAGE_ID = 39


def walk(node):
    yield node
    for child in node['children']:
        yield from walk(child)


class Window:
    def __init__(self, payload, relocations, page):
        self.data = bytearray(payload)
        self.relocations = list(relocations)
        self.tag = page << 17
        self.page = page

    def append(self, value):
        self.data.extend(bytes(-len(self.data) % 4))
        position = len(self.data)
        self.data.extend(value)
        if len(self.data) >= 0x20000:
            raise ValueError('window exceeds observed relative pointer width')
        return position

    def pointer(self, position, target):
        struct.pack_into('<I', self.data, position, self.tag | target if target else 0)
        if position not in self.relocations:
            self.relocations.append(position)

    def css(self, template, rect):
        value = bytearray(template)
        value[1] = 0  # observed invisible byte; additional controls start visible
        struct.pack_into('<4I', value, 4, *rect)
        return self.append(value)

    def record(self, template, identifier):
        value = bytearray(template)
        value[4] = self.page
        struct.pack_into('<I', value, 8, identifier)
        return self.append(value)


def record_template(raw, node):
    start = node['offset']
    return raw[start:start + node['size']]


def css_template(raw, node):
    start = struct.unpack_from('<I', raw, node['offset'] + 12)[0] & 0x1ffff
    return raw[start:start + 36]


def menu_footer(raw, relocations, tree, page):
    window = Window(raw, relocations, page)
    nodes = list(walk(tree))
    layer = tree['children'][0]
    layout = next(node for node in nodes if node['sdk_type'] == 'layout')
    picture = next(node for node in nodes if node['sdk_type'] == 'picture')
    text = next(node for node in nodes if node['sdk_type'] == 'text')
    if tree['children'] != [layer] or layer['size'] != 32 or layout['size'] != 28:
        raise ValueError('unexpected menu layer/layout structure')

    # Keep the original layer and its entire descendant tree. Reserve a footer
    # by changing only that layer's viewport, not its grid/item counts or IDs.
    css = struct.unpack_from('<I', raw, layer['offset'] + 12)[0] & 0x1ffff
    struct.pack_into('<I', window.data, css + 16, 8500)
    old_layer = window.append(record_template(raw, layer))
    new_layer = window.record(record_template(raw, layer), (page << 17) | 0x1001)
    window.data[new_layer + 1] = 1
    if new_layer != old_layer + 32:
        raise ValueError('layer siblings are not contiguous')
    window.data[1] = 2
    window.pointer(24, old_layer)
    for offset in relocations:
        if layer['offset'] <= offset < layer['offset'] + layer['size']:
            window.relocations.append(old_layer + offset - layer['offset'])
    window.pointer(new_layer + 12, window.css(css_template(raw, layer), (0, 8500, 10000, 1500)))
    actions = window.append(bytes.fromhex('0000ffff'))
    window.pointer(new_layer + 20, actions)
    window.pointer(new_layer + 24, actions)
    new_layout = window.record(record_template(raw, layout), (page << 17) | 0xffe)
    window.data[new_layout + 1] = 2
    window.pointer(new_layer + 28, new_layout)
    window.pointer(new_layout + 12, window.css(css_template(raw, layer), (0, 0, 10000, 10000)))
    window.pointer(new_layout + 16, actions)
    window.pointer(new_layout + 20, actions)

    pic = window.record(record_template(raw, picture), (page << 17) | 0x23fe)
    label = window.record(record_template(raw, text), (page << 17) | 0x33fe)
    if label != pic + picture['size']:
        raise ValueError('footer children are not contiguous')
    window.pointer(new_layout + 24, pic)
    window.pointer(pic + 12, window.css(css_template(raw, picture), (3500, 500, 1700, 9000)))
    window.pointer(pic + 36, 0)
    images = window.append(struct.pack('<HH', 1, MENU_IMAGE_ID))
    window.pointer(pic + 40, images)
    window.pointer(pic + 44, images)
    window.pointer(pic + 48, 0)
    window.data[label + 16:label + 24] = b'none\0\0\0\0'
    window.data[label + 24:label + 32] = b'ascii\0\0\0'
    window.pointer(label + 12, window.css(css_template(raw, text), (5500, 500, 4000, 9000)))
    window.pointer(label + 40, window.append(bytes(4)))
    window.pointer(label + 44, 0)
    window.pointer(label + 48, 0)
    control_tree(window.data, window.relocations)
    return bytes(window.data), sorted(set(window.relocations))


def shell_window(raw, tree):
    nodes = list(walk(tree))
    layer = tree['children'][0]
    layout = next(node for node in nodes if node['sdk_type'] == 'layout')
    text = next(node for node in nodes if node['sdk_type'] == 'text' and
                raw[node['offset'] + 24:node['offset'] + 32].split(b'\0')[0] == b'text')
    root = bytearray(record_template(raw, tree))
    root[4] = SHELL_PAGE
    window = Window(root, [], SHELL_PAGE)
    layer_at = window.record(record_template(raw, layer), (SHELL_PAGE << 17) | 0x1000)
    layout_at = window.record(record_template(raw, layout), (SHELL_PAGE << 17) | 0xc00)
    window.data[1] = 1
    window.data[layer_at + 1] = 1
    window.data[layout_at + 1] = 7
    window.pointer(24, layer_at)
    window.pointer(layer_at + 28, layout_at)
    # All sibling records precede their CSS/lists, matching the native format.
    positions = [window.record(record_template(raw, text), (SHELL_PAGE << 17) | 0x3000 | i) for i in range(7)]
    window.pointer(layout_at + 24, positions[0])
    window.pointer(layer_at + 12, window.css(css_template(raw, layer), (0, 0, 10000, 10000)))
    window.pointer(layout_at + 12, window.css(css_template(raw, layer), (0, 0, 10000, 10000)))
    empty = window.append(bytes(4))
    actions = window.append(bytes.fromhex('0000ffff'))
    window.pointer(layer_at + 20, actions)
    window.pointer(layer_at + 24, actions)
    window.pointer(layout_at + 16, actions)
    window.pointer(layout_at + 20, actions)
    for index, position in enumerate(positions):
        window.data[position + 16:position + 24] = b'none\0\0\0\0'
        window.data[position + 24:position + 32] = b'ascii\0\0\0'
        window.pointer(position + 12, window.css(css_template(raw, text), (400, 300 + index * 1350, 9200, 1200)))
        window.pointer(position + 40, empty)
        window.pointer(position + 44, 0)
        window.pointer(position + 48, 0)
    control_tree(window.data, window.relocations)
    return bytes(window.data), sorted(set(window.relocations))


def build(stock):
    if hashlib.sha256(stock).hexdigest() != STOCK_SHA256:
        raise ValueError('unrecognized style')
    windows = inventory(stock)['windows']
    graphs = trees(stock)
    if len(windows) != SHELL_PAGE:
        raise ValueError('unexpected original window count')
    pieces = []
    for meta, graph in zip(windows, graphs):
        raw = stock[meta['offset']:meta['offset'] + meta['length']]
        if meta['index'] in MENU_PAGES:
            pieces.append(menu_footer(raw, meta['relocations'], graph['root'], meta['index']))
        else:
            pieces.append((raw, meta['relocations']))
    meta = windows[40]
    pieces.append(shell_window(stock[meta['offset']:meta['offset'] + meta['length']], graphs[40]['root']))
    header = bytearray(stock[:24])
    header[17] = len(pieces)
    output = bytearray(header + bytes(20 * len(pieces)))
    for index, (raw, relocations) in enumerate(pieces):
        output.extend(bytes(-len(output) % 4))
        start = len(output)
        output.extend(raw)
        output.extend(bytes(-len(output) % 2))
        table = len(output)
        packed = struct.pack('<' + 'H' * len(relocations), *relocations)
        output.extend(packed)
        normalized = bytearray(raw)
        for position in relocations:
            value = struct.unpack_from('<I', normalized, position)[0]
            struct.pack_into('<I', normalized, position, value & 0x1ffff)
        directory = 24 + index * 20
        struct.pack_into('<IIIHHH', output, directory, start, len(raw), table, len(packed),
                         binascii.crc_hqx(normalized, 0), binascii.crc_hqx(packed, 0))
        struct.pack_into('<H', output, directory + 18, binascii.crc_hqx(output[directory:directory + 14], 0))
    result = bytes(output)
    observed = inventory(result)
    if len(observed['windows']) != SHELL_PAGE + 1 or not all(all(w[key] for key in (
            'header_crc_matches', 'table_crc_matches', 'normalized_data_crc_matches',
            'pointer_targets_in_window')) for w in observed['windows']):
        raise ValueError('rebuilt style validation failed')
    trees(result)
    return result
