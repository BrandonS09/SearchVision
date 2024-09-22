# create_label_map.py

def create_label_map(class_names, output_path):
    with open(output_path, 'w') as f:
        for idx, class_name in enumerate(class_names, 1):
            f.write('item {\n')
            f.write(f'  id: {idx}\n')
            f.write(f"  name: '{class_name}'\n")
            f.write('}\n')
