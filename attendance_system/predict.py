import model_maker as mm

model = mm.ModelMaker()

model.load_local_dataset()

model.create_model(6)

model.train_model(20)

model.loss_accuracy()

model.save_model("model1")

