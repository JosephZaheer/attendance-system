import model_maker as mm

#model = mm.ModelMaker()

#model.load_tf_dataset("mnist", "train[:30%]", "test[30%:40%]", 30)

#model.load_local_dataset()

#print(model.train_ds.class_names)

#model.create_model()

#model.train_model()

#model.loss_accuracy()

#model.save_model("model1")


import tensorflow as tf

model = tf.keras.models.load_model("/workspaces/attendance-system/attendance_system/model1.keras")
model.summary()