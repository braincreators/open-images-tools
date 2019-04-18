import csv
import json

import click
import imagesize

from open_images_tools.utils import get_column, get_bbox


def parse_class_names(class_names_file):
    with open(class_names_file, 'r') as f:
        class_code_to_idx = {}
        class_idx_to_name = {}

        reader = csv.reader(f)
        for i, row in enumerate(reader):
            class_code_to_idx[row[0]] = i
            class_idx_to_name[i] = row[1]

    return class_idx_to_name, class_code_to_idx


def bbox_annotations_to_coco(images_folder, bbox_annotation_file, class_names_file):

    coco_spec = {
        'categories': [],
        'images': [],
        'annotations': []
    }

    class_idx_to_name, class_code_to_idx = parse_class_names(class_names_file)
    for i, name in class_idx_to_name.items():
        coco_spec['categories'].append({'id': i, 'name': name})

    with open(bbox_annotation_file, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        header = next(reader)
        header_to_idx = {header[idx]: idx for idx in range(len(header))}

        seen_images = set()
        image_id = 0
        for i, row in enumerate(reader):
            image_name = get_column(row, header_to_idx, 'ImageID')
            if image_name not in seen_images:
                image_id += 1
                image_file_name = '{}.jpg'.format(image_name)
                width, height = imagesize.get("{}/{}".format(images_folder, image_file_name))
                coco_spec['images'].append(
                    {
                        'id': image_id,
                        'height': height,
                        'width': width,
                        'file_name': image_file_name
                    }
                )

            bbox = get_bbox(row, header_to_idx, width=width, height=height)
            label_code = get_column(row, header_to_idx, 'LabelName')

            coco_spec['annotations'].append(
                {
                    'id': i,
                    'image_id': image_id,
                    'bbox': bbox.to_list(mode='xywh'),
                    'area': bbox.area(),
                    'iscrowd': get_column(row, header_to_idx, 'IsGroupOf'),
                    'category_id': class_code_to_idx[label_code]
                }
            )

    return coco_spec


@click.command()
@click.option('--images-folder', required=True, help='image folder path')
@click.option('--bbox-annotations', required=True, help='bounding box annotations csv file path')
@click.option('--class-descriptions', required=True, help='class descriptions csv file path')
@click.option('--output-file', required=True, help='output file path')
def main(images_folder, bbox_annotations, class_descriptions, output_file):
    coco = bbox_annotations_to_coco(images_folder, bbox_annotations, class_descriptions)
    with open(output_file, 'w') as f:
        json.dump(coco, f, indent=2)


if __name__ == '__main__':
    main()
