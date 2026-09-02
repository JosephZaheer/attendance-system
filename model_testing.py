import attendance_system.model_maker as mm

model = mm.ModelMaker()

#model.load_tf_dataset("mnist", "train[:30%]", "test[30%:40%]", 30)

model.load_local_dataset("attendance_system/Dataset/Aryan")
print(model.train_ds)
print("end")

#model.create_model(input_shape=(28,28,1))

#model.train_model(32, 10)

#model.loss_accuracy()
