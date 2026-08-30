from tensorflow.keras.layers import RandomTranslation, Conv2D, MaxPool2D, Flatten, Dense, BatchNormalization, Dropout
import tensorflow_datasets as tfds
import matplotlib.pyplot as plt
from tensorflow import keras
import tensorflow as tf

class ModelMaker:
    def __init__(self):
        pass

    def load_model(self, name):
        self.model = keras.models.load_model(f'{name}.keras')
    
    def load_tf_dataset(self, name, train_split, test_split, IMG_SIZE, BATCH_SIZE=32):
        self.IMG_SIZE = IMG_SIZE
        self.BATCH_SIZE = BATCH_SIZE

        #Load dataset for training and testing
        self.train_dataset = tfds.load(
        
            name,
            shuffle_files=True,
            as_supervised=True,
            split=[train_split]
        )
        
        self.test_dataset = tfds.load(
        
            name,
            as_supervised=True,
            split=[test_split]
        )
        
        #preprocess the dataset for better accuracy and efficiency
        def preprocess(image, label):
            return tf.image.resize(image, (self.IMG_SIZE, self.IMG_SIZE))/255.0, label
            
        self.train_dataset = (self.train_dataset
        .map(preprocess)
        .cache()
        .batch(self.BATCH_SIZE)
        .shuffle(buffer_size=8, reshuffle_each_iteration=True)
        .prefetch(tf.data.AUTONE)
        )
        
        self.test_dataset = (self.test_dataset
        .map(preprocess)
        .cache()
        .batch(self.BATCH_SIZE)
        .prefetch(tf.data.AUTONE)
        )
    
    def create_model(self, learning_rate=0.1):
        self.model = keras.Sequential([
        
            RandomTranslation("horizontal"),
            
            Conv2D(filters=6, kernel_size=11, strides=5, padding="valid", activation="relu", input_shape=(self.IMG_SIZE, self.IMG_SIZE, 3)),
            BatchNormalization(),
            MaxPool2D(pool_size=(3, 3), strides=2),
            
            Conv2D(filters=6, kernel_size=11, strides=5, padding="valid", activation="relu"),
            BatchNormalization(),
            MaxPool2D(pool_size=(3, 3), strides=2),
            
            Conv2D(filters=32, kernel_size=3, padding=2, activation="relu"),        
            BatchNormalization(),
            Conv2D(filters=32, kernel_size=3, padding=2, activation="relu"),        
            BatchNormalization(),
            Conv2D(filters=32, kernel_size=3, padding=2, activation="relu"),        
            BatchNormalization(),
            MaxPool2D(pool_size=(3, 3), strides=2),
            
            Flatten(),
            
            Dense(units=256, activation="relu"),
            BatchNormalization(),
        
            Dropout(rate=0.5),
            Dense(units=256, activation="relu"),
            BatchNormalization(),
            
            Dropout(rate=0.5),
            Dense(units=10, activation="sigmoid")
        ])
    
        self.model.summary()
        
        #defining how the model evaluates its inaccuracy and how it improves itself
        self.model.compile(
        
            optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
            loss=keras.losses.BinaryCrossEntropy(),
            metrics="accuracy"
        )
        
    def train_model(self, batch_size, epochs, patience=10):
        
        #define early stopping to avoid overfitting
        early_stop = keras.callbacks.EarlyStopping(
        
            min_delta=0.001,
            patience=patience,
            restore_best_weights=True,
            
            verbose=1
        )
    
        #train model on training dataset
        #test model on validation dataset
        self.history = self.model.fit(
        
            self.train_dataset,
            validation_split=0.2,
            
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stop],
            
            verbose=1
        )
        
    def loss_accuracy(self):
        #plot tarining results for model evaluation
        figure, axes = plt.subplots()
        
        axes[0].plot(self.history.history["loss"], label="Training Loss")
        axes[0].plot(self.history.history["val_loss"], label="Validation Loss")
        
        axes[0].set_xlabel("Epoch")
        axes[0].set_ylabel("Loss")
        axes[0].set_title("Loss VS val_loss")
        
        axes[1].plot(self.history.history["accuracy"], label="Training Accuracy")
        axes[1].plot(self.history.history["val_accuracy"], label="Validation Accuracy")
        
        axes[1].set_xlabel("Epoch")
        axes[1].set_ylabel("Accuracy")
        axes[1].set_title("Accuracy VS val_accuracy")
        
        plt.tight_layout()
        plt.legend()
        plt.show()
        plt.savefig("model_loss_accuracy.png")
        
        #evaluate model performance using test dataset
        loss, accuracy = self.model.evaluate(self.test_dataset)
        
        print(f"This model has {accuracy*100:.2f}% accuracy")
         
    def save_model(self, name):
        #save the model to avoid training over and over again
        self.model.save(f"{name}.keras")
