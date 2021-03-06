import json
import click
from tqdm import tqdm


def sanity_check(coco_data):

    if isinstance(coco_data, str):
        with open(coco_data, 'r') as f:
            coco_data = json.load(f)

    valid_category_ids = {category['id'] for category in coco_data['categories']}
    image_id_to_idx = {coco_data['images'][i]['id']: i for i in range(len(coco_data['images']))}

    seen_annotation_ids = set()
    for annotation in tqdm(coco_data['annotations'], total=len(coco_data['annotations'])):
        try:
            # check ids
            assert isinstance(annotation['id'], int)
            assert annotation['id'] not in seen_annotation_ids
            seen_annotation_ids.add(annotation['id'])

            # check if image id exists
            assert isinstance(annotation['image_id'], int)
            assert annotation['image_id'] in image_id_to_idx

            # check if category id exists
            assert isinstance(annotation['category_id'], int)
            assert annotation["category_id"] in valid_category_ids

            # check bbox
            assert len(annotation['bbox']) == 4
            assert all(isinstance(coord, int) for coord in annotation['bbox'])
            assert all(coord >= 0 for coord in annotation['bbox'])
            x, y, w, h = annotation['bbox']

            assert isinstance(annotation['area'], (int, float))
            assert annotation['area'] == w * h, "area inconsistency found"

            assert x < coco_data['images'][image_id_to_idx[annotation['image_id']]]['width']
            assert y < coco_data['images'][image_id_to_idx[annotation['image_id']]]['height']
            assert x + w <= coco_data['images'][image_id_to_idx[annotation['image_id']]]['width']
            assert y + h <= coco_data['images'][image_id_to_idx[annotation['image_id']]]['height']

            assert isinstance(annotation['iscrowd'], int)
            assert annotation['iscrowd'] in {0, 1}
        except AssertionError as e:
            from pprint import pprint
            print("Assertion failed in annotation:")
            pprint(annotation)
            raise e


@click.command()
@click.option('-f', '--coco-file', required=True, help='coco json path to be checked')
def main(coco_file):
    sanity_check(coco_file)


if __name__ == '__main__':
    main()
