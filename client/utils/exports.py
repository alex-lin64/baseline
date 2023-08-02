from pathlib import Path
import fiftyone as fo
import json


def export_image_to_fo(annotations, dataset):
    """
    Transforms image detection data into format for fiftyone as uploads to 
    existing dataset or as a new dataset

    Annotations format is 
    {
        "path/to/image": {
            "detections": [
                {
                    "bbox": [<top-left-x>, <top-left-y>, <width>, <height>],
                    "label": obj_class,
                    "confidence": 0.00-1.00
                }
            ],
            "tags": [training/validation/testing]
        }
    }

    :params:
        - annotations: dict of images and their filepaths to model predictions
        - dataset: name of dataset to export annotations to in fiftyone, if 
            dataset name already exists in fiftyone, will append to dataset
    """
    samples = []

    for filepath in annotations:
        sample = fo.Sample(filepath=filepath)

        detections = []
        # convert all detections to fo format
        for det in annotations[filepath]['detections']:
            label = det['label']
            # bbox coordingates in format [top-left-x, top-left-y, width, height]
            bbox = det['bbox']
            confidence = det['confidence']

            detections.append(
                fo.Detection(label=label, bounding_box=bbox, confidence=confidence)
            )

        # set sample detections to converted samples
        sample['model_detections'] = fo.Detections(detections=detections)
        sample.tags = annotations[filepath]["tags"]
        samples.append(sample)
                        
    # check if dataset is in list
    if dataset in fo.list_datasets():
        dataset = fo.load_dataset(dataset)
    else:
        print("Dataset does not exist in fiftyone, creating new \
                dataset by default.  Make sure the dataset set to persistent \
                if using existing fiftyone datset")
        dataset = fo.Dataset(dataset)
    
    # set dataset to persistent, stay in fo
    dataset.persistent = True
    # populate dataset with the processed samples
    dataset.add_samples(samples)


def export_video_to_fo(annotations, dataset):
    """
    Transforms video detection data into format for fiftyone as uploads to 
    existing dataset or as a new dataset

    Annotations format is 
    {
        "path/to/video": {
            1: {
                "detections": [
                    {
                        "bbox": [<top-left-x>, <top-left-y>, <width>, <height>],
                        "label": obj_class
                        "confidence": 0.00-1.00
                    }
                ],
                tags": [training/validation/testing]
            }
            2: { ... }
        }
    }

    :params:
        - annotations: dict of videos and their filepaths to model predictions 
            ordered by frame
        - dataset: name of dataset to export annotations to in fiftyone, if 
            dataset name already exists in fiftyone, will append to dataset
    """
    samples = []

    for filepath in annotations:
        sample = fo.Sample(filepath=filepath)

        # create video sample with frame labels
        for n_frame, annotation in annotations[filepath].items():
            detections = []
            frame = fo.Frame()

            for det in annotation["detections"]:
                label = det["label"]
                # bbox coordingates in format [top-left-x, top-left-y, width, height]
                bbox = det['bbox']
                confidence = det['confidence']

                detections.append(
                    fo.Detection(label=label, bounding_box=bbox, confidence=confidence)
                )
            # append detections in frame to the frame
            frame["objects"] = fo.Detections(detections=detections)
            # add frame to sample
            sample.frames[int(n_frame)] = frame
        # add tag to the video
        sample.tags = annotation["tags"]
        samples.append(sample)
    
    # check if dataset is in list
    if dataset in fo.list_datasets():
        dataset = fo.load_dataset(dataset)
    else:
        print("Dataset does not exist in fiftyone, creating new \
                dataset by default.  Make sure the dataset set to persistent \
                if using existing fiftyone datset")
        dataset = fo.Dataset(dataset)
    
    # set dataset to persistent, stay in fo
    dataset.persistent = True
    # populate dataset with the processed samples
    dataset.add_samples(samples)


def export_json(filepath, annotations):
    """
    Exports annotations as a json file

    :params:
        - filepath: Output path of the file, includes filename
            e.g. /my/output/file/path/myfile.json
        - annotations: dict of images or videos and their filepaths to model predictions 
    """
    try:
        with open(filepath, 'x') as fp:
            json.dump(annotations, fp)
        print(f"Success: exported to {filepath}")
    except Exception as e:
        print(f"Error: {e}")