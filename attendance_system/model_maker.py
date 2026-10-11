from tensorflow.keras import layers
import matplotlib.pyplot as plt
import tensorflow as tf

base = "/workspaces/attendance-system/attendance_system/"

class ModelMaker:
    def __init__(self):
        pass

    def load_model(self, name):
        self.model = tf.keras.models.load_model(base + f'{name}.keras')

    def load_local_dataset(self, img_size=(224, 224)):
        self.train_ds = tf.keras.utils.image_dataset_from_directory(
        base + "Dataset/Train",
        labels="inferred",
        label_mode="int",
        image_size=img_size,
        batch_size=32,
        ).cache().shuffle(1000).prefetch(buffer_size=tf.data.AUTOTUNE)

        self.val_ds = tf.keras.utils.image_dataset_from_directory(
        base + "Dataset/Test",
        labels="inferred",
        label_mode="int",
        image_size=img_size,
        batch_size=32,
        ).cache().prefetch(buffer_size=tf.data.AUTOTUNE)
        
        """self.test_ds = tf.keras.utils.image_dataset_from_directory(
        base + "Dataset/Evaluate",
        labels="inferred",
        label_mode="int",
        image_size=img_size,
        batch_size=6,
        shuffle=False
        )"""

    def create_model(self, output, img_size=(224, 224, 3), optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"]):
        
        self.model = tf.keras.Sequential([

            layers.Input(shape=img_size),
            #layers.Rescaling(1/255.0),
            
            #data augmentation
            layers.RandomContrast(factor=0.1),
                                
            #1st convolutional layer
            layers.Conv2D(filters=32, kernel_size=3, strides=1, activation="relu"),
            layers.MaxPool2D(pool_size=2, padding="same"),
            layers.BatchNormalization(),
        
            #2nd convolutional layer
            layers.Conv2D(filters=32, kernel_size=3, strides=1, activation="relu"),
            layers.MaxPool2D(pool_size=2, padding="same"),
            layers.BatchNormalization(),
            
            #3rd convolutional layer
            layers.Conv2D(filters=48, kernel_size=3, strides=1, activation="relu"),        
            layers.MaxPool2D(pool_size=2, padding="same"),
            layers.BatchNormalization(),
            
            #4th convolutional layer
            layers.Conv2D(filters=48, kernel_size=1, strides=1, activation="relu"),
            layers.BatchNormalization(),
            
            layers.Flatten(),
            layers.Dropout(rate=0.1),
            
            #dense layers
            layers.Dense(units=128, activation="relu"),
            layers.Dense(units=128, activation="relu"),
            
            layers.Dense(units=output, activation="softmax")
        ])
    
        self.model.summary()

        self.model.compile(
            optimizer=optimizer,
            loss=loss,
            metrics=metrics
        )
        
    def train_model(self, min_delta=0.0005,batch_size=32, epochs=32, patience=8):
        
        early_stopping = tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            min_delta=min_delta,
            patience=patience,
            restore_best_weights=True,
            verbose=1
        )
        
        logger = tf.keras.callbacks.CSVLogger(
            base + "logs.csv", 
            separator=",",
            append=False
        )
    
        self.history = self.model.fit(
            self.train_ds,
            validation_data=self.val_ds,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stopping, logger],
            verbose=1
        )
        
        #model evaluation through data visualisation
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
        plt.savefig(base + "model_loss_accuracy.png")
        
        #evaluation
        test_labels = ["Arush", "Aryan", "Jaffar", "Krishna", "Yusuf", "Zoheb"]

        """
        print("\n", "#"*50, "\n", "#"*50, "\n")
        loss, acc = self.model.evaluate(self.test_ds, test_labels, verbose=2)
        print(f"Accuracy: {acc*100:.2f}%")
        print(self.model.predict(self.test_ds).shape)"""
        
        #save model
        print("\n", "#"*50, "\n", "#"*50, "\n")
        if "y" == input("Save model? [y/n]"):
            name = input("Please enter model name: ")
            self.model.save(base + f"{name}.keras")
            
        print("\n", "#"*50, "\n", "#"*50, "\n")
