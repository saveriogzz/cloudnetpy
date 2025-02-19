""" This module contains unit tests for ceilo-module. """
from cloudnetpy.instruments import ceilo
import pytest
from os import path
from tempfile import NamedTemporaryFile
import netCDF4
from numpy.testing import assert_almost_equal


SCRIPT_PATH = path.dirname(path.realpath(__file__))


def test_find_ceilo_model_jenoptik():
    assert ceilo._find_ceilo_model('ceilo.nc') == 'chm15k'


@pytest.mark.parametrize("fix, result", [
    ('CL01', 'cl31_or_cl51'),
    ('CL02', 'cl31_or_cl51'),
    ('CT02', 'ct25k'),
])
def test_find_ceilo_model_vaisala(fix, result, tmpdir):
    file_name = '/'.join((str(tmpdir), 'ceilo.txt'))
    f = open(file_name, 'w')
    f.write('row\n')
    f.write('\n')
    f.write('row\n')
    f.write(f"-{fix}\n")
    f.close()
    assert ceilo._find_ceilo_model(str(file_name)) == result


def test_cl51_reading():
    output_file = NamedTemporaryFile()
    file = f'{SCRIPT_PATH}/data/vaisala/cl51.DAT'
    ceilo.ceilo2nc(file, output_file.name, {'name': 'Norunda', 'altitude': 100})
    nc = netCDF4.Dataset(output_file.name)
    assert nc.source == 'cl51'
    assert nc.cloudnet_file_type == 'lidar'
    assert nc.location == 'Norunda'
    assert nc.year == '2020'
    assert nc.month == '11'
    assert nc.day == '15'
    assert nc.variables['time'].shape == (2,)
    assert nc.variables['tilt_angle'][:].all() < 5
    assert_almost_equal(nc.variables['altitude'][:], 100)
    nc.close()


def test_cl31_reading():
    output_file = NamedTemporaryFile()
    file = f'{SCRIPT_PATH}/data/vaisala/cl31.DAT'
    ceilo.ceilo2nc(file, output_file.name, {'name': 'Norunda', 'altitude': 100})
    nc = netCDF4.Dataset(output_file.name)
    assert nc.source == 'cl31'
    assert_almost_equal(nc.variables['wavelength'][:], 910)
    nc.close()
