import model_maker as mm
import numpy as np

model = mm.ModelMaker()

#model.load_tf_dataset("mnist", "train[:30%]", "test[30%:40%]", 30)

model.load_local_dataset()

classes = model.train_ds.class_names

#model.create_model()

#model.train_model()

#model.loss_accuracy()

#model.save_model("attendance_system/model1")


import tensorflow as tf
model = tf.keras.models.load_model("/workspaces/attendance-system/attendance_system/model1.keras")
#model.summary()

img = tf.keras.utils.load_img(
    "attendance_system/Zoheb.jpg",
    target_size=(128, 128)
)

img_array = tf.keras.utils.img_to_array(img)
img_array = tf.expand_dims(img_array, 0)

predictions = model.predict(img_array)
score = tf.nn.softmax(predictions[0])

print("Prediction:", classes[np.argmax(score)])
print(f"Confidence: {100*np.max(score):.2f}%")

print(predictions)