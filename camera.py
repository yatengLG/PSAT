# -*- coding: utf-8 -*-
# @Author  : LG

from PyQt5.QtGui import QVector3D, QQuaternion, QMatrix4x4

class Camera:
    def __init__(self):
        self.local_forward = QVector3D(0.0, 0.0, -1.0)
        self.local_up = QVector3D(0.0, 1.0, 0.0)
        self.local_right = QVector3D(1.0, 0.0, 0.0)
        self.m_translation = QVector3D()
        self.m_rotation = QQuaternion()
        self.m_world = QMatrix4x4()

    def translate(self, dx, dy, dz):
        self.m_translation += QVector3D(dx, dy, dz)

    def rotate(self, angle, ax, ay, az):
        self.m_rotation = QQuaternion.fromAxisAndAngle(ax, ay, az, angle) * self.m_rotation

    def setTranslation(self, x, y, z):
        self.m_translation = QVector3D(x, y, z)

    def setRotation(self, angle, ax, ay, az):
        self.m_rotation = QQuaternion.fromAxisAndAngle(ax, ay, az, angle)

    def toMatrix(self):
        self.m_world.setToIdentity()
        self.m_world.rotate(self.m_rotation.conjugate())
        self.m_world.translate(-self.m_translation)
        return self.m_world

    def right(self):
        return self.m_rotation.rotatedVector(self.local_right)

    def up(self):
        return self.m_rotation.rotatedVector(self.local_up)

    def forward(self):
        return self.m_rotation.rotatedVector(self.local_forward)
