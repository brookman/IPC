def lookup_material(name):
    materials = {
        'default': ('1000', '1e5', '0.4'),
        'aluminium': ('2700', '7e10', '0.35'),
        'copper': ('8950', '1e11', '0.34'),
        'gold': ('19320', '8e10', '0.44'),
        'iron': ('7870', '2e11', '0.29'),
        'lead': ('11350', '2e10', '0.44'),
        'abs': ('1020', '2e09', '0.46'),
        'glass': ('2500', '7e10', '0.25'),
        'nylon': ('1150', '3e9', '0.39'),
        'wood': ('700', '1e10', '0.43'),
        'rubber': ('2300', '1e6', '0.47'),
        'hardrubber': ('1000', '5e6', '0.47'),
        'cork': ('240', '3e7', '0.26'),
        'hydrogel': ('1000', '1e5', '0.45')
    }

    mat = materials['default']
    if name and name in materials:
        mat = materials[name]
    return ' material {} {} {} '.format(mat[0], mat[1], mat[2])


def get_material(object):
    parts = object.name.split('_')
    material = lookup_material('default')
    if len(parts) >= 2:
        material = lookup_material(parts[1])
    return material