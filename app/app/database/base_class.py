from odmantic import Model, ObjectId

Base = Model

Base.model_config["json_encoders"] = {ObjectId: lambda v: str(v)}
