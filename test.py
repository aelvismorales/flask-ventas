def find_modified_deleted_and_added(data1, data2):
    modified = []
    deleted = []
    added = []

    # Crear conjuntos de 'id' para comparación
    set_ids_data1 = {item['id'] for item in data1}
    set_ids_data2 = {item['id'] for item in data2}

    # Encontrar elementos modificados y eliminados
    for item in data1:
        if item['id'] in set_ids_data2:
            corresponding_item = next((i for i in data2 if i['id'] == item['id']), None)
            if corresponding_item and corresponding_item != item:
                modified.append(item)
        else:
            deleted.append(item)

    # Encontrar elementos agregados
    for item in data2:
        if item['id'] not in set_ids_data1:
            added.append(item)

    return modified, deleted, added

# Datos iniciales
data1 = [
    {"id": 1, "precio": 55, "cantidad": 10},
    {"id": 2, "precio": 55, "cantidad": 10},
    {"id": 3, "precio": 55, "cantidad": 10}
]

data2 = [
    {"id": 2, "precio": 55, "cantidad": 8},
    {"id": 3, "precio": 55, "cantidad": 10},
    {"id": 4, "precio": 25, "cantidad": 4}
]

# Encontrar elementos modificados, eliminados y agregados
modified_items, deleted_items, added_items = find_modified_deleted_and_added(data1, data2)

print("Datos modificados en la lista 1:")
print(modified_items)

print("\nDatos eliminados de la lista 1:")
print(deleted_items)

print("\nDatos agregados en la lista 2:")
print(added_items)
