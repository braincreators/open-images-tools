import csv
import json
from subprocess import Popen, PIPE

import click
import imagesize
from tqdm import tqdm

from open_images_tools.utils import get_column, get_bbox
from open_images_tools.coco.sanity_check import sanity_check


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

    try:
        p1 = Popen(['cat', '{}'.format(bbox_annotation_file)], stdout=PIPE)
        p2 = Popen(['wc', '-l'], stdin=p1.stdout, stdout=PIPE)
        out, _ = p2.communicate()
        row_count = int(out)
    except Exception:
        row_count = None

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
        for i, row in tqdm(enumerate(reader), total=row_count - 1):
            image_name = get_column(row, header_to_idx, 'ImageID')
            if image_name not in seen_images:
                image_id += 1
                image_file_name = '{}.jpg'.format(image_name)

                try:
                    width, height = imagesize.get("{}/{}".format(images_folder, image_file_name))
                except FileNotFoundError:
                    print("file {}/{} not found, skipping!".format(images_folder, image_name))
                    image_id -= 1
                    continue

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
                    'iscrowd': int(get_column(row, header_to_idx, 'IsGroupOf')),
                    'category_id': class_code_to_idx[label_code]
                }
            )

    return coco_spec


@click.command()
@click.option('--images-folder', required=True, help='image folder path')
@click.option('--bbox-annotations', required=True, help='bounding box annotations csv file path')
@click.option('--class-descriptions', required=True, help='class descriptions csv file path')
@click.option('--output-file', required=True, help='output file path')
@click.option('--sanity-checker', default=False, is_flag=True, help='run sanity checker on the produced file')
def main(images_folder, bbox_annotations, class_descriptions, output_file, sanity_checker):
    coco = bbox_annotations_to_coco(images_folder, bbox_annotations, class_descriptions)
    with open(output_file, 'w') as f:
        json.dump(coco, f, indent=2)

    if sanity_checker:
        sanity_check(coco)


if __name__ == '__main__':
    main()
