# -*- coding: utf-8 -*-
# @Author  : LG
from PyQt5.QtGui import QMatrix4x4, QVector3D, QQuaternion


class Transform(object):
    def __init__(self):
        self.m_translation = QVector3D()
        self.m_scale = QVector3D(1, 1, 1)
        self.m_rotation = QQuaternion()
        self.m_world = QMatrix4x4()

        self.localforward = QVector3D(0.0, 0.0, 1.0)
        self.localup = QVector3D(0.0, 1.0, 0.0)
        self.localright = QVector3D(1.0, 0.0, 0.0)

    def forward(self):
        return self.m_rotation.rotatedVector(self.localforward)

    def up(self):
        return self.m_rotation.rotatedVector(self.localup)

    def right(self):
        return self.m_rotation.rotatedVector(self.localright)

    def translate(self, dx, dy, dz):
        self.m_translation += QVector3D(dx, dy, dz)

    def scale(self, sx, sy, sz):
        self.m_scale *= QVector3D(sx, sy, sz)

    def rotate(self, axis, angle):
        dr = QQuaternion.fromAxisAndAngle(axis, angle)
        self.m_rotation = dr * self.m_rotation
        self.m_translation = dr.rotatedVector(self.m_translation)

    def rotate_in_place(self, axis, angle):
        dr = QQuaternion.fromAxisAndAngle(axis, angle)
        self.m_rotation = dr * self.m_rotation

    def setTranslation(self, dx, dy, dz):
        self.m_translation = QVector3D(dx, dy, dz)

    def setTranslationwithRotate(self, dx, dy, dz):
        self.m_translation = self.m_rotation.rotatedVector(QVector3D(dx, dy, dz))

    def setScale(self, sx, sy, sz):
        self.m_scale = QVector3D(sx, sy, sz)

    def setRotation(self, r:QQuaternion):
        dr = r * self.m_rotation.inverted()
        self.m_translation = dr.rotatedVector(self.m_translation)
        self.m_rotation = r

    def toMatrix(self):
        self.m_world.setToIdentity()
        self.m_world.translate(self.m_translation)
        self.m_world.scale(self.m_scale)
        self.m_world.rotate(self.m_rotation)
        return self.m_world
