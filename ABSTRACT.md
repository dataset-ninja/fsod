The **FSOD: A High-Diverse Few-Shot Object Detection Dataset** stands out as a meticulously crafted dataset tailored for few-shot object detection. Its design focuses on assessing a model's versatility across new categories. With a collection of 1000 diverse object categories accompanied by high-quality annotations, this dataset marks a pioneering effort in the realm of few-shot object detection datasets.


## Motivation

Object detection finds extensive applications across various fields. However, current methods typically depend heavily on large sets of annotated data and entail prolonged training periods. They also struggle to adapt to unseen objects not included in the training data. In contrast, the human visual system excels at recognizing new objects with minimal guidance. Few-shot learning poses significant challenges due to the diverse characteristics of objects in real-world scenarios, including variations in illumination, shape, and texture. Despite recent advancements in few-shot learning, these techniques have primarily focused on image classification, with little exploration in the realm of few-shot object detection. This is primarily because transferring insights from few-shot classification to few-shot object detection presents considerable complexity. Few-shot object detection faces a critical obstacle in localizing unseen objects within cluttered backgrounds, representing a broader challenge in generalizing object localization from a scant number of training examples belonging to novel categories. This challenge often leads to missed detections or false positives, stemming from inadequate scoring of potentially suitable bounding boxes in region proposal networks (RPNs), rendering novel object detection difficult. Such inherent issues distinguish few-shot object detection from few-shot classification.

## Dataset description

The authors endeavor to tackle the challenge of few-shot object detection. Their objective is to detect all foreground objects belonging to a specific target object category in a test set, given only a limited number of support set images depicting the target object. In pursuit of this goal, the authors present two significant contributions. Firstly, they introduce a comprehensive few-shot detection model capable of detecting novel objects without necessitating re-training or fine-tuning. Their approach leverages the matching relationship between pairs of objects within a siamese network across multiple network stages. Experimental results demonstrate that the model benefits from an attention module in the early stages, enhancing proposal quality, and a multi-relation module in the later stages, effectively suppressing and filtering out false detections in complex backgrounds. Secondly, for model training, the authors curate a large, meticulously annotated dataset comprising 1000 categories, each with a few examples. This dataset fosters broad learning in object detection.

<img src="https://github.com/dataset-ninja/fsod/assets/120389559/d93290f1-90a0-4258-89f4-d5a7056b8e55" alt="image" width="800">

<span style="font-size: smaller; font-style: italic;">Given different objects as supports, the authors approach can detect all objects with same categories in the given query image.</span>

## Dataset construction

The authors developed their dataset by drawing from existing extensive supervised object detection datasets. However, direct utilization of these datasets is hindered by several factors:

Inconsistencies in labeling systems across different datasets, wherein objects with identical semantics are denoted by different terms.
Suboptimal annotations characterized by inaccuracies, missing labels, duplicate bounding boxes, excessively large objects, among other issues.
The train/test splits in these datasets often contain identical categories, whereas for a few-shot dataset, the aim is to have distinct categories in the train and test sets to evaluate the model's generalization to unseen objects.
To construct their dataset, the authors initially standardized the labeling system by consolidating labels with similar meanings, such as merging "ice bear" and "polar bear" into a single category while eliminating semantically irrelevant labels. They then filtered out images with subpar labeling quality and bounding boxes of inappropriate sizes. Bounding boxes smaller than 0.05% of the image size, typically indicative of poor visual quality and unsuitable for serving as support examples, were specifically discarded.

Subsequently, adhering to the principles of few-shot learning, the authors partitioned the data into training and test sets devoid of category overlap. The training set comprised categories from the [MS COCO Dataset](https://cocodataset.org/#home) and [ImageNet Dataset](https://www.image-net.org/), while for the test set containing 200 categories, categories with the least similarity to those in the training set were selected. The remaining categories were merged into the training set, resulting in a total of 800 categories.

In summary, the authors curated a dataset encompassing 1000 categories with distinct category splits for training and testing, with 531 categories sourced from the ImageNet Dataset and 469 from the [Open Image Dataset](https://docs.ultralytics.com/datasets/detect/open-images-v7/).

## Dataset analysis

The dataset is specifically designed for few-shot learning and intrinsically designed to evaluate the generality of a model on novel categories. The authors dataset contains 1000 categories with 800/200 split for training and test set separately, around 66,000 images and 182,000 bounding boxes in total. The dataset has the following attributes.

<img src="https://github.com/dataset-ninja/fsod/assets/120389559/bbfe6dc0-69d1-4ec1-a9e5-548571fd2b1f" alt="image" width="800">

<span style="font-size: smaller; font-style: italic;">Given different objects as supports, the authors approach can detect all objects with same categories in the given query image.</span>

The dataset has the following attributes:

* **Extensive category diversity:** The dataset boasts a wide range of semantic categories, encompassing 83 overarching parent semantics such as mammals, clothing, and weaponry, further branching out into 1000 distinct leaf categories. The rigorous dataset split implemented by the authors ensures that the semantic categories in the train and test sets are markedly dissimilar, posing a significant challenge for model evaluation.

* **Demanding evaluation conditions:** Evaluation of models on this dataset presents formidable challenges. Notably, objects exhibit considerable variation in box size and aspect ratios. Moreover, a substantial portion of the test set, comprising 26.5% of images, features three or more objects. It's pertinent to highlight that the test set includes numerous bounding boxes representing categories not included in our label system, adding an additional layer of complexity to the evaluation process.
