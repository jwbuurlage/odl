# Copyright 2014-2017 The ODL contributors
#
# This file is part of ODL.
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at https://mozilla.org/MPL/2.0/.

"""Tomography helpers for Elekta systems."""

import numpy as np
import odl


__all__ = ('elekta_icon_geometry', 'elekta_icon_space',
           'elekta_icon_reconstruction')


def elekta_icon_geometry(sad=780, sdd=1000,
                         piercing_point=(390.0, 0.0),
                         angles=np.linspace(1.2, 5.0, 332),
                         detector_shape=(780, 720)):
    """Tomographic geometry of the Elekta Icon CBCT system.

    See the [whitepaper]_ for specific descriptions of each parameter.

    All measurments are given in millimeters unless otherwise stated.

    Parameters
    ----------
    sad : float, optional
        Source to Axis distance.
    sdd : float, optional
        Source to Detector distance.
    piercing_point : sequence of foat
        Position in the detector (in pixel coordinates) that a beam from the
        source, passing through the axis of rotation at a straight angle,
        hits.
    angles : array-like, optional
        List of angles that the projection images were taken at.
        Given in radians.
    detector_shape : sequence of int, optional
        Shape of the detector (in pixels). Useful if a sub-sampled system
        should be studied.

    See Also
    --------
    elekta_icon_space : Default reconstruction space for the Elekta Icon CBCT.

    References
    ----------
    .. [whitepaper] *Design and performance characteristics of a Cone Beam
       CT system for Leksell Gamma Knife Icon*
    """
    sad = float(sad)
    assert sad > 0
    sdd = float(sdd)
    assert sdd > sad
    piercing_point = np.array(piercing_point, dtype=float)
    assert piercing_point.size == 2
    angles = np.array(angles, dtype=float)
    detector_shape = np.array(detector_shape, dtype=int)

    # Constant system parameters
    pixel_size = 0.368
    det_shape_mm = np.array([287.04, 264.96])

    # Create a (possible non-uniform) partition given the angles
    angle_partition = odl.nonuniform_partition(angles)

    # Compute the detector partition
    piercing_point_mm = pixel_size * piercing_point
    det_min_pt = -piercing_point_mm
    det_max_pt = det_min_pt + det_shape_mm
    detector_partition = odl.uniform_partition(min_pt=det_min_pt,
                                               max_pt=det_max_pt,
                                               shape=detector_shape)

    # Create the geometry
    geometry = odl.tomo.CircularConeFlatGeometry(
        angle_partition, detector_partition,
        src_radius=sad, det_radius=sdd - sad,
        axis=[0, 0, 1])

    return geometry


def elekta_icon_space(shape=(448, 448, 448), **kwargs):
    """Default reconstruction space for the Elekta Icon CBCT.

    See the [whitepaper]_ for further information.

    Parameters
    ----------
    shape : sequence of int, optional
        Shape of the space, in voxels.
    kwargs :
        Keyword arguments to pass to `uniform_discr` to modify the space, e.g.
        use another backend.

    Returns
    -------
    elekta_icon_geometry : DiscreteLp

    Examples
    --------
    >>> space = odl.contrib.tomo.elekta_icon_volume()
    """
    return odl.uniform_discr(min_pt=[-112.0, -112.0, 0.0],
                             max_pt=[112.0, 112.0, 224.0],
                             shape=shape,
                             dtype='float32')


def elekta_icon_reconstruction(ray_transform, parker_weighting=True):
    """Approximation of the FDK reconstruction used in the Elekta Icon."""

    fbp_op = odl.tomo.fbp_op(ray_transform, padding=False,
                             filter_type='Hann', frequency_scaling=0.6)
    if parker_weighting:
        parker_weighting = odl.tomo.parker_weighting(ray_transform)
        fbp_op = fbp_op * parker_weighting

    return fbp_op


if __name__ == '__main__':
    # Run doctests
    # pylint: disable=wrong-import-position
    from odl.util.testutils import run_doctests
    run_doctests()
