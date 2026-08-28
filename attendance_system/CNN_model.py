import matplotlib.pyplot as pl
from keras import layers
import tensorflow as tf
import pandas as pd
import keras

pretrained_base = keras.applications.VGG16(
    weights=None,
    include_top=False,
    input_shape=(224,224,3)
)

pretrained_base.trainable = False

model = keras.Sequential([

    layers.RandomFlip("vertical"),
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(factor=0.2),
    layers.RandomContrast(factor=0.2),
    layers.RandomZoom(height_factor=0.1, width_factor=0.1),
    layers.RandomTranslation(height_factor=0.1, width_factor=0.1),

    layers.BatchNormalization(renorm=True),
    layers.Conv2D(filters=64, kernel_size=3, activation="relu", padding="same",
    input_shape=(224,224,3)),
    layers.MaxPool2D(),

    layers.BatchNormalization(renorm=True),
    layers.Conv2D(filters=64, kernel_size=3, activation="relu", padding="same"),
    layers.MaxPool2D(),

    layers.BatchNormalization(renorm=True),
    layers.Conv2D(filters=64, kernel_size=3, activation="relu", padding="same"),
    layers.MaxPool2D(),

    layers.Flatten(),

    layers.Dropout(rate=0.3),
    layers.Dense(16, activation="relu"),
    layers.BatchNormalization(),

    layers.Dropout(rate=0.3),
    layers.Dense(16, activation="relu"),
    layers.BatchNormalization(),

    layers.Dropout(rate=0.3),
    layers.Dense(16, activation="relu"),

    layers.Dense(1, activation="sigmoid")
])

model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["binary_accuracy"]
)

#early stopping
early_stopping = keras.callbacks.EarlyStopping(
    min_delta=0.001,
    patience=4,
    restore_best_weights=True
)

ds_train = keras.utils.image_dataset_from_directory(
    "/workspaces/Yusuf/dataset/train",
    image_size=(224,224),
)

ds_valid = keras.utils.image_dataset_from_directory(
    "/workspaces/Yusuf/dataset/valid",
    image_size=(224,224),
)

history = model.fit(
    ds_train,
    validation_data=ds_valid,
    batch_size=10,
    epochs=32,
    callbacks = [early_stopping],
    verbose=1
)

fig, axes = pl.subplots(1,2, figsize=(12,4))

df = pd.DataFrame(history.history)
df[["loss", "val_loss"]].plot(ax=axes[0])
axes[0].set_title("TRAINING VS VALIDATION LOSS")
axes[0].set_xlabel("Epoch")

df[["binary_accuracy", "val_binary_accuracy"]].plot(ax=axes[1])
axes[1].set_title("TRAINING VS VALIDATION ACCURACY")
axes[1].set_xlabel("Epoch")

pl.tight_layout()
pl.savefig("MODEL_ACCURACY_LOSS.png")