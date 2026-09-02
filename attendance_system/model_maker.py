from tensorflow.keras.layers import Conv2D, MaxPool2D, Flatten, Dense, BatchNormalization, Dropout, Rescaling # pyright: ignore[reportMissingModuleSource]
import tensorflow_datasets as tfds
import matplotlib.pyplot as plt
from tensorflow import keras # pyright: ignore[reportMissingModuleSource]
import tensorflow as tf

class ModelMaker:
    def __init__(self):
        self.IMG_SIZE = 28
        self.BATCH_SIZE = 32

    def load_model(self, name):
        self.model = keras.models.load_model(f'{name}.keras')

    def load_local_dataset(self, name, IMG_SIZE=224, BATCH_SIZE=32):

        self.IMG_SIZE = IMG_SIZE
        self.BATCH_SIZE = BATCH_SIZE
        self.train_ds = tf.keras.utils.image_dataset_from_directory(
        name,
        seed=123,
        image_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE)
    
    def load_tf_dataset(self, name, IMG_SIZE=28, BATCH_SIZE=32):
        self.IMG_SIZE = IMG_SIZE
        self.BATCH_SIZE = BATCH_SIZE
        
        #Load dataset for training and testing
        (self.train_ds, self.val_ds), self.ds_info = tfds.load(
        
            name,
            split=["train[:15%]", "test[:5%]"],
            shuffle_files=True,
            as_supervised=True,
            with_info=True
        )
        """
        self.val_ds = tfds.load(
            name,
            as_supervised=True,
            split=[val_split]
        )
        
        self.test_ds = tfds.load(
        
            name,
            as_supervised=True,
            split=[test_split]
        )
        """
        #preprocess the dataset for better accuracy and efficiency
        def preprocess(image, label):
            #image, label = feature["image"], feature["label"]
            return tf.image.resize(image, (self.IMG_SIZE, self.IMG_SIZE))/255.0, label

        self.train_ds = (self.train_ds
        .map(preprocess, num_parallel_calls=tf.data.AUTOTUNE)
        .cache()
        .batch(self.BATCH_SIZE)
        .shuffle(self.ds_info.splits["train"].num_examples)
        .prefetch(tf.data.AUTOTUNE)
        )

        
        self.val_ds = (self.val_ds
        .map(preprocess, num_parallel_calls=tf.data.AUTOTUNE)
        .cache()
        .batch(self.BATCH_SIZE)
        .shuffle(self.ds_info.splits["test"].num_examples)
        .prefetch(tf.data.AUTOTUNE)
        )        
        
    def create_model(self, input_shape, learning_rate=0.005):
        self.model = keras.Sequential([
                    
            Conv2D(filters=16, kernel_size=3, strides=1, padding="same", activation="relu", input_shape=input_shape),
            BatchNormalization(),
            MaxPool2D(pool_size=3, strides=1, padding="same"),
            
            Conv2D(filters=22, kernel_size=1, strides=1, padding="same", activation="relu"),
            BatchNormalization(),
            MaxPool2D(pool_size=3, strides=2, padding="same"),
            
            Conv2D(filters=26, kernel_size=3, padding="same", activation="relu"),        
            BatchNormalization(),
            MaxPool2D(pool_size=3, strides=2, padding="same"),
            
            Flatten(),
            
            Dense(units=1000, activation="relu"),
            BatchNormalization(),
        
            Dropout(rate=0.4),
            Dense(units=100, activation="relu"),
            BatchNormalization(),
            
            Dropout(rate=0.4),
            Dense(units=10, activation="sigmoid")
        ])
    
        self.model.summary()
        
        #defining how the model evaluates its inaccuracy and how it improves itself
        self.model.compile(
        
            optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"]
        )
        
    def train_model(self, batch_size, epochs, patience=10):
        
        #define early stopping to avoid overfitting
        early_stop = keras.callbacks.EarlyStopping(
        
            min_delta=0.005,
            patience=patience,
            restore_best_weights=True,
            
            verbose=1
        )
    
        #train model on training dataset
        #test model on validation dataset
        self.history = self.model.fit(
        
            self.train_ds,
            validation_data=self.val_ds,            
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stop],
            
            verbose=1
        )
        
    def loss_accuracy(self):
        #plot tarining results for model evaluation
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
        
        #evaluate model performance using test dataset
        #loss, accuracy = self.model.evaluate(self.test_ds)
        
        #print(f"This model has {accuracy*100:.2f}% accuracy")
         
    def save_model(self, name):
        #save the model to avoid training over and over again
        self.model.save(f"{name}.keras")
