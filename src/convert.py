import os
import shutil
from collections import defaultdict
from urllib.parse import unquote, urlparse

import supervisely as sly
from dataset_tools.convert import unpack_if_archive
from supervisely.io.fs import get_file_name, get_file_name_with_ext
from supervisely.io.json import load_json_file
from tqdm import tqdm

import src.settings as s


def download_dataset(teamfiles_dir: str) -> str:
    """Use it for large datasets to convert them on the instance"""
    api = sly.Api.from_env()
    team_id = sly.env.team_id()
    storage_dir = sly.app.get_data_dir()

    if isinstance(s.DOWNLOAD_ORIGINAL_URL, str):
        parsed_url = urlparse(s.DOWNLOAD_ORIGINAL_URL)
        file_name_with_ext = os.path.basename(parsed_url.path)
        file_name_with_ext = unquote(file_name_with_ext)

        sly.logger.info(f"Start unpacking archive '{file_name_with_ext}'...")
        local_path = os.path.join(storage_dir, file_name_with_ext)
        teamfiles_path = os.path.join(teamfiles_dir, file_name_with_ext)

        fsize = api.file.get_directory_size(team_id, teamfiles_dir)
        with tqdm(
            desc=f"Downloading '{file_name_with_ext}' to buffer...",
            total=fsize,
            unit="B",
            unit_scale=True,
        ) as pbar:
            api.file.download(team_id, teamfiles_path, local_path, progress_cb=pbar)
        dataset_path = unpack_if_archive(local_path)

    if isinstance(s.DOWNLOAD_ORIGINAL_URL, dict):
        for file_name_with_ext, url in s.DOWNLOAD_ORIGINAL_URL.items():
            local_path = os.path.join(storage_dir, file_name_with_ext)
            teamfiles_path = os.path.join(teamfiles_dir, file_name_with_ext)

            if not os.path.exists(get_file_name(local_path)):
                fsize = api.file.get_directory_size(team_id, teamfiles_dir)
                with tqdm(
                    desc=f"Downloading '{file_name_with_ext}' to buffer...",
                    total=fsize,
                    unit="B",
                    unit_scale=True,
                ) as pbar:
                    api.file.download(team_id, teamfiles_path, local_path, progress_cb=pbar)

                sly.logger.info(f"Start unpacking archive '{file_name_with_ext}'...")
                unpack_if_archive(local_path)
            else:
                sly.logger.info(
                    f"Archive '{file_name_with_ext}' was already unpacked to '{os.path.join(storage_dir, get_file_name(file_name_with_ext))}'. Skipping..."
                )

        dataset_path = storage_dir
    return dataset_path


def count_files(path, extension):
    count = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(extension):
                count += 1
    return count


def convert_and_upload_supervisely_project(
    api: sly.Api, workspace_id: int, project_name: str
) -> sly.ProjectInfo:
    ### Function should read local dataset and upload it to Supervisely project, then return project info.###
    dataset_path = "/home/alex/DATASETS/TODO/FSOD"

    batch_size = 30
    images_folder_name = "images"
    train_json_path = (
        "/home/alex/DATASETS/TODO/FSOD/annotations-20231225T123412Z-001/annotations/fsod_train.json"
    )
    test_json_path = (
        "/home/alex/DATASETS/TODO/FSOD/annotations-20231225T123412Z-001/annotations/fsod_test.json"
    )

    ds_name_to_ann = {"train": train_json_path, "test": test_json_path}

    def create_ann(image_path):
        labels = []

        image_name = get_file_name_with_ext(image_path)
        img_height = im_name_to_shape[image_name][0]
        img_wight = im_name_to_shape[image_name][1]

        seq_value = image_path.split("/")[-2]
        seq = sly.Tag(seq_meta, value=seq_value)

        ann_data = image_name_to_ann_data[get_file_name_with_ext(image_path)]
        for curr_ann_data in ann_data:
            category_id = curr_ann_data[0]
            curr_obj_class = idx_to_obj_class[category_id]
            super_value = class_name_to_super.get(curr_obj_class.name)

            supercategory = sly.Tag(super_meta, value=super_value)
            bbox_coord = curr_ann_data[1]
            rectangle = sly.Rectangle(
                top=int(bbox_coord[1]),
                left=int(bbox_coord[0]),
                bottom=int(bbox_coord[1] + bbox_coord[3]),
                right=int(bbox_coord[0] + bbox_coord[2]),
            )
            label_rectangle = sly.Label(rectangle, curr_obj_class, tags=[supercategory])
            labels.append(label_rectangle)

        return sly.Annotation(img_size=(img_height, img_wight), labels=labels, img_tags=[seq])

    project = api.project.create(workspace_id, project_name, change_name_if_conflict=True)

    seq_meta = sly.TagMeta("sequence", sly.TagValueType.ANY_STRING)
    super_meta = sly.TagMeta("supercategory", sly.TagValueType.ANY_STRING)

    meta = sly.ProjectMeta(tag_metas=[seq_meta, super_meta])

    idx_to_obj_class = {}
    im_name_to_shape = {}
    class_name_to_super = {}

    for ds_name, ann_path in ds_name_to_ann.items():
        unique_names = []
        dataset = api.dataset.create(project.id, ds_name, change_name_if_conflict=True)
        image_id_to_name = {}
        image_name_to_ann_data = defaultdict(list)
        images_path_names_temp = defaultdict(list)

        ann = load_json_file(ann_path)
        for curr_category in ann["categories"]:
            if idx_to_obj_class.get(curr_category["id"]) is None:
                obj_class = sly.ObjClass(curr_category["name"], sly.Rectangle)
                class_name_to_super[curr_category["name"]] = curr_category["supercategory"]
                meta = meta.add_obj_class(obj_class)
                idx_to_obj_class[curr_category["id"]] = obj_class
        api.project.update_meta(project.id, meta.to_json())

        for curr_image_info in ann["images"]:
            image_id_to_name[curr_image_info["id"]] = curr_image_info["file_name"]
            im_name_to_shape[get_file_name_with_ext(curr_image_info["file_name"])] = (
                curr_image_info["height"],
                curr_image_info["width"],
            )

        for curr_ann_data in ann["annotations"]:
            image_id = curr_ann_data["image_id"]
            images_path_names_temp[image_id_to_name[image_id]].append(0)
            image_name_to_ann_data[get_file_name_with_ext(image_id_to_name[image_id])].append(
                [curr_ann_data["category_id"], curr_ann_data["bbox"]]
            )

        images_path_names = list(images_path_names_temp.keys())

        progress = sly.Progress("Create dataset {}".format(ds_name), len(images_path_names))

        for img_pathes_names_batch in sly.batched(images_path_names, batch_size=batch_size):
            img_names_batch = []
            images_pathes_batch = []
            for image_path_name in img_pathes_names_batch:
                im_name = get_file_name_with_ext(image_path_name)
                img_names_batch.append(im_name)
                images_pathes_batch.append(os.path.join(dataset_path, image_path_name))

            img_infos = api.image.upload_paths(dataset.id, img_names_batch, images_pathes_batch)
            img_ids = [im_info.id for im_info in img_infos]

            anns_batch = [create_ann(image_path) for image_path in images_pathes_batch]
            api.annotation.upload_anns(img_ids, anns_batch)

            progress.iters_done_report(len(img_names_batch))

    return project
