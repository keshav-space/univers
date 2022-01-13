#
# Copyright (c) nexB Inc. and others.
# SPDX-License-Identifier: Apache-2.0
#
# Visit https://aboutcode.org and https://github.com/nexB/univers for support and download.

from unittest import TestCase
import pytest

from univers.version_constraint import VersionConstraint
from univers.version_range import GemVersionRange
from univers.version_range import PypiVersionRange
from univers.version_range import VersionRange
from univers.version_range import RANGE_CLASS_BY_SCHEMES
from univers.versions import PypiVersion
from univers.versions import RubygemsVersion


class TestVersionRange(TestCase):
    def test_VersionRange_afrom_string(self):
        version_range = VersionRange.from_string("vers:pypi/>0.0.2")
        assert version_range == PypiVersionRange(
            constraints=[VersionConstraint(comparator=">", version=PypiVersion(string="0.0.2"))]
        )

    def test_VersionRange_to_string(self):
        vers = "vers:pypi/0.0.2|0.0.6|>=0.0.0|0.0.1|0.0.4|0.0.5|0.0.3"
        version_range = VersionRange.from_string(vers)
        # note the sorting taking place
        assert str(version_range) == "vers:pypi/>=0.0.0|0.0.1|0.0.2|0.0.3|0.0.4|0.0.5|0.0.6"

    def test_VersionRange_pypi_does_not_contain_basic(self):
        vers = "vers:pypi/0.0.2|0.0.6|>=0.0.0|0.0.1|0.0.4|0.0.5|0.0.3"
        version_range = VersionRange.from_string(vers)
        assert not version_range.contains(PypiVersion("2.0.3"))

    def test_VersionRange_does_not_contain_version_after_range(self):
        vers = "vers:pypi/>=1.0.0|<=2.0.0"
        version_range = VersionRange.from_string(vers)
        assert not version_range.contains(PypiVersion("2.0.3"))

    def test_VersionRange_does_not_contain_version_before_range(self):
        vers = "vers:pypi/>=1.0.0|<=2.0.0"
        version_range = VersionRange.from_string(vers)
        assert not version_range.contains(PypiVersion("0.0.9"))

    def test_VersionRange_does_not_contain_version_in_between(self):
        vers = "vers:pypi/<=1.0.0|>=2.0.0"
        version_range = VersionRange.from_string(vers)
        assert not version_range.contains(PypiVersion("1.5"))

    def test_VersionRange_does_not_contain_version_excluded(self):
        vers = "vers:pypi/>=3.0.0|!=2.0.3"
        version_range = VersionRange.from_string(vers)
        assert not version_range.contains(PypiVersion("2.0.3"))

    def test_VersionRange_contains_version_after(self):
        version_range = VersionRange.from_string("vers:pypi/>0.0.2")
        assert PypiVersion("0.0.3") in version_range

    def test_VersionRange_contains_version_before(self):
        version_range = VersionRange.from_string("vers:pypi/<0.0.2")
        assert PypiVersion("0.0.0.1") in version_range

    def test_VersionRange_contains_version_included(self):
        vers = "vers:pypi/>=3.0.0|2.0.3"
        version_range = VersionRange.from_string(vers)
        assert version_range.contains(PypiVersion("2.0.3"))

    def test_VersionRange_contains_version_in_between(self):
        vers = "vers:pypi/>=1.0.0|<=2.0.0"
        version_range = VersionRange.from_string(vers)
        assert version_range.contains(PypiVersion("1.5"))

    def test_VersionRange_from_string_pypi(self):
        vers = "vers:pypi/0.0.2|0.0.6|0.0.0|0.0.1|0.0.4|0.0.5|0.0.3"
        version_range = VersionRange.from_string(vers)
        assert version_range.scheme == "pypi"
        # note the sorting taking place
        expected = (
            VersionConstraint(comparator="=", version=PypiVersion(string="0.0.0")),
            VersionConstraint(comparator="=", version=PypiVersion(string="0.0.1")),
            VersionConstraint(comparator="=", version=PypiVersion(string="0.0.2")),
            VersionConstraint(comparator="=", version=PypiVersion(string="0.0.3")),
            VersionConstraint(comparator="=", version=PypiVersion(string="0.0.4")),
            VersionConstraint(comparator="=", version=PypiVersion(string="0.0.5")),
            VersionConstraint(comparator="=", version=PypiVersion(string="0.0.6")),
        )
        assert version_range.constraints == expected
        # note the sorting taking place
        assert str(version_range) == "vers:pypi/0.0.0|0.0.1|0.0.2|0.0.3|0.0.4|0.0.5|0.0.6"

        version_range1 = VersionRange.from_string(vers, simplify=False, validate=True)
        assert version_range1.constraints == expected

        version_range2 = VersionRange.from_string(vers, simplify=True, validate=False)
        assert version_range2.constraints == expected

        version_range3 = VersionRange.from_string(vers, simplify=True, validate=True)
        assert version_range3.constraints == expected

    def test_VersionRange_from_string_pypi_complex_simplify(self):
        vers = "vers:pypi/>0.0.0|>=0.0.1|0.0.2|<0.0.3|0.0.4|<0.0.5|>=0.0.6"
        version_range = VersionRange.from_string(vers, simplify=True)
        assert str(version_range) == "vers:pypi/>0.0.0|<0.0.5|>=0.0.6"
        try:
            version_range = VersionRange.from_string(vers, validate=True)
            raise Exception(f"Exception not raised: {vers}")
        except ValueError:
            pass
        version_range = VersionRange.from_string(vers, validate=True, simplify=True)
        assert str(version_range) == "vers:pypi/>0.0.0|<0.0.5|>=0.0.6"

    def test_VersionRange_from_string_pypi_complex_simplify_and_validate(self):
        vers = "vers:pypi/>0.0.0|>=0.0.1|0.0.2|0.0.3|0.0.4|<0.0.5|>=0.0.6|!=0.8"
        version_range = VersionRange.from_string(vers, simplify=True)
        assert str(version_range) == "vers:pypi/>0.0.0|<0.0.5|>=0.0.6|!=0.8"
        version_range = VersionRange.from_string(vers, simplify=True, validate=True)

    def test_VersionRange_from_string_pypi_complex_simplify2(self):
        vers = (
            "vers:pypi/>0.0.0|>=0.0.1|>=0.0.1|0.0.2|0.0.3|0.0.4|<0.0.5|<=0.0.6|!=0.7|8.0|>12|<15.3"
        )
        version_range = VersionRange.from_string(vers, simplify=True)
        assert str(version_range) == "vers:pypi/>0.0.0|<=0.0.6|!=0.7|8.0|>12|<15.3"

    def test_VersionRange_from_string_pypi_simple_cases(self):
        vers = "vers:pypi/>0.0.1"
        version_range = VersionRange.from_string(vers, simplify=True, validate=True)
        assert str(version_range) == vers

        vers = "vers:pypi/>=0.0.1"
        version_range = VersionRange.from_string(vers, simplify=True, validate=True)
        assert str(version_range) == vers

        vers = "vers:pypi/<0.0.1"
        version_range = VersionRange.from_string(vers, simplify=True, validate=True)
        assert str(version_range) == vers

        vers = "vers:pypi/<=0.0.1"
        version_range = VersionRange.from_string(vers, simplify=True, validate=True)
        assert str(version_range) == vers

        vers = "vers:pypi/0.0.1"
        version_range = VersionRange.from_string(vers, simplify=True, validate=True)
        assert str(version_range) == vers

        vers = "vers:pypi/!=0.0.1"
        version_range = VersionRange.from_string(vers, simplify=True, validate=True)
        assert str(version_range) == vers

        vers = "vers:pypi/*"
        version_range = VersionRange.from_string(vers, simplify=True, validate=True)
        assert str(version_range) == vers

    def test_VersionRange_from_string_pypi_two_cases(self):
        vers = "vers:pypi/>0.0.1|<0.1"
        version_range = VersionRange.from_string(vers, simplify=True, validate=True)
        assert str(version_range) == vers

        vers = "vers:pypi/>=0.0.1|<0.1"
        version_range = VersionRange.from_string(vers, simplify=True, validate=True)
        assert str(version_range) == vers

        vers = "vers:pypi/<0.0.1|>0.1"
        version_range = VersionRange.from_string(vers, simplify=True, validate=True)
        assert str(version_range) == vers

        vers = "vers:pypi/<=0.0.1|>0.1"
        version_range = VersionRange.from_string(vers, simplify=True, validate=True)
        assert str(version_range) == vers

        vers = "vers:pypi/0.0.1|>0.1"
        version_range = VersionRange.from_string(vers, simplify=True, validate=True)
        assert str(version_range) == vers

        vers = "vers:pypi/!=0.0.1|>0.1"
        version_range = VersionRange.from_string(vers, simplify=True, validate=True)
        assert str(version_range) == vers

    def test_GemVersionRange_from_native_range_with_pessimistic_operator(self):
        gem_range = "~>2.0.8"
        version_range = GemVersionRange.from_native(gem_range)
        assert version_range.to_string() == "vers:gem/>=2.0.8|<2.1"
        assert version_range.constraints == (
            VersionConstraint(comparator=">=", version=RubygemsVersion(string="2.0.8")),
            VersionConstraint(comparator="<", version=RubygemsVersion(string="2.1")),
        )

    def test_VersionRange_contains_works_for_star_range(self):
        from univers.versions import SemverVersion

        SemverVersion("1.0.0") in VersionRange.from_string("vers:nginx/*")

@pytest.mark.parametrize("scheme, range_class", RANGE_CLASS_BY_SCHEMES.items())
class TestVersionRangeImplementations:
    VERSION_RANGES_BY_SCHEMES = {
        "nginx": ["0.8.40+", "0.7.52-0.8.39", "0.9.10", "1.5.0+, 1.4.1+"],
    }

    def test_from_native_and_from_string_equality(self, scheme, range_class):
        if scheme not in self.VERSION_RANGES_BY_SCHEMES:
            pytest.skip(f"No {scheme} in VERSION_RANGES_BY_SCHEMES")

        for rng in self.VERSION_RANGES_BY_SCHEMES.get(scheme, []):
            rng_from_native = range_class.from_native(rng)
            rng_from_string = range_class.from_string(rng_from_native.to_string())
            assert rng_from_native == rng_from_string
