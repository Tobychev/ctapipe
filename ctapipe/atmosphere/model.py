#!/usr/bin/env python3

"""Atmosphere density models and functions to transform between column density
(X in grammage units) and height (meters) units.

Zenith angle is taken into account in the line-of-sight integral to compute the
column density X assuming Earth as a flat plane (the curvature is not taken into
account)

"""

import abc
from dataclasses import dataclass
from functools import partial

import numpy as np
from astropy import units as u
from astropy.table import Table
from scipy.interpolate import interp1d

__all__ = [
    "AtmosphereDensityProfile",
    "ExponentialAtmosphereDensityProfile",
    "TableAtmosphereDensityProfile",
    "FiveLayerAtmosphereDensityProfile",
]


class AtmosphereDensityProfile:
    """
    Base class for models of atmosphere density.
    """

    @abc.abstractmethod
    def __call__(self, h: u.Quantity) -> u.Quantity:
        """
        Returns
        -------
        u.Quantity["g cm-3"]
            the density at height h
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def integral(self, h: u.Quantity, output_units=u.g / u.cm**2) -> u.Quantity:
        """
        Integral of the profile along the height axis

        Returns
        -------
        u.Quantity["g/cm2"]:
            Integral of the density from height h to infinity
        """
        raise NotImplementedError()

    def line_of_sight_integral(
        self, distance: u.Quantity, zenith_angle=0 * u.deg, output_units=u.g / u.cm**2
    ):
        """Line-of-sight integral from the shower distance to infinity, along
        the direction specified by the zenith angle. The atmosphere here is
        assumed to be Cartesian, the curvature of the Earth is not taken into account.

        .. math:: X(h', \\Psi) = \\int_{h'}^{\\infty} \\rho(h \\cos{\\Psi}) dh

        Parameters
        ----------
        distance: u.Quantity["length"]
           line-of-site distance from observer to point
        zenith_angle: u.Quantity["angle"]
           zenith angle of observation
        output_units: u.Unit
           unit to output (must be convertible to g/cm2)
        """

        return (
            self.integral(distance * np.cos(zenith_angle)) / np.cos(zenith_angle)
        ).to(output_units)

    def peek(self):
        """
        Draw quick plot of profile
        """
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(1, 3, constrained_layout=True, figsize=(10, 3))

        fig.suptitle(self.__class__.__name__)
        height = np.linspace(1, 100, 500) * u.km
        density = self(height)
        ax[0].set_xscale("linear")
        ax[0].set_yscale("log")
        ax[0].plot(height, density)
        ax[0].set_xlabel(f"Height / {height.unit.to_string('latex')}")
        ax[0].set_ylabel(f"Density / {density.unit.to_string('latex')}")
        ax[0].grid(True)

        distance = np.linspace(1, 100, 500) * u.km
        for zenith_angle in [0, 40, 50, 70] * u.deg:
            column_density = self.line_of_sight_integral(distance, zenith_angle)
            ax[1].plot(distance, column_density, label=f"$\\Psi$={zenith_angle}")

        ax[1].legend(loc="best")
        ax[1].set_xlabel(f"Distance / {distance.unit.to_string('latex')}")
        ax[1].set_ylabel(f"Column Density / {column_density.unit.to_string('latex')}")
        ax[1].set_yscale("log")
        ax[1].grid(True)

        zenith_angle = np.linspace(0, 80, 20) * u.deg
        for distance in [0, 5, 10, 20] * u.km:
            column_density = self.line_of_sight_integral(distance, zenith_angle)
            ax[2].plot(zenith_angle, column_density, label=f"Height={distance}")

        ax[2].legend(loc="best")
        ax[2].set_xlabel(
            f"Zenith Angle $\\Psi$ / {zenith_angle.unit.to_string('latex')}"
        )
        ax[2].set_ylabel(f"Column Density / {column_density.unit.to_string('latex')}")
        ax[2].set_yscale("log")
        ax[2].grid(True)

        plt.show()


@dataclass
class ExponentialAtmosphereDensityProfile(AtmosphereDensityProfile):
    """
    A simple functional density profile modeled as an exponential.

    The is defined following the form:

    .. math:: \\rho(h) = \\rho_0 e^{-h/h_0}


    .. code-block:: python

        from ctapipe.atmosphere import ExponentialAtmosphereDensityProfile
        density_profile = ExponentialAtmosphereDensityProfile()
        density_profile.peek()


    Attributes
    ----------
    h0: u.Quantity["m"]
        scale height
    rho0: u.Quantity["g cm-3"]
        scale density
    """

    h0: u.Quantity = 8 * u.km
    rho0: u.Quantity = 0.00125 * u.g / (u.cm**3)

    @u.quantity_input(h=u.m)
    def __call__(self, h) -> u.Quantity:
        return self.rho0 * np.exp(-h / self.h0)

    @u.quantity_input(h=u.m)
    def integral(
        self,
        h,
        output_units=u.g / u.cm**2,
    ) -> u.Quantity:
        return self.rho0 * self.h0 * np.exp(-h / self.h0)


class TableAtmosphereDensityProfile(AtmosphereDensityProfile):
    """Tabular profile from a table that has both the density and it's integral
    pre-computed.  The table is interpolated to return the density and its integral.

    .. code-block:: python

        from astropy.table import Table
        from astropy import units as u

        from ctapipe.atmosphere import TableAtmosphereDensityProfile

        table = Table(
            dict(
                height=[1,10,20] * u.km,
                density=[0.00099,0.00042, 0.00009] * u.g / u.cm**3
                column_density=[1044.0, 284.0, 57.0] * u.g / u.cm**2
            )
        )

        profile = TableAtmosphereDensityProfile(table=table)
        print(profile(10 * u.km))


    Attributes
    ----------
    table: Table
        Points that define the model

    See Also
    --------
    ctapipe.io.eventsource.EventSource.atmosphere_profile:
        load a TableAtmosphereDensityProfile from a supported EventSource
    """

    def __init__(self, table: Table):
        """
        Parameters
        ----------
        table: Table
            Table with columns `height`, `density`, and `column_density`
        """

        for col in ["height", "density", "column_density"]:
            if col not in table.colnames:
                raise ValueError(f"Missing expected column: {col} in table")

        self.table = table[
            (table["height"] >= 0)
            & (table["density"] > 0)
            & (table["column_density"] > 0)
        ]

        # interpolation is done in log-y to minimize spline wobble

        self._density_interp = interp1d(
            self.table["height"].to("km").value,
            np.log10(self.table["density"].to("g cm-3").value),
            kind="cubic",
        )
        self._col_density_interp = interp1d(
            self.table["height"].to("km").value,
            np.log10(self.table["column_density"].to("g cm-2").value),
            kind="cubic",
        )

    @u.quantity_input(h=u.m)
    def __call__(self, h) -> u.Quantity:
        return u.Quantity(10 ** self._density_interp(h.to_value(u.km)), u.g / u.cm**3)

    @u.quantity_input(h=u.m)
    def integral(self, h) -> u.Quantity:
        return u.Quantity(
            10 ** self._col_density_interp(h.to_value(u.km)), u.g / u.cm**2
        )

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(meta={self.table.meta}, rows={len(self.table)})"
        )


def _exponential(h, a, b, c):
    """exponential atmosphere"""
    return a + b * np.exp(-h / c)


def _d_exponential(h, a, b, c):
    """derivative of exponential atmosphere"""
    return -b / c * np.exp(-h / c)


def _linear(h, a, b, c):
    """linear atmosphere"""
    return a - b * h / c


def _d_linear(h, a, b, c):
    """derivative of linear atmosphere"""
    return -b / c


class FiveLayerAtmosphereDensityProfile(AtmosphereDensityProfile):
    r"""
    CORSIKA 5-layer atmosphere model

    Layers 1-4  are modeled with:

    .. math:: T(h) = a_i + b_i \exp{-h/c_i}

    Layer 5 is modeled with:

    ..math:: T(h) = a_5 - b_5 \frac{h}{c_5}

    References
    ----------
    [corsika-user] D. Heck and T. Pierog, "Extensive Air Shower Simulation with CORSIKA:
        A User’s Guide", 2021, Appendix F
    """

    def __init__(self, table: Table):
        self.table = table
        self._funcs = []

        param_a = self.table["a"].to("g/cm2")
        param_b = self.table["b"].to("g/cm2")
        param_c = self.table["c"].to("km")

        # build list of column density functions and their derivatives:
        self._funcs = [
            partial(f, a=param_a[i], b=param_b[i], c=param_c[i])
            for i, f in enumerate([_exponential] * 4 + [_linear])
        ]
        self._d_funcs = [
            partial(f, a=param_a[i], b=param_b[i], c=param_c[i])
            for i, f in enumerate([_d_exponential] * 4 + [_d_linear])
        ]

    @classmethod
    def from_array(cls, array: np.ndarray):
        """construct from a 5x5 array as provided by eventio"""

        if array.shape != (5, 5):
            raise ValueError("expected ndarray with shape (5,5)")

        table = Table(
            array,
            names=["height", "a", "b", "c", "1/c"],
            units=["cm", "g/cm2", "g/cm2", "cm", "cm-1"],
        )
        return cls(table)

    @u.quantity_input(h=u.m)
    def __call__(self, h) -> u.Quantity:
        which_func = np.digitize(h, self.table["height"]) - 1
        condlist = [which_func == i for i in range(5)]
        return -1 * np.piecewise(
            h,
            condlist=condlist,
            funclist=self._d_funcs,
        ).to(u.g / u.cm**3)

    @u.quantity_input(h=u.m)
    def integral(self, h) -> u.Quantity:
        which_func = np.digitize(h, self.table["height"]) - 1
        condlist = [which_func == i for i in range(5)]
        return np.piecewise(
            x=h,
            condlist=condlist,
            funclist=self._funcs,
        ).to(u.g / u.cm**2)
