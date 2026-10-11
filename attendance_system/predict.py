import model_maker as mm

model = mm.ModelMaker()

model.load_local_dataset()

model.create_model(6)

model.train_model()

