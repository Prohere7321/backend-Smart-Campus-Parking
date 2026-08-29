from roboflow import Roboflow
rf = Roboflow(api_key="abcJyR0I8xJlpEWBJwxp")
project = rf.workspace("hayroo").project("helmet-detector-brbf5")
version = project.version(7)
dataset = version.download("yolov8")
print(dataset.location)