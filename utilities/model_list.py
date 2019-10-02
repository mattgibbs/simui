from p4p.client.thread import Context
from p4p.nt import NTTable
import numpy as np

c = Context('pva')

def pv_table():
    return c.get("BMAD:SYS0:1:FULL_MACHINE:DESIGN:TWISS")

def model_list(start_element=None, end_element=None):
    table = unwrap_to_np(c.get("BMAD:SYS0:1:FULL_MACHINE:DESIGN:TWISS"))
    start_index = 0
    if start_element:
        i = np.argmax(table['element']==start_element.upper())
        # if nothing is found, np.argmax returns 0, so we need to check if
        # we got a zero because the first element was a match, or because
        # it wasn't found at all.
        if i == 0 and table['element'][0] != start_element.upper():
            raise ValueError("Start element not found in table.")
        start_index = i
    end_index = -1
    if end_element:
        i = np.argmax(table['element']==end_element.upper())
        if i == 0 and table['element'][0] != end_element.upper():
            raise ValueError("End element not found in table.")
        end_index = i
    return table[start_index:end_index]

def unwrap_to_np(value):
    m = np.zeros(len(value.value.items()[0][1]), dtype=[('element', 'U30'), ('device_name', 'U30'), ('s', 'float32'), ('length', 'float32'), ('p0c', 'float32'), ("alpha_x", "float32"), ("beta_x", "float32"), ("eta_x", "float32"), ("etap_x", "float32"), ("psi_x", "float32"), ("alpha_y", "float32"), ("beta_y", "float32"), ("eta_y", "float32"), ("etap_y", "float32"), ("psi_y", "float32"), ('r_mat', 'float32', (6,6))])
    for col_name, data in value.value.items()[0:14]:
        m[col_name] = data
    m['r_mat'] = np.reshape(np.array([
        value.value.items()[15][1], #R11
        value.value.items()[16][1], #R12
        value.value.items()[17][1], #R13
        value.value.items()[18][1], #R14
        value.value.items()[19][1], #R15
        value.value.items()[20][1], #R16
        value.value.items()[21][1], #R21
        value.value.items()[22][1], #R22
        value.value.items()[23][1], #R23
        value.value.items()[24][1], #R24
        value.value.items()[25][1], #R25
        value.value.items()[26][1], #R26
        value.value.items()[27][1], #R31
        value.value.items()[28][1], #R32
        value.value.items()[29][1], #R33
        value.value.items()[30][1], #R34
        value.value.items()[31][1], #R35
        value.value.items()[32][1], #R36
        value.value.items()[33][1], #R41
        value.value.items()[34][1], #R42
        value.value.items()[35][1], #R43
        value.value.items()[36][1], #R44
        value.value.items()[37][1], #R45
        value.value.items()[38][1], #R46
        value.value.items()[39][1], #R51
        value.value.items()[40][1], #R52
        value.value.items()[41][1], #R53
        value.value.items()[42][1], #R54
        value.value.items()[43][1], #R55
        value.value.items()[44][1], #R56
        value.value.items()[45][1], #R61
        value.value.items()[46][1], #R62
        value.value.items()[47][1], #R63
        value.value.items()[48][1], #R64
        value.value.items()[49][1], #R65
        value.value.items()[50][1], #R66
    ]).T, (-1,6,6))
    return m
        