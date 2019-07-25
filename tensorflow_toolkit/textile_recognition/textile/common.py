# Copyright (C) 2019 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions
# and limitations under the License.

import os
import cv2
import numpy as np


def max_central_square_crop(image):
    h, w = image.shape[:2]

    if w > h:
        image = image[:, (w - h) // 2:(w - h) // 2 + h]
    else:
        image = image[(h - w) // 2:(h - w) // 2 + w, :]

    return image


def preproces_image(image):
    image = image / 127.5 - 1.0
    return image


def depreprocess_image(image):
    image = (image + 1.0) * 127.5
    image = image.astype(np.uint8)
    return image


def fit_to_max_size(image, max_side):
    if image.shape[0] > max_side or image.shape[1] > max_side:
        if image.shape[0] > image.shape[1]:
            image = cv2.resize(image, (int(image.shape[1] / (image.shape[0] / max_side)), max_side))
        else:
            image = cv2.resize(image, (max_side, int(image.shape[0] / (image.shape[1] / max_side))))

    return image


def crop_resize_shift_scale(image, input_size):
    image = max_central_square_crop(image)
    image = cv2.resize(image, (input_size, input_size))
    image = preproces_image(image)
    image = np.expand_dims(image, axis=0)
    return image


def central_crop(image, divide_by, shift):
    h, w = image.shape[0:2]
    image = image[h // divide_by * shift: h // divide_by * (divide_by - shift),
                  w // divide_by * shift: w // divide_by * (divide_by - shift)]
    return image


def from_list(path, multiple_images_per_label=True):
    impaths = []
    labels = []
    is_real = []

    text_label_to_class_id = {}

    uniques_labels = set()

    data_dir = os.path.dirname(path)

    with open(path) as f:
        for line in f.readlines():
            line = line.strip().split(' ')
            if len(line) == 2:
                impath, label = line
                real = False
            else:
                impath, label, real = line
                real = real.lower() == 'r'

            text_label_to_class_id[os.path.basename(impath).split('.')[0]] = int(label)

            if not multiple_images_per_label and label in uniques_labels:
                continue

            uniques_labels.add(label)

            real_path = os.path.join(data_dir, impath)

            is_real.append(real)
            impaths.append(real_path)
            labels.append(int(label))

    return impaths, labels, is_real, text_label_to_class_id