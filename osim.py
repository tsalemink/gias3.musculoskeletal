"""
FILE: osim.py
LAST MODIFIED: 09-02-2016
DESCRIPTION: Module of wrappers and helper functions and classes for opensim
models

===============================================================================
This file is part of GIAS2. (https://bitbucket.org/jangle/gias2)

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
===============================================================================
"""

import opensim
from opensim.opensim import ProbeSet
import numpy as np
import pdb

class Body(object):

    def __init__(self, b):
        self._osimBody = b
        self._massScaleFactor = None
        self._inertialScaleFactor = None

    @property
    def name(self):
        return self._osimBody.getName()

    @name.setter
    def name(self, name):
        self._osimBody.setName(name)

    @property
    def mass(self):
        return self._osimBody.getMass()

    @mass.setter
    def mass(self, m):
        self._osimBody.setMass(m)

    @property
    def massCenter(self):
        v = opensim.Vec3()
        self._osimBody.getMassCenter(v)
        return np.array([v.get(i) for i in range(3)])

    @massCenter.setter
    def massCenter(self, x):
        v = opensim.Vec3(x[0], x[1], x[2])
        self._osimBody.setMassCenter(v)

    @property
    def inertia(self):
        m = opensim.Mat33()
        ma = np.zeros((3,3))
        self._osimBody.getInertia(m)
        for i in range(3):
            for j in range(3):
                ma[i,j] = m.get(i,j)
        return ma

    @inertia.setter
    def inertia(self, I):
        inertia = opensim.Inertia(I[0], I[1], I[2])
        self._osimBody.setInertia(inertia)

    @property
    def scaleFactors(self):
        v = opensim.Vec3()
        self._osimBody.getScaleFactors(v)
        return np.array([v.get(i) for i in range(3)])

    @scaleFactors.setter
    def scaleFactors(self, s):
        v = opensim.Vec3(s[0], s[1], s[2])
        self._osimBody.scale(v)
    
    def scale(self, scaleFactors, scaleMass=False):
        v = opensim.Vec3(scaleFactors[0], scaleFactors[1], scaleFactors[2])
        self._osimBody.scale(v, scaleMass)

    def scaleInertialProperties(self, scaleFactors, scaleMass=True):
        v = opensim.Vec3(scaleFactors[0], scaleFactors[1], scaleFactors[2])
        self._osimBody.scaleInertialProperties(v, scaleMass)

    def scaleMass(self, scaleFactor):
        self._osimBody.scaleMass(scaleFactor)

    def setDisplayGeometryFileName(self, filenames):
        geoset = self._osimBody.getDisplayer().getGeometrySet()
        nGeoms = geoset.getSize()

        # # remove existing geoms
        # for gi in xrange(nGeoms):
        #     geoset.remove(0)

        # # add new geoms
        # for fi, fn in enumerate(filenames):
        #     dgnew = opensim.DisplayGeometry()
        #     dgnew.setGeometryFile(fn)
        #     geoset.insert(fi, dgnew)

        # remove existing geoms
        if len(filenames)!=nGeoms:
            raise ValueError(
                'Expected {} filenames, got {}'.format(
                    nGeoms, len(filenames)
                    )
                )

        # add new geoms
        for fi, fn in enumerate(filenames):
            disp_geo = geoset.get(fi)
            disp_geo.setGeometryFile(fn)

        # if oldfilename is None:
        #     visibles.setGeometryFileName(0, filename)
        # else:
        #     for i in xrange(visibles.getNumGeometryFiles()):
        #         if oldfilename==visibles.getGeometryFileName(i):
        #             visibles.setGeometryFileName(i, filename)

class PathPoint(object):

    def __init__(self, p):
        self._osimPathPoint = p

    @property
    def name(self):
        return self._osimPathPoint.getName()

    @name.setter
    def name(self, name):
        self._osimPathPoint.setName(name)

    @property
    def location(self):
        return np.array([self._osimPathPoint.getLocationCoord(i) for i in range(3)])

    @location.setter
    def location(self, x):
        self._osimPathPoint.setLocationCoord(0, x[0])
        self._osimPathPoint.setLocationCoord(1, x[1])
        self._osimPathPoint.setLocationCoord(2, x[2])

    @property
    def body(self):
        return Body(self._osimPathPoint.getBody())

    def scale(self, sf):
        raise(NotImplementedError)
        # state = opensim.State()
        # scaleset = opensim.ScaleSet() # ???
        # scaleset.setScale([integer]) #???
        # mus._osimMuscle.scale(state, scaleset)
    
    
class Muscle(object):

    def __init__(self, m):
        self._osimMuscle = m
        self.path_points = {}
        self._init_path_points()

    def _init_path_points(self):
        pps = self.getAllPathPoints()
        for pp in pps:
            self.path_points[pp.name] = pp

    @property
    def name(self):
        return self._osimMuscle.getName()

    @name.setter
    def name(self, name):
        self._osimMuscle.setName(name)

    def getPathPoint(self, i):
        gp = self._osimMuscle.getGeometryPath()
        pathPoints = gp.getPathPointSet()
        pp = pathPoints.get(i)
        return PathPoint(pp)

    def getAllPathPoints(self):
        pps = []
        gp = self._osimMuscle.getGeometryPath()
        pathPoints = gp.getPathPointSet()
        for i in range(pathPoints.getSize()):
            pp = pathPoints.get(i)
            pps.append(PathPoint(pp))

        return pps

    def scale(self, sf):
        raise(NotImplementedError)
        # state = opensim.State()
        # scaleset = opensim.ScaleSet() # ???
        # scaleset.setScale([integer]) #???
        # mus._osimMuscle.scale(state, scaleset)

class CoordinateSet(object):

    def __init__(self, cs):
        self._cs = cs
        self._defaultValue = None

    @property
    def defaultValue(self):
        return self._cs.getDefaultValue()

    @defaultValue.setter
    def defaultValue(self, x):
        self._cs.setDefaultValue(x)
    
class Joint(object):

    def __init__(self, j):
        self._osimJoint = j
        self.coordSets = {}
        cs = self._osimJoint.getCoordinateSet()
        for csi in range(cs.getSize()):
            _cs = cs.get(csi)
            self.coordSets[_cs.getName()] = CoordinateSet(_cs)

    @property
    def locationInParent(self):
        v = opensim.Vec3()
        self._osimJoint.getLocationInParent(v)
        return np.array([v.get(i) for i in range(3)])
    
    @locationInParent.setter
    def locationInParent(self, x):
        v = opensim.Vec3(x[0], x[1], x[2])
        self._osimJoint.setLocationInParent(v)

    @property
    def location(self):
        v = opensim.Vec3()
        self._osimJoint.getLocation(v)
        return np.array([v.get(i) for i in range(3)])
    
    @location.setter
    def location(self, x):
        v = opensim.Vec3(x[0], x[1], x[2])
        self._osimJoint.setLocation(v)

    @property
    def orientationInParent(self):
        v = opensim.Vec3()
        self._osimJoint.getOrientationInParent(v)
        return np.array([v.get(i) for i in range(3)])
    
    @orientationInParent.setter
    def orientationInParent(self, x):
        v = opensim.Vec3(x[0], x[1], x[2])
        self._osimJoint.setOrientationInParent(v)

    @property
    def orientation(self):
        v = opensim.Vec3()
        self._osimJoint.getOrientation(v)
        return np.array([v.get(i) for i in range(3)])
    
    @orientation.setter
    def orientation(self, x):
        v = opensim.Vec3(x[0], x[1], x[2])
        self._osimJoint.setOrientation(v)

    @property
    def parentName(self):
        return self._osimJoint.getParentName()

    @parentName.setter
    def parentName(self, name):
        self._osimJoint.setParentName(name)

    def scale(self, sf):
        raise(NotImplementedError)
        # scaleset = opensim.ScaleSet() # ???
        # scaleset.setScale([integer]) #???
        # mus._osimMuscle.scale(state, scaleset)
    
class Model(object):

    def __init__(self, filename=None):
        if filename is not None:
            self.load(filename)
        self.joints = {}
        self.bodies = {}
        self.muscles = {}
        self._init_joints()
        self._init_bodies()
        self._init_muscles()

    def load(self, filename):
        self._model = opensim.Model(filename)

    def save(self, filename):
        self._model.printToXML(filename)

    def _init_joints(self):
        """
        Make a dict of all joints in model
        """
        joints = self._model.getJointSet()
        for ji in range(joints.getSize()):
            j = joints.get(ji)
            self.joints[j.getName()] = Joint(j)

    def _init_bodies(self):
        """
        Make a dict of all bodies in model
        """
        bodies = self._model.getBodySet()
        for bi in range(bodies.getSize()):
            b = bodies.get(bi)
            self.bodies[b.getName()] = Body(b)

    def _init_muscles(self):
        """
        Make a dict of all muscles in body
        """
        muscles = self._model.getMuscles()
        for mi in range(muscles.getSize()):
            m = muscles.get(mi)
            self.muscles[m.getName()] = Muscle(m)