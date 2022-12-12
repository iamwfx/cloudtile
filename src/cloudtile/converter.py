# -*- coding: utf-8 -*-
"""
Created on Wednesday, 31st December 1969 7:00:00 pm
===============================================================================
@filename:  converter.py
@author:    Manuel Martinez (manmart@uchicago.edu)
@project:   cloudtile
@purpose:   Convert between file types.
===============================================================================
"""
from dataclasses import dataclass, field

from cloudtile.geofile import FlatGeobuf, GeoFile, MBTiles, PMTiles, VectorFile


@dataclass
class Converter:
    """
    This class represents an instance of a conversion between two files.

    Raises:
        TypeError: If you're trying to set the origin attribute as something
            other than a GeoFile subclass.
        ValueError: If you're trying to create a VectorTile file using a file
            format that's not explicitely supported.
    """

    origin_str: str
    remote: bool = False
    _origin: GeoFile = field(init=False)

    def __post_init__(self):
        self.origin = self.load_file(self.origin_str, self.remote)

    @property
    def origin(self) -> GeoFile:
        """
        The origin or source file object that we wish to convert.
        """
        return self._origin

    @origin.setter
    def origin(self, value: GeoFile) -> None:
        if not isinstance(value, GeoFile):
            raise TypeError("origin must be a subclass of GeoFile")
        self._origin = value

    def convert(self, **kwargs):
        """
        Converts the origin file object and uploads it to S3 once done. If
        the files are being downloaded and uploaded from S3 the local temp
        files are deleted afterwards.
        """
        if isinstance(self.origin, FlatGeobuf):
            self.origin.set_zoom_levels(**kwargs)

        result = self.origin.convert()

        if self.remote:
            result.upload()
            self.origin.remove()
            result.remove()

    @staticmethod
    def load_file(origin_str: str, remote: bool) -> GeoFile:
        """
        Helper method for distributing filenames into their respective GeoFile
        subclasses.

        Args:
            origin_str (str): The origin file name.
            remote (bool): Whether the file is located in the S3 (True) or if
                the file is located in the local machine (False)
        Raises:
            ValueError: If you're trying to create a VectorTile file using a
                file format that's not explicitely supported.

        Returns:
            GeoFile: A GeoFile subclass that will be converted.
        """
        origin: GeoFile
        if origin_str.endswith(".fgb"):
            if remote:
                origin = FlatGeobuf.from_s3(file_key=origin_str)
            else:
                origin = FlatGeobuf(fpath_str=origin_str)

        elif origin_str.endswith(".mbtiles"):
            if remote:
                origin = MBTiles.from_s3(file_key=origin_str)
            else:
                origin = MBTiles(fpath_str=origin_str)
        elif origin_str.endswith(".pmtiles"):
            if remote:
                origin = PMTiles.from_s3(file_key=origin_str)
            else:
                origin = PMTiles(fpath_str=origin_str)
        else:
            try:
                if remote:
                    origin = VectorFile.from_s3(file_key=origin_str)
                else:
                    origin = VectorFile(fpath_str=origin_str)
            except ValueError as e:
                raise e from e

        return origin
