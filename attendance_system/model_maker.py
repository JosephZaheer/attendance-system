from tensorflow.keras import layers
import matplotlib.pyplot as plt
from tensorflow import keras
import tensorflow as tf

class ModelMaker:
    def __init__(self):
        pass

    def load_model(self, name):
        self.model = keras.models.load_model(f'{name}.keras')

    def load_local_dataset(self, img_size=(128, 128)):
        self.train_ds = tf.keras.utils.image_dataset_from_directory(
        "/workspaces/attendance-system/attendance_system/Dataset/Train",
        labels="inferred",
        label_mode="int",
        image_size=img_size,
        batch_size=16,
        shuffle=True
        )

        self.val_ds = tf.keras.utils.image_dataset_from_directory(
        "/workspaces/attendance-system/attendance_system/Dataset/Test",
        labels="inferred",
        label_mode="int",
        image_size=img_size,
        batch_size=16,
        shuffle=False
        )

    def transfer_learning(self, img_size=(128, 128, 3)):
        self.base = tf.keras.applications.EfficientNetV2B3(
            include_top=True,
            weights='imagenet',
            input_shape=img_size
        )

        self.base.trainable = False

    def create_model(self, output, img_size=(128, 128, 3), optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"]):
        self.model = keras.Sequential([

            layers.Input(shape=img_size),
            layers.Rescaling(1./255),
                                
            layers.Conv2D(filters=16, kernel_size=3, padding="same", activation="relu"),
            layers.BatchNormalization(),
            layers.MaxPool2D(pool_size=2, strides=2),
        
            layers.Conv2D(filters=32, kernel_size=3, padding="same", activation="relu"),
            layers.BatchNormalization(),
            layers.MaxPool2D(pool_size=2, strides=2),
            
            layers.Conv2D(filters=48, kernel_size=3, padding="same", activation="relu"),        
            layers.BatchNormalization(),
            layers.MaxPool2D(pool_size=2, strides=2),
            
            layers.Flatten(),
            
            layers.Dense(units=125, activation="relu"),
            layers.BatchNormalization(),
            
            layers.Dense(units=output, activation="softmax")
        ])
    
        self.model.summary()

        self.model.compile(
            optimizer=optimizer,
            loss=loss,
            metrics=metrics
        )
        
    def train_model(self, batch_size=16, epochs=20, patience=10):
        early_stop = keras.callbacks.EarlyStopping(
            min_delta=0.005,
            patience=patience,
            restore_best_weights=True,
            verbose=1
        )
    
        self.history = self.model.fit(
            self.train_ds,
            validation_data=self.val_ds,            
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stop],
            verbose=1
        )
        
    def loss_accuracy(self):
        figure, axes = plt.subplots(1,2)
        
        axes[0].plot(self.history.history["loss"], label="Training Loss")
        axes[0].plot(self.history.history["val_loss"], label="Validation Loss")
        
        axes[0].set_xlabel("Epoch")
        axes[0].set_ylabel("Loss")
        axes[0].set_title("Loss VS val_loss")
        axes[0].legend()
        
        axes[1].plot(self.history.history["accuracy"], label="Training Accuracy")
        axes[1].plot(self.history.history["val_accuracy"], label="Validation Accuracy")
        
        axes[1].set_xlabel("Epoch")
        axes[1].set_ylabel("Accuracy")
        axes[1].set_title("Accuracy VS val_accuracy")
        axes[1].legend()
        
        plt.tight_layout()
        plt.show()
        plt.savefig("model_loss_accuracy.png")
         
    def save_model(self, name):
        self.model.save(f"/workspaces/attendance-system/attendance_system/{name}.keras")
