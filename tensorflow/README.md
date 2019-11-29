## Prerequisites
- Tensorflow 2.0

## How to use

```sh
# train the model
python nn_floor.py \
  --mode train \
  --input_dir ../ECP/image_train \
  --num_epochs 60 \
  --use_augmentation \
  --augmentation_factor 100
# test the model
python nn_floor.py \
  --mode test \
  --input_dir ../ECP/image_test
```