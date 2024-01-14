from PyQt5.QtCore import QObject


def bind(objectName, propertyName):
    def getter(self):
        obj = self.findChild(QObject, objectName)
        if obj is None:
            raise Exception("(getter)No such object: " + objectName)
        # if isinstance(obj, QSlider):
        #     obj.property(propertyName)
        # 返回属性值
        return obj.property(propertyName)

    def setter(self, value):
        obj = self.findChild(QObject, objectName)
        if obj is None:
            raise Exception("(setter)No such object: " + objectName)
        # 设置属性值
        obj.setProperty(propertyName, value)

    return property(getter, setter)